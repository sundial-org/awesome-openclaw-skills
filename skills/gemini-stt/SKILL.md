---
name: gemini-stt
description: Transcribe audio files using Google's Gemini API or Vertex AI
metadata: {"clawdbot":{"emoji":"🎤","os":["linux","darwin"]}}
---

# Gemini Speech-to-Text Skill

Transcribe audio files using Google's Gemini API or Vertex AI. Default model is `gemini-2.0-flash-lite` for fastest transcription.

## Authentication (choose one)

### Option 1: Vertex AI with Application Default Credentials (Recommended)

```bash
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

The script will automatically detect and use ADC when available.

### Option 2: Direct Gemini API Key

Set `GEMINI_API_KEY` in environment (e.g., `~/.env` or `~/.clawdbot/.env`)

## Requirements

- Python 3.10+ (no external dependencies)
- Either GEMINI_API_KEY or gcloud CLI with ADC configured

## Supported Formats

- `.ogg` / `.opus` (Telegram voice messages)
- `.mp3`
- `.wav`
- `.m4a`

## Usage

```bash
# Auto-detect auth (tries ADC first, then GEMINI_API_KEY)
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg

# Force Vertex AI
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg --vertex

# With a specific model
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg --model gemini-2.5-pro

# Vertex AI with specific project and region
python ~/.claude/skills/gemini-stt/transcribe.py /path/to/audio.ogg --vertex --project my-project --region us-central1

# With Clawdbot media
python ~/.claude/skills/gemini-stt/transcribe.py ~/.clawdbot/media/inbound/voice-message.ogg
```

## Options

| Option | Description |
|--------|-------------|
| `<audio_file>` | Path to the audio file (required) |
| `--model`, `-m` | Gemini model to use (default: `gemini-2.0-flash-lite`) |
| `--vertex`, `-v` | Force use of Vertex AI with ADC |
| `--project`, `-p` | GCP project ID (for Vertex, defaults to gcloud config) |
| `--region`, `-r` | GCP region (for Vertex, default: `us-central1`) |

## Supported Models

Any Gemini model that supports audio input can be used. Recommended models:

| Model | Notes |
|-------|-------|
| `gemini-2.0-flash-lite` | **Default.** Fastest transcription speed. |
| `gemini-2.0-flash` | Fast and cost-effective. |
| `gemini-2.5-flash-lite` | Lightweight 2.5 model. |
| `gemini-2.5-flash` | Balanced speed and quality. |
| `gemini-2.5-pro` | Higher quality, slower. |
| `gemini-3-flash-preview` | Latest flash model. |
| `gemini-3-pro-preview` | Latest pro model, best quality. |

See [Gemini API Models](https://ai.google.dev/gemini-api/docs/models) for the latest list.

## How It Works

1. Reads the audio file and base64 encodes it
2. Auto-detects authentication:
   - If ADC is available (gcloud), uses Vertex AI endpoint
   - Otherwise, uses GEMINI_API_KEY with direct Gemini API
3. Sends to the selected Gemini model with transcription prompt
4. Returns the transcribed text

## Example Integration

For Clawdbot voice message handling:

```bash
# Transcribe incoming voice message
TRANSCRIPT=$(python ~/.claude/skills/gemini-stt/transcribe.py "$AUDIO_PATH")
echo "User said: $TRANSCRIPT"
```

## Error Handling

The script exits with code 1 and prints to stderr on:
- No authentication available (neither ADC nor GEMINI_API_KEY)
- File not found
- API errors
- Missing GCP project (when using Vertex)

## Notes

- Uses Gemini 2.0 Flash Lite by default for fastest transcription
- No external Python dependencies (uses stdlib only)
- Automatically detects MIME type from file extension
- Prefers Vertex AI with ADC when available (no API key management needed)