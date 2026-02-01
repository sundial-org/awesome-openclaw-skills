# Meshy API notes (for this skill)

Docs: <https://docs.meshy.ai/en>

## Auth

- Header: `Authorization: Bearer $MESHY_API_KEY`

## Base URL

- Default assumed: `https://api.meshy.ai`
- Override with env: `MESHY_BASE_URL`

## Endpoints used

### Text → 2D (Text to Image)

- Create: `POST /openapi/v1/text-to-image`
- Get: `GET /openapi/v1/text-to-image/{id}`
- Result: `image_urls: string[]`

### Image → 3D

- Create: `POST /openapi/v1/image-to-3d`
- Get: `GET /openapi/v1/image-to-3d/{id}`
- Result: `model_urls.obj` (and sometimes `model_urls.mtl`)

## Status polling

Poll until `status` is one of: `SUCCEEDED | FAILED | CANCELED`.
