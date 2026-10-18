import asyncio
import hashlib
import hmac
import json
import logging
import time
from collections import OrderedDict
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Literal
from uuid import UUID, uuid4

from fastapi import FastAPI, Header, HTTPException, Query, Request
from fastapi.responses import JSONResponse, FileResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, StrictInt, Field
from prometheus_client import CollectorRegistry, Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from redis.asyncio import Redis
from redis.exceptions import RedisError
from sqlalchemy import select, text
from sqlalchemy.exc import SQLAlchemyError
from starlette.concurrency import run_in_threadpool

from .catalog import Catalog, load_sources, fingerprint
from .config import ROOT, Settings
from .database import make_engine, initialize, read_catalog, persist_result, IdempotencyConflict, catalog_versions, submissions
from .survey import VERSIONS, select_questions, public_questions, validate_answers
from .sharing import create_share, read_share, card_png, share_html, poster_svg
from .i18n import localize_questions, localize_movie, localize_result, localize_snapshot

log = logging.getLogger('moviegame')
logging.basicConfig(level=logging.INFO, format='%(message)s')
RATE_LUA = "local n=redis.call('INCR',KEYS[1]); if n==1 then redis.call('EXPIRE',KEYS[1],120) end; return n"


class MatchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    survey_version: str
    catalog_version: str
    answers: dict[str, StrictInt]
    category: Literal['all', 'hollywood', 'bangladeshi', 'anime'] = 'all'
    mode: Literal['story', 'character'] = 'story'
    seed: UUID | None = None


class ShareRequest(BaseModel):
    model_config = ConfigDict(extra='forbid')
    display_name: str = Field(default='', max_length=48)
    language: Literal['en', 'bn'] = 'en'


