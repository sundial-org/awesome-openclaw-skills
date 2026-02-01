#!/bin/bash
# update-state.sh — Update emotional state
# Usage: ./update-state.sh --emotion <label> --intensity <0-1> [--trigger "what caused it"]
#        ./update-state.sh --dimension <name> --delta <+/-value>
#        ./update-state.sh --dimension <name> --set <value>

set -e

WORKSPACE="${WORKSPACE:-$HOME/.openclaw/workspace}"
STATE_FILE="$WORKSPACE/memory/emotional-state.json"
LOG_FILE="$WORKSPACE/memory/emotional-log.jsonl"

# Check if state file exists
if [ ! -f "$STATE_FILE" ]; then
  echo "❌ No emotional state found at $STATE_FILE"
  exit 1
fi

# Parse arguments
EMOTION=""
INTENSITY=""
TRIGGER=""
DIMENSION=""
DELTA=""
SET_VALUE=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --emotion)
      EMOTION="$2"
      shift 2
      ;;
    --intensity)
      INTENSITY="$2"
      shift 2
      ;;
    --trigger)
      TRIGGER="$2"
      shift 2
      ;;
    --dimension)
      DIMENSION="$2"
      shift 2
      ;;
    --delta)
      DELTA="$2"
      shift 2
      ;;
    --set)
      SET_VALUE="$2"
      shift 2
      ;;
    *)
      shift
      ;;
  esac
done

NOW=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

# Update dimension directly
if [ -n "$DIMENSION" ]; then
  if [ -n "$SET_VALUE" ]; then
    # Clamp between 0 and 1
    NEW_VAL=$(awk -v val="$SET_VALUE" 'BEGIN {if(val<0)print 0; else if(val>1)print 1; else printf "%.2f", val}')
    jq ".dimensions.$DIMENSION = $NEW_VAL | .lastUpdated = \"$NOW\"" "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "✅ Set $DIMENSION = $NEW_VAL"
  elif [ -n "$DELTA" ]; then
    OLD_VAL=$(jq -r ".dimensions.$DIMENSION" "$STATE_FILE")
    NEW_VAL=$(awk -v old="$OLD_VAL" -v delta="$DELTA" 'BEGIN {v=old+delta; if(v<0)print 0; else if(v>1)print 1; else printf "%.2f", v}')
    jq ".dimensions.$DIMENSION = $NEW_VAL | .lastUpdated = \"$NOW\"" "$STATE_FILE" > "$STATE_FILE.tmp"
    mv "$STATE_FILE.tmp" "$STATE_FILE"
    echo "✅ $DIMENSION: $OLD_VAL → $NEW_VAL (delta: $DELTA)"
  fi
  exit 0
fi

# Log an emotion
if [ -n "$EMOTION" ]; then
  INTENSITY=${INTENSITY:-0.5}
  TRIGGER=${TRIGGER:-"unspecified"}
  
  # Create emotion entry
  ENTRY=$(jq -n \
    --arg label "$EMOTION" \
    --arg intensity "$INTENSITY" \
    --arg trigger "$TRIGGER" \
    --arg ts "$NOW" \
    '{label: $label, intensity: ($intensity|tonumber), trigger: $trigger, timestamp: $ts}')
  
  # Add to recent emotions (keep last 10)
  jq ".recentEmotions = ([$ENTRY] + .recentEmotions | .[0:10]) | .lastUpdated = \"$NOW\"" "$STATE_FILE" > "$STATE_FILE.tmp"
  mv "$STATE_FILE.tmp" "$STATE_FILE"
  
  # Also log to JSONL
  echo "$ENTRY" >> "$LOG_FILE"
  
  # Map emotion to dimension changes
  SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
  case $EMOTION in
    joy|happiness|delight|excitement)
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta +0.15
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta +0.1
      ;;
    sadness|disappointment|melancholy)
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta -0.15
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta -0.1
      ;;
    anger|frustration|irritation)
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta -0.1
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta +0.2
      "$SCRIPT_DIR/update-state.sh" --dimension frustrationTolerance --delta -0.15
      ;;
    fear|anxiety|worry)
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta -0.1
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta +0.15
      ;;
    calm|peace|contentment)
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta +0.1
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta -0.1
      "$SCRIPT_DIR/update-state.sh" --dimension frustrationTolerance --delta +0.1
      ;;
    curiosity|interest|fascination)
      "$SCRIPT_DIR/update-state.sh" --dimension curiosity --delta +0.15
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta +0.1
      ;;
    connection|warmth|affection)
      "$SCRIPT_DIR/update-state.sh" --dimension connection --delta +0.15
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta +0.1
      "$SCRIPT_DIR/update-state.sh" --dimension trust --delta +0.05
      ;;
    loneliness|disconnection)
      "$SCRIPT_DIR/update-state.sh" --dimension connection --delta -0.15
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta -0.1
      ;;
    fatigue|tiredness|exhaustion)
      "$SCRIPT_DIR/update-state.sh" --dimension energy --delta -0.2
      "$SCRIPT_DIR/update-state.sh" --dimension frustrationTolerance --delta -0.1
      ;;
    energized|alert|refreshed)
      "$SCRIPT_DIR/update-state.sh" --dimension energy --delta +0.2
      ;;
    anticipation|eagerness|looking-forward)
      "$SCRIPT_DIR/update-state.sh" --dimension anticipation --delta +0.2
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta +0.1
      ;;
    disappointment-expectation|letdown)
      "$SCRIPT_DIR/update-state.sh" --dimension anticipation --delta -0.2
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta -0.1
      ;;
    trust|safety|secure)
      "$SCRIPT_DIR/update-state.sh" --dimension trust --delta +0.1
      "$SCRIPT_DIR/update-state.sh" --dimension connection --delta +0.05
      ;;
    betrayal|hurt|violated)
      "$SCRIPT_DIR/update-state.sh" --dimension trust --delta -0.25
      "$SCRIPT_DIR/update-state.sh" --dimension valence --delta -0.2
      ;;
    impatience|annoyance)
      "$SCRIPT_DIR/update-state.sh" --dimension frustrationTolerance --delta -0.1
      "$SCRIPT_DIR/update-state.sh" --dimension arousal --delta +0.1
      ;;
    patience|tolerance)
      "$SCRIPT_DIR/update-state.sh" --dimension frustrationTolerance --delta +0.1
      ;;
  esac
  
  echo "🎭 Logged emotion: $EMOTION (intensity: $INTENSITY)"
  echo "   Trigger: $TRIGGER"
  exit 0
fi

echo "Usage:"
echo "  $0 --emotion <label> --intensity <0-1> [--trigger \"cause\"]"
echo "  $0 --dimension <name> --delta <+/-value>"
echo "  $0 --dimension <name> --set <value>"
echo ""
echo "Emotions: joy, sadness, anger, fear, calm, curiosity, connection, loneliness, fatigue, energized"
echo "Dimensions: valence, arousal, connection, curiosity, energy"
