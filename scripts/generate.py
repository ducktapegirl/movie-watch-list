#!/usr/bin/env python3
import csv
import json
import os
import re
import sys
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
HULU_ID = 15
HULU_LIVE_TV_ID = 381

ALLOWED_PROVIDERS = {
    "Netflix",
    "Amazon Prime Video",
    "Amazon Video",
    "Apple TV",
    "Apple TV Store",
    "Disney Plus",
    "Hulu",
    "HBO Max",
    "Peacock Premium",
    "Fandango At Home",
    "FlixFling",
    "Google Play Movies",
    "Hoopla",
    "Plex",
    "Pluto TV",
    "The Roku Channel",
    "Tubi TV",
    "Xumo Play",
    "YouTube",
    "YouTube TV",
    "fuboTV",
}

_WORD_RE = re.compile(r"[A-Za-z0-9]+(?:['’][A-Za-z]+)*")


def to_title_case(text):
    # str.title() splits words on apostrophes too, so "it's" becomes
    # "It'S". Treat an apostrophe followed by letters as part of the
    # same word instead.
    return _WORD_RE.sub(lambda m: m.group(0)[0].upper() + m.group(0)[1:].lower(), text)


def fetch_movie_list():
    url = os.environ["SHEETS_CSV_URL"]
    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    r.raise_for_status()
    if r.text.lstrip().lower().startswith(("<!doctype", "<html")):
        raise RuntimeError(
            "SHEETS_CSV_URL did not return CSV (got an HTML page instead). "
            "Check that the sheet is still published (File > Share > Publish "
            "to web) and that the URL ends with output=csv."
        )
    titles = []
    for row in csv.reader(StringIO(r.text)):
        if not row or not row[0].strip():
            continue
        title = row[0].strip()
        if title.lower() == "title":
            continue
        titles.append(title)
    return titles


def tmdb_search(title):
    r = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": title, "language": "en-US"},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json().get("results", [])
    if not results:
        return None, None
    top = results[0]
    return top["id"], top.get("release_date") or None


def tmdb_providers(movie_id):
    r = requests.get(
        f"{TMDB_BASE}/movie/{movie_id}/watch/providers",
        params={"api_key": TMDB_API_KEY},
        timeout=10,
    )
    r.raise_for_status()
    us = r.json().get("results", {}).get("US", {})

    seen = {}
    for bucket in ("flatrate", "free", "ads", "rent", "buy"):
        for p in us.get(bucket, []):
            pid = p["provider_id"]
            if pid not in seen:
                seen[pid] = {
                    "id": pid,
                    "name": p["provider_name"],
                    "logo": TMDB_IMAGE_BASE + p["logo_path"],
                    "priority": p.get("display_priority", 999),
                    "note": None,
                }
            if bucket in ("rent", "buy") and seen[pid]["note"] is None:
                seen[pid]["note"] = "rent/buy"

    if HULU_LIVE_TV_ID in seen and HULU_ID not in seen:
        seen[HULU_LIVE_TV_ID]["note"] = "Live TV tier"

    kept = [p for p in seen.values() if p["name"] in ALLOWED_PROVIDERS]
    return sorted(kept, key=lambda x: x["priority"])


def build_data(movies):
    results = []
    for title in movies:
        print(f"  {title}")
        movie_id, release_date = tmdb_search(title)
        providers = tmdb_providers(movie_id) if movie_id else []
        results.append(
            {"title": to_title_case(title), "release_date": release_date, "providers": providers}
        )
    return results


def main():
    print("Fetching movie list from Google Sheet...")
    movies = fetch_movie_list()
    print(f"Found {len(movies)} movies. Fetching streaming data...")

    data = build_data(movies)
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    out_dir = Path(__file__).parent.parent / "docs"
    out_dir.mkdir(exist_ok=True)

    (out_dir / "data.json").write_text(
        json.dumps({"updated_at": updated_at, "movies": data}, indent=2, default=str)
    )

    env = Environment(loader=FileSystemLoader(Path(__file__).parent))
    template = env.get_template("template.html")
    (out_dir / "index.html").write_text(template.render(movies=data, updated_at=updated_at))

    print(f"Done - docs/index.html ({len(data)} movies)")


if __name__ == "__main__":
    main()
