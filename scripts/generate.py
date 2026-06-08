#!/usr/bin/env python3
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

import google.auth.transport.requests
from google.oauth2.credentials import Credentials
import requests
from jinja2 import Environment, FileSystemLoader

TMDB_BASE = "https://api.themoviedb.org/3"
TMDB_IMAGE_BASE = "https://image.tmdb.org/t/p/original"
KEEP_API = "https://keep.googleapis.com/v1"
KEEP_NOTE_TITLE = os.environ.get("KEEP_NOTE_TITLE") or "Movies to Watch"
TMDB_API_KEY = os.environ["TMDB_API_KEY"]
HULU_ID = 15
HULU_LIVE_TV_ID = 381


def _keep_access_token():
    creds = Credentials(
        token=None,
        refresh_token=os.environ["GOOGLE_REFRESH_TOKEN"],
        client_id=os.environ["GOOGLE_CLIENT_ID"],
        client_secret=os.environ["GOOGLE_CLIENT_SECRET"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/keep.readonly"],
    )
    creds.refresh(google.auth.transport.requests.Request())
    return creds.token


def fetch_movie_list():
    token = _keep_access_token()
    headers = {"Authorization": f"Bearer {token}"}

    page_token = None
    while True:
        params = {"pageSize": 100}
        if page_token:
            params["pageToken"] = page_token
        r = requests.get(f"{KEEP_API}/notes", headers=headers, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        for note in data.get("notes", []):
            if note.get("trashed"):
                continue
            if note.get("title", "").lower() == KEEP_NOTE_TITLE.lower():
                body = note.get("body", {})
                if "listContent" in body:
                    return [
                        item["text"].strip()
                        for item in body["listContent"].get("listItems", [])
                        if not item.get("checked", False) and item.get("text", "").strip()
                    ]
                if "text" in body:
                    return [
                        line.strip()
                        for line in body["text"].get("text", "").splitlines()
                        if line.strip()
                    ]

        page_token = data.get("nextPageToken")
        if not page_token:
            break

    sys.exit(f"Keep note '{KEEP_NOTE_TITLE}' not found.")


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
    print(f"Reading Keep note: '{KEEP_NOTE_TITLE}'")
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

    print(f"Done → docs/index.html ({len(data)} movies)")


if __name__ == "__main__":
    main()
