import concurrent.futures
import io
import json
from datetime import datetime, timedelta, timezone
from uuid import uuid4
import pytest
from PIL import Image
from sqlalchemy import select, func
from app.database import shares, submissions
from app.survey import BANKS, TRAITS, select_questions
from .helpers import payload, key
from .test_game import client, template_db


def test_two_varied_surveys_cover_all_traits(client):
    first=client.get('/api/v1/survey').json()
    second=client.get('/api/v1/survey').json()
    replay=client.get('/api/v1/survey',params={'seed':first['seed']}).json()
    character=client.get('/api/v1/survey?mode=character').json()
    assert first==replay
    assert first['questions']!=second['questions']
    assert len(first['questions'])==len(character['questions'])==15
    assert {q['id'] for q in first['questions']}.isdisjoint({q['id'] for q in character['questions']})
    assert {q['trait'] for q in character['questions']}==set(TRAITS)
    assert len(BANKS['story'])>15 and len(BANKS['character'])>15
    assert any([o['id'] for o in q['options']] != sorted(o['id'] for o in q['options']) for q in character['questions'])
    assert all('value' not in o for q in first['questions'] for o in q['options'])


def test_character_game_matches_across_movies(client):
    body=payload(client,mode='character')
    response=client.post('/api/v1/matches',json=body,headers=key())
    assert response.status_code==200
    assert response.json()['mode']=='character'
    assert len(response.json()['matches'][0]['reasons'])==5
    body['seed']=str(uuid4())
    assert client.post('/api/v1/matches',json=body,headers=key()).status_code==422


def saved_result(client):
    headers=key()
    response=client.post('/api/v1/matches',json=payload(client),headers=headers)
    assert response.status_code==200
    return headers,response.json()


def test_named_share_is_public_only_by_explicit_request(client):
    headers,result=saved_result(client)
    with client.app.state.engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(shares)).scalar()==0
    shared=client.post('/api/v1/shares',json={'display_name':'Ayesha'},headers=headers)
    assert shared.status_code==200
    data=shared.json()
    page=client.get(data['share_url'])
    assert page.status_code==200
    assert 'Ayesha' in page.text and result['matches'][0]['character']['name'] in page.text
    assert 'og:image' in page.text and 'card.png' in page.text
    assert '<meta name="robots" content="noindex,follow">' in page.text
    snapshot=data['snapshot']
    assert snapshot['profile']==result['profile']
    assert 'answers' not in snapshot and 'reasons' not in snapshot and 'key' not in snapshot
    assert not any(r['answer'] in page.text for r in result['matches'][0]['reasons'])
    png=client.get(data['image_url'])
    assert png.status_code==200 and png.headers['content-type']=='image/png'
    image=Image.open(io.BytesIO(png.content))
    assert image.size==(1200,630)
    assert len(png.content)>5000
    downloaded=client.get(data['image_url']+'?download=1')
    assert 'attachment' in downloaded.headers['content-disposition']
    again=client.post('/api/v1/shares',json={'display_name':'Ayesha'},headers=headers)
    assert again.json()['share_url']==data['share_url']


def test_shares_escape_names_and_require_a_saved_result(client):
    assert client.post('/api/v1/shares',json={'display_name':'N'},headers=key()).status_code==404
    headers,_=saved_result(client)
    result=client.post('/api/v1/shares',json={'display_name':'<script>alert(1)</script>'},headers=headers).json()
    page=client.get(result['share_url']).text
    assert '<script>alert(1)</script>' not in page
    assert '&lt;script&gt;' in page
    assert client.post('/api/v1/shares',json={'display_name':'x'*49},headers=headers).status_code==422


def test_concurrent_share_requests_have_one_public_link(client):
    headers,_=saved_result(client)
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        responses=list(pool.map(lambda _:client.post('/api/v1/shares',headers=headers,json={'display_name':'Rafi'}),range(16)))
    assert all(r.status_code==200 for r in responses)
    assert len({r.json()['share_url'] for r in responses})==1
    with client.app.state.engine.connect() as conn:
        assert conn.execute(select(func.count()).select_from(shares)).scalar()==1


def test_expired_shared_page_and_image_are_unavailable(client):
    headers,_=saved_result(client)
    data=client.post('/api/v1/shares',json={'display_name':'A'},headers=headers).json()
    with client.app.state.engine.begin() as conn:
        conn.execute(shares.update().values(expires_at=datetime.now(timezone.utc)-timedelta(seconds=1)))
    assert client.get(data['share_url']).status_code==404
    assert client.get(data['image_url']).status_code==404


def test_every_movie_has_artwork_with_safe_fallback(client):
    catalog=client.get('/api/v1/catalog?limit=48').json()['items']
    assert all(m['image']['url'] for m in catalog)
    movie=catalog[0]
    cover=client.get(f'/api/v1/posters/{movie["id"]}.svg')
    assert cover.status_code==200 and 'image/svg+xml' in cover.headers['content-type']
    assert 'ORIGINAL COVER ART' in cover.text
    assert client.get('/api/v1/posters/not-a-real-movie.svg').status_code==404
