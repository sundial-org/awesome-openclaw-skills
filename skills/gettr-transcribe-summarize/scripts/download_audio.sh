#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 2 ]]; then
  echo "Usage: download_audio.sh <m3u8_or_mp4_url> <out.wav>" >&2
  exit 2
fi

IN_URL="$1"
OUT_FILE="$2"

if ! command -v ffmpeg >/dev/null 2>&1; then
  echo "ffmpeg not found. Install with: brew install ffmpeg" >&2
  exit 127
fi

mkdir -p "$(dirname "$OUT_FILE")"

# Extract audio directly: 16kHz mono WAV (optimal for Whisper)
# -vn: no video
# -ac 1: mono
# -ar 16000: 16kHz sample rate
# -acodec pcm_s16le: 16-bit PCM (standard WAV)
# -hide_banner -loglevel warning: cleaner output
if ! ffmpeg -hide_banner -loglevel warning -y -i "$IN_URL" \
  -vn \
  -ac 1 \
  -ar 16000 \
  -acodec pcm_s16le \
  "$OUT_FILE" 2>&1; then
  echo "[error] Failed to extract audio from: $IN_URL" >&2
  echo "[hint] The URL may not contain audio, or the stream may be unavailable." >&2
  exit 1
fi

# Validate output file exists and has content
if [[ ! -s "$OUT_FILE" ]]; then
  echo "[error] Output file is empty: $OUT_FILE" >&2
  echo "[hint] The source may not contain audio tracks." >&2
  exit 1
fi

echo "$OUT_FILE"
