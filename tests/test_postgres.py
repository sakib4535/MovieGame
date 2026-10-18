"""Real cross-replica checks, enabled in CI or against a disposable PostgreSQL database."""
import os
from concurrent.futures import ThreadPoolExecutor
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from app.config import Settings
from app.main import create_app
from app.database import submissions
from .helpers import payload, key


@pytest.mark.skipif(not os.getenv('TEST_DATABASE_URL'), reason='Requires disposable PostgreSQL + Redis services')
def test_postgres_atomic_replay_across_replicas():
    settings = Settings(database_url=os.environ['TEST_DATABASE_URL'], redis_url=os.environ['TEST_REDIS_URL'], rate_limit=1000)
    with TestClient(create_app(settings)) as a, TestClient(create_app(settings)) as b:
        body, headers = payload(a), key()
        def send(i):
            return (a if i % 2 else b).post('/api/v1/matches', json=body, headers=headers)
        with ThreadPoolExecutor(max_workers=16) as pool:
            responses = list(pool.map(send, range(32)))
        assert all(r.status_code == 200 for r in responses)
        assert sum(r.headers['Idempotency-Replayed'] == 'false' for r in responses) == 1
        assert all(r.json() == responses[0].json() for r in responses)
        first = next(iter(body['answers']))
        body['answers'][first] = (body['answers'][first] + 1) % 5
        assert b.post('/api/v1/matches', json=body, headers=headers).status_code == 409
