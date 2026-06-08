#!/usr/bin/env python3
"""
Run this once locally to get a Google OAuth refresh token for GitHub Secrets.

Usage:
  python3 scripts/auth_keep.py /path/to/your/downloaded-credentials.json

  1. Download your OAuth2 credentials from Google Cloud Console
     (APIs & Services -> Credentials -> your OAuth 2.0 Client ID -> Download JSON)
  2. Pass the path to that file as the argument - any filename works
  3. A browser window opens -- sign in and grant access
  4. Copy the three values printed at the end into GitHub Secrets
"""
import sys
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/keep.readonly"]

if len(sys.argv) != 2:
    print("Usage: python3 scripts/auth_keep.py /path/to/credentials.json")
    sys.exit(1)

CREDS_FILE = Path(sys.argv[1])

if not CREDS_FILE.exists():
    raise FileNotFoundError("File not found: {}".format(CREDS_FILE))

flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
creds = flow.run_local_server(port=0)

print("\nAuth complete. Add these three values to GitHub Secrets:")
print("  (Settings -> Secrets and variables -> Actions -> New repository secret)\n")
print("  GOOGLE_CLIENT_ID     = {}".format(creds.client_id))
print("  GOOGLE_CLIENT_SECRET = {}".format(creds.client_secret))
print("  GOOGLE_REFRESH_TOKEN = {}".format(creds.refresh_token))
