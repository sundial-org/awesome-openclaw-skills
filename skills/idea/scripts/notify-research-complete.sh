#!/bin/bash
# notify-research-complete.sh - Send research file and wake Clawdbot to notify
#
# Usage: notify-research-complete.sh <file_path> <title>

set -e

FILE_PATH="$1"
TITLE="$2"

if [ -z "$FILE_PATH" ] || [ -z "$TITLE" ]; then
    echo "Usage: notify-research-complete.sh <file_path> <title>"
    exit 1
fi

if [ ! -f "$FILE_PATH" ]; then
    echo "Error: File not found: $FILE_PATH"
    exit 1
fi

# Config
HOOKS_TOKEN="17f568bf286f486c1a73956fe9112125"
GATEWAY_URL="http://localhost:18789"

echo "Sending file to Saved Messages..."
telegram send-file "me" "$FILE_PATH" "$TITLE"

echo "Waking Clawdbot..."
# Use simple ASCII text to avoid JSON encoding issues
# Escape the title for JSON
SAFE_TITLE=$(echo "$TITLE" | sed 's/"/\\"/g' | tr -cd '[:print:]')
curl -s -X POST "${GATEWAY_URL}/hooks/wake" \
  -H "Content-Type: application/json" \
  -H "X-Clawdbot-Token: ${HOOKS_TOKEN}" \
  -d "{\"text\": \"RESEARCH_COMPLETE: ${SAFE_TITLE} - File sent to Saved Messages.\", \"mode\": \"now\"}"

echo ""
echo "Done!"
