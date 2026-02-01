---
name: fal-api
description: Generate images, videos, and audio via fal.ai API (FLUX, SDXL, Whisper, etc.)
version: 0.1.0
metadata:
  {
    "openclaw": { "requires": { "env": ["FAL_KEY"] }, "primaryEnv": "FAL_KEY" },
  }
---

# fal.ai API Skill

Generate images, videos, and transcripts using fal.ai's API with support for FLUX, Stable Diffusion, Whisper, and more.

## Features

- Queue-based async generation (submit → poll → result)
- Support for 600+ AI models
- Image generation (FLUX, SDXL, Recraft)
- Video generation (MiniMax, WAN)
- Speech-to-text (Whisper)
- Stdlib-only dependencies (no `fal_client` required)

## Setup

1. Get your API key from https://fal.ai/dashboard/keys
2. Configure with:

```bash
export FAL_KEY="your-api-key"
```

Or via clawdbot config:

```bash
clawdbot config set skill.fal_api.key YOUR_API_KEY
```

## Usage

### Interactive Mode

```
You: Generate a cyberpunk cityscape with FLUX
Klawf: Creates the image and returns the URL
```

### Python Script

```python
from fal_api import FalAPI

api = FalAPI()

# Generate and wait
urls = api.generate_and_wait(
    prompt="A serene Japanese garden",
    model="flux-dev"
)
print(urls)
```

### Available Models

| Model         | Endpoint                              | Type         |
| ------------- | ------------------------------------- | ------------ |
| flux-schnell  | `fal-ai/flux/schnell`                 | Image (fast) |
| flux-dev      | `fal-ai/flux/dev`                     | Image        |
| flux-pro      | `fal-ai/flux-pro/v1.1-ultra`          | Image (2K)   |
| fast-sdxl     | `fal-ai/fast-sdxl`                    | Image        |
| recraft-v3    | `fal-ai/recraft-v3`                   | Image        |
| sd35-large    | `fal-ai/stable-diffusion-v35-large`   | Image        |
| minimax-video | `fal-ai/minimax-video/image-to-video` | Video        |
| wan-video     | `fal-ai/wan/v2.1/1.3b/text-to-video`  | Video        |
| whisper       | `fal-ai/whisper`                      | Audio        |

For the full list, run:

```bash
python3 fal_api.py --list-models
```

## Parameters

| Parameter  | Type | Default          | Description                                        |
| ---------- | ---- | ---------------- | -------------------------------------------------- |
| prompt     | str  | required         | Image/video description                            |
| model      | str  | "flux-dev"       | Model name from table above                        |
| image_size | str  | "landscape_16_9" | Preset: square, portrait_4_3, landscape_16_9, etc. |
| num_images | int  | 1                | Number of images to generate                       |
| seed       | int  | None             | Random seed for reproducibility                    |

## Credits

Built following the krea-api skill pattern. Uses fal.ai's queue-based API for reliable async generation.
