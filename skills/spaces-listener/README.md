# 🎧 spaces-listener

Record and transcribe X/Twitter Spaces — live or replays.

**Zero API costs.** Everything runs locally on your Mac.

## Features

- 📥 **Audio recording** — Direct download via yt-dlp
- 📝 **Auto-transcription** — Local Whisper (no API key)
- ⏺️ **Live Spaces** — Record in real-time as they happen
- 🔄 **Replays** — Download at full speed
- 💰 **Free** — No API costs, no rate limits

## Installation

### Prerequisites

```bash
brew install yt-dlp ffmpeg openai-whisper
```

### Install the skill

```bash
# Clone to your skills directory
git clone https://github.com/jamesalmeida/spaces-listener.git ~/clawd/skills/spaces-listener

# Add to PATH (add to your .zshrc or .bashrc)
export PATH="$HOME/clawd/skills/spaces-listener/scripts:$PATH"

# Or create a symlink
ln -s ~/clawd/skills/spaces-listener/scripts/spaces /usr/local/bin/spaces
```

## Usage

### Basic

```bash
spaces listen "https://x.com/i/spaces/1ABC..."
```

### Options

| Flag | Description |
|------|-------------|
| `--output`, `-o` | Output directory (default: ~/Desktop) |
| `--model` | Whisper model: tiny/base/small/medium/large |
| `--no-transcribe` | Skip transcription |

### Examples

```bash
# Record a live Space
spaces listen "https://x.com/i/spaces/1ABC..."

# High-quality transcription
spaces listen "https://x.com/i/spaces/1ABC..." --model large

# Save to specific folder
spaces listen "https://x.com/i/spaces/1ABC..." -o ~/Spaces
```

## Output

Files saved to output directory:
- `space_<username>_<date>.m4a` — Audio
- `space_<username>_<date>.txt` — Transcript

## Video Recording

Want video of the Space UI? Use **QuickTime Player**:

1. Install BlackHole for system audio capture:
   ```bash
   brew install blackhole-2ch
   ```

2. Set up Multi-Output Device in Audio MIDI Setup:
   - Open Audio MIDI Setup (in /Applications/Utilities)
   - Click + → Create Multi-Output Device
   - Check both your speakers AND BlackHole 2ch
   - Set this as your system output in Sound settings

3. Record with QuickTime:
   - File → New Screen Recording
   - Click dropdown arrow, select "BlackHole 2ch" for audio
   - Record your screen while the Space plays

**Why isn't video automated?** macOS requires Screen Recording permission granted to a proper .app bundle. CLI tools running as background services (like Clawdbot) can't easily get this permission. Audio-only mode works perfectly automated.

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   X Space   │────▶│   yt-dlp    │────▶│    .m4a     │
│    (URL)    │     │  (download) │     │   (audio)   │
└─────────────┘     └─────────────┘     └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │   Whisper   │
                                        │ (transcribe)│
                                        └──────┬──────┘
                                               │
                                               ▼
                                        ┌─────────────┐
                                        │    .txt     │
                                        │ (transcript)│
                                        └─────────────┘
```

## Whisper Models

| Model | Speed | Accuracy | Download |
|-------|-------|----------|----------|
| tiny | ⚡⚡⚡⚡ | ⭐ | 39 MB |
| base | ⚡⚡⚡ | ⭐⭐ | 142 MB |
| small | ⚡⚡ | ⭐⭐⭐ | 466 MB |
| medium | ⚡ | ⭐⭐⭐⭐ | 1.5 GB |
| large | 🐢 | ⭐⭐⭐⭐⭐ | 2.9 GB |

First run downloads the model. Subsequent runs use the cached model.

## License

MIT
