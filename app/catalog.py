"""Validate source data, assign stable IDs, and build immutable matching profiles."""
import hashlib
import json
import math
from pathlib import Path
from urllib.parse import urlparse
from .survey import TRAITS, profile, answer_option

CATEGORIES = ('hollywood', 'bangladeshi', 'anime')


def stable_id(value):
    return hashlib.sha256(value.encode()).hexdigest()[:24]


def load_sources(directory: Path, minimum=1089):
    movies, seen = [], set()
    poster_file = directory / '_posters.json'
    posters = json.loads(poster_file.read_text(encoding='utf-8')) if poster_file.exists() else {}
    for path in sorted(directory.glob('*.json')):
        if path.name.startswith('_'):
            continue
        for original in json.loads(path.read_text(encoding='utf-8-sig')):
            m = dict(original)
            key = (m['title'].strip().casefold(), m['year'])
            if key in seen:
                raise ValueError(f'Duplicate film: {key}')
            seen.add(key)
            assert m['category'] in CATEGORIES, key
            assert isinstance(m['year'], int) and 1900 <= m['year'] <= 2026, key
            assert len(m['description']) >= 15 and len(m['themes']) >= 2, key
            assert urlparse(m['source_url']).scheme == 'https', key
            m['id'] = stable_id(f'{key[0]}:{key[1]}')
            m['source_verified'] = bool(m.get('source_verified', False))
            m['themes'] = sorted(set(t.strip().lower() for t in m['themes']))
            assert len(m['characters']) in (2, 4), f'{key}: each film needs two or four characters'
            character_names = set()
            for c in m['characters']:
                assert c['name'] not in character_names, (key, c['name'])
                character_names.add(c['name'])
                assert c['identity'] and c['description'], key
                assert set(c['traits']) == set(TRAITS), (key, c['name'])
                assert all(type(v) is int and 0 <= v <= 4 for v in c['traits'].values()), key
                c['id'] = stable_id(f'{m["id"]}:{c["name"]}')
            m['characters'].sort(key=lambda c: c['id'])
            image = posters.get(m['source_url'])
            if image and urlparse(image['url']).hostname == 'upload.wikimedia.org':
                m['image'] = image
            else:
                m['image'] = {'url': f'/api/v1/posters/{m["id"]}.svg', 'kind': 'illustrated-cover',
                              'source_url': m['source_url'], 'credit': 'Original MovieGame cover artwork'}
            movies.append(m)
    assert len(movies) >= minimum, f'Need {minimum} films; found {len(movies)}'
    assert set(m['category'] for m in movies) == set(CATEGORIES)
    return sorted(movies, key=lambda m: (m['title'].casefold(), m['year']))


def fingerprint(movies):
    return stable_id(json.dumps(movies, sort_keys=True, ensure_ascii=False))


