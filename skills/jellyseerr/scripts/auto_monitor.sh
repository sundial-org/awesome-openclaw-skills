#!/bin/bash
# Automatically monitor Jellyseerr requests and notify when available

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.cache/jellyseerr/monitor.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] Checking Jellyseerr availability..." >> "$LOG_FILE"

# Make sure scripts are executable
chmod +x "$SCRIPT_DIR"/*.py

# Run monitoring
OUTPUT=$("$SCRIPT_DIR/monitor_availability.py" 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date)] Error: $OUTPUT" >> "$LOG_FILE"
    exit 1
fi

echo "$OUTPUT" >> "$LOG_FILE"

# Check for newly available items
AVAILABLE_COUNT=$(echo "$OUTPUT" | grep "^NOTIFY:" | wc -l)

if [ "$AVAILABLE_COUNT" -gt 0 ]; then
    echo "[$(date)] $AVAILABLE_COUNT item(s) became available!" >> "$LOG_FILE"
    
    # Extract notifications and send messages
    echo "$OUTPUT" | grep "^NOTIFY:" | while read -r line; do
        MESSAGE="${line#NOTIFY: }"
        echo "[$(date)] Sending notification: $MESSAGE" >> "$LOG_FILE"
        
        # TODO: Send via Clawdbot message tool
        # For now, just log it
    done
fi

echo "[$(date)] Monitoring check complete" >> "$LOG_FILE"
