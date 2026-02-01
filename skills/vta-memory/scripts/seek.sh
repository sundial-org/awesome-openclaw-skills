#!/bin/bash
# seek.sh — Add or remove things we're actively seeking/wanting
# Usage: ./seek.sh --add "creative work"
#        ./seek.sh --remove "creative work"
#        ./seek.sh --list

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
      echo "Usage: $0 --add \"thing to seek\""
      exit 1
    fi
    jq --arg item "$ITEM" --arg now "$NOW" \
       '.seeking = (.seeking + [$item] | unique) | .lastUpdated = $now' \
       "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "⭐ Now seeking: $ITEM"
    ;;
    
  remove)
    if [ -z "$ITEM" ]; then
      echo "Usage: $0 --remove \"thing\""
      exit 1
    fi
    jq --arg item "$ITEM" --arg now "$NOW" \
       '.seeking = [.seeking[] | select(. != $item)] | .lastUpdated = $now' \
       "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "⭐ No longer seeking: $ITEM"
    ;;
    
  list)
    echo "⭐ Currently seeking:"
    jq -r '.seeking[]?' "$STATE_FILE" | while read -r item; do
      echo "  • $item"
    done
    COUNT=$(jq -r '.seeking | length' "$STATE_FILE")
    if [ "$COUNT" = "0" ]; then
      echo "  (nothing specific)"
    fi
    ;;
    
  clear)
    jq --arg now "$NOW" '.seeking = [] | .lastUpdated = $now' "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "⭐ Cleared all seeking"
    ;;
    
  *)
    echo "Usage:"
    echo "  $0 --add \"thing to seek\""
    echo "  $0 --remove \"thing\""
    echo "  $0 --list"
    echo "  $0 --clear"
    ;;
esac
