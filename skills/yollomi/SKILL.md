---
name: yollomi-ai-api
description: Generate AI images and videos using Yollomi API. Use when the user wants to create images from text, remove image backgrounds, or generate AI videos. Requires YOLLOMI_API_KEY and optionally YOLLOMI_BASE_URL.
---

# Yollomi AI API Skill

Generates images and videos via the Yollomi API. All models use a **single unified endpoint** with different `modelId` parameters.

## Setup

1. **API Key**: User must provide `YOLLOMI_API_KEY` (env var, .env file, or Cursor rule).
2. **Base URL** (optional): `YOLLOMI_BASE_URL` defaults to `https://yollomi.com`.

## Unified Endpoint

```
POST /api/v1/generate
```

**Headers**: `Authorization: Bearer ${YOLLOMI_API_KEY}` or `X-API-Key: ${YOLLOMI_API_KEY}`  
**Content-Type**: `application/json`

**Body**:
- `type` (required): `"image"` or `"video"`
- `modelId` (required): Model identifier
- Additional params depend on model (prompt, imageUrl, etc.)

**Response (image)**: `{ images: string[], remainingCredits: number }`  
**Response (video)**: `{ video: string, remainingCredits: number }`

## List Models

```
GET /api/v1/models
```

Returns all available image and video modelIds.

## Common Examples

**Generate image (Flux)**:
```bash
curl -X POST "${YOLLOMI_BASE_URL:-https://yollomi.com}/api/v1/generate" \
  -H "Authorization: Bearer $YOLLOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"image","modelId":"flux","prompt":"A cat in a hat","aspectRatio":"1:1"}'
```

**Remove background**:
```bash
curl -X POST "${YOLLOMI_BASE_URL:-https://yollomi.com}/api/v1/generate" \
  -H "Authorization: Bearer $YOLLOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"image","modelId":"remove-bg","imageUrl":"https://example.com/photo.jpg"}'
```

**Generate video**:
```bash
curl -X POST "${YOLLOMI_BASE_URL:-https://yollomi.com}/api/v1/generate" \
  -H "Authorization: Bearer $YOLLOMI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"type":"video","modelId":"kling-2-1","prompt":"A cat walking in the rain"}'
```

## Aspect Ratio (aspectRatio)

文生图类模型支持的比例参数：

| 比例 | 说明 |
|------|------|
| 1:1 | 正方形（默认） |
| 16:9 | 横屏 |
| 9:16 | 竖屏 |

## Image ModelIds

| modelId | Credits | Required | aspectRatio |
|---------|---------|----------|-------------|
| flux | 4/img | prompt | 1:1, 16:9, 9:16 |
| flux-schnell | 2/img | prompt | 同上 |
| flux-2-pro | 15/img | prompt | 同上 |
| remove-bg | 0 | imageUrl | - |
| nano-banana | 4 | prompt | 1:1, 16:9, 9:16 |
| nano-banana-pro | 15 | prompt | 同上 |
| flux-kontext-pro | 4 | prompt | 同上 |
| z-image-turbo | 1 | prompt | width, height |
| imagen-4-ultra | 6 | prompt | 同上 |
| image-4-fast | 3 | prompt | 同上 |
| ideogram-v3-turbo | 3 | prompt | 同上 |
| stable-diffusion-3-5-large | 7/img | prompt | 同上 |
| seedream-4-5 | 4 | prompt | 同上 |
| object-remover | 3 | image, mask | - |
| face-swap | 3 | swapImage, inputImage | - |
| image-upscaler | 1 | imageUrl, scale | - |
| photo-restoration | 4 | imageUrl | - |
| qwen-image-edit | 3 | image, prompt | - |
| qwen-image-edit-plus | 3 | image, prompt | - |
| virtual-try-on | 3 | clothImage, personImage | - |
| ai-background-generator | 5 | imageUrl | prompt |

## Video ModelIds

| modelId | Credits |
|---------|---------|
| openai-sora-2 | ~50+ |
| google-veo-3 | 10 |
| google-veo-3-fast | 9 |
| google-veo-3-1 | 10 |
| google-veo-3-2 | 10 |
| google-veo-3-1-fast | 9 |
| kling-2-1 | 9 |
| kling-v2-6-motion-control | 7/sec |
| minimax-hailuo-2-3 | 9 |
| minimax-hailuo-2-3-fast | 9 |
| bytedance-seedance-1-pro-fast | 8 |
| runway-gen4-turbo | varies |
| pixverse-5 | 9 |
| wan-2-5-i2v | 9 |
| wan-2-5-t2v | 9 |
| wan-2-6-i2v | 29 |
| wan-2-6-t2v | 29 |

## Workflow

1. **Generate image** → POST /api/v1/generate with `type: "image"`, `modelId`, and model params
2. **Generate video** → POST /api/v1/generate with `type: "video"`, `modelId`, `prompt`, optional `inputs`
3. **List models** → GET /api/v1/models
4. **401/402** → Check API key and credits

## Reference

Full model list and params: [models-reference.md](models-reference.md) or GET /api/v1/models