class Gate:
    """Bound memory, body size/time, and concurrent work before parsing JSON."""
    def __init__(self, app, settings):
        self.app, self.settings = app, settings
        self.slots = asyncio.Semaphore(settings.max_inflight)
        self.local_rates = OrderedDict()

    async def __call__(self, scope, receive, send):
        if scope['type'] != 'http':
            return await self.app(scope, receive, send)
        started, request_id, status = time.monotonic(), str(uuid4()), 500
        path = scope['path']
        state = scope['app'].state
        protected = path.startswith(('/api/', '/s/'))
        headers = [(b'x-request-id', request_id.encode()), (b'x-content-type-options', b'nosniff'),
            (b'referrer-policy', b'no-referrer'), (b'x-frame-options', b'DENY'),
            (b'content-security-policy', b"default-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://upload.wikimedia.org; script-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'self'; frame-ancestors 'none'")]
        async def wrapped_send(message):
            nonlocal status
            if message['type'] == 'http.response.start':
                status = message['status']
                message['headers'] = list(message.get('headers', [])) + headers
                if scope['method'] != 'GET' or status >= 400:
                    message['headers'].append((b'cache-control', b'no-store'))
            await send(message)
        async def reject(code, detail, retry=False):
            response = JSONResponse({'detail': detail, 'request_id': request_id}, code,
                                    headers={'Retry-After': '5'} if retry else {})
            await response(scope, receive, wrapped_send)
        acquired = False
        try:
            if protected:
                try:
                    await asyncio.wait_for(self.slots.acquire(), timeout=0.025)
                    acquired = True
                except TimeoutError:
                    return await reject(503, 'The cinema is busy. Please retry in a moment.', True)
            if protected and scope['method'] == 'POST':
                ip = scope.get('client', ('unknown', 0))[0]
                digest = hmac.new(self.settings.rate_secret.encode(), ip.encode(), hashlib.sha256).hexdigest()
                window = int(time.time() // 60)
                key = f'rate:{window}:{digest}'
                try:
                    if state.redis:
                        count = await state.redis.eval(RATE_LUA, 1, key)
                    else:
                        count = self.local_rates.get(key, 0) + 1
                        self.local_rates[key] = count
                        if len(self.local_rates) > 10000:
                            self.local_rates.popitem(last=False)
                except (RedisError, TimeoutError):
                    return await reject(503, 'Submissions are temporarily unavailable. Your answers are still in this tab.', True)
                if count > self.settings.rate_limit:
                    response = JSONResponse({'detail': 'Too many attempts. Please try again next minute.'}, 429,
                                            headers={'Retry-After': str(60 - int(time.time()) % 60)})
                    return await response(scope, receive, wrapped_send)
                chunks, size = [], 0
                try:
                    async with asyncio.timeout(5):
                        while True:
                            message = await receive()
                            if message['type'] == 'http.disconnect':
                                return
                            chunk = message.get('body', b'')
                            size += len(chunk)
                            if size > 8192:
                                return await reject(413, 'Request body exceeds 8 KB.')
                            chunks.append(chunk)
                            if not message.get('more_body', False):
                                break
                except TimeoutError:
                    return await reject(408, 'Request body timed out.')
                delivered = False
                async def buffered_receive():
                    nonlocal delivered
                    if not delivered:
                        delivered = True
                        return {'type': 'http.request', 'body': b''.join(chunks), 'more_body': False}
                    return await receive()
                await self.app(scope, buffered_receive, wrapped_send)
            else:
                await self.app(scope, receive, wrapped_send)
        finally:
            if acquired:
                self.slots.release()
            elapsed = time.monotonic() - started
            route = path if path in ('/api/v1/survey', '/api/v1/catalog', '/api/v1/matches', '/health/live', '/health/ready', '/metrics') else 'static_or_unknown'
            state.requests.labels(route, str(status)).inc()
            state.latency.labels(route).observe(elapsed)
            if protected:
                log.info(json.dumps({'request_id': request_id, 'route': route, 'status': status, 'duration_ms': round(elapsed*1000, 2)}))


def create_app(settings=None):
    settings = settings or Settings()
    settings.validate()
    engine = make_engine(settings)

    @asynccontextmanager
    async def lifespan(app):
        try:
            source = load_sources(ROOT / 'data')
            if settings.environment != 'production':
                await run_in_threadpool(initialize, engine, source)
            loaded = await run_in_threadpool(read_catalog, engine)
            if fingerprint(source) != fingerprint(loaded):
                raise RuntimeError('Bundled catalog does not match the database.')
            app.state.catalog = Catalog(loaded)
            app.state.catalog_views = {'en': loaded, 'bn': [localize_movie(m, 'bn') for m in loaded]}
            app.state.catalog_search = [' '.join([m['title'], *m['themes'], *(c['name'] for c in m['characters']),
                b['title'], *b['themes'], *(c['name'] for c in b['characters'])]).casefold()
                for m, b in zip(loaded, app.state.catalog_views['bn'])]
            if settings.redis_url:
                app.state.redis = Redis.from_url(settings.redis_url, socket_timeout=0.5, socket_connect_timeout=0.5,
                                                max_connections=50, decode_responses=True)
                await app.state.redis.ping()
            yield
        finally:
            if app.state.redis:
                await app.state.redis.aclose()
            engine.dispose()

    app = FastAPI(title='MovieGame', version='1.0.0', lifespan=lifespan,
                  docs_url='/docs' if settings.environment == 'development' else None, redoc_url=None)
    app.state.redis = None
    app.state.engine = engine
    app.state.registry = CollectorRegistry()
    app.state.requests = Counter('moviegame_requests_total', 'HTTP responses', ['route', 'status'], registry=app.state.registry)
    app.state.latency = Histogram('moviegame_request_seconds', 'HTTP latency', ['route'], registry=app.state.registry)
    app.add_middleware(Gate, settings=settings)

    @app.exception_handler(SQLAlchemyError)
    async def database_unavailable(request, exc):
        log.error('database_unavailable: %s', type(exc).__name__)
        return JSONResponse({'detail': 'Could not save the result. Retry with the same key.'}, 503, headers={'Retry-After': '5'})

    @app.get('/health/live')
    def live():
        return {'status': 'alive'}

    @app.get('/health/ready')
    async def ready():
        try:
            def ping():
                with engine.connect() as conn:
                    conn.execute(text('SELECT 1'))
            await run_in_threadpool(ping)
            if app.state.redis:
                await app.state.redis.ping()
            return {'status': 'ready'}
        except (SQLAlchemyError, RedisError, TimeoutError):
            return JSONResponse({'status': 'unavailable'}, 503)

    @app.get('/metrics')
    def metrics(authorization: str = Header(default='')):
        if not settings.metrics_token or not hmac.compare_digest(authorization, f'Bearer {settings.metrics_token}'):
            raise HTTPException(404)
        return Response(generate_latest(app.state.registry), media_type=CONTENT_TYPE_LATEST)

    @app.get('/api/v1/survey')
    def survey(mode: Literal['story', 'character'] = 'story', seed: UUID | None = None,
               lang: Literal['en', 'bn'] = 'en'):
        catalog = app.state.catalog
        seed = str(seed or uuid4())
        questions = select_questions(mode, seed)
        return JSONResponse({'version': VERSIONS[mode], 'catalog_version': catalog.version,
                             'mode': mode, 'seed': seed, 'language': lang,
                             'questions': localize_questions(public_questions(questions), mode, lang),
                             'movie_count': len(catalog.movies), 'character_count': len(catalog.characters),
                             'categories': catalog.counts}, headers={'Cache-Control': 'no-store'})

    @app.get('/api/v1/catalog')
    def browse(q: str = Query('', max_length=100), category: Literal['all', 'hollywood', 'bangladeshi', 'anime'] = 'all',
               page: int = Query(1, ge=1, le=10000), limit: int = Query(12, ge=1, le=48),
               lang: Literal['en', 'bn'] = 'en'):
        query = q.casefold()
        rows = [movie for movie, search in zip(app.state.catalog_views[lang], app.state.catalog_search)
                if (category == 'all' or movie['category'] == category) and (not query or query in search)]
        return JSONResponse({'total': len(rows), 'page': page, 'items': rows[(page-1)*limit:page*limit]},
                             headers={'Cache-Control': 'public, max-age=60'})

    @app.post('/api/v1/matches')
    def match(payload: MatchRequest, idempotency_key: UUID = Header()):
        legacy = payload.seed is None and payload.survey_version == 'story-1' and payload.mode == 'story'
        request_payload = payload.model_dump(mode='json')
        if legacy:
            request_payload = {k:request_payload[k] for k in ('survey_version','catalog_version','category','answers')}
            questions = []
        else:
            if payload.seed is None:
                raise HTTPException(422, 'Send the survey seed returned with these questions.')
            questions = select_questions(payload.mode, str(payload.seed))
            if not validate_answers(payload.answers, questions):
                raise HTTPException(422, 'Answer exactly the 15 questions from this survey with one of their listed options.')
            if payload.mode == 'character' and payload.category != 'all':
                raise HTTPException(422, 'Character Game matches across all movies. Use category=all.')
        # Replays must survive a deployment. New keys are checked against current versions inside compute.
        def compute():
            if payload.survey_version != VERSIONS[payload.mode] or payload.catalog_version != app.state.catalog.version:
                raise HTTPException(409, 'This survey has been updated. Reload to start the current edition.')
            result = app.state.catalog.match(payload.answers, questions, payload.category, payload.mode)
            result['survey_version'] = VERSIONS[payload.mode]
            return result
        try:
            result, replay = persist_result(engine, str(idempotency_key), request_payload, compute, settings.retention_days)
        except IdempotencyConflict:
            raise HTTPException(409, 'This key already belongs to different answers. Start a new quiz.')
        return JSONResponse(result, headers={'Idempotency-Replayed': str(replay).lower(),
                                            'Idempotency-Retention-Days': str(settings.retention_days)})

    @app.get('/api/v1/results/current')
    def current_result(idempotency_key: UUID = Header(), lang: Literal['en', 'bn'] = 'en'):
        key_hash = hashlib.sha256(str(idempotency_key).encode()).hexdigest()
        with engine.connect() as conn:
            result = conn.execute(select(submissions.c.result).where(submissions.c.key_hash == key_hash,
                       submissions.c.expires_at > datetime.now(timezone.utc))).scalar_one_or_none()
        if result is None:
            raise HTTPException(404, 'This result is unavailable or has expired. Complete a new quiz before sharing.')
        return JSONResponse(localize_result(result, lang), headers={'Cache-Control':'no-store'})

    @app.post('/api/v1/shares')
    def share(payload: ShareRequest, idempotency_key: UUID = Header()):
        row = create_share(engine, idempotency_key, payload.display_name, payload.language)
        if row is None:
            raise HTTPException(404, 'This result is unavailable or has expired. Complete a new quiz before sharing.')
        return {'share_url': f'/s/{row["token"]}', 'image_url': f'/s/{row["token"]}/card.png',
                'expires_at': row['expires_at'].isoformat(), 'snapshot': row['snapshot']}

    @app.get('/s/{token}', response_class=HTMLResponse)
    def public_share(token: str, request: Request, lang: Literal['en', 'bn'] | None = None):
        row = read_share(engine, token)
        if row is None:
            raise HTTPException(404, 'This shared result is unavailable or has expired.')
        origin = settings.public_base_url or str(request.base_url).rstrip('/')
        return HTMLResponse(share_html(row, origin, lang), headers={'Cache-Control':'public, max-age=60',
                                                            'X-Robots-Tag':'noindex'})

    @app.get('/s/{token}/card.png')
    def public_card(token: str, download: bool = False, lang: Literal['en', 'bn'] | None = None):
        row = read_share(engine, token)
        if row is None:
            raise HTTPException(404, 'This shared result is unavailable or has expired.')
        language = lang or row['snapshot'].get('language', 'en')
        snapshot = localize_snapshot(row['snapshot'], language)
        content = card_png(json.dumps(snapshot, sort_keys=True, ensure_ascii=False))
        headers = {'Cache-Control':'public, max-age=300', 'X-Robots-Tag':'noindex'}
        if download:
            headers['Content-Disposition'] = 'attachment; filename="moviegame-result.png"'
        return Response(content, media_type='image/png', headers=headers)

    @app.get('/api/v1/posters/{movie_id}.svg')
    def cover(movie_id: str, lang: Literal['en', 'bn'] = 'en'):
        movie = app.state.catalog.by_id.get(movie_id)
        if movie is None:
            raise HTTPException(404)
        return Response(poster_svg(localize_movie(movie, lang), lang), media_type='image/svg+xml',
                        headers={'Cache-Control':'public, max-age=86400'})

    @app.get('/')
    def index():
        return FileResponse(ROOT / 'web' / 'index.html', headers={'Cache-Control': 'no-cache'})

    app.mount('/assets', StaticFiles(directory=ROOT / 'web'), name='assets')
    return app


app = create_app()
