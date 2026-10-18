import io
import json
import re
from uuid import uuid4
import pytest
from PIL import Image
from sqlalchemy import select
from app.catalog import load_sources, fingerprint
from app.config import ROOT
from app.database import submissions
from app.i18n import catalog_text, survey_text, localize_questions, localize_result, localize_snapshot, THEMES
from app.survey import BANKS, public_questions
from app.typography import shape, text_width
from .test_game import client, template_db
from . import helpers


def bengali(value):
    return re.search('[\u0980-\u09ff]', value) is not None


def test_complete_bangla_catalog_and_immutable_sources():
    movies = load_sources(ROOT / 'data')
    before = fingerprint(movies)
    localized = catalog_text()
    assert set(localized['movies']) == {m['id'] for m in movies}
    assert set(localized['characters']) == {c['id'] for m in movies for c in m['characters']}
    for kind in localized.values():
        for fields in kind.values():
            assert all(bengali(value) and not re.search('[A-Za-z\ufffd]', value) for value in fields.values())
    assert {t for m in movies for t in m['themes']} <= THEMES.keys()
    assert fingerprint(movies) == before == 'bea334eaa576e57db1afba7d'


@pytest.mark.parametrize('mode', ['story','character'])
def test_language_keeps_question_ids_choices_seed_and_scores(client, mode):
    seed = str(uuid4())
    english = client.get('/api/v1/survey', params={'mode':mode,'seed':seed}).json()
    bangla = client.get('/api/v1/survey', params={'mode':mode,'seed':seed,'lang':'bn'}).json()
    assert english['version'] == bangla['version']
    assert english['seed'] == bangla['seed'] == seed
    for a,b in zip(english['questions'], bangla['questions']):
        assert a['id'] == b['id'] and a['trait'] == b['trait']
        assert bengali(b['text']) and a['text'] != b['text']
        assert [o['id'] for o in a['options']] == [o['id'] for o in b['options']]
        assert all(bengali(o['text']) for o in b['options'])
    assert set(survey_text()[mode]) == {q['id'] for q in BANKS[mode]}
    all_questions = localize_questions(public_questions(BANKS[mode]),mode,'bn')
    assert all(bengali(o['text']) and not re.search('[A-Za-z]',o['text']) for q in all_questions for o in q['options'])
    assert json.loads((ROOT/'web/survey-bn.json').read_text(encoding='utf-8-sig')) == survey_text()
    headers = helpers.key()
    payload = dict(survey_version=english['version'], catalog_version=english['catalog_version'],
                   seed=seed, mode=mode, category='all', answers={q['id']:q['options'][0]['id'] for q in bangla['questions']})
    original = client.post('/api/v1/matches', headers=headers, json=payload).json()
    localized = client.get('/api/v1/results/current?lang=bn',headers=headers)
    assert localized.status_code == 200 and localized.headers['cache-control'] == 'no-store'
    translated = localized.json()
    assert original['profile'] == translated['profile']
    for a,b in zip(original['matches'],translated['matches']):
        assert a['affinity'] == b['affinity'] and a['character']['id'] == b['character']['id']
        assert bengali(b['character']['name']) and bengali(b['movie']['title'])
        assert all(bengali(r['answer']) and bengali(r['text']) for r in b['reasons'])
        for reason in b['reasons']:
            question = next(q for q in bangla['questions'] if q['id'] == reason['question_id'])
            assert reason['answer'] == next(o['text'] for o in question['options'] if o['id'] == payload['answers'][question['id']])
    assert client.get('/api/v1/results/current',headers=headers).json() == original
    assert client.post('/api/v1/matches', headers=headers, json=payload).json() == original
    with client.app.state.engine.connect() as conn:
        assert conn.execute(select(submissions.c.result)).scalar_one() == original
    assert client.get('/api/v1/results/current?lang=bn').status_code == 422
    assert client.get('/api/v1/results/current?lang=bn', headers=helpers.key()).status_code == 404


def test_bangla_search_and_poster(client):
    en = client.get('/api/v1/catalog?limit=48').json()
    bn = client.get('/api/v1/catalog?lang=bn&limit=48').json()
    assert en['total'] == bn['total'] == 1126
    assert [m['id'] for m in en['items']] == [m['id'] for m in bn['items']]
    movie = bn['items'][0]
    assert bengali(movie['description'])
    results = client.get('/api/v1/catalog',params={'q':movie['title'],'lang':'bn'}).json()
    assert movie['id'] in [m['id'] for m in results['items']]
    poster = client.get(f'/api/v1/posters/{movie["id"]}.svg?lang=bn')
    assert poster.status_code == 200 and 'মুভিগেম' in poster.text and movie['title'] in poster.text


def test_bangla_share_html_image_language_and_privacy(client):
    headers = helpers.key()
    result = client.post('/api/v1/matches',headers=headers,json=helpers.payload(client)).json()
    request = {'display_name':'তানিয়া','language':'bn'}
    shared = client.post('/api/v1/shares',headers=headers,json=request).json()
    assert client.post('/api/v1/shares',headers=headers,json=request).json() == shared
    html = client.get(shared['share_url'])
    assert 'lang="bn"' in html.text and 'তানিয়া' in html.text and 'গল্পের মিল' in html.text
    assert 'language-switcher' in html.text and 'সাহস' in html.text
    assert 'card.png?lang=bn' in html.text
    assert all(r['answer'] not in html.text for r in result['matches'][0]['reasons'])
    english = client.get(shared['share_url']+'?lang=en')
    assert 'lang="en"' in english.text and result['matches'][0]['character']['name'] in english.text
    image = client.get(shared['image_url'])
    assert image.status_code == 200
    assert Image.open(io.BytesIO(image.content)).size == (1200,630)
    assert image.content != client.get(shared['image_url']+'?lang=en').content
    assert 'attachment' in client.get(shared['image_url']+'?lang=bn&download=1').headers['content-disposition']
    legacy = dict(shared['snapshot'])
    legacy.pop('movie_id'); legacy.pop('character_id')
    assert bengali(localize_snapshot(legacy,'bn')['character_name'])


def test_bengali_shaping_has_ligatures_and_no_missing_glyphs():
    text = 'সৃজনশীলতা — ব্যক্তিত্বের বৈশিষ্ট্য'
    infos, positions = shape(text,24)
    assert all(info.codepoint != 0 for info in infos)
    assert len(infos) < len(text)
    assert text_width(text,24) > 100
