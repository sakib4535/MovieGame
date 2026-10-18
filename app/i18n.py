"""Presentation-only translations. Canonical IDs, answers and stored scores stay unchanged."""
import json
from copy import deepcopy
from functools import lru_cache
from .config import ROOT
from .survey import BANKS

TRAIT_LABELS = dict(zip(
    ('courage', 'empathy', 'curiosity', 'discipline', 'independence', 'sociability', 'creativity', 'resilience'),
    ('সাহস', 'সহমর্মিতা', 'কৌতূহল', 'শৃঙ্খলা', 'স্বাধীনচেতা মনোভাব', 'মিশুক স্বভাব', 'সৃজনশীলতা', 'ঘুরে দাঁড়ানোর ক্ষমতা')))
CATEGORY_LABELS = {'all':'সব সিনেমা', 'hollywood':'হলিউড', 'bangladeshi':'বাংলাদেশি', 'anime':'জাপানি অ্যানিমে'}
THEMES = dict(line.split('=', 1) for line in '''absurdity=অযৌক্তিকতা
acceptance=মেনে নেওয়া
accountability=জবাবদিহি
adaptability=মানিয়ে নেওয়ার ক্ষমতা
adaptation=অভিযোজন
adventure=রোমাঞ্চকর অভিযান
alienation=বিচ্ছিন্নতা
ambition=উচ্চাকাঙ্ক্ষা
anxiety=উদ্বেগ
appearance=বাহ্যিক রূপ
art=শিল্প
attraction=আকর্ষণ
authenticity=নিজের প্রতি সৎ থাকা
authority=কর্তৃত্ব
autonomy=নিজস্ব সিদ্ধান্তের অধিকার
awareness=সচেতনতা
balance=ভারসাম্য
belief=বিশ্বাস
belonging=আপন হয়ে ওঠা
betrayal=বিশ্বাসঘাতকতা
boundaries=ব্যক্তিগত সীমারেখা
brotherhood=ভ্রাতৃত্ব
care=যত্ন
censorship=মতপ্রকাশে বাধা
chance=দৈব সুযোগ
change=পরিবর্তন
childhood=শৈশব
choice=সিদ্ধান্ত
choices=বেছে নেওয়া
cinema=সিনেমা
civic duty=নাগরিক দায়িত্ব
class=শ্রেণিবৈষম্য
coexistence=সহাবস্থান
commitment=অঙ্গীকার
communication=যোগাযোগ
community=সমাজ
compassion=মমতা
competition=প্রতিযোগিতা
confidence=আত্মবিশ্বাস
conflict=দ্বন্দ্ব
conformity=প্রচলিত নিয়ম মেনে চলা
connection=সংযোগ
conscience=বিবেক
consciousness=চেতনা
consequences=পরিণতি
control=নিয়ন্ত্রণ
conviction=দৃঢ় বিশ্বাস
cooperation=সহযোগিতা
corruption=দুর্নীতি
courage=সাহস
craft=নৈপুণ্য
creativity=সৃজনশীলতা
critical thinking=বিচার করে ভাবা
cultural understanding=সংস্কৃতিকে বোঝা
curiosity=কৌতূহল
deception=প্রতারণা
defiance=অবাধ্যতা
desperation=মরিয়া অবস্থা
determination=দৃঢ় সংকল্প
devotion=নিষ্ঠা
dignity=মর্যাদা
discipline=শৃঙ্খলা
discovery=আবিষ্কার
distance=দূরত্ব
diversity=বৈচিত্র্য
dreams=স্বপ্ন
duty=কর্তব্য
empathy=সহমর্মিতা
endurance=সহনশীলতা
envy=ঈর্ষা
equality=সমতা
escapism=বাস্তবতা থেকে পালানোর আকাঙ্ক্ষা
ethics=নৈতিকতা
excellence=উৎকর্ষ
expectations=প্রত্যাশা
exploitation=শোষণ
exploration=অনুসন্ধান
expression=অভিব্যক্তি
fairness=ন্যায্যতা
faith=আস্থা
fame=খ্যাতি
family=পরিবার
fear=ভয়
forgiveness=ক্ষমা
found-family=বেছে পাওয়া পরিবার
fragility=ভঙ্গুরতা
freedom=স্বাধীনতা
friendship=বন্ধুত্ব
generosity=উদারতা
gentleness=কোমলতা
gratitude=কৃতজ্ঞতা
greed=লোভ
grief=শোক
growing up=বড় হয়ে ওঠা
growth=বিকাশ
guilt=অপরাধবোধ
healing=মনের ক্ষত সারানো
history=ইতিহাস
honesty=সততা
honor=সম্মান
hope=আশা
humanity=মানবিকতা
humility=বিনয়
humor=রসবোধ
idealism=আদর্শবাদ
identity=পরিচয়
illusion=মায়া
imagination=কল্পনা
inclusion=অন্তর্ভুক্তি
independence=স্বাধীনচেতা মনোভাব
individuality=স্বাতন্ত্র্য
inequality=অসমতা
ingenuity=উদ্ভাবনী বুদ্ধি
injustice=অবিচার
inner peace=মনের শান্তি
innovation=উদ্ভাবন
insecurity=অনিরাপত্তাবোধ
integrity=নীতিতে অটল থাকা
interdependence=পারস্পরিক নির্ভরতা
invention=উদ্ভাবন
investigation=তদন্ত
isolation=নিঃসঙ্গতা
jealousy=ঈর্ষা
journey=যাত্রা
joy=আনন্দ
judgment=বিচারবোধ
justice=ন্যায়বিচার
kindness=সদয়তা
language=ভাষা
leadership=নেতৃত্ব
learning=শেখা
legacy=উত্তরাধিকার
letting go=ছেড়ে দিতে শেখা
liberation=মুক্তি
listening=মন দিয়ে শোনা
loneliness=একাকিত্ব
loss=হারানোর বেদনা
love=ভালোবাসা
loyalty=বিশ্বস্ততা
magic=জাদু
manipulation=কৌশলে প্রভাব খাটানো
maturity=পরিণতিবোধ
media=গণমাধ্যম
memory=স্মৃতি
mentorship=পথ দেখানো
mistrust=অনাস্থা
misunderstanding=ভুল বোঝাবুঝি
moral choice=নৈতিক সিদ্ধান্ত
moral responsibility=নৈতিক দায়িত্ব
moral uncertainty=নৈতিক দ্বিধা
morality=নৈতিকতা
mortality=মরণশীলতা
music=সংগীত
mystery=রহস্য
nature=প্রকৃতি
nonviolence=অহিংসা
nurture=লালনপালন
obligation=দায়বদ্ধতা
observation=পর্যবেক্ষণ
obsession=আচ্ছন্নতা
open mindedness=খোলা মন
opportunity=সুযোগ
optimism=আশাবাদ
parenthood=মা-বাবার ভূমিকা
partnership=অংশীদারত্ব
patience=ধৈর্য
peace=শান্তি
perception=উপলব্ধি
performance=পরিবেশনা
perseverance=অধ্যবসায়
persistence=লেগে থাকা
perspective=দৃষ্টিভঙ্গি
possibility=সম্ভাবনা
potential=সুপ্ত সম্ভাবনা
power=ক্ষমতা
prejudice=পক্ষপাত
presence=বর্তমান মুহূর্তে থাকা
pride=অহংকার
priorities=অগ্রাধিকার
privacy=গোপনীয়তা
problem-solving=সমস্যার সমাধান
professionalism=পেশাদারিত্ব
progress=অগ্রগতি
promise=প্রতিশ্রুতি
protection=সুরক্ষা
public duty=জনসেবার দায়িত্ব
purpose=উদ্দেশ্য
reason=যুক্তি
reasoning=যুক্তিবিচার
reconciliation=পুনর্মিলন
recovery=সেরে ওঠা
redemption=প্রায়শ্চিত্ত
reinvention=নিজেকে নতুনভাবে গড়া
relationships=সম্পর্ক
renewal=নবায়ন
repair=মেরামত
reputation=সুনাম
resilience=ঘুরে দাঁড়ানোর ক্ষমতা
resistance=প্রতিরোধ
resolve=দৃঢ় সংকল্প
resourcefulness=উপায় বের করার দক্ষতা
responsibility=দায়িত্ব
revenge=প্রতিশোধ
risk=ঝুঁকি
rivalry=প্রতিদ্বন্দ্বিতা
sacrifice=ত্যাগ
second chances=দ্বিতীয় সুযোগ
second-chances=দ্বিতীয় সুযোগ
self acceptance=নিজেকে মেনে নেওয়া
self belief=নিজের ওপর বিশ্বাস
self discovery=নিজেকে আবিষ্কার
self knowledge=আত্মজ্ঞান
self worth=আত্মমর্যাদা
self-acceptance=নিজেকে মেনে নেওয়া
self-control=আত্মসংযম
self-discovery=নিজেকে আবিষ্কার
serendipity=অপ্রত্যাশিত সুন্দর প্রাপ্তি
service=সেবা
sisterhood=বোনের বন্ধন
solidarity=সংহতি
storytelling=গল্প বলা
strategy=কৌশল
surveillance=নজরদারি
survival=বেঁচে থাকা
suspicion=সন্দেহ
teaching=শিক্ষাদান
teamwork=দলগত কাজ
technology=প্রযুক্তি
temptation=প্রলোভন
time=সময়
timing=সঠিক সময় বেছে নেওয়া
tolerance=সহিষ্ণুতা
tradition=ঐতিহ্য
transformation=রূপান্তর
trust=আস্থা
truth=সত্য
uncertainty=অনিশ্চয়তা
understanding=বোঝাপড়া
unity=ঐক্য
vanity=আত্মমুগ্ধতা
violence=সহিংসতা
vitality=প্রাণশক্তি
voice=নিজের কথা বলার অধিকার
vulnerability=নাজুক অনুভূতি প্রকাশ
war=যুদ্ধ
wonder=বিস্ময়
work=কাজ'''.splitlines())

