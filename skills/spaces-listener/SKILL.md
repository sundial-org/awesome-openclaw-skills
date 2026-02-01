# spaces-listener

Record and transcribe X/Twitter Spaces — live or replays. Supports multiple concurrent recordings.

## Commands

```bash
# Start recording (runs in background)
spaces listen <url>

# Record multiple Spaces at once
spaces listen "https://x.com/i/spaces/1ABC..."
spaces listen "https://x.com/i/spaces/2DEF..."

# List all active recordings
spaces list

# Check specific recording status
spaces status 1

# Stop a recording
spaces stop 1
spaces stop all

# Transcribe when done
spaces transcribe ~/Desktop/space.m4a --model medium
```

## Requirements

```bash
brew install yt-dlp ffmpeg openai-whisper
```

## How It Works

1. Each `spaces listen` starts a new background recording with a unique ID
2. Recordings persist even if you close terminal
3. Run `spaces list` to see all active recordings
4. When done, `spaces stop <id>` or `spaces stop all`
5. Transcribe with `spaces transcribe <file>`

## Output

Files saved to `--output` dir (default: `~/Desktop`):
- `space_<username>_<date>.m4a` — audio
- `space_<username>_<date>.log` — progress log
- `space_<username>_<date>.txt` — transcript

## Whisper Models

| Model | Speed | Accuracy |
|-------|-------|----------|
| tiny | ⚡⚡⚡⚡ | ⭐ |
| base | ⚡⚡⚡ | ⭐⭐ |
| small | ⚡⚡ | ⭐⭐⭐ |
| medium | ⚡ | ⭐⭐⭐⭐ |
| large | 🐢 | ⭐⭐⭐⭐⭐ |
