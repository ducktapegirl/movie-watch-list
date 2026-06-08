# Handoff Notes

Last updated: 2026-06-08

## Current status

The app is working end-to-end. The most recent successful workflow run (run #2, 2026-06-08 05:10 UTC) read 43 movies from the Gist and published live streaming data to GitHub Pages.

**Live page:** https://ducktapegirl.github.io/movie-watch-list/

---

## How it works right now

```
GitHub Gist (movies.txt, one title per line)
    -> GitHub Actions (daily 4am UTC + manual trigger)
       reads Gist, queries TMDB Watch Providers API per movie
       commits updated docs/index.html + docs/data.json to main
    -> GitHub Pages serves docs/
```

**Configured secrets/variables** (Settings -> Secrets and variables -> Actions):
- `TMDB_API_KEY` (secret) - TMDB v3 API key
- `GIST_URL` (variable) - raw URL of the movies.txt Gist

**Gist:** https://gist.github.com/ducktapegirl/f87259c8947e5262b5e47627444c6f65
(edit at gist.github.com - one movie title per line)

---

## Two warnings in the last workflow run

### 1. uv cache glob warning (cosmetic, low priority)
```
No file matched to [**/uv.lock,**/requirements*.txt].
The cache will never get invalidated.
```
The `setup-uv` action looks for `uv.lock` or `requirements*.txt` to invalidate its cache, but we use `pyproject.toml`. Fix: either run `uv lock` to generate a `uv.lock` file and commit it, or configure `cache-dependency-glob: pyproject.toml` in the workflow.

### 2. Node.js 20 deprecation warning (time-sensitive)
```
Node.js 20 actions are deprecated...
Actions will be forced to run with Node.js 24 by default starting June 16th, 2026.
```
`actions/checkout@v4` and `astral-sh/setup-uv@v5` need to be updated. **Deadline: June 16, 2026** (8 days from last run). Fix: bump both to their latest versions that support Node 24, or add `FORCE_JAVASCRIPT_ACTIONS_TO_NODE24: true` as an env var in the workflow in the meantime.

---

## UI tweaks wanted

- Alternating row colors on the table
- New page title (user to specify what they want it changed to)

---

## Open questions / things to explore next

### 1. Movie list data source
Currently using a GitHub Gist. Limitations: no collaborative editing (only owner can edit).

Options under consideration:

**Google Sheets (published as CSV)**
- Best mobile editing experience (Sheets app)
- Supports multiple editors
- No auth needed in workflow - just a plain URL fetch like the Gist
- One setting to flip: File -> Share -> Publish to web -> CSV
- Sheet becomes publicly readable (fine for a movie list)
- `generate.py` change: swap `requests.get(GIST_URL)` for `requests.get(SHEETS_CSV_URL)` + CSV parsing

**In-page refresh button with GitHub PAT**
- A button on the live page that triggers the workflow directly
- Requires a fine-grained PAT with `Actions: write` scope stored in the page JS
- Token is visible in page source - acceptable risk for a personal page since worst case is someone spamming your workflow
- If token exposure is a concern, a Netlify/Cloudflare Worker proxy (10-15 lines) would hide it server-side
- Status: discussed but not implemented

**Google Docs**
- No public API for reading doc content as plain text without OAuth
- Not worth pursuing

### 2. Collaborative editing
Gists don't support collaborators. If a second person needs to edit the list:
- Google Sheets (above) is the cleanest solution
- Alternatively: add the collaborator as a repo contributor and have them edit a `movies.txt` file in the repo via GitHub's web UI

---

## Repo structure

```
.github/workflows/refresh.yml   - Actions workflow (cron + manual trigger)
scripts/generate.py             - reads Gist, queries TMDB, renders HTML
scripts/template.html           - Jinja2 template for the page
pyproject.toml                  - Python 3.12 + dependencies (requests, jinja2)
docs/index.html                 - generated output, served by GitHub Pages
docs/data.json                  - raw generated data (useful for debugging)
README.md                       - setup instructions
```

---

## Local dev

```bash
uv sync                         # creates .venv with Python 3.12
uv run python scripts/generate.py   # requires TMDB_API_KEY and GIST_URL env vars
```

---

## Known deleted/obsolete things
- `scripts/auth_keep.py` - removed (was for Google Keep OAuth, abandoned)
- `scripts/requirements.txt` - removed (replaced by pyproject.toml)
- Secrets `GOOGLE_EMAIL`, `GOOGLE_APP_PASSWORD`, `GOOGLE_CLIENT_ID`,
  `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` can be deleted from GitHub
  if still present - none are referenced in the workflow anymore
