#!/bin/bash
# Force Mail.app to check for new mail across all accounts (or a specific account)
# Usage: mail-refresh.sh [account] [wait_seconds]
#
# Arguments:
#   account      - Optional: specific account name (from mail-accounts.sh)
#   wait_seconds - Optional: max seconds to wait for sync (default: 10, 0 = no wait)
#
# Examples:
#   mail-refresh.sh                    # Refresh all accounts, wait up to 10s
#   mail-refresh.sh Google             # Refresh only Google account
#   mail-refresh.sh "" 5               # Refresh all, wait up to 5 seconds
#   mail-refresh.sh Google 0           # Refresh Google, return immediately
#
# The script will return early if sync appears complete (database stops updating).

set -e

ACCOUNT="${1:-}"
MAX_WAIT="${2:-10}"

# Ensure wait is a number
if ! [[ "$MAX_WAIT" =~ ^[0-9]+$ ]]; then
    echo "ERROR: wait_seconds must be a non-negative integer" >&2
    exit 1
fi

# Check if Mail.app is running
if ! pgrep -q "Mail"; then
    echo "ERROR: Mail.app is not running. Please open Mail.app first." >&2
    exit 1
fi

# Find the database
find_db() {
    for v in 11 10 9; do
        local db="$HOME/Library/Mail/V$v/MailData/Envelope Index"
        if [[ -f "$db" ]]; then
            echo "$db"
            return 0
        fi
    done
    return 1
}

DB_PATH=$(find_db)

# Get initial message count
get_msg_count() {
    if [[ -n "$DB_PATH" ]]; then
        sqlite3 "$DB_PATH" "SELECT COUNT(*) FROM messages;" 2>/dev/null || echo "0"
    else
        echo "0"
    fi
}

INITIAL_COUNT=$(get_msg_count)

if [ -n "$ACCOUNT" ]; then
    # Refresh specific account
    ACCOUNT_EXISTS=$(osascript -e "tell application \"Mail\" to exists account \"$ACCOUNT\"" 2>/dev/null || echo "false")
    
    if [ "$ACCOUNT_EXISTS" != "true" ]; then
        echo "ERROR: Account '$ACCOUNT' not found. Run mail-accounts.sh to see available accounts." >&2
        exit 1
    fi
    
    osascript <<EOF
tell application "Mail"
    check for new mail in account "$ACCOUNT"
end tell
EOF
    
    echo "Refresh triggered for account: $ACCOUNT"
else
    # Refresh all accounts
    osascript <<EOF
tell application "Mail"
    check for new mail
end tell
EOF
    
    echo "Refresh triggered for all accounts"
fi

# Wait for sync with smart detection
if [ "$MAX_WAIT" -gt 0 ]; then
    echo "Waiting for sync (max ${MAX_WAIT}s)..."
    
    STABLE_COUNT=0
    LAST_COUNT=$INITIAL_COUNT
    
    for ((i=1; i<=MAX_WAIT; i++)); do
        sleep 1
        CURRENT_COUNT=$(get_msg_count)
        
        if [ "$CURRENT_COUNT" != "$LAST_COUNT" ]; then
            # Database changed, reset stability counter
            STABLE_COUNT=0
            LAST_COUNT=$CURRENT_COUNT
        else
            # No change, increment stability counter
            STABLE_COUNT=$((STABLE_COUNT + 1))
        fi
        
        # Consider stable after 2 seconds of no changes
        if [ "$STABLE_COUNT" -ge 2 ]; then
            NEW_MSGS=$((CURRENT_COUNT - INITIAL_COUNT))
            if [ "$NEW_MSGS" -gt 0 ]; then
                echo "Sync complete in ${i}s (+${NEW_MSGS} messages)"
            else
                echo "Sync complete in ${i}s (no new messages)"
            fi
            exit 0
        fi
    done
    
    # Timeout reached
    FINAL_COUNT=$(get_msg_count)
    NEW_MSGS=$((FINAL_COUNT - INITIAL_COUNT))
    if [ "$NEW_MSGS" -gt 0 ]; then
        echo "Timeout reached (+${NEW_MSGS} messages, sync may still be in progress)"
    else
        echo "Timeout reached (no new messages detected)"
    fi
fi
