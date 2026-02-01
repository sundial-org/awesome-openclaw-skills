#!/usr/bin/env python3
"""
Monitor pending Jellyseerr requests and notify when available.
"""
import json
import sys
from pathlib import Path
import requests
from track_requests import get_pending, update_status, remove_request

CONFIG_PATH = Path.home() / ".config" / "jellyseerr" / "config.json"

def load_config():
    if not CONFIG_PATH.exists():
        print("Error: Configuration not found.", file=sys.stderr)
        sys.exit(1)
    
    with open(CONFIG_PATH) as f:
        return json.load(f)

def check_media_status(config, media_id, media_type):
    """Check the status of a media item."""
    url = f"{config['server_url']}/api/v1/{media_type}/{media_id}"
    headers = {'X-Api-Key': config['api_key']}
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        # Get status from mediaInfo
        media_info = data.get('mediaInfo')
        if media_info:
            status = media_info.get('status', 0)
            status_text = {
                0: "NOT_REQUESTED",
                1: "PENDING",
                2: "PROCESSING",
                3: "PARTIALLY_AVAILABLE",
                4: "AVAILABLE",
                5: "AVAILABLE"
            }.get(status, "UNKNOWN")
            return status_text, status >= 4
        
        return "UNKNOWN", False
    
    except Exception as e:
        print(f"Error checking {media_type} {media_id}: {e}", file=sys.stderr)
        return "ERROR", False

def send_notification(title, media_type, channel='telegram', chat_id=None):
    """Send notification that content is available."""
    import json
    from pathlib import Path
    
    media_icon = "🎬" if media_type == "movie" else "📺"
    message = f"{media_icon} **{title} is now available!**\n\nYour requested {'movie' if media_type == 'movie' else 'TV show'} is ready to watch on Plex/Jellyfin. Enjoy! 🥚"
    
    # Print for logging
    print(f"NOTIFY: {message}")
    
    # Write to notification queue file for Clawdbot to pick up
    notify_file = Path.home() / ".cache" / "jellyseerr" / "pending_notifications.json"
    notify_file.parent.mkdir(parents=True, exist_ok=True)
    
    notifications = []
    if notify_file.exists():
        with open(notify_file) as f:
            notifications = json.load(f)
    
    notifications.append({
        'title': title,
        'media_type': media_type,
        'message': message,
        'channel': channel,
        'chat_id': chat_id,
        'timestamp': __import__('datetime').datetime.now().isoformat()
    })
    
    with open(notify_file, 'w') as f:
        json.dump(notifications, f, indent=2)
    
    print(f"Notification queued to: {notify_file}")

def should_check_now(requested_at):
    """Determine if we should check this item based on age."""
    from datetime import datetime, timedelta
    
    requested_time = datetime.fromisoformat(requested_at)
    age = datetime.now() - requested_time
    
    # Within first hour: always check (called every minute)
    if age < timedelta(hours=1):
        return True
    
    # After 1 hour: only check on the hour
    # This function is called every minute, so check if current minute is 0
    return datetime.now().minute == 0

def main():
    config = load_config()
    pending = get_pending()
    
    if not pending:
        print("No pending requests to check")
        return
    
    # Filter to only items that should be checked now
    items_to_check = []
    for item in pending:
        if item.get('status') == 'AVAILABLE':
            continue  # Skip already available items
        
        if should_check_now(item['requested_at']):
            items_to_check.append(item)
    
    if not items_to_check:
        print("No items need checking at this time")
        return
    
    print(f"Checking {len(items_to_check)} pending request(s)...")
    
    newly_available = []
    
    for item in items_to_check:
        media_id = item['media_id']
        media_type = item['media_type']
        title = item['title']
        current_status = item.get('status', 'PENDING')
        
        print(f"  Checking: {title} ({media_type})")
        
        new_status, is_available = check_media_status(config, media_id, media_type)
        
        if new_status != current_status:
            print(f"    Status changed: {current_status} -> {new_status}")
            update_status(media_id, media_type, new_status)
        
        if is_available and current_status != "AVAILABLE":
            print(f"    ✓ Now available!")
            newly_available.append(item)
    
    # Send notifications for newly available content
    for item in newly_available:
        send_notification(
            item['title'], 
            item['media_type'],
            item.get('channel', 'telegram'),
            item.get('chat_id')
        )
        # Keep in tracking but mark as notified
        update_status(item['media_id'], item['media_type'], "AVAILABLE")
    
    if newly_available:
        print(f"\n{len(newly_available)} item(s) became available!")
    else:
        print("\nNo new content available yet")

if __name__ == '__main__':
    main()
