from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from app.config import ROOT, Settings
from app.catalog import load_sources
from app.database import (metadata, make_engine, schema, surveys, catalog_versions, movies,
                          characters, submissions, shares, initialize, read_catalog, persist_result)
from app.main import create_app


def test_version_one_upgrade_preserves_results_and_old_replays(tmp_path):
    settings=Settings(database_url=f'sqlite:///{tmp_path / "legacy.db"}')
    engine=make_engine(settings)
    source=load_sources(ROOT/'data')
    legacy_tables=[t for t in metadata.sorted_tables if t.name not in ('movie_images','shared_results')]
    metadata.create_all(engine,tables=legacy_tables)
    movie=source[0]
    with engine.begin() as conn:
        conn.execute(schema.insert().values(version=1))
        conn.execute(surveys.insert().values(version='story-1',questions=[]))
        conn.execute(catalog_versions.insert().values(version='legacy-catalog'))
        conn.execute(movies.insert().values(**{k:v for k,v in movie.items() if k in movies.c}))
        conn.execute(characters.insert().values(**dict(movie['characters'][0],movie_id=movie['id'])))
    key=str(uuid4())
    body={'survey_version':'story-1','catalog_version':'legacy-catalog','category':'all',
          'answers':{f'q{i}':2 for i in range(1,16)}}
    result={'catalog_version':'legacy-catalog','survey_version':'story-1','matches':[],
            'profile':{'courage':50},'test_marker':'preserve-this-result'}
    persist_result(engine,key,body,lambda:result,30)
    initialize(engine,source,upgrade=True)
    initialize(engine,source,upgrade=True)
    assert len(read_catalog(engine))==len(source)
    with engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(submissions)).scalar()==1
        assert conn.execute(select(submissions.c.result)).scalar_one()==result
        assert conn.execute(select(func.max(schema.c.version))).scalar()==2
        assert conn.execute(select(surveys.c.questions).where(surveys.c.version=='story-1')).scalar_one()==[]
    engine.dispose()
    with TestClient(create_app(settings)) as client:
        replay=client.post('/api/v1/matches',json=body,headers={'Idempotency-Key':key})
        assert replay.status_code==200 and replay.json()==result
        assert replay.headers['Idempotency-Replayed']=='true'
        assert client.post('/api/v1/matches',json=body,headers={'Idempotency-Key':str(uuid4())}).status_code==409
