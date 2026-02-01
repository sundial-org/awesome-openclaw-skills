#!/bin/bash
# Claude Code Session Reminder
# Notifies when session quota refreshes, then schedules next reminder

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Get current usage (force fresh to get accurate reset time)
USAGE=$("$SCRIPT_DIR/claude-usage.sh" --json --fresh 2>/dev/null)

if [ -z "$USAGE" ]; then
  echo "❌ Failed to fetch Claude Code usage" >&2
  exit 1
fi

# Extract session info
SESSION_UTIL=$(echo "$USAGE" | grep -A3 '"session"' | grep '"utilization"' | grep -o '[0-9]*')
SESSION_RESETS=$(echo "$USAGE" | grep -A3 '"session"' | grep '"resets_in"' | sed 's/.*"resets_in": "//;s/".*//')
SESSION_RESETS_AT=$(echo "$USAGE" | grep -A3 '"session"' | grep '"resets_at"' | sed 's/.*"resets_at": "//;s/".*//')

SESSION_UTIL=${SESSION_UTIL:-0}

# Parse the reset timestamp to get cron schedule
if [ -z "$SESSION_RESETS_AT" ] || [ "$SESSION_RESETS_AT" = "null" ]; then
  echo "❌ Could not determine session reset time" >&2
  exit 1
fi

# Convert ISO timestamp to cron format
# Example: 2026-01-22T01:22:00.000Z → minute=22, hour=1, day=22, month=1
if [[ "$OSTYPE" == "darwin"* ]]; then
  # macOS date parsing
  RESET_TS=$(date -j -f "%Y-%m-%dT%H:%M:%S" "${SESSION_RESETS_AT%.*}" "+%s" 2>/dev/null)
else
  # Linux date parsing
  RESET_TS=$(date -d "${SESSION_RESETS_AT}" "+%s" 2>/dev/null)
fi

if [ -z "$RESET_TS" ] || [ "$RESET_TS" -eq 0 ]; then
  echo "❌ Failed to parse reset timestamp" >&2
  exit 1
fi

# Extract cron components
if [[ "$OSTYPE" == "darwin"* ]]; then
  CRON_MINUTE=$(date -r "$RESET_TS" "+%-M")
  CRON_HOUR=$(date -r "$RESET_TS" "+%-H")
  CRON_DAY=$(date -r "$RESET_TS" "+%-d")
  CRON_MONTH=$(date -r "$RESET_TS" "+%-m")
else
  CRON_MINUTE=$(date -d "@$RESET_TS" "+%-M")
  CRON_HOUR=$(date -d "@$RESET_TS" "+%-H")
  CRON_DAY=$(date -d "@$RESET_TS" "+%-d")
  CRON_MONTH=$(date -d "@$RESET_TS" "+%-m")
fi

# Prepare notification message
MESSAGE="🔄 *Claude Code Session Status*

⏱️  Current usage: *${SESSION_UTIL}%*
⏰ Next refresh: ${SESSION_RESETS}

Your 5-hour quota will reset soon! 🦞"

# Send notification
echo -e "$MESSAGE"

# Schedule next reminder using clawdbot cron
if command -v clawdbot >/dev/null 2>&1; then
  # Try to remove existing session reminder (ignore errors if none exists)
  EXISTING=$(clawdbot cron list 2>/dev/null | grep "Claude Code Session Reminder" | head -1 || echo "")
  if [ -n "$EXISTING" ]; then
    # Extract ID from the output (format: "id: <uuid>")
    EXISTING_ID=$(echo "$EXISTING" | grep -o 'id: [a-f0-9-]*' | sed 's/id: //')
    if [ -n "$EXISTING_ID" ]; then
      clawdbot cron remove --id "$EXISTING_ID" >/dev/null 2>&1 || true
    fi
  fi
  
  # Add new one-time cron for next session reset
  # Note: Using session target to send results back to this session
  NEXT_TIME=$(date -r "$RESET_TS" "+%Y-%m-%d %H:%M")
  clawdbot cron add \
    --cron "$CRON_MINUTE $CRON_HOUR $CRON_DAY $CRON_MONTH *" \
    --message "Run Claude Code session reminder: $SCRIPT_DIR/session-reminder.sh" \
    --name "Claude Code Session Reminder" \
    --description "Next refresh at $NEXT_TIME" \
    --delete-after-run \
    --session isolated \
    --deliver \
    --channel telegram \
    >/dev/null 2>&1
  
  echo ""
  echo "✅ Next reminder scheduled for: $(date -r "$RESET_TS" "+%b %d at %I:%M %p")"
else
  echo "⚠️  clawdbot not found - cannot schedule next reminder" >&2
fi
