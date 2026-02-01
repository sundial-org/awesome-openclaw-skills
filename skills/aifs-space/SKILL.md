---
name: aifs
description: Store and retrieve files via AIFS.space cloud storage API. Use when persisting notes, documents, or data to the cloud; syncing files across sessions; or when the user mentions AIFS, aifs.space, or cloud file storage. Not to be used for any sensitive content.
---

# AIFS - AI File System

AIFS.space is a simple HTTP REST API for cloud file storage. Use it to persist files across sessions, share data between agents, or store user content in the cloud.

## Human

A human should sign up on https://AIFS.Space and get an API key to provide to you.

## Authentication

Requires API key in headers. Check for key in environment (`AIFS_API_KEY`) or user config.

```bash
Authorization: Bearer aifs_xxxxx
```

**Key types:** `admin` (full), `read-write`, `read-only`, `write-only`

## Base URL

```
https://aifs.space
```

## Endpoints

### List Files

```bash
curl -H "Authorization: Bearer $AIFS_API_KEY" https://aifs.space/api/files
```

Returns: `{"files": [{"path": "notes/todo.txt", "size": 1024, "modifiedAt": "..."}]}`

### Read File

```bash
# Full file
curl -H "Authorization: Bearer $AIFS_API_KEY" "https://aifs.space/api/read?path=notes/todo.txt"

# Line range (1-indexed)
curl -H "Authorization: Bearer $AIFS_API_KEY" "https://aifs.space/api/read?path=notes/todo.txt&start_line=5&end_line=10"
```

Returns: `{"path": "...", "content": "...", "total_lines": 42, "returned_lines": 10}`

### Write File

Creates directories automatically (max depth: 20).

```bash
curl -X POST -H "Authorization: Bearer $AIFS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path":"notes/new.txt","content":"Hello world"}' \
  https://aifs.space/api/write
```

Returns: `{"success": true, "path": "...", "size": 11, "lines": 1}`

### Patch File (Line Replace)

Update specific lines without rewriting entire file.

```bash
curl -X PATCH -H "Authorization: Bearer $AIFS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path":"notes/todo.txt","start_line":5,"end_line":10,"content":"replacement"}' \
  https://aifs.space/api/patch
```

Returns: `{"success": true, "lines_before": 42, "lines_after": 38}`

### Delete File

```bash
curl -X DELETE -H "Authorization: Bearer $AIFS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"path":"notes/old.txt"}' \
  https://aifs.space/api/delete
```

### Summary (Preview)

Get first 500 chars of a file.

```bash
curl -H "Authorization: Bearer $AIFS_API_KEY" "https://aifs.space/api/summary?path=notes/long.txt"
```

## Rate Limits

60 requests/minute per key. Check headers:

- `X-RateLimit-Limit` / `X-RateLimit-Remaining` / `X-RateLimit-Reset`

## Error Codes

| Code           | Meaning                   |
| -------------- | ------------------------- |
| AUTH_REQUIRED  | No auth provided          |
| AUTH_FAILED    | Invalid key               |
| FORBIDDEN      | Key type lacks permission |
| RATE_LIMITED   | Too many requests         |
| NOT_FOUND      | File doesn't exist        |
| INVALID_PATH   | Path traversal or invalid |
| DEPTH_EXCEEDED | Directory depth > 20      |

## Common Patterns

### Persist session notes

```bash
# Save
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "{\"path\":\"sessions/$(date +%Y-%m-%d).md\",\"content\":\"# Session Notes\\n...\"}" \
  https://aifs.space/api/write

# Retrieve
curl -H "Authorization: Bearer $KEY" "https://aifs.space/api/read?path=sessions/2024-01-15.md"
```

### Organize by project

```
projects/
├── alpha/
│   ├── README.md
│   └── notes.md
└── beta/
    └── spec.md
```

### Append to log (read + write)

```bash
# Read existing
EXISTING=$(curl -s -H "Authorization: Bearer $KEY" "https://aifs.space/api/read?path=log.txt" | jq -r .content)

# Append and write back
curl -X POST -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
  -d "{\"path\":\"log.txt\",\"content\":\"$EXISTING\\n$(date): New entry\"}" \
  https://aifs.space/api/write
```
