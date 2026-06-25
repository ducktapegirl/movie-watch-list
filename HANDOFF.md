# Handoff Notes

Last updated: 2026-06-08

## Current status

The data source was switched from a GitHub Gist to a published Google Sheets
CSV, so multiple people can edit the list (including from the Sheets mobile
app).

**Live page:** https://ducktapegirl.github.io/movie-watch-list/

---

## How it works right now

```
Google Sheet (published to web as CSV, one title per row)
    -> GitHub Actions (daily 4am UTC + manual trigger)
       reads CSV, queries TMDB Watch Providers API per movie
       commits updated docs/index.html + docs/data.json to main
    -> GitHub Pages serves docs/
```

**Configured secrets/variables** (Settings -> Secrets and variables -> Actions):
- `TMDB_API_KEY` (secret) - TMDB v3 API key
- `SHEETS_CSV_URL` (variable) - published CSV URL of the Google Sheet

**Sheet:** published via File -> Share -> Publish to web -> CSV.
(edit the Sheet directly - one movie title per row in column A; an optional
header row of "Title" is ignored by `generate.py`)

> **Gotcha:** the Sheet must stay published for the workflow to read it -
> if publishing is turned off (Share -> Publish to web), the CSV URL starts
> returning an error page instead of CSV data.

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
Now using a Google Sheet published to web as CSV (implemented). Was
previously a GitHub Gist, which didn't support collaborative editing (only
the owner could edit).

**Google Sheets (published as CSV)** - implemented
- Best mobile editing experience (Sheets app)
- Supports multiple editors
- No auth needed in workflow - just a plain URL fetch like the Gist
- One setting to flip: File -> Share -> Publish to web -> CSV
- Sheet becomes publicly readable (fine for a movie list)
- `generate.py` reads `SHEETS_CSV_URL` and parses the response with Python's
  `csv` module, taking column A of each row and skipping a "Title" header
  row if present

**In-page refresh button with GitHub PAT**
- Implemented in `scripts/template.html` - a `<button>` POSTs to GitHub's
  `workflow_dispatch` API directly from the browser using a fine-grained PAT
  (`Actions: read and write`, scoped to this repo only)
- Originally tried hardcoding the PAT as a JS constant in the template, but
  GitHub's push protection blocks commits containing recognizable tokens -
  switched to prompting for it on first click and storing it in
  `localStorage` instead, so it's never written to the page source or git
- On a 401/403 the stored token is cleared and the user is re-prompted
  (handles rotation/expiry)
- If even browser-local storage of the token is a concern, a Netlify/Cloudflare Worker proxy (10-15 lines) would hide it server-side entirely

**Google Docs**
- No public API for reading doc content as plain text without OAuth
- Not worth pursuing

### 2. Collaborative editing
Solved by the Google Sheets switch (above) - share the Sheet with anyone who
needs to edit the list.

---

## Repo structure

```
.github/workflows/refresh.yml   - Actions workflow (cron + manual trigger)
scripts/generate.py             - reads Sheets CSV, queries TMDB, renders HTML
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
uv run python scripts/generate.py   # requires TMDB_API_KEY and SHEETS_CSV_URL env vars
```

---

## Known deleted/obsolete things
- `scripts/auth_keep.py` - removed (was for Google Keep OAuth, abandoned)
- `scripts/requirements.txt` - removed (replaced by pyproject.toml)
- Secrets `GOOGLE_EMAIL`, `GOOGLE_APP_PASSWORD`, `GOOGLE_CLIENT_ID`,
  `GOOGLE_CLIENT_SECRET`, `GOOGLE_REFRESH_TOKEN` can be deleted from GitHub
  if still present - none are referenced in the workflow anymore