class Catalog:
    def __init__(self, movies):
        self.movies = movies
        self.version = fingerprint(movies)
        self.by_id = {m['id']: m for m in movies}
        self.counts = {category: sum(m['category'] == category for m in movies) for category in CATEGORIES}
        self.characters = [(m, c, tuple(c['traits'][t] / 4 for t in TRAITS), character_values(m,c))
                           for m in movies for c in m['characters']]

    def match(self, answers, questions, category='all', mode='story'):
        user = profile(answers, questions)
        vector = tuple(user[t] for t in TRAITS)
        seed = json.dumps(answers, sort_keys=True)
        values = [answer_option(q, answers[q['id']])['theme'] for q in questions if q.get('kind') == 'values']
        ranked = []
        for movie, character, character_vector, signals in self.characters:
            if category != 'all' and movie['category'] != category:
                continue
            trait_distance = sum((a-b)**2 for a, b in zip(vector, character_vector)) / len(TRAITS)
            affinity = 1-math.sqrt(trait_distance)
            if values:
                overlap = sum(value in signals for value in values) / len(values)
                affinity = 0.9*affinity + 0.1*overlap
            distance = (1-affinity)**2
            ranked.append((distance, stable_id(seed + character['id']), movie, character))
        ranked.sort(key=lambda row: (row[0], row[1]))
        matches, names = [], set()
        for distance, _, movie, character in ranked:
            name = character['name'].casefold()
            if name in names:
                continue
            names.add(name)
            traits = sorted(TRAITS, key=lambda t: (abs(user[t] - character['traits'][t]/4), t))[:5]
            reasons = []
            for trait in traits:
                related = [q for q in questions if q['trait'] == trait and q.get('kind') != 'values']
                q = min(related, key=lambda q: abs(answer_option(q, answers[q['id']])['value'] - character['traits'][trait]))
                value = character['traits'][trait]
                tendency = TRAIT_MEANINGS[trait][value]
                reasons.append({'trait': trait, 'question_id': q['id'],
                    'answer': answer_option(q, answers[q['id']])['text'],
                    'text': f'In our {movie["title"]} profile, {character["name"]} leans toward {tendency}. Your choices show a similar approach to {trait}.',
                    'user_value': round(user[trait]*100), 'character_value': value*25})
            matches.append({'character': character, 'movie': {k:v for k,v in movie.items() if k != 'characters'},
                            'affinity': round(100 * (1 - math.sqrt(distance))), 'reasons': reasons})
            if len(matches) == 3:
                break
        gap = matches[0]['affinity'] - matches[1]['affinity'] if len(matches)>1 else 0
        return {'matches': matches, 'profile': {t: round(v*100) for t,v in user.items()},
                'mode': mode, 'score_gap': gap, 'close_match': gap <= 2, 'story_values': values,
                'catalog_version': self.version, 'method': '90% eight-trait similarity, 10% shared story-value signals from editorial themes and roles. Entertainment only.'}


VALUE_WORDS = {
 'care': ('care','protect','compassion','kindness','nurse','doctor','parent','mother','father','guardian'),
 'freedom': ('freedom','independence','liberation','rebel','escape','outlaw','autonomy'),
 'justice': ('justice','duty','crime','corruption','detective','police','lawyer','investigat','resistance'),
 'discovery': ('discovery','curiosity','truth','science','scientist','explor','research','mystery','knowledge'),
 'belonging': ('belong','family','friend','community','identity','love','brother','sister','child','daughter','son '),
 'creation': ('creativ','art','music','artist','musician','invent','writer','imagination','dream'),
 'redemption': ('redemption','forgiveness','recovery','healing','guilt','second chance','reconciliation'),
 'achievement': ('ambition','achievement','competition','success','athlete','champion','career','discipline','performer'),
}


def character_values(movie, character):
    text = ' '.join([*movie['themes'], character['identity'], character['description']]).casefold()
    return {value for value, words in VALUE_WORDS.items() if any(word in text for word in words)}


TRAIT_MEANINGS = {
 'courage': ('protecting safety before acting', 'taking cautious steps', 'balancing risk with care', 'stepping forward despite uncertainty', 'facing substantial risks for a purpose'),
 'empathy': ('focusing on practical consequences', 'keeping emotional boundaries', 'balancing feelings with practical needs', 'making room for other people’s feelings', 'actively caring for people through difficulty'),
 'curiosity': ('valuing familiar answers', 'exploring only when useful', 'asking questions with a clear purpose', 'following clues beneath the surface', 'pursuing unanswered questions into new territory'),
 'discipline': ('acting when inspiration strikes', 'working in flexible bursts', 'mixing structure with flexibility', 'keeping a steady routine', 'following through even without recognition'),
 'independence': ('finding direction in a shared path', 'drawing heavily on trusted guidance', 'balancing advice with personal judgment', 'standing behind personal choices', 'following a personal vision despite disagreement'),
 'sociability': ('recharging in solitude', 'investing in a small number of close bonds', 'balancing company and quiet time', 'keeping a group connected', 'building connections with a wide circle'),
 'creativity': ('trusting clear proven methods', 'improving familiar approaches', 'combining practical and fresh ideas', 'noticing unconventional possibilities', 'imagining entirely new approaches'),
 'resilience': ('choosing a new direction when a goal no longer fits', 'taking substantial time to recover', 'restarting with support and smaller steps', 'learning from setbacks and returning', 'persisting through repeated difficult setbacks'),
}
