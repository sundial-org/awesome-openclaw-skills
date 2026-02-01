#!/usr/bin/env python3
"""
Monitor for new Strava rides and send analysis.
"""
import json
import sys
from pathlib import Path
import requests
import time
from cache_manager import load_cached_activities, update_cache_with_new_activities

CONFIG_PATH = Path.home() / ".config" / "strava" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found.", file=sys.stderr)
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

def fetch_recent_activities(config, limit=10):
    """Fetch recent activities from Strava."""
    config = refresh_token_if_needed(config)
    
    url = "https://www.strava.com/api/v3/athlete/activities"
    headers = {'Authorization': f"Bearer {config['access_token']}"}
    params = {'per_page': limit}
    
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    
    return response.json()

def find_new_virtual_rides():
    """Check for new virtual rides since last check."""
    config = load_config()
    
    # Get cached activities
    cached = load_cached_activities()
    cached_ids = {a['id'] for a in cached}
    
    # Fetch recent activities
    recent = fetch_recent_activities(config, limit=20)
    
    # Find new virtual rides
    new_rides = []
    for activity in recent:
        if activity['id'] not in cached_ids and activity.get('type') == 'VirtualRide':
            new_rides.append(activity)
    
    # Update cache
    if new_rides:
        update_cache_with_new_activities(recent)
    
    return new_rides

def main():
    try:
        new_rides = find_new_virtual_rides()
        
        if new_rides:
            print(f"Found {len(new_rides)} new virtual ride(s):")
            for ride in new_rides:
                print(f"  - {ride['name']} ({ride['id']})")
            
            # Output ride IDs for processing
            for ride in new_rides:
                print(f"NEW_RIDE:{ride['id']}")
        else:
            print("No new rides found")
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()
