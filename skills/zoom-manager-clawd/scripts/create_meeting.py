#!/usr/bin/env python3
import json
import requests
import sys
import os

# Load config
config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
with open(config_path, 'r') as f:
    config = json.load(f)

ACCOUNT_ID = config['account_id']
CLIENT_ID = config['client_id']
CLIENT_SECRET = config['client_secret']
USER_ID = config['user_id']

def get_access_token():
    url = "https://api.zoom.us/oauth/token"
    data = {
        "grant_type": "account_credentials",
        "account_id": ACCOUNT_ID
    }
    response = requests.post(url, auth=(CLIENT_ID, CLIENT_SECRET), data=data)
    response.raise_for_status()
    return response.json()['access_token']

def create_meeting(topic, start_time, duration_minutes):
    access_token = get_access_token()
    url = f"https://api.zoom.us/v2/users/{USER_ID}/meetings"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    payload = {
        "topic": topic,
        "type": 2,  # Scheduled meeting
        "start_time": start_time,
        "duration": duration_minutes,
        "timezone": "UTC",
        "settings": {
            "host_video": True,
            "participant_video": True,
            "join_before_host": False,
            "mute_upon_entry": False,
            "approval_type": 0,
            "audio": "both",
            "auto_recording": "cloud"
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: create_meeting.py <topic> <start_time> <duration_minutes>")
        sys.exit(1)
    
    topic = sys.argv[1]
    start_time = sys.argv[2]
    duration_minutes = int(sys.argv[3])
    
    try:
        meeting = create_meeting(topic, start_time, duration_minutes)
        print(f"Meeting created successfully!")
        print(f"ID: {meeting['id']}")
        print(f"Join URL: {meeting['join_url']}")
        print(f"Start Time: {meeting['start_time']}")
    except Exception as e:
        print(f"Error: {e}")