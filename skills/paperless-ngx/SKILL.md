---
name: paperless-ngx
description: Interact with Paperless-ngx document management system via REST API. Use when users want to search, upload, download, organize documents, manage tags, correspondents, or document types in their Paperless-ngx instance.
---

# Paperless-ngx Skill

Manage documents in Paperless-ngx via its REST API using HTTP requests.

## Configuration

Requires environment variables:
- `PAPERLESS_URL`: Base URL (e.g., `https://paperless.example.com`)
- `PAPERLESS_TOKEN`: API token from Paperless-ngx settings

## Authentication

Include token in all requests:
```
Authorization: Token $PAPERLESS_TOKEN
```

## Core Operations

### Search Documents

```bash
curl -s "$PAPERLESS_URL/api/documents/?query=invoice" \
  -H "Authorization: Token $PAPERLESS_TOKEN"
```

Filter options: `correspondent__id`, `document_type__id`, `tags__id__in`, `created__date__gte`, `created__date__lte`, `added__date__gte`.

### Get Document Details

```bash
curl -s "$PAPERLESS_URL/api/documents/{id}/" \
  -H "Authorization: Token $PAPERLESS_TOKEN"
```

### Download Document

```bash
# Original file
curl -s "$PAPERLESS_URL/api/documents/{id}/download/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" -o document.pdf

# Archived (OCR'd) version
curl -s "$PAPERLESS_URL/api/documents/{id}/download/?original=false" \
  -H "Authorization: Token $PAPERLESS_TOKEN" -o document.pdf
```

### Upload Document

```bash
curl -s "$PAPERLESS_URL/api/documents/post_document/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -F "document=@/path/to/file.pdf" \
  -F "title=Document Title" \
  -F "correspondent=1" \
  -F "document_type=2" \
  -F "tags=3" \
  -F "tags=4"
```

Optional fields: `title`, `created`, `correspondent`, `document_type`, `storage_path`, `tags` (repeatable), `archive_serial_number`, `custom_fields`.

### Update Document Metadata

```bash
curl -s -X PATCH "$PAPERLESS_URL/api/documents/{id}/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title", "correspondent": 1, "tags": [1, 2]}'
```

### Delete Document

```bash
curl -s -X DELETE "$PAPERLESS_URL/api/documents/{id}/" \
  -H "Authorization: Token $PAPERLESS_TOKEN"
```

## Organization Endpoints

### Tags

```bash
# List tags
curl -s "$PAPERLESS_URL/api/tags/" -H "Authorization: Token $PAPERLESS_TOKEN"

# Create tag
curl -s -X POST "$PAPERLESS_URL/api/tags/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Important", "color": "#ff0000"}'
```

### Correspondents

```bash
# List correspondents
curl -s "$PAPERLESS_URL/api/correspondents/" -H "Authorization: Token $PAPERLESS_TOKEN"

# Create correspondent
curl -s -X POST "$PAPERLESS_URL/api/correspondents/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "ACME Corp"}'
```

### Document Types

```bash
# List document types
curl -s "$PAPERLESS_URL/api/document_types/" -H "Authorization: Token $PAPERLESS_TOKEN"

# Create document type
curl -s -X POST "$PAPERLESS_URL/api/document_types/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"name": "Invoice"}'
```

## Bulk Operations

```bash
curl -s -X POST "$PAPERLESS_URL/api/documents/bulk_edit/" \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [1, 2, 3],
    "method": "add_tag",
    "parameters": {"tag": 5}
  }'
```

Methods: `set_correspondent`, `set_document_type`, `add_tag`, `remove_tag`, `delete`, `reprocess`.

## Task Status

After upload, check task status:
```bash
curl -s "$PAPERLESS_URL/api/tasks/?task_id={uuid}" \
  -H "Authorization: Token $PAPERLESS_TOKEN"
```

## Response Handling

- List endpoints return `{"count": N, "results": [...]}` with pagination
- Single objects return the object directly
- Use `?page=2` for pagination
- Add `?ordering=-created` for sorting (prefix `-` for descending)
