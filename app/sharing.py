"""Explicit public snapshots and original share graphics; never publishes full answers."""
import hashlib
import html
import io
import json
import secrets
import textwrap
import unicodedata
from datetime import datetime, timezone
from functools import lru_cache
from sqlalchemy import select
from .config import ROOT
from .database import submissions, shares, upsert
from .survey import TRAITS
from .i18n import TRAIT_LABELS, CATEGORY_LABELS, number, localize_snapshot


def clean_name(value):
    return ''.join(c for c in value.strip() if not unicodedata.category(c).startswith('C'))[:48]


def create_share(engine, key, name, language='en'):
    source_hash = hashlib.sha256(str(key).encode()).hexdigest()
    name = clean_name(name)
    identity = f'{source_hash}:{name}' + (':bn' if language == 'bn' else '')
    share_key = hashlib.sha256(identity.encode()).hexdigest()
    now = datetime.now(timezone.utc)
    with engine.begin() as conn:
        source = conn.execute(select(submissions).where(submissions.c.key_hash == source_hash,
                                     submissions.c.expires_at > now)).mappings().first()
        if not source:
            return None
        best = source['result']['matches'][0]
        snapshot = {'display_name': name, 'character_name': best['character']['name'],
                    'movie_title': best['movie']['title'], 'movie_year': best['movie']['year'],
                    'affinity': best['affinity'], 'profile': source['result']['profile'],
                    'mode': source['result'].get('mode', 'story'), 'language': language,
                    'movie_id': best['movie']['id'], 'character_id': best['character']['id']}
        upsert(conn, shares, {'token': secrets.token_urlsafe(24), 'share_key': share_key,
                             'snapshot': snapshot, 'created_at': now, 'expires_at': source['expires_at']})
        row = conn.execute(select(shares).where(shares.c.share_key == share_key)).mappings().one()
        return dict(row)


def read_share(engine, token):
    if len(token) != 32 or not all(c.isalnum() or c in '_-' for c in token):
        return None
    with engine.connect() as conn:
        row = conn.execute(select(shares).where(shares.c.token == token,
                           shares.c.expires_at > datetime.now(timezone.utc))).mappings().first()
        return dict(row) if row else None