TENDENCIES = {
 'courage': ('আগে নিরাপত্তার কথা ভাবা', 'সতর্কভাবে পা বাড়ানো', 'ঝুঁকি ও সতর্কতার ভারসাম্য রাখা', 'অনিশ্চয়তার মধ্যেও এগিয়ে যাওয়া', 'কোনো উদ্দেশ্যে বড় ঝুঁকির মুখোমুখি হওয়া'),
 'empathy': ('বাস্তব পরিণতিকে গুরুত্ব দেওয়া', 'আবেগের সীমারেখা রাখা', 'অনুভূতি ও বাস্তব চাহিদার ভারসাম্য রাখা', 'অন্যের অনুভূতিকে জায়গা দেওয়া', 'কঠিন সময়ে মানুষের পাশে থেকে যত্ন নেওয়া'),
 'curiosity': ('পরিচিত উত্তরকে মূল্য দেওয়া', 'প্রয়োজন হলে অনুসন্ধান করা', 'স্পষ্ট উদ্দেশ্য নিয়ে প্রশ্ন করা', 'উপরের দৃশ্যের আড়ালে সূত্র খোঁজা', 'অজানা প্রশ্নের উত্তর খুঁজতে নতুন পথে যাওয়া'),
 'discipline': ('অনুপ্রেরণা এলে কাজে নামা', 'সুযোগমতো নমনীয়ভাবে কাজ করা', 'পরিকল্পনার সঙ্গে নমনীয়তা মেলানো', 'নিয়মিত রুটিন বজায় রাখা', 'স্বীকৃতি না পেলেও কাজ শেষ করা'),
 'independence': ('সবার সঙ্গে চলার পথে দিশা খোঁজা', 'বিশ্বস্ত পরামর্শের ওপর বেশি নির্ভর করা', 'পরামর্শ ও নিজের বিচার মিলিয়ে সিদ্ধান্ত নেওয়া', 'নিজের সিদ্ধান্তের পাশে থাকা', 'মতবিরোধের মধ্যেও নিজের ভাবনা ধরে চলা'),
 'sociability': ('একা সময় কাটিয়ে শক্তি ফিরে পাওয়া', 'অল্প কয়েকটি ঘনিষ্ঠ সম্পর্কে মন দেওয়া', 'সঙ্গ ও নিরিবিলি সময়ের ভারসাম্য রাখা', 'দলের মানুষদের যুক্ত রাখা', 'অনেক মানুষের সঙ্গে সম্পর্ক গড়া'),
 'creativity': ('পরীক্ষিত স্পষ্ট পদ্ধতিতে ভরসা করা', 'পরিচিত পদ্ধতির উন্নতি করা', 'বাস্তবসম্মত ও নতুন ভাবনা মেলানো', 'গতানুগতিকতার বাইরে সম্ভাবনা দেখা', 'সম্পূর্ণ নতুন পদ্ধতি কল্পনা করা'),
 'resilience': ('লক্ষ্য আর মানানসই না হলে নতুন পথ বেছে নেওয়া', 'সেরে উঠতে যথেষ্ট সময় নেওয়া', 'সাহায্য নিয়ে ছোট পদক্ষেপে আবার শুরু করা', 'ব্যর্থতা থেকে শিখে ফিরে আসা', 'বারবার কঠিন বাধা পেরিয়েও লেগে থাকা'),
}

