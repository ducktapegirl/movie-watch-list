#!/usr/bin/env python3
"""
Run this once locally to get a Google OAuth refresh token for GitHub Secrets.

Usage:
  1. Download your OAuth2 credentials from Google Cloud Console as credentials.json
     (APIs & Services → Credentials → your OAuth 2.0 Client ID → Download JSON)
  2. Place credentials.json in this directory (scripts/)
  3. Run: python scripts/auth_keep.py
  4. A browser window opens — sign in and grant access
  5. Copy the three values printed at the end into GitHub Secrets
"""
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/keep.readonly"]
CREDS_FILE = Path(__file__).parent / "credentials.json"

if not CREDS_FILE.exists():
    raise FileNotFoundError(
        "credentials.json not found in scripts/.\n"
        "Download it from Google Cloud Console → APIs & Services → Credentials → "
        "your OAuth 2.0 Client ID → Download JSON"
    )

flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
creds = flow.run_local_server(port=0)

print("\n✓ Auth complete. Add these three values to GitHub Secrets:")
print(f"  (Settings → Secrets and variables → Actions → New repository secret)\n")
print(f"  GOOGLE_CLIENT_ID     = {creds.client_id}")
print(f"  GOOGLE_CLIENT_SECRET = {creds.client_secret}")
print(f"  GOOGLE_REFRESH_TOKEN = {creds.refresh_token}")
