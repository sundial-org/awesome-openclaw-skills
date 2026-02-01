#!/bin/bash
# Automatically check for and analyze new Strava rides

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$HOME/.cache/strava/monitor.log"

mkdir -p "$(dirname "$LOG_FILE")"

echo "[$(date)] Checking for new rides..." >> "$LOG_FILE"

# Make sure scripts are executable
chmod +x "$SCRIPT_DIR"/*.py

# Check for new rides
NEW_RIDES=$("$SCRIPT_DIR/monitor_new_rides.py" 2>&1)
EXIT_CODE=$?

if [ $EXIT_CODE -ne 0 ]; then
    echo "[$(date)] Error checking for rides: $NEW_RIDES" >> "$LOG_FILE"
    exit 1
fi

echo "$NEW_RIDES" >> "$LOG_FILE"

# Extract ride IDs
RIDE_IDS=$(echo "$NEW_RIDES" | grep "^NEW_RIDE:" | cut -d: -f2)

if [ -z "$RIDE_IDS" ]; then
    echo "[$(date)] No new rides found" >> "$LOG_FILE"
    exit 0
fi

# Analyze each new ride
for RIDE_ID in $RIDE_IDS; do
    echo "[$(date)] Analyzing ride $RIDE_ID..." >> "$LOG_FILE"
    
    # Call analysis script
    # STRAVA_TELEGRAM_CHAT_ID should be set in environment or config
    "$SCRIPT_DIR/analyze_and_notify.py" "$RIDE_ID" >> "$LOG_FILE" 2>&1
    
    if [ $? -eq 0 ]; then
        echo "[$(date)] Successfully analyzed and notified: $RIDE_ID" >> "$LOG_FILE"
    else
        echo "[$(date)] Error analyzing ride $RIDE_ID" >> "$LOG_FILE"
    fi
done

echo "[$(date)] Monitoring check complete" >> "$LOG_FILE"
