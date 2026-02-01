#!/usr/bin/env python3
"""
Google Search Console OAuth Authentication

Generates OAuth credentials for the Search Console API.
Run this once to get a refresh token, then use it in .env

Usage:
    python gsc_auth.py --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET
    
Or set environment variables:
    GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
"""

import argparse
import os
import sys

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
except ImportError:
    print("ERROR: Required package not installed. Run:")
    print("  pip install google-auth-oauthlib")
    sys.exit(1)

# Search Console API scopes
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    # Add write scope if you need to submit sitemaps etc:
    # "https://www.googleapis.com/auth/webmasters",
]


def main():
    parser = argparse.ArgumentParser(description="Authenticate with Google Search Console")
    parser.add_argument("--client-id", help="Google OAuth Client ID")
    parser.add_argument("--client-secret", help="Google OAuth Client Secret")
    args = parser.parse_args()
    
    client_id = args.client_id or os.environ.get("GOOGLE_CLIENT_ID")
    client_secret = args.client_secret or os.environ.get("GOOGLE_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        print("ERROR: Need client_id and client_secret.")
        print("Either pass --client-id and --client-secret, or set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET")
        sys.exit(1)
    
    # Build client config
    client_config = {
        "installed": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": ["http://localhost", "urn:ietf:wg:oauth:2.0:oob"]
        }
    }
    
    print("=" * 60)
    print("Google Search Console OAuth Setup")
    print("=" * 60)
    print()
    print("This will open a browser window for authentication.")
    print("Make sure your Google Cloud OAuth consent screen includes")
    print("the Search Console API scope.")
    print()
    print("Scopes requested:")
    for scope in SCOPES:
        print(f"  - {scope}")
    print()
    
    # Run OAuth flow
    flow = InstalledAppFlow.from_client_config(client_config, SCOPES)
    
    try:
        creds = flow.run_local_server(port=8080, prompt="consent")
    except Exception as e:
        print(f"Browser auth failed: {e}")
        print("Trying console-based auth...")
        creds = flow.run_console()
    
    print()
    print("=" * 60)
    print("SUCCESS! Add these to your .env file:")
    print("=" * 60)
    print()
    print(f"GOOGLE_CLIENT_ID={client_id}")
    print(f"GOOGLE_CLIENT_SECRET={client_secret}")
    print(f"GOOGLE_REFRESH_TOKEN={creds.refresh_token}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
