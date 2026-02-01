# Canva Connect API Reference

Base URL: `https://api.canva.com/rest`

## Authentication

All requests require OAuth 2.0 Bearer token:
```
Authorization: Bearer <access_token>
```

## Endpoints

### User Profile
```
GET /v1/users/me
```
Returns current user's profile (display name, team, etc.)

### Designs

#### List Designs
```
GET /v1/designs
```
Query params: `ownership` (owned|shared), `limit`, `continuation`

#### Get Design
```
GET /v1/designs/{designId}
```

#### Create Design
```
POST /v1/designs
```
Body:
```json
{
  "design_type": "doc|presentation|whiteboard|poster|...",
  "title": "Design Title"
}
```

Design types:
- `doc` - Document
- `presentation` - Presentation
- `whiteboard` - Whiteboard
- `poster` - Poster
- `instagram_post` - Instagram Post (1080x1080)
- `instagram_story` - Instagram Story (1080x1920)
- `facebook_post` - Facebook Post
- `video` - Video
- `logo` - Logo
- `flyer` - Flyer
- `banner` - Banner

#### Delete Design
```
DELETE /v1/designs/{designId}
```

### Export

#### Create Export Job
```
POST /v1/exports
```
Body:
```json
{
  "design_id": "DAFxxx...",
  "format": {
    "type": "pdf|png|jpg|gif|pptx|mp4",
    "quality": "regular|high",
    "size": "original|a4|letter"
  },
  "pages": [1, 2, 3]  // optional, specific pages
}
```

#### Get Export Status
```
GET /v1/exports/{jobId}
```
Response includes `job.status` (in_progress|success|failed) and `job.result.urls[]` when complete.

### Assets

#### List Assets
```
GET /v1/assets
```

#### Get Asset
```
GET /v1/assets/{assetId}
```

#### Upload Asset
```
POST /v1/asset-uploads
```
Headers:
- `Content-Type: application/octet-stream`
- `Asset-Upload-Metadata: {"name_base64": "<base64-encoded-name>"}`

Body: Binary file content

Supported formats: PNG, JPG, GIF, SVG, PDF, MP4, MOV, WEBM

#### Update Asset
```
PATCH /v1/assets/{assetId}
```
Body:
```json
{
  "name": "New Name",
  "tags": ["tag1", "tag2"]
}
```

#### Delete Asset
```
DELETE /v1/assets/{assetId}
```

### Brand Templates

#### List Templates
```
GET /v1/brand-templates
```
Query params: `limit`, `continuation`, `dataset` (owned|shared)

#### Get Template
```
GET /v1/brand-templates/{templateId}
```

#### Get Template Dataset
```
GET /v1/brand-templates/{templateId}/dataset
```
Returns the data fields available for autofill.

### Autofill

#### Create Autofill Job
```
POST /v1/autofills
```
Body:
```json
{
  "brand_template_id": "DAFxxx...",
  "title": "Filled Design",
  "data": {
    "field_name": {
      "type": "text",
      "text": "Value"
    },
    "image_field": {
      "type": "image",
      "asset_id": "asset_id_here"
    }
  }
}
```

#### Get Autofill Status
```
GET /v1/autofills/{jobId}
```

### Folders

#### List Folders
```
GET /v1/folders
```

#### Get Folder Items
```
GET /v1/folders/{folderId}/items
```

#### Create Folder
```
POST /v1/folders
```
Body:
```json
{
  "name": "Folder Name",
  "parent_folder_id": "optional_parent_id"
}
```

#### Move Item to Folder
```
POST /v1/folders/{folderId}/items
```
Body:
```json
{
  "item_id": "design_or_asset_id",
  "item_type": "design|asset"
}
```

### Comments

#### List Comments
```
GET /v1/designs/{designId}/comments
```

#### Create Comment
```
POST /v1/designs/{designId}/comments
```
Body:
```json
{
  "message": "Comment text",
  "attached_to": {
    "type": "design|element",
    "element_id": "optional_element_id"
  }
}
```

## Rate Limits

Per-endpoint limits (requests per minute per user):

| Endpoint | Limit |
|----------|-------|
| GET endpoints | 100 |
| POST/PATCH endpoints | 30 |
| DELETE endpoints | 30 |
| Asset uploads | 10 |
| Export jobs | 10 |

## Error Responses

```json
{
  "error": {
    "code": "error_code",
    "message": "Human readable message"
  }
}
```

Common error codes:
- `invalid_token` - Token expired or invalid
- `insufficient_scopes` - Missing required scope
- `not_found` - Resource not found
- `rate_limited` - Too many requests
- `invalid_request` - Malformed request

## Webhooks (Advanced)

Canva supports webhooks for design events. Configure in Developer Portal.

Events:
- `design.publish` - Design published
- `design.export.complete` - Export finished
- `comment.create` - New comment added
