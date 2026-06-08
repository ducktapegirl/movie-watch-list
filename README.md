# Movie Streaming Tracker

Reads your Google Keep movie watchlist, checks which streaming services have each film, and publishes the results as a static webpage via GitHub Pages. Updates automatically every night; you can also trigger a refresh manually from the page.

## How It Works

1. GitHub Actions reads your Keep checklist using [gkeepapi](https://github.com/kiwiz/gkeepapi)
2. For each movie it queries [TMDB](https://www.themoviedb.org) for US streaming availability (data from JustWatch)
3. Results are rendered as `docs/index.html` and committed back to the repo
4. GitHub Pages serves the page

---

## One-Time Setup

### 1. Get a TMDB API Key (free)

1. Create a free account at [themoviedb.org](https://www.themoviedb.org)
2. Go to **Settings → API → Request an API Key**
3. Select **Developer**, fill out the short form
4. Copy the **API Key (v3 auth)** — it looks like a short alphanumeric string

### 2. Get a Google App Password

gkeepapi signs in with your Google account. If you have 2-Step Verification (you should), you need an App Password instead of your regular password.

1. Go to [myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
2. Sign in if prompted, then enable 2-Step Verification if not already on
3. Under **App name**, type `Movie Watchlist` and click **Create**
4. Copy the 16-character password shown (no spaces)

### 3. Add GitHub Secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `TMDB_API_KEY` | Your TMDB API Key (v3 auth) |
| `GOOGLE_EMAIL` | Your Gmail address |
| `GOOGLE_APP_PASSWORD` | The 16-character App Password from step 2 |

### 4. Set your Keep note title (if needed)

The app looks for a Keep note titled **"Movies to Watch"** by default.

To use a different title: **Settings → Secrets and variables → Actions → Variables tab → New repository variable**

| Variable name | Value |
|---|---|
| `KEEP_NOTE_TITLE` | Your note's exact title (case-insensitive) |

### 5. Enable GitHub Pages

1. Go to **Settings → Pages**
2. Under **Source**, choose **Deploy from a branch**
3. Select **main** branch, **/docs** folder → Save

Your page will be at: `https://ducktapegirl.github.io/movie-watch-list/`

### 6. Run the first refresh

Go to **Actions → Refresh Streaming Data → Run workflow → Run workflow**.

It takes about 30–60 seconds. Reload the page when it finishes.

---

## Keep Note Format

Use a standard Keep **checklist**:

- ☐ Unchecked = want to watch → shown on the page
- ☑ Checked = already watched → hidden

A plain text note with one movie title per line also works.

---

## Manual Refresh

Click the **↻ Refresh** link at the top of the watchlist page. It opens the GitHub Actions workflow page where you click **Run workflow**.

The page auto-refreshes every night at midnight ET (4am UTC).

---

## Streaming data notes

- Annotations on logos:
  - **(rent/buy)** — available but not included in a base subscription
  - **(Live TV tier)** — Hulu, but only on the Live TV plan
- A **—** means no US streaming found in TMDB's database
- Data is powered by JustWatch via TMDB and updates when streaming rights change
