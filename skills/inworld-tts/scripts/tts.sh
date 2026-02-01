#!/bin/bash
# Inworld.ai TTS - Text to Speech
# Usage: tts.sh <text> <output.mp3> [--voice NAME] [--rate FLOAT] [--temp FLOAT] [--stream]

set -euo pipefail

# Defaults
VOICE="Dennis"
RATE=1
TEMP=1.1
MODEL="inworld-tts-1.5-max"
STREAM=false

# Args
TEXT="${1:-}"
OUTPUT="${2:-output.mp3}"
shift 2 || true

while [[ $# -gt 0 ]]; do
  case $1 in
    --voice) VOICE="$2"; shift 2 ;;
    --rate) RATE="$2"; shift 2 ;;
    --temp) TEMP="$2"; shift 2 ;;
    --model) MODEL="$2"; shift 2 ;;
    --stream) STREAM=true; shift ;;
    *) shift ;;
  esac
done

if [[ -z "$TEXT" ]]; then
  echo "Usage: tts.sh <text> <output.mp3> [--voice NAME] [--rate FLOAT] [--stream]" >&2
  exit 1
fi

if [[ -z "${INWORLD_API_KEY:-}" ]]; then
  echo "Error: INWORLD_API_KEY not set" >&2
  exit 1
fi

PAYLOAD=$(cat <<EOF
{
  "text": $(echo "$TEXT" | jq -Rs .),
  "voice_id": "$VOICE",
  "audio_config": {
    "audio_encoding": "MP3",
    "speaking_rate": $RATE
  },
  "temperature": $TEMP,
  "model_id": "$MODEL"
}
EOF
)

if [[ "$STREAM" == "true" ]]; then
  curl -s --request POST \
    --url "https://api.inworld.ai/tts/v1/voice:stream" \
    --header "Authorization: Basic $INWORLD_API_KEY" \
    --header "Content-Type: application/json" \
    --data "$PAYLOAD" \
    --no-buffer \
    | jq -r --unbuffered '(.result.audioContent? // .audioContent? // empty)' \
    | base64 -d > "$OUTPUT"
else
  curl -s --request POST \
    --url "https://api.inworld.ai/tts/v1/voice" \
    --header "Authorization: Basic $INWORLD_API_KEY" \
    --header "Content-Type: application/json" \
    --data "$PAYLOAD" \
    | jq -r '.audioContent' \
    | base64 -d > "$OUTPUT"
fi

if [[ -s "$OUTPUT" ]]; then
  echo "$OUTPUT"
else
  echo "Error: No audio generated" >&2
  exit 1
fi
