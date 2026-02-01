#!/usr/bin/env python3
"""
Complete Strava OAuth by exchanging authorization code for tokens.
"""
import json
import sys
from pathlib import Path
import requests

CONFIG_PATH = Path.home() / ".config" / "strava" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found. Run scripts/setup.sh first.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def exchange_token(config, auth_code):
    """Exchange authorization code for access token."""
    url = "https://www.strava.com/oauth/token"
    
    data = {
        'client_id': config['client_id'],
        'client_secret': config['client_secret'],
        'code': auth_code,
        'grant_type': 'authorization_code'
    }
    
    response = requests.post(url, data=data)
    response.raise_for_status()
    
    return response.json()

def save_tokens(config, token_response):
    """Save access and refresh tokens to config."""
    config['access_token'] = token_response['access_token']
    config['refresh_token'] = token_response['refresh_token']
    config['expires_at'] = token_response['expires_at']
    config['athlete'] = token_response['athlete']
    
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=2)
    
    CONFIG_PATH.chmod(0o600)

def main():
    if len(sys.argv) < 2:
        print("Usage: complete_auth.py <authorization_code>", file=sys.stderr)
        sys.exit(1)
    
    auth_code = sys.argv[1]
    config = load_config()
    
    print("Exchanging authorization code for tokens...")
    token_response = exchange_token(config, auth_code)
    
    print("Saving tokens...")
    save_tokens(config, token_response)
    
    athlete = token_response['athlete']
    print(f"\n✓ Authentication complete!")
    print(f"  Athlete: {athlete['firstname']} {athlete['lastname']}")
    print(f"  ID: {athlete['id']}")
    print(f"\nYou can now use the Strava API!")

if __name__ == '__main__':
    main()
