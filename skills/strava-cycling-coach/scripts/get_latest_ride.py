#!/usr/bin/env python3
"""
Get the latest virtual ride from Strava.
"""
import json
import sys
from pathlib import Path
import requests
import time

CONFIG_PATH = Path.home() / ".config" / "strava" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found. Run scripts/setup.sh first.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def refresh_token_if_needed(config):
    """Refresh access token if expired."""
    if config['expires_at'] < time.time():
        url = "https://www.strava.com/oauth/token"
        data = {
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
            'refresh_token': config['refresh_token'],
            'grant_type': 'refresh_token'
        }
        
        response = requests.post(url, data=data)
        response.raise_for_status()
        
        token_data = response.json()
        config['access_token'] = token_data['access_token']
        config['refresh_token'] = token_data['refresh_token']
        config['expires_at'] = token_data['expires_at']
        
        with open(CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=2)
    
    return config

def get_latest_activity(config):
    config = refresh_token_if_needed(config)
    
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f"Bearer {config['access_token']}"}
    params = {'per_page': 20}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    activities = response.json()
    
    # Find latest virtual ride
    for activity in activities:
        if activity.get('type') == 'VirtualRide':
            return activity
    
    return None

def main():
    config = load_config()
    activity = get_latest_activity(config)
    
    if activity:
        print(json.dumps(activity, indent=2))
    else:
        print("No virtual rides found", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
