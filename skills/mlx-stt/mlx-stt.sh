#!/bin/bash

set -ueo pipefail

audio=$1

# Create a temporary directory for this task
task_temp_dir=$(mktemp -d)

# cleanup on exit
cleanup() {
  rm -rf "$task_temp_dir"
}
trap cleanup EXIT

# If user provided output path, use it. Otherwise use temp dir.
if [ -n "${2:-}" ]; then
    out="$2"
else
    out="$task_temp_dir/out"
fi

# https://github.com/Blaizzy/mlx-audio/tree/main
# mlx_audio is installed as cli tools only
# uv tool install --force mlx-audio --prerelease=allow
# Installed 4 executables: mlx_audio.convert, mlx_audio.server, mlx_audio.stt.generate, mlx_audio.tts.generate

# Convert audio to WAV format (mlx-audio has issues with .ogg/opus)
temp_wav="$task_temp_dir/input.wav"
ffmpeg -i "${audio}" -ar 16000 -ac 1 -c:a pcm_s16le "${temp_wav}" -y > /dev/null 2>&1

#model=mlx-community/GLM-ASR-Nano-2512-4bit
model=mlx-community/GLM-ASR-Nano-2512-8bit
mlx_audio.stt.generate --model "${model}" --audio "${temp_wav}" --format txt --output "${out}" > /dev/null 2>&1
cat "${out}.txt"
