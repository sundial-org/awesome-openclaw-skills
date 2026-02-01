---
name: nano-banana-antigravity
description: Generate or edit images via Nano Banana Pro using Antigravity OAuth (no API key needed!)
homepage: https://antigravity.google
metadata: {"openclaw":{"emoji":"🍌","requires":{"bins":["uv"]}}}
---

# Nano Banana Antigravity (Gemini 3 Pro Image via OAuth)

Generate images using Nano Banana Pro (Gemini 3 Pro Image) via your existing Google Antigravity OAuth credentials.

**No separate API key needed!** Uses the same OAuth tokens as your OpenClaw Antigravity provider.

## Generate Image

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "your image description" --filename "output.png"
```

## Generate with Options

```bash
uv run {baseDir}/scripts/generate_image.py \
  --prompt "a sunset over mountains" \
  --filename "sunset.png" \
  --aspect-ratio 16:9 \
  --resolution 2K
```

## Edit/Composite Images

```bash
uv run {baseDir}/scripts/generate_image.py \
  --prompt "add sunglasses to this person" \
  --filename "edited.png" \
  -i original.png
```

## Multi-image Composition

```bash
uv run {baseDir}/scripts/generate_image.py \
  --prompt "combine these into one scene" \
  --filename "composite.png" \
  -i image1.png -i image2.png -i image3.png
```

## Options

- `--prompt, -p` (required): Image description or edit instructions
- `--filename, -f` (required): Output filename
- `--input-image, -i`: Input image(s) for editing (can be repeated)
- `--aspect-ratio, -a`: 1:1 (default), 2:3, 3:2, 3:4, 4:3, 4:5, 5:4, 9:16, 16:9, 21:9
- `--resolution, -r`: 1K (default), 2K, 4K

## Authentication

Uses existing OpenClaw Antigravity OAuth credentials. Make sure you're authenticated:

```bash
openclaw models auth login --provider google-antigravity
```

The script looks for credentials in:
- `~/.openclaw/credentials/google-antigravity.json`
- `~/.config/openclaw/credentials/google-antigravity.json`
- `~/.config/opencode/antigravity-accounts.json`

## Notes

- The script prints a `MEDIA:` line for OpenClaw to auto-attach on supported chat providers.
- Do not read the image back; report the saved path only.
- Uses timestamps in filenames for uniqueness: `yyyy-mm-dd-hh-mm-ss-name.png`
- Falls back to regular Nano Banana if Nano Banana Pro isn't available yet.
