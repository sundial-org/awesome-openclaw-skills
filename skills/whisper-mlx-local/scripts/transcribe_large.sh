#!/bin/bash
#
# transcribe_large.sh - Use distil-large-v3 for long audio files
#
# Usage:
#   transcribe_large.sh <audio_file> [--translate]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
AUDIO_FILE="$1"
shift || true

if [[ -z "$AUDIO_FILE" ]]; then
    echo "Usage: transcribe_large.sh <audio_file> [--translate]" >&2
    exit 1
fi

if [[ ! -f "$AUDIO_FILE" ]]; then
    echo "Error: File not found: $AUDIO_FILE" >&2
    exit 1
fi

# Convert to absolute path
AUDIO_FILE="$(cd "$(dirname "$AUDIO_FILE")" && pwd)/$(basename "$AUDIO_FILE")"

# Parse additional args
TRANSLATE=""
LANGUAGE=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --translate|-t) TRANSLATE="--translate"; shift ;;
        --language|-l) LANGUAGE="--language $2"; shift 2 ;;
        *) shift ;;
    esac
done

echo "Transcribing with distil-large-v3 model (this may take a moment)..." >&2

# Use Python directly with the large model
/usr/bin/python3 << EOF
import sys
sys.path.insert(0, "$SCRIPT_DIR")
from transcriber import Transcriber

translation_mode = $([[ -n "$TRANSLATE" ]] && echo "True" || echo "False")
t = Transcriber(backend='mlx', model='distil-large-v3', translation_mode=translation_mode)
result = t.transcribe("$AUDIO_FILE")
print(result)
EOF
