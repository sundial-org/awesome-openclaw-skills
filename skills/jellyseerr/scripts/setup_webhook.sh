#!/bin/bash
# Setup webhook server as a systemd service

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SERVICE_NAME="jellyseerr-webhook"
PORT="${1:-8384}"

# Create systemd service file
sudo tee /etc/systemd/system/${SERVICE_NAME}.service > /dev/null << EOF
[Unit]
Description=Jellyseerr Webhook Receiver
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/webhook_server.py $PORT
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable ${SERVICE_NAME}
sudo systemctl start ${SERVICE_NAME}

echo "✓ Webhook server installed and started on port $PORT"
echo ""
echo "Next steps:"
echo "1. Get your server's IP address: hostname -I"
echo "2. In Jellyseerr, go to Settings → Notifications → Webhook"
echo "3. Enable the Webhook agent"
echo "4. Set Webhook URL to: http://YOUR_IP:$PORT/"
echo "5. In JSON Payload, paste the following (base64 encoded):"
echo ""
echo 'eyJub3RpZmljYXRpb25fdHlwZSI6Int7bm90aWZpY2F0aW9uX3R5cGV9fSIsInN1YmplY3QiOiJ7e3N1YmplY3R9fSIsIm1lc3NhZ2UiOiJ7e21lc3NhZ2V9fSIsIm1lZGlhX3R5cGUiOiJ7e21lZGlhX3R5cGV9fSIsIm1lZGlhX3RtZGJpZCI6Int7bWVkaWFfdG1kYmlkfX0ifQ=='
echo ""
echo "6. Enable notification type: Media Available"
echo "7. Test the webhook and Save Changes"
echo ""
echo "Check status: sudo systemctl status ${SERVICE_NAME}"
echo "View logs: sudo journalctl -u ${SERVICE_NAME} -f"
