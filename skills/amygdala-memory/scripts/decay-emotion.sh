#!/bin/bash
# decay-emotion.sh — Return emotional state toward baseline over time
# Usage: ./decay-emotion.sh [--dry-run]
# Run via cron (e.g., every 6 hours) to gradually normalize emotions
# Now supports per-dimension decay rates!

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/emotional-state.json"

if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No emotional state found"
  exit 1
fi

DRY_RUN=false
[ "$1" = "--dry-run" ] && DRY_RUN=true

# Default decay rate if not specified per-dimension
DEFAULT_DECAY_RATE=0.1

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "🎭 Emotional Decay"
echo "─────────────────────"
echo ""

# Get all dimensions
DIMENSIONS=$(jq -r '.dimensions | keys[]' "$STATE_FILE")

for DIM in $DIMENSIONS; do
  CURRENT=$(jq -r ".dimensions.$DIM" "$STATE_FILE")
  BASELINE=$(jq -r ".baseline.$DIM // $CURRENT" "$STATE_FILE")
  
  # Get per-dimension decay rate if available
  DECAY_RATE=$(jq -r ".decayRates.$DIM // $DEFAULT_DECAY_RATE" "$STATE_FILE")
  
  # Calculate decay: move DECAY_RATE toward baseline
  DIFF=$(awk -v b="$BASELINE" -v c="$CURRENT" 'BEGIN {print b - c}')
  CHANGE=$(awk -v d="$DIFF" -v r="$DECAY_RATE" 'BEGIN {printf "%.3f", d * r}')
  NEW=$(awk -v c="$CURRENT" -v ch="$CHANGE" 'BEGIN {printf "%.2f", c + ch}')
  
  if [ "$DRY_RUN" = true ]; then
    echo "$DIM: $CURRENT → $NEW (baseline: $BASELINE, rate: $DECAY_RATE)"
  else
    # Update the state file
    jq ".dimensions.$DIM = $NEW" "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "$DIM: $CURRENT → $NEW (rate: $DECAY_RATE)"
  fi
done

# Update timestamp
if [ "$DRY_RUN" = false ]; then
  jq ".lastUpdated = \"$NOW\"" "$STATE_FILE" > "$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"
  echo ""
  echo "✅ State decayed toward baseline"
else
  echo ""
  echo "(dry run - no changes made)"
fi

# Clear old emotions from recent list (older than 24h)
if [ "$DRY_RUN" = false ]; then
  CUTOFF=$(date -u -v-24H +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u -d "24 hours ago" +"%Y-%m-%dT%H:%M:%SZ")
  jq ".recentEmotions = [.recentEmotions[] | select(.timestamp > \"$CUTOFF\")]" "$STATE_FILE" > "$STATE_FILE.tmp" 2>/dev/null && mv "$STATE_FILE.tmp" "$STATE_FILE" || true
  
  # Sync to AMYGDALA_STATE.md for auto-injection
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  "$SCRIPT_DIR/sync-state.sh"
fi