@lru_cache(maxsize=32)
def card_png(serialized):
    from PIL import Image, ImageDraw, ImageFont
    result = json.loads(serialized)
    bn = result.get('language') == 'bn'
    n = lambda value: number(value, 'bn' if bn else 'en')
    canvas = Image.new('RGB', (1200, 630), '#141613')
    draw = ImageDraw.Draw(canvas)
    def font(size, value=''):
        bengali = any('\u0980' <= c <= '\u09ff' for c in value)
        path = ROOT / 'web' / 'fonts' / ('NotoSansBengali.ttf' if bengali else 'Inter.ttf')
        return ImageFont.truetype(str(path), size) if path.exists() else ImageFont.load_default(size=size)
    def text(xy, value, color, size):
        if any('\u0980' <= c <= '\u09ff' for c in value):
            from .typography import draw_bengali
            draw_bengali(canvas, xy, value, size, color)
        else:
            draw.text(xy, value, fill=color, font=font(size, value))
    def width(value, size):
        if any('\u0980' <= c <= '\u09ff' for c in value):
            from .typography import text_width
            return text_width(value, size)
        return draw.textlength(value, font=font(size, value))
    def fitted(value, x, y, available, size, color):
        while width(value, size) > available and size > 15:
            size -= 1
        text((x,y), value, color, size)
    draw.rounded_rectangle((24,24,1176,606), radius=24, outline='#363b31', width=2)
    heading = 'মুভিগেম / আপনার চরিত্র' if bn else 'moviegame / CHARACTER REVEAL'
    text((60,48), heading, '#d7ff77', 18)
    name = result['display_name']
    owner = (f'{name} — চরিত্র পরিচয়' if name else 'আমার চরিত্র') if bn else (f'{name}’s character' if name else 'My character')
    fitted(owner, 60,92,880,30,'#c9b3ee')
    fitted(result['character_name'],60,145,880,57,'#f4f3e9')
    fitted(f'{result["movie_title"]} ({n(result["movie_year"])})',60,222,900,27,'#aab0a3')
    draw.rounded_rectangle((985,94,1138,232),radius=22,fill='#d7ff77')
    fitted(f'{n(result["affinity"])}%',1001,117,130,43,'#141613')
    label = 'গল্পের মিল' if bn else 'AFFINITY'
    text((1011,183),label,'#141613',15)
    for i, trait in enumerate(TRAITS):
        x, y = 60 + (i//4)*570, 300 + (i%4)*64
        value = int(result['profile'][trait])
        label = TRAIT_LABELS[trait] if bn else trait.capitalize()
        text((x,y),label,'#f4f3e9',19)
        text((x+421,y),n(value),'#d7ff77',19)
        draw.rounded_rectangle((x,y+32,x+465,y+43),radius=5,fill='#363b31')
        if value:
            draw.rounded_rectangle((x,y+32,x+max(10,465*value/100),y+43),radius=5,fill='#d7ff77' if i<4 else '#c9b3ee')
    footnote = '১৫টি পছন্দ। চেনা এক গল্প।  |  মজার ছলে মিল খোঁজা, ব্যক্তিত্বের বৈজ্ঞানিক মূল্যায়ন নয়।' if bn else '15 choices. A familiar story.  |  A playful match, not a personality assessment.'
    text((60,574),footnote,'#aab0a3',14)
    output = io.BytesIO()
    canvas.save(output, format='PNG', optimize=True)
    return output.getvalue()


def share_html(row, origin, language=None):
    language = language or row['snapshot'].get('language', 'en')
    data, token = localize_snapshot(row['snapshot'], language), row['token']
    bn = language == 'bn'
    n = lambda value: number(value, language)
    owner = f'{data["display_name"]}’s' if data['display_name'] else 'My'
    title = (f'{data["display_name"] or "আমার"} — চরিত্র {data["character_name"]} | মুভিগেম' if bn else f'{owner} character is {data["character_name"]} | MovieGame')
    description = (f'{data["movie_title"]} ছবির {data["character_name"]}-এর সঙ্গে গল্পের মিল {n(data["affinity"])}%। আটটি বৈশিষ্ট্যের ফলাফল দেখুন এবং নিজের চরিত্র খুঁজে নিন।' if bn else f'{data["affinity"]}% story affinity with {data["character_name"]} from {data["movie_title"]}. See the eight-trait bar result and find your own character.')
    e = html.escape
    image, url = f'{origin}/s/{token}/card.png?lang={language}', f'{origin}/s/{token}?lang={language}'
    mode_hash = '#character' if data.get('mode') == 'character' else '#quiz'
    bars = ''.join(f'<div><div class="trait-label"><span>{TRAIT_LABELS[t] if bn else t}</span><span>{n(int(data["profile"][t]))}</span></div><div class="bar"><span style="width:{int(data["profile"][t])}%"></span></div></div>' for t in TRAITS)
    cta = 'আমার চরিত্র খুঁজুন ↗' if bn else 'Find my character ↗'
    reveal = 'চরিত্র পরিচয়' if bn else 'A CHARACTER REVEAL'
    affinity = 'গল্পের মিল' if bn else 'story affinity'
    privacy = 'কাল্পনিক চরিত্রের সঙ্গে মজার ছলে মিল খোঁজা। এই পাতায় একটি নাম এবং বৈশিষ্ট্যের বার দেখানো হয়; জরিপের সম্পূর্ণ উত্তর প্রকাশ করা হয় না। সংরক্ষিত ফলাফলের মেয়াদ শেষ হলে এই পাতারও মেয়াদ শেষ হবে।' if bn else 'A playful interpretation of fictional characters. This shared page includes a display name and trait bars, not the full survey answers. It expires with the saved result.'
    download = 'ফলাফলের ছবি ডাউনলোড করুন' if bn else 'Download the result image'
    alt = 'আটটি বৈশিষ্ট্যের বারসহ ফলাফল' if bn else 'character result and eight trait bars'
    return f'''<!doctype html><html lang="{language}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{e(title)}</title><meta name="description" content="{e(description, quote=True)}"><meta name="robots" content="noindex,follow">
<meta property="og:type" content="website"><meta property="og:title" content="{e(title, quote=True)}"><meta property="og:description" content="{e(description, quote=True)}">
<meta property="og:url" content="{e(url, quote=True)}"><meta property="og:image" content="{e(image, quote=True)}"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630"><meta property="og:image:type" content="image/png"><meta property="og:image:alt" content="{e(alt, quote=True)}">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:image" content="{e(image, quote=True)}"><link rel="stylesheet" href="/assets/style.css?v=ec9b7cbcd15c"><script src="/assets/language.js?v=020d48106dd5" defer></script></head>
<body data-public-share><header class="topbar"><a class="brand" href="/?lang={language}">{'মুভিগেম' if bn else 'moviegame'}®</a><nav><a class="button small" href="/?lang={language}{mode_hash}">{cta}</a><fieldset class="language-control" id="language-switcher" aria-label="{'ভাষা' if bn else 'Language'}"><legend class="sr-only">{'ভাষা' if bn else 'Language'}</legend><button type="button" data-language="en" lang="en" aria-pressed="{str(not bn).lower()}">English</button><button type="button" data-language="bn" lang="bn" aria-pressed="{str(bn).lower()}">বাংলা</button></fieldset></nav></header>
<main class="section shared-page"><span class="eyebrow">{reveal}</span><h1>{e(title.split(' | ')[0])}</h1><p class="quiet">{e(data['movie_title'])} ({n(data['movie_year'])}) · {n(data['affinity'])}% {affinity}</p>
<img class="share-card-preview" src="/s/{token}/card.png?lang={language}" width="1200" height="630" alt="{e(alt, quote=True)}"><div class="trait-bars">{bars}</div>
<p class="quiet">{privacy}</p>
<a class="button" href="/?lang={language}{mode_hash}">{cta}</a> <a class="reference" href="/s/{token}/card.png?lang={language}&amp;download=1">{download}</a></main></body></html>'''


def poster_svg(movie, language='en'):
    e = html.escape
    color = {'hollywood':'#d7ff77','bangladeshi':'#f1a56a','anime':'#c9b3ee'}[movie['category']]
    lines = textwrap.wrap(movie['title'], width=19, break_long_words=True)[:5]
    title = ''.join(f'<tspan x="28" dy="39">{e(line)}</tspan>' for line in lines)
    brand = 'মুভিগেম' if language == 'bn' else 'MOVIEGAME'
    label = f'নিজস্ব প্রচ্ছদচিত্র · {CATEGORY_LABELS[movie["category"]]}' if language == 'bn' else f'ORIGINAL COVER ART · {movie["category"].upper()}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 360 510" role="img" aria-label="{e(movie['title'], quote=True)}"><rect width="360" height="510" rx="14" fill="{color}"/><circle cx="180" cy="152" r="98" fill="none" stroke="#23311e"/><circle cx="180" cy="152" r="59" fill="#23311e"/><path d="M164 112l57 40-57 40z" fill="{color}"/><text x="28" y="35" font-family="sans-serif" font-size="11" letter-spacing="2" fill="#23311e">{brand} / {number(movie['year'], language)}</text><text x="28" y="268" font-family="sans-serif" font-size="32" font-weight="bold" fill="#23311e">{title}</text><text x="28" y="484" font-family="sans-serif" font-size="10" fill="#23311e">{label}</text></svg>'''
