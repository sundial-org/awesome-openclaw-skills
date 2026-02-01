#!/bin/bash
# anticipate.sh — Add or remove things to look forward to
# Usage: ./anticipate.sh --add "morning conversation"
#        ./anticipate.sh --remove "morning conversation"
#        ./anticipate.sh --list
#        ./anticipate.sh --clear

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/reward-state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No reward state found"
  exit 1
fi

ACTION=""
ITEM=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --add)
      ACTION="add"
      ITEM="$2"
      shift 2
      ;;
    --remove)
      ACTION="remove"
      ITEM="$2"
      shift 2
      ;;
    --list)
      ACTION="list"
      shift
      ;;
    --clear)
      ACTION="clear"
      shift
      ;;
    *)
      shift
      ;;
  esac
done

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

case $ACTION in
  add)
    if [ -z "$ITEM" ]; then
      echo "Usage: $0 --add \"thing to look forward to\""
      exit 1
    fi
    jq --arg item "$ITEM" --arg now "$NOW" \
       '.anticipating = (.anticipating + [$item] | unique) | .lastUpdated = $now' \
       "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "⭐ Now looking forward to: $ITEM"
    
    # Anticipation boosts drive slightly
    CURRENT_DRIVE=$(jq -r '.drive' "$STATE_FILE")
    NEW_DRIVE=$(awk -v d="$CURRENT_DRIVE" 'BEGIN {v=d+0.05; if(v>1)print 1; else printf "%.2f", v}')
    jq --argjson drive "$NEW_DRIVE" '.drive = $drive' "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "   Drive: $CURRENT_DRIVE → $NEW_DRIVE (+0.05)"
    ;;
    
  remove)
    if [ -z "$ITEM" ]; then
      echo "Usage: $0 --remove \"thing to remove\""
      exit 1
    fi
    jq --arg item "$ITEM" --arg now "$NOW" \
       '.anticipating = [.anticipating[] | select(. != $item)] | .lastUpdated = $now' \
       "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "⭐ Removed from anticipation: $ITEM"
    ;;
    
  list)
    echo "⭐ Looking forward to:"
    jq -r '.anticipating[]?' "$STATE_FILE" | while read -r item; do
      echo "  • $item"
    done
    COUNT=$(jq -r '.anticipating | length' "$STATE_FILE")
    if [ "$COUNT" = "0" ]; then
      echo "  (nothing specific)"
    fi
    ;;
    
  clear)
    jq --arg now "$NOW" '.anticipating = [] | .lastUpdated = $now' "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "⭐ Cleared all anticipations"
    ;;
    
  *)
    echo "Usage:"
    echo "  $0 --add \"thing to look forward to\""
    echo "  $0 --remove \"thing\""
    echo "  $0 --list"
    echo "  $0 --clear"
    ;;
esac
