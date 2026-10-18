"""Cache public Wikipedia artwork metadata; never download media or run in requests.

Usage: python scripts/fetch_posters.py [--refresh] [--batch-size 30]
Sources: https://www.mediawiki.org/wiki/API:Pageimages
PageImages with pilicense=any may return non-free movie posters. These references
do not assert a free license or grant reuse rights. Review rights before publishing.
Run again after adding catalog files; the default preserves existing cached URLs.
"""

import argparse
import json
import time
import unicodedata
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, unquote, urlencode, urlsplit
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CACHE = DATA / "_posters.json"
API = "https://en.wikipedia.org/w/api.php"
CREDIT = "Reference artwork via Wikipedia; rights belong to the respective owners"
SOURCE_TITLES = {
    "https://rootfilms.org/the-salt-in-our-waters": "Nonajoler Kabbo",
    "https://archiv.zlinfest.cz/en/film-detail?id=17907": "Rickshaw Girl",
}


def normalize(title):
    return " ".join(unicodedata.normalize("NFC", title).replace("_", " ").split()).casefold()


def source_title(source):
    if source in SOURCE_TITLES:
        return SOURCE_TITLES[source]
    parsed = urlsplit(source)
    if parsed.scheme != "https" or parsed.hostname != "en.wikipedia.org" or not parsed.path.startswith("/wiki/"):
        return None
    title = unquote(parsed.path.removeprefix("/wiki/"))
    namespaces = {"file", "category", "special", "talk", "user", "wikipedia", "help", "template", "portal", "draft", "module", "media"}
    return title if title and title.split(":", 1)[0].casefold() not in namespaces else None


def catalog_sources():
    paths = [DATA / name for name in ("asian_cinema.json", "hollywood_classic.json", "hollywood_modern.json")]
    paths += sorted(DATA.glob("additional*.json"))
    sources = {}
    film_count = 0
    for path in paths:
        try:
            movies = json.loads(path.read_text(encoding="utf-8-sig"))
        except (OSError, json.JSONDecodeError) as error:
            print(f"Skipping unreadable catalog {path.name}: {error}", flush=True)
            continue
        for movie in movies:
            film_count += 1
            source = movie.get("source_url", "")
            title = source_title(source)
            if title:
                sources[source] = title
    return sources, film_count


def request_images(titles):
    params = dict(action="query", format="json", formatversion=2,
                  prop="pageimages|pageprops", ppprop="disambiguation", redirects=1,
                  piprop="thumbnail|name", pithumbsize=400, pilicense="any",
                  pilimit="max", titles="|".join(titles))
    request = Request(API + "?" + urlencode(params), headers={
        "User-Agent": "MovieGameCatalog/2.0 (public artwork metadata cache)",
        "Accept": "application/json",
    })
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                payload = json.load(response)
            if "error" in payload:
                raise ValueError(str(payload["error"]))
            return payload.get("query", {})
        except (HTTPError, URLError, TimeoutError, ValueError, OSError) as error:
            if attempt == 2:
                print(f"Batch failed after two retries: {error}", flush=True)
                return None
            retry_after = error.headers.get("Retry-After", "") if isinstance(error, HTTPError) else ""
            delay = min(float(retry_after), 30) if retry_after.isdigit() else 3 * 2 ** attempt
            time.sleep(delay)


def resolved_pages(query):
    aliases = {}
    for kind in ("normalized", "converted", "redirects"):
        for item in query.get(kind, []):
            aliases[normalize(item["from"])] = normalize(item["to"])
    pages = {normalize(page["title"]): page for page in query.get("pages", [])}

    def resolve(title):
        title = normalize(title)
        seen = set()
        while title in aliases and title not in seen:
            seen.add(title)
            title = aliases[title]
        return pages.get(title, {})

    return resolve


def artwork(page, source):
    if page.get("ns") != 0 or page.get("missing") or page.get("invalid") or "disambiguation" in page.get("pageprops", {}):
        return None
    thumbnail = page.get("thumbnail", {}).get("source", "")
    parsed = urlsplit(thumbnail)
    filename = page.get("pageimage", "")
    if parsed.scheme != "https" or parsed.hostname not in {"upload.wikimedia.org", "thumb.wikimedia.org"} or not parsed.path.startswith("/wikipedia/") or not filename:
        return None
    # The newer thumb host exposes the same paths on Wikimedia's upload host.
    # Preserve API-provided file paths; only normalize the verified CDN alias.
    thumbnail = parsed._replace(netloc="upload.wikimedia.org").geturl()
    page_url = "https://en.wikipedia.org/wiki/" + quote(page["title"].replace(" ", "_"), safe="()!,'-._:")
    return dict(url=thumbnail, kind="reference-artwork", source_url=page_url, credit=CREDIT,
                file_page="https://en.wikipedia.org/wiki/File:" + quote(filename.replace(" ", "_"), safe="()!,'-._"))


def save(cache):
    temporary = CACHE.with_suffix(".json.tmp")
    try:
        temporary.write_text(json.dumps(cache, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        temporary.replace(CACHE)
    finally:
        temporary.unlink(missing_ok=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="Recheck sources already cached")
    parser.add_argument("--batch-size", type=int, default=30, choices=range(20, 41), metavar="20..40")
    args = parser.parse_args()
    sources, film_count = catalog_sources()
    cache = json.loads(CACHE.read_text(encoding="utf-8-sig")) if CACHE.exists() else {}
    pending = [(source, title) for source, title in sources.items() if args.refresh or source not in cache]
    print(f"Catalog: {film_count} films; {len(sources)} distinct eligible sources; {len(cache)} cached; {len(pending)} pending", flush=True)
    for offset in range(0, len(pending), args.batch_size):
        batch = pending[offset:offset + args.batch_size]
        query = request_images(list(dict.fromkeys(title for _, title in batch)))
        if query is None:
            print("Fetch interrupted; existing cache preserved. Rerun to resume.", flush=True)
            break
        resolve = resolved_pages(query)
        added = 0
        for source, title in batch:
            entry = artwork(resolve(title), source)
            if entry:
                cache[source] = entry
                added += 1
        save(cache)
        print(f"Processed {min(offset + len(batch), len(pending))}/{len(pending)} pending sources: {added} references; {len(cache)} cached", flush=True)
        time.sleep(1)
    if not CACHE.exists():
        save(cache)
    available = sum(source in cache for source in sources)
    print(f"Complete: {available}/{len(sources)} eligible sources have artwork; {len(sources) - available} use original generated covers.", flush=True)


if __name__ == "__main__":
    main()
