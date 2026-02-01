#!/usr/bin/env python3
"""
List all upcoming meetings for the authenticated user.
Usage: python list_meetings.py
"""

import json
import requests
import os

# Load config
with open('config.json', 'r') as f:
    config = json.load(f)

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
    response.raise_for_status()
    return response.json()['access_token']

def list_meetings(access_token):
    url = f"https://api-us.zoom.us/v2/users/{USER_ID}/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    params = {
        "type": "upcoming"
    }
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    try:
        token = get_access_token()
        meetings = list_meetings(token)
        
        if 'meetings' not in meetings or not meetings['meetings']:
            print("No upcoming meetings found.")
        else:
            print(f"Found {len(meetings['meetings'])} upcoming meeting(s):")
            for meeting in meetings['meetings']:
                print(f"- ID: {meeting['id']}")
                print(f"  Topic: {meeting['topic']}")
                print(f"  Start: {meeting['start_time']}")
                print(f"  Join URL: {meeting['join_url']}\n")
                
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")