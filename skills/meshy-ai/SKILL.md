---
name: meshy-ai
description: "Use the Meshy.ai REST API to generate assets: (1) text-to-2d (Meshy Text to Image) and (2) image-to-3d, then download outputs locally. Use when the user wants Meshy generations, needs polling async tasks, and especially when they want the resulting OBJ saved to disk. Requires MESHY_API_KEY in the environment."
---

# Meshy.ai

Generate Meshy assets via API and save outputs locally.

## Setup

- Add env var: `MESHY_API_KEY=msy-...`
- Optional: `MESHY_BASE_URL` (defaults to `https://api.meshy.ai`)

## Text → 2D (Text to Image)

Use `scripts/text_to_image.py`.

```bash
python3 skills/public/meshy-ai/scripts/text_to_image.py \
  --prompt "a cute robot mascot, flat vector style" \
  --out-dir ./meshy-out
```

- Downloads one or more images (if multi-view) into `./meshy-out/text-to-image_<taskId>_<slug>/`.

## Image → 3D (always save OBJ)

Use `scripts/image_to_3d_obj.py`.

### Local image

```bash
python3 skills/public/meshy-ai/scripts/image_to_3d_obj.py \
  --image ./input.png \
  --out-dir ./meshy-out
```

### Public URL

```bash
python3 skills/public/meshy-ai/scripts/image_to_3d_obj.py \
  --image-url "https://.../input.png" \
  --out-dir ./meshy-out
```

- Always downloads `model.obj` (and `model.mtl` if provided by Meshy) into `./meshy-out/image-to-3d_<taskId>_<slug>/`.

## Notes

- Meshy tasks are async: create → poll until `status=SUCCEEDED` → download URLs.
- API reference for this skill: `references/api-notes.md`.
