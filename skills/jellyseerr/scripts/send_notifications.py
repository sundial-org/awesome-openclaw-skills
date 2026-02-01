#!/usr/bin/env python3
"""
Process pending notifications and send them via configured method.
This script is meant to be called from Clawdbot context with message tool access.
"""
import json
from pathlib import Path
import sys

NOTIFY_FILE = Path.home() / ".cache" / "jellyseerr" / "pending_notifications.json"

def get_pending_notifications():
    """Get all pending notifications."""
    if not NOTIFY_FILE.exists():
        return []
    
    with open(NOTIFY_FILE) as f:
        return json.load(f)

def clear_notifications():
    """Clear all pending notifications."""
    if NOTIFY_FILE.exists():
        NOTIFY_FILE.unlink()

def main():
    notifications = get_pending_notifications()
    
    if not notifications:
        print("No pending notifications")
        return
    
    print(f"Found {len(notifications)} pending notification(s)")
    
    # Output notifications in a format that can be picked up
    for notif in notifications:
        print(f"SEND_MESSAGE:{notif['message']}")
    
    # Clear after outputting
    clear_notifications()

if __name__ == '__main__':
    main()
