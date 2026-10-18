import concurrent.futures
import json
import shutil
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from redis.exceptions import ConnectionError as RedisConnectionError
from sqlalchemy import select, func
from . import helpers
from app.main import create_app
from app.config import Settings, ROOT
from app.database import submissions, initialize, read_catalog, IdempotencyConflict, persist_result, make_engine
from app.catalog import Catalog, load_sources, fingerprint
from app.survey import TRAITS, select_questions, answer_option


@pytest.fixture(scope='session')
def template_db(tmp_path_factory):
    path = tmp_path_factory.mktemp('seed') / 'template.db'
    engine = make_engine(Settings(database_url=f'sqlite:///{path}'))
    initialize(engine, load_sources(ROOT / 'data'))
    engine.dispose()
    return path


@pytest.fixture
def client(tmp_path, template_db):
    shutil.copyfile(template_db, tmp_path / 'test.db')
    app = create_app(Settings(database_url=f'sqlite:///{tmp_path / "test.db"}', rate_limit=1000))
    with TestClient(app) as client:
        yield client


def test_catalog_is_real_and_complete(client):
    data = load_sources(ROOT / 'data')
    assert len(data) >= 1089
    assert all(len(m['characters']) in (2,4) for m in data)
    assert all(m['image']['url'] for m in data)
    assert len({(m['title'].casefold(), m['year']) for m in data}) == len(data)
    assert {m['category'] for m in data} == {'hollywood', 'bangladeshi', 'anime'}
    assert fingerprint(read_catalog(client.app.state.engine)) == fingerprint(data)
    initialize(client.app.state.engine, data)  # Repeatable, transaction-safe catalog setup.
    assert len(read_catalog(client.app.state.engine)) == len(data)


def test_survey_fifteen_questions_five_options_and_all_dimensions(client):
    survey = client.get('/api/v1/survey').json()
    assert len(survey['questions']) == 15
    assert all(5 <= len(q['options']) <= 10 for q in survey['questions'])
    assert {q['trait'] for q in survey['questions']} == set(TRAITS)
    assert client.get('/').status_code == 200
    assert client.get('/assets/app.js').status_code == 200
    assert client.get('/health/ready').json() == {'status':'ready'}


@pytest.mark.parametrize('category', ['all', 'hollywood', 'bangladeshi', 'anime'])
def test_matches_have_five_grounded_reasons_and_filter(client, category):
    body = helpers.payload(client, category)
    response = client.post('/api/v1/matches', json=body, headers=helpers.key())
    assert response.status_code == 200, response.text
    result = response.json()
    assert len(result['matches']) == 3
    assert len({m['character']['name'] for m in result['matches']}) == 3
    for match in result['matches']:
        assert len(match['reasons']) == 5
        assert len({r['trait'] for r in match['reasons']}) == 5
        assert 0 <= match['affinity'] <= 100
        if category != 'all':
            assert match['movie']['category'] == category
        for reason in match['reasons']:
            q = next(q for q in select_questions(body['mode'],body['seed']) if q['id'] == reason['question_id'])
            assert reason['answer'] == answer_option(q, body['answers'][q['id']])['text']
    assert response.headers['cache-control'] == 'no-store'


def test_replay_and_conflict(client):
    headers, body = helpers.key(), helpers.payload(client)
    first = client.post('/api/v1/matches', headers=headers, json=body)
    second = client.post('/api/v1/matches', headers=headers, json=body)
    assert first.json() == second.json()
    assert second.headers['Idempotency-Replayed'] == 'true'
    first = next(iter(body['answers']))
    body['answers'][first] = (body['answers'][first] + 1) % 5
    assert client.post('/api/v1/matches', headers=headers, json=body).status_code == 409
    with client.app.state.engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(submissions)).scalar() == 1


