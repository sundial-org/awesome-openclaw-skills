#!/usr/bin/env python3
"""
Get detailed information about a specific Zoom meeting.
Usage: python get_meeting_info.py <meeting_id>
"""

import os
import sys
import json
import requests

# Load config
CONFIG_PATH = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(CONFIG_PATH, 'r') as f:
    config = json.load(f)

ACCOUNT_ID = config['account_id']
CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
USER_ID = config['user_id']

def get_access_token():
    """Get OAuth access token."""
    url = "https://api.zoom.us/oauth/token"
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET), data=data)
    response.raise_for_status()
    return response.json()['access_token']

def get_meeting_info(meeting_id):
    """Get details of a specific meeting."""
    token = get_access_token()
    url = f"https://api-us.zoom.us/v2/meetings/{meeting_id}"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python get_meeting_info.py <meeting_id>")
        sys.exit(1)

    meeting_id = sys.argv[1]
    try:
        info = get_meeting_info(meeting_id)
        print(json.dumps(info, indent=2))
    except requests.exceptions.HTTPError as e:
        print(f"Error: {e}")
        print(f"Response: {e.response.text}")
    except Exception as e:
        print(f"Unexpected error: {e}")