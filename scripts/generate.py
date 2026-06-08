#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests
from jinja2 import Environment, FileSystemLoader

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
HULU_ID = 15
HULU_LIVE_TV_ID = 381


def fetch_movie_list():
    url = os.environ["GIST_URL"]
    r = requests.get(url, timeout=10)
    r.raise_for_status()
    return [line.strip() for line in r.text.splitlines() if line.strip()]


def tmdb_search(title):
    r = requests.get(
        f"{TMDB_BASE}/search/movie",
        params={"api_key": TMDB_API_KEY, "query": title, "language": "en-US"},
        timeout=10,
    )
    r.raise_for_status()
    results = r.json().get("results", [])
    return results[0]["id"] if results else None


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

    return sorted(seen.values(), key=lambda x: x["priority"])


def build_data(movies):
    results = []
    for title in movies:
        print(f"  {title}")
        movie_id = tmdb_search(title)
        providers = tmdb_providers(movie_id) if movie_id else []
        results.append({"title": title, "providers": providers})
    return results


def main():
    print("Fetching movie list from Gist...")
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
