# Movie Streaming Tracker

Reads your Google Keep movie watchlist, checks which streaming services have each film, and publishes the results as a static webpage via GitHub Pages. Updates automatically every night; you can also trigger a refresh manually from the page.

## How It Works

1. GitHub Actions reads your Keep checklist using the [official Google Keep API](https://developers.google.com/workspace/keep/api/reference/rest)
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

### 2. Set up Google Keep API access

#### a. Create a Google Cloud project and enable the Keep API

1. Go to [console.cloud.google.com](https://console.cloud.google.com) and create a new project (or select an existing one)
2. Go to **APIs & Services → Library**, search for **Google Keep API**, and click **Enable**

#### b. Create OAuth 2.0 credentials

1. Go to **APIs & Services → Credentials → Create Credentials → OAuth client ID**
2. If prompted, configure the OAuth consent screen first:
   - User type: **External**; fill in app name and your email; no scopes needed on this screen
3. Application type: **Desktop app** → name it anything → **Create**
4. Click **Download JSON** on the newly created credential — save it as `credentials.json`

#### c. Run the one-time auth script locally

You need Python 3.10+ and the dependencies installed:

```bash
pip install google-auth-oauthlib
python scripts/auth_keep.py
```

A browser window will open. Sign in with your Google account and grant access. The script prints three values — copy them.

### 3. Add GitHub Secrets

In your GitHub repo: **Settings → Secrets and variables → Actions → New repository secret**

| Secret name | Value |
|---|---|
| `TMDB_API_KEY` | Your TMDB API Key (v3 auth) |
| `GOOGLE_CLIENT_ID` | Printed by `auth_keep.py` |
| `GOOGLE_CLIENT_SECRET` | Printed by `auth_keep.py` |
| `GOOGLE_REFRESH_TOKEN` | Printed by `auth_keep.py` |

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

Click the **↻ Refresh** button at the top of the watchlist page. It triggers the GitHub Actions workflow directly from the page (no GitHub login needed) and reloads automatically once it's done.

The first time you click it, you'll be prompted for a [fine-grained personal access token](https://github.com/settings/personal-access-tokens) scoped to **this repo only**, with **Actions: Read and write** permission and nothing else. It's saved in your browser's `localStorage` (never committed to the repo or written into the page source) so you only need to enter it once per browser.

If the button ever fails with a 401/403, the saved token is cleared automatically and you'll be re-prompted — handy after rotating the token. Revoke/regenerate it any time from the same GitHub settings page.

The page auto-refreshes every night at midnight ET (4am UTC).

---

## Streaming data notes

- Annotations on logos:
  - **(rent/buy)** — available but not included in a base subscription
  - **(Live TV tier)** — Hulu, but only on the Live TV plan
- A **—** means no US streaming found in TMDB's database
- Data is powered by JustWatch via TMDB and updates when streaming rights change
