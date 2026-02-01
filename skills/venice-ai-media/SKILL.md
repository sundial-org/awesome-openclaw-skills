---
name: venice-ai-media
description: Generate, edit, and upscale images; create videos from images or other videos via Venice AI. Supports text-to-image, image-to-video (Sora, WAN), video-to-video (Runway Gen4), upscaling, and AI editing.
homepage: https://venice.ai
metadata:
  {
    "clawdbot":
      {
        "emoji": "🎨",
        "requires": { "bins": ["python3"], "env": ["VENICE_API_KEY"] },
        "primaryEnv": "VENICE_API_KEY",
        "notes": "Requires Python 3.10+",
        "install":
          [
            {
              "id": "python-brew",
              "kind": "brew",
              "formula": "python",
              "bins": ["python3"],
              "label": "Install Python (brew)",
            },
          ],
      },
  }
---

# Venice AI Media

Generate images and videos using Venice AI APIs. Venice is an uncensored AI platform with competitive pricing.

## Prerequisites

- **Python 3.10+** (`brew install python` or system Python)
- **Venice API key** (free tier available)
- **requests** library (auto-installed by scripts if missing)

## Setup

### 1. Get Your API Key

1. Create account at [venice.ai](https://venice.ai)
2. Go to [venice.ai/settings/api](https://venice.ai/settings/api)
3. Click "Create API Key"
4. Copy the key (starts with `vn_...`)

### 2. Configure the Key

**Option A: Environment variable**

```bash
export VENICE_API_KEY="vn_your_key_here"
```

**Option B: Clawdbot config** (recommended - persists across sessions)

Add to `~/.clawdbot/clawdbot.json`:

```json5
{
  skills: {
    entries: {
      "venice-ai-media": {
        env: {
          VENICE_API_KEY: "vn_your_key_here",
        },
      },
    },
  },
}
```

### 3. Verify Setup

```bash
python3 {baseDir}/scripts/venice-image.py --list-models
```

If you see a list of models, you're ready!

## Pricing Overview

| Feature          | Cost                              |
| ---------------- | --------------------------------- |
| Image generation | ~$0.01-0.03 per image             |
| Image upscale    | ~$0.02-0.04                       |
| Image edit       | $0.04                             |
| Video (WAN)      | ~$0.10-0.50 depending on duration |
| Video (Sora)     | ~$0.50-2.00 depending on duration |
| Video (Runway)   | ~$0.20-1.00                       |

Use `--quote` with video commands to check pricing before generation.

## Quick Start

```bash
# Generate an image
python3 {baseDir}/scripts/venice-image.py --prompt "a serene canal in Venice at sunset"

# Upscale an image
python3 {baseDir}/scripts/venice-upscale.py photo.jpg --scale 2

# Edit an image with AI
python3 {baseDir}/scripts/venice-edit.py photo.jpg --prompt "add sunglasses"

# Create a video from an image
python3 {baseDir}/scripts/venice-video.py --image photo.jpg --prompt "gentle camera pan" --duration 5s
```

---

## Image Generation

```bash
python3 {baseDir}/scripts/venice-image.py --prompt "a serene canal in Venice at sunset"
python3 {baseDir}/scripts/venice-image.py --prompt "cyberpunk city" --count 4
python3 {baseDir}/scripts/venice-image.py --prompt "portrait" --width 768 --height 1024
python3 {baseDir}/scripts/venice-image.py --prompt "abstract art" --out-dir /tmp/venice
python3 {baseDir}/scripts/venice-image.py --list-models
python3 {baseDir}/scripts/venice-image.py --list-styles
python3 {baseDir}/scripts/venice-image.py --prompt "fantasy" --model flux-2-pro --no-validate
python3 {baseDir}/scripts/venice-image.py --prompt "photo" --style-preset "Cinematic" --embed-exif
```

**Key flags:** `--prompt`, `--model` (default: flux-2-max), `--count` (uses efficient batch API for same prompt), `--width`, `--height`, `--format` (webp/png/jpeg), `--resolution` (1K/2K/4K), `--aspect-ratio`, `--negative-prompt`, `--style-preset` (use `--list-styles` to see options), `--cfg-scale` (prompt adherence 0-20, default 7.5), `--seed` (for reproducible results), `--safe-mode` (disabled by default for uncensored output), `--hide-watermark` (only use if explicitly requested - watermark supports Venice), `--embed-exif` (embed prompt in image metadata), `--lora-strength` (0-100 for applicable models), `--steps` (inference steps, model-dependent), `--enable-web-search`, `--no-validate` (skip model check for new/beta models)

## Image Upscale

```bash
python3 {baseDir}/scripts/venice-upscale.py photo.jpg --scale 2
python3 {baseDir}/scripts/venice-upscale.py photo.jpg --scale 4 --enhance
python3 {baseDir}/scripts/venice-upscale.py photo.jpg --enhance --enhance-prompt "sharpen details"
python3 {baseDir}/scripts/venice-upscale.py --url "https://example.com/image.jpg" --scale 2
```

**Key flags:** `--scale` (1-4, default: 2), `--enhance` (AI enhancement), `--enhance-prompt`, `--enhance-creativity` (0.0-1.0), `--replication` (0.0-1.0, preserves lines/noise, default: 0.35), `--url` (use URL instead of local file), `--output`, `--out-dir`

## Image Edit

```bash
python3 {baseDir}/scripts/venice-edit.py photo.jpg --prompt "add sunglasses"
python3 {baseDir}/scripts/venice-edit.py photo.jpg --prompt "change the sky to sunset"
python3 {baseDir}/scripts/venice-edit.py photo.jpg --prompt "remove the person in background"
python3 {baseDir}/scripts/venice-edit.py --url "https://example.com/image.jpg" --prompt "colorize"
```

**Key flags:** `--prompt` (required - AI interprets what to modify), `--url` (use URL instead of local file), `--output`, `--out-dir`

**Note:** The edit endpoint uses the Qwen-Image model which has some content restrictions (unlike other Venice endpoints).

## Video Generation

```bash
# Get price quote first (no generation)
python3 {baseDir}/scripts/venice-video.py --quote --model wan-2.6-image-to-video --duration 10s --resolution 720p

# Image-to-video (WAN 2.6 - default)
python3 {baseDir}/scripts/venice-video.py --image photo.jpg --prompt "camera pans slowly" --duration 10s

# Image-to-video (Sora)
python3 {baseDir}/scripts/venice-video.py --image photo.jpg --prompt "cinematic" \
  --model sora-2-image-to-video --duration 8s --aspect-ratio 16:9 --skip-audio-param

# Video-to-video (Runway Gen4)
python3 {baseDir}/scripts/venice-video.py --video input.mp4 --prompt "anime style" \
  --model runway-gen4-turbo-v2v

# List models (shows available durations per model)
python3 {baseDir}/scripts/venice-video.py --list-models

# Clean up a video downloaded with --no-delete
python3 {baseDir}/scripts/venice-video.py --complete <queue_id> --model <model>
```

**Key flags:** `--image` or `--video` (required for generation), `--prompt` (required for generation), `--model` (default: wan-2.6-image-to-video), `--duration` (model-dependent, see --list-models), `--resolution` (480p/720p/1080p), `--aspect-ratio`, `--audio`/`--no-audio`, `--skip-audio-param`, `--quote` (price estimate), `--timeout`, `--poll-interval`, `--no-delete` (keep server media), `--complete` (cleanup previously downloaded video), `--no-validate` (skip model check)

**Progress:** During generation, the script shows estimated progress based on Venice's average execution time.

## Model Notes

Use `--list-models` to see current availability and status. Models change frequently.

**Image:** Default is `flux-2-max`. Common options include flux, gpt-image, and nano-banana variants.

**Video:**

- **WAN** models: Image-to-video, configurable audio, various durations (5s-21s)
- **Sora** models: Requires `--aspect-ratio`, use `--skip-audio-param`
- **Runway** models: Video-to-video transformation

**Tips:**

- Use `--no-validate` for new or beta models not yet in the model list
- Use `--quote` for video to check pricing before generation
- Safe mode is disabled by default (Venice is an uncensored API)

## Output

Scripts print a `MEDIA: /path/to/file` line for Clawdbot auto-attach.

**Tip:** Use `--out-dir /tmp/venice-$(date +%s)` when generating media to send via iMessage (ensures accessibility across user accounts).

## Troubleshooting

**"VENICE_API_KEY not set"**

- Check your config in `~/.clawdbot/clawdbot.json`
- Or export the env var: `export VENICE_API_KEY="vn_..."`

**"Invalid API key"**

- Verify your key at [venice.ai/settings/api](https://venice.ai/settings/api)
- Keys start with `vn_`

**"Model not found"**

- Run `--list-models` to see available models
- Use `--no-validate` for new/beta models

**Video stuck/timeout**

- Videos can take 1-5 minutes depending on model and duration
- Use `--timeout 600` for longer videos
- Check Venice status at [venice.ai](https://venice.ai)

**"requests" module not found**

- Install it: `pip3 install requests`
