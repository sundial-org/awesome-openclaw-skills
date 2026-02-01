#!/usr/bin/env python3
"""
Manage local cache of Strava activities.
"""
import json
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / ".cache" / "strava"
ACTIVITIES_CACHE = CACHE_DIR / "activities.json"
LAST_SYNC_FILE = CACHE_DIR / "last_sync.txt"

def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_cached_activities():
    """Load activities from cache."""
    ensure_cache_dir()
    if not ACTIVITIES_CACHE.exists():
        return []
    
    with open(ACTIVITIES_CACHE) as f:
        return json.load(f)

def save_activities_to_cache(activities):
    """Save activities to cache."""
    ensure_cache_dir()
    with open(ACTIVITIES_CACHE, 'w') as f:
        json.dump(activities, f, indent=2)
    
    # Update last sync time
    with open(LAST_SYNC_FILE, 'w') as f:
        f.write(datetime.now().isoformat())

def get_last_sync_time():
    """Get the last sync timestamp."""
    if not LAST_SYNC_FILE.exists():
        return None
    
    with open(LAST_SYNC_FILE) as f:
        return f.read().strip()

def update_cache_with_new_activities(new_activities):
    """Merge new activities into cache, avoiding duplicates."""
    cached = load_cached_activities()
    cached_ids = {a['id'] for a in cached}
    
    # Add only new activities
    for activity in new_activities:
        if activity['id'] not in cached_ids:
            cached.insert(0, activity)  # Add to front (most recent first)
    
    # Sort by start date (most recent first)
    cached.sort(key=lambda x: x['start_date'], reverse=True)
    
    save_activities_to_cache(cached)
    return cached

def get_activity_by_id(activity_id):
    """Get a specific activity from cache."""
    cached = load_cached_activities()
    for activity in cached:
        if activity['id'] == activity_id:
            return activity
    return None

if __name__ == '__main__':
    # Test cache functions
    print(f"Cache directory: {CACHE_DIR}")
    print(f"Last sync: {get_last_sync_time()}")
    print(f"Cached activities: {len(load_cached_activities())}")
