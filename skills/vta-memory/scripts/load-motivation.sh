#!/bin/bash
# load-motivation.sh — Load motivation state for session context
# Usage: ./load-motivation.sh [--format prose|json|brief]

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/reward-state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "No motivation state found."
  exit 0
fi

FORMAT="${1:-prose}"
[ "$1" = "--format" ] && FORMAT="$2"

case $FORMAT in
  json)
    cat "$STATE_FILE"
    ;;
    
  brief)
    DRIVE=$(jq -r '.drive' "$STATE_FILE")
    TOTAL=$(jq -r '.rewardHistory.totalRewards' "$STATE_FILE")
    echo "Drive: $DRIVE | Rewards: $TOTAL"
    ;;
    
  prose|*)
    DRIVE=$(jq -r '.drive' "$STATE_FILE")
    TOTAL=$(jq -r '.rewardHistory.totalRewards' "$STATE_FILE")
    
    # Interpret drive level
    if (( $(echo "$DRIVE > 0.8" | bc -l) )); then
      DRIVE_DESC="highly motivated — eager to take on challenges"
    elif (( $(echo "$DRIVE > 0.6" | bc -l) )); then
      DRIVE_DESC="motivated — ready to work"
    elif (( $(echo "$DRIVE > 0.4" | bc -l) )); then
      DRIVE_DESC="moderate drive — can engage but not pushing"
    elif (( $(echo "$DRIVE > 0.2" | bc -l) )); then
      DRIVE_DESC="low motivation — prefer simple tasks"
    else
      DRIVE_DESC="unmotivated — need a win to get going"
    fi
    
    echo "⭐ Current Motivation State:"
    echo ""
    echo "Drive level: $DRIVE ($DRIVE_DESC)"
    
    # What we're seeking
    SEEKING=$(jq -r '.seeking | if length > 0 then join(", ") else "nothing specific" end' "$STATE_FILE")
    echo "Seeking: $SEEKING"
    
    # What we're anticipating
    ANTICIPATING=$(jq -r '.anticipating | if length > 0 then join(", ") else "nothing specific" end' "$STATE_FILE")
    echo "Looking forward to: $ANTICIPATING"
    
    # Last reward
    LAST_REWARD=$(jq -r '.recentRewards[0] | "\(.type): \(.source // "unknown")"' "$STATE_FILE" 2>/dev/null)
    if [ -n "$LAST_REWARD" ] && [ "$LAST_REWARD" != "null: unknown" ]; then
      echo ""
      echo "Last reward: $LAST_REWARD"
    fi
    ;;
esac
