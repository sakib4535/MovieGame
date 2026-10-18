"""Normalized catalog, immutable survey versions, and atomic idempotent results."""
import hashlib
import json
from datetime import datetime, timedelta, timezone
from sqlalchemy import (MetaData, Table, Column, String, Integer, Boolean, Text, JSON,
                        DateTime, ForeignKey, create_engine, event, select, text, func)
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects.sqlite import insert as sqlite_insert
from .catalog import fingerprint
from .survey import VERSIONS, BANKS

metadata = MetaData()
schema = Table('schema_versions', metadata, Column('version', Integer, primary_key=True))
movies = Table('movies', metadata,
    Column('id', String(24), primary_key=True), Column('title', Text, nullable=False),
    Column('year', Integer, nullable=False), Column('category', String(20), nullable=False, index=True),
    Column('description', Text, nullable=False), Column('source_url', Text, nullable=False),
    Column('source_verified', Boolean, nullable=False))
characters = Table('characters', metadata,
    Column('id', String(24), primary_key=True), Column('movie_id', ForeignKey('movies.id'), nullable=False, index=True),
    Column('name', Text, nullable=False), Column('identity', Text, nullable=False),
    Column('description', Text, nullable=False), Column('traits', JSON, nullable=False))
themes = Table('themes', metadata, Column('name', String(100), primary_key=True))
movie_themes = Table('movie_themes', metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True),
    Column('theme', ForeignKey('themes.name'), primary_key=True))
surveys = Table('survey_versions', metadata,
    Column('version', String(32), primary_key=True), Column('questions', JSON, nullable=False))
catalog_versions = Table('catalog_versions', metadata, Column('version', String(24), primary_key=True))
movie_images = Table('movie_images', metadata,
    Column('movie_id', ForeignKey('movies.id'), primary_key=True), Column('image', JSON, nullable=False))
submissions = Table('submissions', metadata,
    Column('key_hash', String(64), primary_key=True), Column('request_hash', String(64), nullable=False),
    Column('survey_version', ForeignKey('survey_versions.version'), nullable=False),
    Column('catalog_version', String(24), nullable=False), Column('result', JSON, nullable=False),
    Column('created_at', DateTime(timezone=True), nullable=False),
    Column('expires_at', DateTime(timezone=True), nullable=False, index=True))
shares = Table('shared_results', metadata,
    Column('token', String(32), primary_key=True), Column('share_key', String(64), nullable=False, unique=True),
    Column('snapshot', JSON, nullable=False), Column('created_at', DateTime(timezone=True), nullable=False),
    Column('expires_at', DateTime(timezone=True), nullable=False, index=True))


def make_engine(settings):
    sqlite = settings.database_url.startswith('sqlite:')
    kwargs = dict(pool_size=settings.pool_size, max_overflow=0, pool_timeout=2, pool_pre_ping=True)
    if sqlite:
        kwargs['connect_args'] = {'check_same_thread': False, 'timeout': 5}
    else:
        kwargs['connect_args'] = {'connect_timeout': 3, 'options': '-c statement_timeout=4000 -c lock_timeout=2000 -c idle_in_transaction_session_timeout=5000'}
    engine = create_engine(settings.database_url, **kwargs)
    if sqlite:
        @event.listens_for(engine, 'connect')
        def sqlite_options(connection, _):
            connection.execute('PRAGMA foreign_keys=ON')
            connection.execute('PRAGMA journal_mode=WAL')
    return engine


def upsert(conn, table, values):
    stmt = sqlite_insert(table) if conn.dialect.name == 'sqlite' else pg_insert(table)
    return conn.execute(stmt.values(values).on_conflict_do_nothing())


