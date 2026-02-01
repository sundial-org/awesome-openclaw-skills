#!/bin/bash
# wait_for_session.sh <session_id> [poll_interval_seconds]

SESSION_ID=$1
INTERVAL=${2:-30}

if [ -z "$SESSION_ID" ]; then
    echo "Usage: $0 <session_id> [poll_interval]"
    exit 1
fi

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PARSE_SCRIPT="$SCRIPT_DIR/parse_sessions.py"

echo "Waiting for session $SESSION_ID to complete..."

while true; do
    # Get session list and parse it using parse_sessions.py
    SESSION_JSON=$(jules remote list --session | python3 "$PARSE_SCRIPT" 2>/dev/null)
    
    if [ -z "$SESSION_JSON" ]; then
        echo "Error: Failed to retrieve or parse session list"
        exit 1
    fi
    
    # Extract status for the specific session ID using jq or python
    STATUS=$(echo "$SESSION_JSON" | python3 -c "
import sys, json
try:
    sessions = json.load(sys.stdin)
    for s in sessions:
        if s.get('id') == '$SESSION_ID':
            print(s.get('status', ''))
            break
except:
    pass
")
    
    if [ -z "$STATUS" ]; then
        echo "Session $SESSION_ID not found."
        exit 1
    fi

    echo "Current Status: $STATUS"

    case "$STATUS" in
        "Completed")
            echo "Session $SESSION_ID finished successfully!"
            exit 0
            ;;
        "Failed"|"Error"|"Cancelled")
            echo "Session $SESSION_ID ended with status: $STATUS"
            exit 1
            ;;
        *)
            # Still in progress (e.g., "Awaiting User Feedback", "In Progress", etc.)
            sleep "$INTERVAL"
            ;;
    esac
done