def number(value, lang='en'):
    text = str(value)
    return text.translate(str.maketrans('0123456789', '০১২৩৪৫৬৭৮৯')) if lang == 'bn' else text


@lru_cache(maxsize=1)
def catalog_text():
    merged = {'movies': {}, 'characters': {}}
    for name in ('classic', 'modern', 'asian'):
        data = json.loads((ROOT / 'data' / f'_bn_{name}.json').read_text(encoding='utf-8-sig'))
        for kind in merged:
            merged[kind].update(data[kind])
    return merged


@lru_cache(maxsize=1)
def survey_text():
    return json.loads((ROOT / 'data' / '_bn_survey.json').read_text(encoding='utf-8-sig'))


def localize_questions(questions, mode, lang):
    if lang != 'bn':
        return questions
    translated = survey_text()[mode]
    return [dict(q, text=translated[q['id']]['text'], options=[dict(o, text=translated[q['id']]['options'][str(o['id'])])
                 for o in q['options']]) for q in questions]


def localize_character(character, lang):
    return dict(character, **catalog_text()['characters'].get(character['id'], {})) if lang == 'bn' else character


def localize_movie(movie, lang):
    if lang != 'bn':
        return movie
    translated = dict(movie, **catalog_text()['movies'].get(movie['id'], {}))
    translated['themes'] = [THEMES[t] for t in movie['themes']]
    if 'characters' in movie:
        translated['characters'] = [localize_character(c, lang) for c in movie['characters']]
    if movie.get('image', {}).get('kind') == 'illustrated-cover':
        translated['image'] = dict(movie['image'], url=f'/api/v1/posters/{movie["id"]}.svg?lang=bn', credit='মুভিগেমের নিজস্ব প্রচ্ছদচিত্র')
    return translated