def initialize(engine, catalog, upgrade=False):
    """Run once as a deployment job; never on production API startup."""
    metadata.create_all(engine)
    version = fingerprint(catalog)
    with engine.begin() as conn:
        if conn.dialect.name == 'postgresql':
            conn.execute(text('SELECT pg_advisory_xact_lock(62841001)'))
        current = conn.execute(select(catalog_versions.c.version)).scalars().all()
        if current and current != [version] and not upgrade:
            raise RuntimeError('Catalog differs from database. Use a reviewed catalog migration; never silently overwrite live data.')
        for mode, survey_version in VERSIONS.items():
            old_survey = conn.execute(select(surveys.c.questions).where(surveys.c.version == survey_version)).scalar_one_or_none()
            if old_survey is not None and old_survey != BANKS[mode]:
                raise RuntimeError('Survey changed without a version bump.')
            upsert(conn, surveys, {'version': survey_version, 'questions': BANKS[mode]})
        upsert(conn, schema, {'version': 2})
        if not current or (upgrade and current != [version]):
            if current:
                existing = set(conn.execute(select(movies.c.id)).scalars())
                if not existing.issubset({m['id'] for m in catalog}):
                    raise RuntimeError('Upgrade must preserve every existing movie.')
            for movie in catalog:
                upsert(conn, movies, {k:v for k,v in movie.items() if k in movies.c})
                for theme in movie['themes']:
                    upsert(conn, themes, {'name': theme})
                    upsert(conn, movie_themes, {'movie_id': movie['id'], 'theme': theme})
                for character in movie['characters']:
                    upsert(conn, characters, dict(character, movie_id=movie['id']))
                image_values = {'movie_id': movie['id'], 'image': movie['image']}
                image_stmt = sqlite_insert(movie_images) if conn.dialect.name == 'sqlite' else pg_insert(movie_images)
                conn.execute(image_stmt.values(image_values).on_conflict_do_update(
                    index_elements=['movie_id'], set_={'image': movie['image']}))
            conn.execute(catalog_versions.delete())
            upsert(conn, catalog_versions, {'version': version})


def read_catalog(engine):
    with engine.connect() as conn:
        if conn.execute(select(func.max(schema.c.version))).scalar() != 2:
            raise RuntimeError('Run python -m app.manage upgrade before starting the updated API.')
        for mode, version in VERSIONS.items():
            stored = conn.execute(select(surveys.c.questions).where(surveys.c.version == version)).scalar_one()
            if stored != BANKS[mode]:
                raise RuntimeError('Survey version does not match this deployment.')
        result = {row['id']: dict(row, themes=[], characters=[]) for row in conn.execute(select(movies)).mappings()}
        for row in conn.execute(select(movie_themes)).mappings():
            result[row['movie_id']]['themes'].append(row['theme'])
        for row in conn.execute(select(characters)).mappings():
            result[row['movie_id']]['characters'].append({k:v for k,v in row.items() if k != 'movie_id'})
        for row in conn.execute(select(movie_images)).mappings():
            result[row['movie_id']]['image'] = row['image']
    for movie in result.values():
        movie['themes'].sort()
        movie['characters'].sort(key=lambda c: c['id'])
    return sorted(result.values(), key=lambda m: (m['title'].casefold(), m['year']))


class IdempotencyConflict(Exception):
    pass


def persist_result(engine, key, payload, compute, retention_days):
    key_hash = hashlib.sha256(key.encode()).hexdigest()
    request_hash = hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()
    with engine.connect() as conn:
        existing = conn.execute(select(submissions).where(submissions.c.key_hash == key_hash)).mappings().first()
    if existing:
        if existing['request_hash'] != request_hash:
            raise IdempotencyConflict()
        return existing['result'], True
    result = compute()
    now = datetime.now(timezone.utc)
    values = dict(key_hash=key_hash, request_hash=request_hash, survey_version=payload['survey_version'],
                  catalog_version=result['catalog_version'], result=result, created_at=now,
                  expires_at=now + timedelta(days=retention_days))
    with engine.begin() as conn:
        inserted = upsert(conn, submissions, values).rowcount == 1
        # The unique key serializes contenders; only the committed winner is returned.
        winner = conn.execute(select(submissions).where(submissions.c.key_hash == key_hash)).mappings().one()
        if winner['request_hash'] != request_hash:
            raise IdempotencyConflict()
        return winner['result'], not inserted
