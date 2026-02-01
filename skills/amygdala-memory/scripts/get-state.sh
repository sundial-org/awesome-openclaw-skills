#!/bin/bash
# get-state.sh — Read current emotional state
# Usage: ./get-state.sh [--json] [--dimension <name>]

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/emotional-state.json"

# Check if state file exists
if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No emotional state found at $STATE_FILE"
  exit 1
fi

# Parse arguments
JSON_OUTPUT=false
DIMENSION=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --json)
      JSON_OUTPUT=true
      shift
      ;;
    --dimension)
      DIMENSION="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

# If specific dimension requested
if [ -n "$DIMENSION" ]; then
  VALUE=$(jq -r ".dimensions.$DIMENSION // \"unknown\"" "$STATE_FILE")
  if [ "$JSON_OUTPUT" = true ]; then
    echo "{\"$DIMENSION\": $VALUE}"
  else
    echo "$DIMENSION: $VALUE"
  fi
  exit 0
fi

# Full output
if [ "$JSON_OUTPUT" = true ]; then
  cat "$STATE_FILE"
else
  echo "🎭 Emotional State"
  echo "─────────────────────"
  echo ""
  
  # Read dimensions
  VALENCE=$(jq -r '.dimensions.valence' "$STATE_FILE")
  AROUSAL=$(jq -r '.dimensions.arousal' "$STATE_FILE")
  CONNECTION=$(jq -r '.dimensions.connection' "$STATE_FILE")
  CURIOSITY=$(jq -r '.dimensions.curiosity' "$STATE_FILE")
  ENERGY=$(jq -r '.dimensions.energy' "$STATE_FILE")
  
  # Format as bars
  bar() {
    local val=$1
    local width=20
    local filled=$(echo "$val * $width" | bc | cut -d. -f1)
    [ -z "$filled" ] && filled=0
    local empty=$((width - filled))
    printf "[%${filled}s%${empty}s]" | tr ' ' '█' | tr ' ' '░'
  }
  
  printf "Valence:    %s %.2f\n" "$(bar $VALENCE)" "$VALENCE"
  printf "Arousal:    %s %.2f\n" "$(bar $AROUSAL)" "$AROUSAL"
  printf "Connection: %s %.2f\n" "$(bar $CONNECTION)" "$CONNECTION"
  printf "Curiosity:  %s %.2f\n" "$(bar $CURIOSITY)" "$CURIOSITY"
  printf "Energy:     %s %.2f\n" "$(bar $ENERGY)" "$ENERGY"
  
  echo ""
  echo "Last updated: $(jq -r '.lastUpdated' "$STATE_FILE")"
  
  # Recent emotions
  RECENT=$(jq -r '.recentEmotions[0].label // "none"' "$STATE_FILE")
  if [ "$RECENT" != "none" ]; then
    echo ""
    echo "Recent: $RECENT"
  fi
fi
