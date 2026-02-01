---
name: runware
description: Generate images and videos via Runware API. Access to FLUX, Stable Diffusion, Kling AI, and other top models. Supports text-to-image, image-to-image, upscaling, text-to-video, and image-to-video. Use when generating images, creating videos from prompts or images, upscaling images, or doing AI image transformation.
---

# Runware

Image and video generation via Runware's unified API. Access FLUX, Stable Diffusion XL, Kling AI, and more.

## Setup

Set `RUNWARE_API_KEY` environment variable, or pass `--api-key` to scripts.

Get API key: https://runware.ai

## Image Generation

### Text-to-Image

```bash
python3 scripts/image.py gen "a cyberpunk city at sunset, neon lights, rain" --count 2 -o ./images
```

Options:
- `--model`: Model ID (default: `runware:101@1` / FLUX.1 Dev)
- `--width/--height`: Dimensions (default: 1024x1024)
- `--steps`: Inference steps (default: 25)
- `--cfg`: CFG scale (default: 7.5)
- `--count/-n`: Number of images
- `--negative`: Negative prompt
- `--seed`: Reproducible seed
- `--lora`: LoRA model ID
- `--format`: png/jpg/webp

### Image-to-Image

Transform an existing image:

```bash
python3 scripts/image.py img2img ./photo.jpg "watercolor painting style" --strength 0.7
```

- `--strength`: How much to transform (0=keep original, 1=ignore original)

### Upscale

```bash
python3 scripts/image.py upscale ./small.png --factor 4 -o ./large.png
```

### List Models

```bash
python3 scripts/image.py models
```

## Video Generation

### Text-to-Video

```bash
python3 scripts/video.py gen "a cat playing with yarn, cute, high quality" --duration 5 -o ./cat.mp4
```

Options:
- `--model`: Model ID (default: `klingai:5@3` / Kling AI 1.6 Pro)
- `--duration`: Length in seconds
- `--width/--height`: Resolution (default: 1920x1080)
- `--negative`: Negative prompt
- `--format`: mp4/webm/mov
- `--max-wait`: Polling timeout (default: 600s)

### Image-to-Video

Animate an image or interpolate between frames:

```bash
# Single image (becomes first frame)
python3 scripts/video.py img2vid ./start.png --prompt "zoom out slowly" -o ./animated.mp4

# Two images (first and last frame)
python3 scripts/video.py img2vid ./start.png ./end.png --duration 5
```

### List Video Models

```bash
python3 scripts/video.py models
```

## Popular Models

### Image
| Model | ID |
|-------|-----|
| FLUX.1 Dev | `runware:101@1` |
| FLUX.1 Schnell (fast) | `runware:100@1` |
| FLUX.1 Kontext | `runware:106@1` |
| Stable Diffusion XL | `civitai:101055@128080` |
| RealVisXL | `civitai:139562@297320` |

### Video
| Model | ID |
|-------|-----|
| Kling AI 1.6 Pro | `klingai:5@3` |
| Kling AI 1.5 Pro | `klingai:3@2` |
| Runway Gen-3 | `runwayml:1@1` |

Browse all: https://runware.ai/models

## Notes

- Video generation is async; scripts poll until complete
- Costs vary by model — check https://runware.ai/pricing
- FLUX models are excellent for quality; Schnell is faster
- For best video results, use descriptive prompts with motion words