@lru_cache(maxsize=1)
def answer_text():
    localized = survey_text()
    return {o['text']: localized[mode][q['id']]['options'][str(o['id'])]
            for mode, questions in BANKS.items() for q in questions for o in q['options']}


def localize_answer(mode, reason):
    question = next((q for q in BANKS[mode] if q['id'] == reason['question_id']), None)
    if question:
        option = next((o for o in question['options'] if o['text'] == reason['answer']), None)
        if option:
            return survey_text()[mode][question['id']]['options'][str(option['id'])]
    return answer_text().get(reason['answer'], 'আপনার নির্বাচিত উত্তর')


def localize_result(result, lang):
    if lang != 'bn':
        return result
    result = deepcopy(result)
    for match in result['matches']:
        match['movie'] = localize_movie(match['movie'], lang)
        match['character'] = localize_character(match['character'], lang)
        c, m = match['character'], match['movie']
        for reason in match['reasons']:
            trait = reason['trait']
            tendency = TENDENCIES[trait][c['traits'][trait]]
            reason['answer'] = localize_answer(result.get('mode', 'story'), reason)
            reason['text'] = f'আমাদের {m["title"]} ছবির বিশ্লেষণে {c["name"]} চরিত্রটির একটি দিক হলো {tendency}। {TRAIT_LABELS[trait]} নিয়ে আপনার পছন্দেও একই ধরনের মনোভাব দেখা যায়।'
    result['method'] = 'আটটি বৈশিষ্ট্যের মিল ৯০% এবং সম্পাদকীয় থিম ও ভূমিকা থেকে পাওয়া গল্পের মূল্যবোধের মিল ১০%। শুধুই বিনোদনের জন্য।'
    return result


def localize_snapshot(snapshot, lang):
    data = dict(snapshot, language=lang)
    if lang == 'bn':
        translated = catalog_text()
        movie_id, character_id = data.get('movie_id'), data.get('character_id')
        if not movie_id or not character_id:
            movie_id, character_id = legacy_ids().get((data['movie_title'], data['movie_year'], data['character_name']), (None, None))
        data['character_name'] = translated['characters'].get(character_id, {}).get('name', data['character_name'])
        data['movie_title'] = translated['movies'].get(movie_id, {}).get('title', data['movie_title'])
    return data


@lru_cache(maxsize=1)
def legacy_ids():
    from .catalog import load_sources
    return {(m['title'], m['year'], c['name']): (m['id'], c['id'])
            for m in load_sources(ROOT / 'data') for c in m['characters']}