def test_concurrent_identical_requests_have_one_winner(client):
    body, headers = helpers.payload(client), helpers.key()
    with concurrent.futures.ThreadPoolExecutor(max_workers=12) as executor:
        results = list(executor.map(lambda _: client.post('/api/v1/matches', json=body, headers=headers), range(24)))
    assert all(r.status_code == 200 for r in results)
    assert len({json.dumps(r.json(), sort_keys=True) for r in results}) == 1
    assert sum(r.headers['Idempotency-Replayed'] == 'false' for r in results) == 1
    with client.app.state.engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(submissions)).scalar() == 1


@pytest.mark.parametrize('mutation', ['missing', 'extra', 'range', 'bool', 'float', 'string', 'category', 'version', 'catalog'])
def test_bad_answers_and_stale_versions_rejected(client, mutation):
    body = helpers.payload(client)
    first = next(iter(body['answers']))
    if mutation == 'missing': del body['answers'][first]
    elif mutation == 'extra': body['answers']['unknown'] = 1
    elif mutation in ('range', 'bool', 'float', 'string'): body['answers'][first] = {'range':99,'bool':True,'float':1.5,'string':'1'}[mutation]
    elif mutation == 'category': body['category'] = 'other'
    elif mutation == 'version': body['survey_version'] = 'old'
    elif mutation == 'catalog': body['catalog_version'] = 'old'
    response = client.post('/api/v1/matches', json=body, headers=helpers.key())
    assert response.status_code == (409 if mutation in ('version','catalog') else 422)


def test_keys_body_limits_and_security_headers(client):
    assert client.post('/api/v1/matches', json=helpers.payload(client)).status_code == 422
    assert client.post('/api/v1/matches', content='x'*9000, headers=helpers.key()).status_code == 413
    response = client.get('/')
    assert response.headers['x-content-type-options'] == 'nosniff'
    assert 'frame-ancestors' in response.headers['content-security-policy']
    assert client.get('/metrics').status_code == 404


def test_catalog_search_pagination(client):
    all_rows = client.get('/api/v1/catalog?limit=1').json()
    assert len(all_rows['items']) == 1 and all_rows['total'] > 500
    anime = client.get('/api/v1/catalog?category=anime&limit=48').json()
    assert all(m['category'] == 'anime' for m in anime['items'])
    title = anime['items'][0]['title']
    assert client.get('/api/v1/catalog', params={'q':title}).json()['total'] >= 1
    assert client.get('/api/v1/catalog?limit=100000').status_code == 422


def test_rate_limit_returns_retry_after(tmp_path):
    app = create_app(Settings(database_url=f'sqlite:///{tmp_path / "rate.db"}', rate_limit=1))
    with TestClient(app) as client:
        body = helpers.payload(client)
        assert client.post('/api/v1/matches', headers=helpers.key(), json=body).status_code == 200
        denied = client.post('/api/v1/matches', headers=helpers.key(), json=body)
        assert denied.status_code == 429 and int(denied.headers['Retry-After']) > 0


def test_redis_outage_fails_closed_but_liveness_survives(client):
    class BrokenRedis:
        async def eval(self, *args): raise RedisConnectionError('unavailable')
        async def ping(self): raise RedisConnectionError('unavailable')
        async def aclose(self): pass
    body = helpers.payload(client)
    client.app.state.redis = BrokenRedis()
    assert client.post('/api/v1/matches', json=body, headers=helpers.key()).status_code == 503
    assert client.get('/health/ready').status_code == 503
    assert client.get('/health/live').status_code == 200


def test_production_refuses_unsafe_defaults():
    with pytest.raises(ValueError):
        create_app(Settings(environment='production'))


def test_exact_profile_ranks_at_top(client):
    movie = dict(client.app.state.catalog.movies[0])
    character = dict(movie['characters'][0])
    character['traits'] = {t:2 for t in TRAITS}
    movie['characters'] = [character]
    questions = [q for q in select_questions('story',str(uuid4())) if q.get('kind') != 'values']
    answers = {q['id']:next(o['id'] for o in q['options'] if o['value']==2) for q in questions}
    result = Catalog([movie]).match(answers, questions)
    assert result['matches'][0]['affinity'] == 100
