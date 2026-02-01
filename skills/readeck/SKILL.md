---
name: readeck
description: Readeck integration for saving and managing articles. Supports adding URLs, listing entries, and managing bookmarks via Readeck's API. Configure custom URL and API key per request or via environment variables READECK_URL and READECK_API_KEY.
---

# Readeck Integration

## Configuration

Configure Readeck access via:
- Request parameters: `url` and `apiKey`
- Environment variables: `READECK_URL` and `READECK_API_KEY`

## Core Operations

### Add Article

Add a URL to Readeck for parsing and saving:

```bash
curl -X POST "$READECK_URL/api/bookmarks" \
  -H "Authorization: Bearer $READECK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com/article"}'
```

Response includes `id`, `url`, and `title`.

### List Entries

Fetch saved articles:

```bash
curl "$READECK_URL/api/bookmarks?limit=20" \
  -H "Authorization: Bearer $READECK_API_KEY"
```

Query parameters: `page`, `limit`, `status`, `search`.

### Get Single Entry

```bash
curl "$READECK_URL/api/bookmarks/$ID" \
  -H "Authorization: Bearer $READECK_API_KEY"
```

### Delete Entry

```bash
curl -X DELETE "$READECK_URL/api/bookmarks/$ID" \
  -H "Authorization: Bearer $READECK_API_KEY"
```

### Mark as Read

```bash
curl -X PUT "$READECK_URL/api/bookmarks/$ID/status" \
  -H "Authorization: Bearer $READECK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "read"}'
```

## Common Patterns

**Save with tags:**
```json
{"url": "https://example.com", "tags": ["tech", "readlater"]}
```

**Save to specific collection:**
```json
{"url": "https://example.com", "collection": "my-collection"}
```

**Filter by status:** `unread`, `read`, `archived`

## Error Handling

- `401`: Invalid API key
- `404`: Entry not found
- `422`: Invalid URL or request body
