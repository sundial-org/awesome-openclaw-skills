#!/bin/bash
# Install Jellyseerr webhook as a systemd service
# Run this with: sudo bash install_service.sh

set -e

SERVICE_NAME="jellyseerr-webhook"
SCRIPT_DIR="/home/clawd/clawd/skills/jellyseerr/scripts"
PORT="8384"
USER="clawd"

echo "Creating systemd service file..."

cat > /etc/systemd/system/${SERVICE_NAME}.service << EOF
[Unit]
Description=Jellyseerr Webhook Receiver
After=network.target

[Service]
Type=simple
User=${USER}
WorkingDirectory=${SCRIPT_DIR}
ExecStart=/usr/bin/python3 ${SCRIPT_DIR}/webhook_server.py ${PORT}
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling service to start on boot..."
systemctl enable ${SERVICE_NAME}

echo "Starting service..."
systemctl start ${SERVICE_NAME}

echo ""
echo "✓ Service installed and started!"
echo ""
echo "Useful commands:"
echo "  Status:  sudo systemctl status ${SERVICE_NAME}"
echo "  Logs:    sudo journalctl -u ${SERVICE_NAME} -f"
echo "  Restart: sudo systemctl restart ${SERVICE_NAME}"
echo "  Stop:    sudo systemctl stop ${SERVICE_NAME}"
echo ""
echo "Webhook URL: http://$(hostname -I | awk '{print $1}'):${PORT}/"
