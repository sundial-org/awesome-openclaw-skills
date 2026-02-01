#!/usr/bin/env python3
import requests
import json
import os
import sys

# Загрузка конфигурации
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
except FileNotFoundError:
    print("Error: config.json not found. Please create it with your Zoom API credentials.")
    sys.exit(1)

ACCOUNT_ID = config['account_id']
CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
USER_ID = config['user_id']

def get_access_token():
    url = "https://api.zoom.us/oauth/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(url, headers=headers, data=data, auth=(CLIENT_ID, CLIENT_SECRET))
    if response.status_code == 200:
        return response.json().get('access_token')
    else:
        print(f"Failed to get access token: {response.status_code} - {response.text}")
        return None

def delete_meeting(meeting_id):
    access_token = get_access_token()
    if not access_token:
        return False

    url = f"https://api.zoom.us/v2/meetings/{meeting_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.delete(url, headers=headers)
    if response.status_code == 204:
        print(f"Meeting {meeting_id} deleted successfully.")
        return True
    else:
        print(f"Failed to delete meeting {meeting_id}: {response.status_code} - {response.text}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python delete_meeting.py <meeting_id>")
        sys.exit(1)

    meeting_id = sys.argv[1]
    delete_meeting(meeting_id)