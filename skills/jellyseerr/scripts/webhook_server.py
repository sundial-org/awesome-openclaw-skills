#!/usr/bin/env python3
"""
Simple webhook receiver for Jellyseerr notifications.
Receives POST requests and queues notifications for pickup.
"""

import json
import logging
import os
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

# Paths
CONFIG_FILE = Path.home() / '.config' / 'jellyseerr' / 'config.json'
CACHE_DIR = Path.home() / '.cache' / 'jellyseerr'
NOTIFY_FILE = CACHE_DIR / 'pending_notifications.json'

def get_chat_id():
    """Get Telegram chat ID from config."""
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                return config.get('telegram_chat_id') or os.environ.get('TELEGRAM_CHAT_ID')
        except Exception as e:
            logger.error(f"Failed to read config: {e}")
    
    return os.environ.get('TELEGRAM_CHAT_ID')

def queue_notification(media_type, title, message):
    """Queue a notification for delivery."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    # Load existing notifications
    notifications = []
    if NOTIFY_FILE.exists():
        try:
            with open(NOTIFY_FILE) as f:
                notifications = json.load(f)
        except Exception as e:
            logger.error(f"Failed to read notifications: {e}")
    
    # Add new notification
    notifications.append({
        'title': title,
        'media_type': media_type,
        'message': message,
        'channel': 'telegram',
        'chat_id': get_chat_id(),
        'timestamp': datetime.utcnow().isoformat()
    })
    
    # Save
    with open(NOTIFY_FILE, 'w') as f:
        json.dump(notifications, f, indent=2)
    
    logger.info(f"✓ Queued notification: {title}")
    return True

class WebhookHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle POST request from Jellyseerr."""
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)
        
        try:
            data = json.loads(body)
            logger.info(f"Received webhook: {json.dumps(data, indent=2)}")
            
            notification_type = data.get('notification_type', '')
            
            # Only handle MEDIA_AVAILABLE notifications
            if notification_type == 'MEDIA_AVAILABLE':
                media_type = data.get('media_type', 'unknown')
                subject = data.get('subject', 'Unknown Media')
                
                message = f"🎬 **{subject} is now available!**\n\nYour requested {media_type} is ready to watch on Plex/Jellyfin. Enjoy! 🥚"
                
                success = queue_notification(media_type, subject, message)
                
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'queued': success}).encode())
            else:
                logger.info(f"Ignoring notification type: {notification_type}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok', 'ignored': True}).encode())
        
        except Exception as e:
            logger.error(f"Error processing webhook: {e}", exc_info=True)
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'error': str(e)}).encode())
    
    def log_message(self, format, *args):
        """Override to use our logger."""
        logger.info(f"{self.address_string()} - {format % args}")

def run_server(port=8384):
    """Run the webhook server."""
    server = HTTPServer(('0.0.0.0', port), WebhookHandler)
    logger.info(f"Webhook server listening on port {port}")
    logger.info(f"Configure Jellyseerr to send webhooks to: http://YOUR_IP:{port}/")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down webhook server")
        server.shutdown()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8384
    run_server(port)
