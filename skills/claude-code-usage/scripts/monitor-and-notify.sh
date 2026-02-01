#!/bin/bash
# Monitor Claude Code usage and send Telegram notifications on resets

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUTPUT=$("$SCRIPT_DIR/monitor-usage.sh" 2>&1)

# Check if a reset was detected (output contains "Reset notification sent")
if echo "$OUTPUT" | grep -q "Reset notification sent"; then
  # Extract just the notification message (before "✅ Reset notification sent")
  MESSAGE=$(echo "$OUTPUT" | sed '/✅ Reset notification sent/q' | sed '$ d')
  
  # Send via Telegram using clawdbot
  if command -v clawdbot >/dev/null 2>&1; then
    # Use printf to handle newlines properly
    printf '%s' "$MESSAGE" | clawdbot message send --telegram --target 5259918241
  fi
fi
