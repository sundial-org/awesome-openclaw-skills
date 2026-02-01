#!/bin/bash
# log-reward.sh — Log a reward event and boost drive
# Usage: ./log-reward.sh --type <type> --source "what happened" [--intensity 0-1]
#
# Types: accomplishment, social, curiosity, connection, creative, competence

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/reward-state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No reward state found at $STATE_FILE"
  exit 1
fi

# Parse arguments
TYPE=""
SOURCE=""
INTENSITY="0.5"

while [[ $# -gt 0 ]]; do
  case $1 in
    --type)
      TYPE="$2"
      shift 2
      ;;
    --source)
      SOURCE="$2"
      shift 2
      ;;
    --intensity)
      INTENSITY="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

if [ -z "$TYPE" ] || [ -z "$SOURCE" ]; then
  echo "Usage: $0 --type <type> --source \"what happened\" [--intensity 0-1]"
  echo ""
  echo "Types: accomplishment, social, curiosity, connection, creative, competence"
  exit 1
fi

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Calculate drive boost based on intensity
# Higher intensity = bigger boost
# Boost formula: intensity * 0.2 (max +0.2 per reward)
BOOST=$(awk -v i="$INTENSITY" 'BEGIN {printf "%.2f", i * 0.2}')

# Get current drive
CURRENT_DRIVE=$(jq -r '.drive' "$STATE_FILE")

# Calculate new drive (capped at 1.0)
NEW_DRIVE=$(awk -v d="$CURRENT_DRIVE" -v b="$BOOST" 'BEGIN {v=d+b; if(v>1)print 1; else printf "%.2f", v}')

# Create reward entry
REWARD_ENTRY=$(jq -n \
  --arg type "$TYPE" \
  --arg source "$SOURCE" \
  --arg intensity "$INTENSITY" \
  --arg boost "$BOOST" \
  --arg ts "$NOW" \
  '{type: $type, source: $source, intensity: ($intensity|tonumber), boost: ($boost|tonumber), timestamp: $ts}')

# Update state file
jq --argjson reward "$REWARD_ENTRY" \
   --argjson newDrive "$NEW_DRIVE" \
   --arg now "$NOW" \
   --arg type "$TYPE" \
   '
   .drive = $newDrive |
   .lastUpdated = $now |
   .recentRewards = ([$reward] + .recentRewards | .[0:10]) |
   .rewardHistory.totalRewards += 1 |
   .rewardHistory.byType[$type] += 1
   ' "$STATE_FILE" > "$STATE_FILE.tmp"
mv "$STATE_FILE.tmp" "$STATE_FILE"

echo "⭐ Reward logged!"
echo "   Type: $TYPE"
echo "   Source: $SOURCE"
echo "   Intensity: $INTENSITY"
echo "   Drive: $CURRENT_DRIVE → $NEW_DRIVE (+$BOOST)"
