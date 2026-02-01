---
name: inworld-tts
description: Text-to-speech via Inworld.ai API. Use when generating voice audio from text, creating spoken responses, or converting text to MP3/audio files. Supports multiple voices, speaking rates, and streaming for long text.
---

# Inworld TTS

Generate speech audio from text using Inworld.ai's TTS API.

## Setup

1. Get API key from https://platform.inworld.ai
2. Generate key with "Voices: Read" permission
3. Copy the "Basic (Base64)" key
4. Set environment variable:

```bash
export INWORLD_API_KEY="your-base64-key-here"
```

For persistence, add to `~/.bashrc` or `~/.clawdbot/.env`.

## Installation

```bash
# Copy skill to your skills directory
cp -r inworld-tts /path/to/your/skills/

# Make script executable
chmod +x /path/to/your/skills/inworld-tts/scripts/tts.sh

# Optional: symlink for global access
ln -sf /path/to/your/skills/inworld-tts/scripts/tts.sh /usr/local/bin/inworld-tts
```

## Usage

```bash
# Basic
./scripts/tts.sh "Hello world" output.mp3

# With options
./scripts/tts.sh "Hello world" output.mp3 --voice Dennis --rate 1.2

# Streaming (for text >4000 chars)
./scripts/tts.sh "Very long text..." output.mp3 --stream
```

## Options

| Option | Default | Description |
|--------|---------|-------------|
| `--voice` | Dennis | Voice ID |
| `--rate` | 1.0 | Speaking rate (0.5-2.0) |
| `--temp` | 1.1 | Temperature (0.1-2.0) |
| `--model` | inworld-tts-1.5-max | Model ID |
| `--stream` | false | Use streaming endpoint |

## API Reference

| Endpoint | Use |
|----------|-----|
| `POST https://api.inworld.ai/tts/v1/voice` | Standard synthesis |
| `POST https://api.inworld.ai/tts/v1/voice:stream` | Streaming for long text |

## Requirements

- `curl` - HTTP requests
- `jq` - JSON processing  
- `base64` - Decode audio

## Examples

```bash
# Quick test
export INWORLD_API_KEY="aXM2..."
./scripts/tts.sh "Testing one two three" test.mp3
mpv test.mp3  # or any audio player

# Different voice and speed
./scripts/tts.sh "Slow and steady" slow.mp3 --rate 0.8

# Fast-paced narration
./scripts/tts.sh "Breaking news!" fast.mp3 --rate 1.5
```

## Troubleshooting

**"INWORLD_API_KEY not set"** - Export the environment variable before running.

**Empty output file** - Check API key is valid and has "Voices: Read" permission.

**Streaming issues** - Ensure `jq` supports `--unbuffered` flag.

## Links

- Inworld Platform: https://platform.inworld.ai
- API Examples: https://github.com/inworld-ai/inworld-api-examples
