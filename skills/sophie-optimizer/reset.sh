#!/bin/bash

# Sophie Optimizer - Reset Script
# Handles session cleanup and service restart

SESSION_DIR="$HOME/.openclaw/agents/main/sessions"
SERVICE_NAME="openclaw-gateway.service"

echo "[Sophie Optimizer] Initiating Hard Reset Protocol..."

# 1. Stop the service (optional, but safer to prevent write race conditions)
# systemctl --user stop $SERVICE_NAME

# 2. Clean Session Files
if [ -d "$SESSION_DIR" ]; then
    echo "[Sophie Optimizer] Cleaning session files in $SESSION_DIR..."
    # Remove .jsonl and .json files, keeping the directory structure
    rm -f "$SESSION_DIR"/*.jsonl
    rm -f "$SESSION_DIR"/*.json
    echo "[Sophie Optimizer] Session storage purged."
else
    echo "[Sophie Optimizer] Warning: Session directory not found at $SESSION_DIR"
fi

# 3. Restart Gateway
echo "[Sophie Optimizer] Restarting OpenClaw Gateway..."
systemctl --user restart $SERVICE_NAME

echo "[Sophie Optimizer] Reset complete. Sophie is rebooting..."
