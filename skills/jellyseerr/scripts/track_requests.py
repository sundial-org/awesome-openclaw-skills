#!/usr/bin/env python3
"""
Track and manage pending Jellyseerr requests.
"""
import json
from pathlib import Path
from datetime import datetime

CACHE_DIR = Path.home() / ".cache" / "jellyseerr"
PENDING_FILE = CACHE_DIR / "pending_requests.json"

def ensure_cache_dir():
    """Create cache directory if it doesn't exist."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

def load_pending():
    """Load pending requests from cache."""
    ensure_cache_dir()
    if not PENDING_FILE.exists():
        return []
    
    with open(PENDING_FILE) as f:
        return json.load(f)

def save_pending(pending):
    """Save pending requests to cache."""
    ensure_cache_dir()
    with open(PENDING_FILE, 'w') as f:
        json.dump(pending, f, indent=2)

def add_request(media_id, media_type, title, requested_at=None, channel=None, chat_id=None):
    """Add a new pending request."""
    import os
    
    pending = load_pending()
    
    # Check if already tracking
    for item in pending:
        if item['media_id'] == media_id and item['media_type'] == media_type:
            return  # Already tracking
    
    # Try to get channel info from environment if not provided
    if not channel:
        channel = os.environ.get('CLAWDBOT_CHANNEL', 'telegram')
    if not chat_id:
        chat_id = os.environ.get('CLAWDBOT_CHAT_ID', os.environ.get('TELEGRAM_CHAT_ID'))
    
    new_request = {
        'media_id': media_id,
        'media_type': media_type,
        'title': title,
        'requested_at': requested_at or datetime.now().isoformat(),
        'status': 'PENDING',
        'channel': channel,
        'chat_id': chat_id
    }
    
    pending.append(new_request)
    save_pending(pending)
    print(f"Now tracking: {title}")

def update_status(media_id, media_type, new_status):
    """Update status of a tracked request."""
    pending = load_pending()
    
    for item in pending:
        if item['media_id'] == media_id and item['media_type'] == media_type:
            old_status = item['status']
            item['status'] = new_status
            item['last_checked'] = datetime.now().isoformat()
            save_pending(pending)
            return old_status, new_status
    
    return None, None

def remove_request(media_id, media_type):
    """Remove a completed/available request from tracking."""
    pending = load_pending()
    pending = [p for p in pending if not (p['media_id'] == media_id and p['media_type'] == media_type)]
    save_pending(pending)

def get_pending():
    """Get all pending requests."""
    return load_pending()

if __name__ == '__main__':
    # Test functions
    pending = get_pending()
    print(f"Currently tracking {len(pending)} request(s):")
    for item in pending:
        print(f"  - {item['title']} ({item['media_type']}) - {item['status']}")
