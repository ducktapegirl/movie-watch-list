# Movie Streaming Tracker

Reads your Google Sheets movie watchlist, checks which streaming services have each film, and publishes the results as a static webpage via GitHub Pages. Updates automatically every night; you can also trigger a refresh manually from the page.

## How It Works

1. GitHub Actions reads a published CSV version of your Google Sheets movie list.
2. For each movie it queries [TMDB](https://www.themoviedb.org) for US streaming availability (data from JustWatch).
3. Results are rendered as `docs/index.html` and committed back to the repo
4. GitHub Pages serves the page

---

## One-Time Setup

### 1. Get a TMDB API Key (free)

1. Create a free account at [themoviedb.org](https://www.themoviedb.org)
2. Go to **Settings → API → Request an API Key**
3. Select **Developer**, fill out the short form
4. Copy the **API Key (v3 auth)** — it looks like a short alphanumeric string
5. In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**
6. 
| Secret name | Value |
|---|---|
| `TMDB_API_KEY` | Your TMDB API Key (v3 auth) |

### 2. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Under **Source**, choose **Deploy from a branch**
3. Select **main** branch, **/docs** folder → Save

Your page will be at: `https://ducktapegirl.github.io/movie-watch-list/`

### 3. Manually run actions if necessary

Go to **Actions → Refresh Streaming Data → Run workflow → Run workflow**.

It takes about 30–60 seconds. Reload the page when it finishes.

## Streaming data notes

- Annotations on logos:
  - **(rent/buy)** — available but not included in a base subscription
  - **(Live TV tier)** — Hulu, but only on the Live TV plan
- A **—** means no US streaming found in TMDB's database
- Data is powered by JustWatch via TMDB and updates when streaming rights change
