# Paperless-ngx API Reference

Direct API access for advanced operations not covered by the convenience scripts.

## Authentication

All requests require the `Authorization` header:

```
Authorization: Token YOUR_API_TOKEN
```

## Base URL

```
${PAPERLESS_URL}/api/
```

## Core Endpoints

### Documents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/documents/` | List documents (paginated) |
| GET | `/api/documents/{id}/` | Get document details |
| POST | `/api/documents/post_document/` | Upload new document |
| PATCH | `/api/documents/{id}/` | Update document metadata |
| DELETE | `/api/documents/{id}/` | Delete document |
| GET | `/api/documents/{id}/download/` | Download archived PDF |
| GET | `/api/documents/{id}/original/` | Download original file |
| GET | `/api/documents/{id}/preview/` | Get document preview |
| GET | `/api/documents/{id}/thumb/` | Get thumbnail |

### Query Parameters for Documents

| Parameter | Description | Example |
|-----------|-------------|---------|
| `query` | Full-text search | `?query=invoice electricity` |
| `tags__id__in` | Filter by tag IDs (comma-sep) | `?tags__id__in=1,2,3` |
| `document_type__id` | Filter by type ID | `?document_type__id=2` |
| `correspondent__id` | Filter by correspondent ID | `?correspondent__id=5` |
| `created__date__gte` | Created on or after | `?created__date__gte=2025-01-01` |
| `created__date__lte` | Created on or before | `?created__date__lte=2025-12-31` |
| `added__date__gte` | Added on or after | `?added__date__gte=2025-01-01` |
| `ordering` | Sort field (prefix `-` for desc) | `?ordering=-created` |
| `page_size` | Results per page | `?page_size=25` |
| `page` | Page number | `?page=2` |

### Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/tags/` | List all tags |
| POST | `/api/tags/` | Create tag |
| GET | `/api/tags/{id}/` | Get tag details |
| PATCH | `/api/tags/{id}/` | Update tag |
| DELETE | `/api/tags/{id}/` | Delete tag |

### Document Types

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/document_types/` | List all types |
| POST | `/api/document_types/` | Create type |
| GET | `/api/document_types/{id}/` | Get type details |
| PATCH | `/api/document_types/{id}/` | Update type |
| DELETE | `/api/document_types/{id}/` | Delete type |

### Correspondents

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/correspondents/` | List all correspondents |
| POST | `/api/correspondents/` | Create correspondent |
| GET | `/api/correspondents/{id}/` | Get correspondent details |
| PATCH | `/api/correspondents/{id}/` | Update correspondent |
| DELETE | `/api/correspondents/{id}/` | Delete correspondent |

### Mail

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/mail_accounts/` | List email accounts |
| GET | `/api/mail_rules/` | List mail rules |
| POST | `/api/mail_accounts/{id}/test/` | Test email connection |

### Saved Views

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/saved_views/` | List saved views |
| POST | `/api/saved_views/` | Create saved view |

## Examples

### Update document metadata

```bash
curl -X PATCH \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Title", "correspondent": 5, "tags": [1, 2]}' \
  "$PAPERLESS_URL/api/documents/28/"
```

### Bulk edit documents

```bash
curl -X POST \
  -H "Authorization: Token $PAPERLESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"documents": [1, 2, 3], "method": "modify_tags", "parameters": {"add_tags": [5]}}' \
  "$PAPERLESS_URL/api/documents/bulk_edit/"
```

### Search with date range

```bash
curl -H "Authorization: Token $PAPERLESS_TOKEN" \
  "$PAPERLESS_URL/api/documents/?query=invoice&created__date__gte=2025-01-01&created__date__lte=2025-12-31"
```

### Get document statistics

```bash
curl -H "Authorization: Token $PAPERLESS_TOKEN" \
  "$PAPERLESS_URL/api/statistics/"
```

## Response Format

All endpoints return JSON. List endpoints use pagination:

```json
{
  "count": 100,
  "next": "http://host/api/documents/?page=2",
  "previous": null,
  "all": [1, 2, 3, ...],
  "results": [...]
}
```

## Error Handling

| Status | Meaning |
|--------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad request (validation error) |
| 401 | Unauthorized (bad/missing token) |
| 404 | Not found |
| 500 | Server error |

Error responses include a message:

```json
{
  "detail": "Error description"
}
```
