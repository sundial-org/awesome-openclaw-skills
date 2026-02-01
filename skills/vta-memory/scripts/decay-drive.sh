#!/bin/bash
# decay-drive.sh — Drive decays without rewards over time
# Usage: ./decay-drive.sh [--dry-run]
#
# Without rewards, motivation fades. This mimics dopamine baseline return.

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/reward-state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No reward state found"
  exit 1
fi

DRY_RUN=false
[ "$1" = "--dry-run" ] && DRY_RUN=true

# Decay rate: 15% toward baseline per run
DECAY_RATE=0.15

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

CURRENT_DRIVE=$(jq -r '.drive' "$STATE_FILE")
BASELINE=$(jq -r '.baseline.drive' "$STATE_FILE")

# Calculate decay
DIFF=$(awk -v b="$BASELINE" -v c="$CURRENT_DRIVE" 'BEGIN {print b - c}')
CHANGE=$(awk -v d="$DIFF" -v r="$DECAY_RATE" 'BEGIN {printf "%.3f", d * r}')
NEW_DRIVE=$(awk -v c="$CURRENT_DRIVE" -v ch="$CHANGE" 'BEGIN {printf "%.2f", c + ch}')

echo "⭐ Drive Decay"
echo "─────────────────────"
echo ""
echo "Drive: $CURRENT_DRIVE → $NEW_DRIVE (baseline: $BASELINE)"

if [ "$DRY_RUN" = true ]; then
  echo ""
  echo "(dry run - no changes made)"
else
  jq --argjson drive "$NEW_DRIVE" --arg now "$NOW" \
     '.drive = $drive | .lastUpdated = $now' "$STATE_FILE" > "$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"
  
  echo ""
  echo "✅ Drive decayed"
  
  # Sync to VTA_STATE.md
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  if [ -f "$SCRIPT_DIR/sync-motivation.sh" ]; then
    "$SCRIPT_DIR/sync-motivation.sh"
  fi
fi
