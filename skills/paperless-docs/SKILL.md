---
name: paperless-ngx
description: Manage documents in Paperless-ngx - search, upload, tag, and retrieve.
homepage: https://github.com/paperless-ngx/paperless-ngx
metadata: {"clawdbot":{"requires":{"env":["PAPERLESS_URL","PAPERLESS_TOKEN"]},"primaryEnv":"PAPERLESS_TOKEN"}}
---

# Paperless-ngx

Document management via Paperless-ngx REST API.

## Configuration

Set environment variables in `~/.clawdbot/clawdbot.json`:

```json
{
  "env": {
    "PAPERLESS_URL": "http://your-paperless-host:8000",
    "PAPERLESS_TOKEN": "your-api-token"
  }
}
```

Or configure via the skills entry (allows using `apiKey` shorthand):

```json
{
  "skills": {
    "entries": {
      "paperless-ngx": {
        "env": { "PAPERLESS_URL": "http://your-paperless-host:8000" },
        "apiKey": "your-api-token"
      }
    }
  }
}
```

Get your API token from Paperless web UI: Settings → Users & Groups → [user] → Generate Token.

## Quick Reference

| Task | Command |
|------|---------|
| Search documents | `node {baseDir}/scripts/search.mjs "query"` |
| List recent | `node {baseDir}/scripts/list.mjs [--limit N]` |
| Get document | `node {baseDir}/scripts/get.mjs <id> [--content]` |
| Upload document | `node {baseDir}/scripts/upload.mjs <file> [--title "..."] [--tags "a,b"]` |
| Download PDF | `node {baseDir}/scripts/download.mjs <id> [--output path]` |
| List tags | `node {baseDir}/scripts/tags.mjs` |
| List types | `node {baseDir}/scripts/types.mjs` |
| List correspondents | `node {baseDir}/scripts/correspondents.mjs` |

All scripts are in `{baseDir}/scripts/`.

## Common Workflows

### Find a document

```bash
# Full-text search
node {baseDir}/scripts/search.mjs "electricity bill december"

# Filter by tag
node {baseDir}/scripts/search.mjs --tag "tax-deductible"

# Filter by document type
node {baseDir}/scripts/search.mjs --type "Invoice"

# Filter by correspondent
node {baseDir}/scripts/search.mjs --correspondent "AGL"

# Combine filters
node {baseDir}/scripts/search.mjs "2025" --tag "unpaid" --type "Invoice"
```

### Get document details

```bash
# Metadata only
node {baseDir}/scripts/get.mjs 28

# Include OCR text content
node {baseDir}/scripts/get.mjs 28 --content

# Full content (no truncation)
node {baseDir}/scripts/get.mjs 28 --content --full
```

### Upload a document

```bash
# Basic upload (title auto-detected)
node {baseDir}/scripts/upload.mjs /path/to/invoice.pdf

# With metadata
node {baseDir}/scripts/upload.mjs /path/to/invoice.pdf \
  --title "AGL Electricity Jan 2026" \
  --tags "unpaid,utility" \
  --type "Invoice" \
  --correspondent "AGL" \
  --created "2026-01-15"
```

### Download a document

```bash
# Download to current directory
node {baseDir}/scripts/download.mjs 28

# Specify output path
node {baseDir}/scripts/download.mjs 28 --output ~/Downloads/document.pdf

# Get original (not archived/OCR'd version)
node {baseDir}/scripts/download.mjs 28 --original
```

### Manage metadata

```bash
# List all tags
node {baseDir}/scripts/tags.mjs

# List document types
node {baseDir}/scripts/types.mjs

# List correspondents
node {baseDir}/scripts/correspondents.mjs

# Create new tag
node {baseDir}/scripts/tags.mjs --create "new-tag-name"

# Create new correspondent
node {baseDir}/scripts/correspondents.mjs --create "New Company Name"
```

## Output Format

All scripts output JSON for easy parsing. Use `jq` for formatting:

```bash
node {baseDir}/scripts/search.mjs "invoice" | jq '.results[] | {id, title, created}'
```

## Advanced Usage

For complex queries or bulk operations, see [references/api.md](references/api.md) for direct API access patterns.

## Troubleshooting

**"PAPERLESS_URL not set"** — Add to `~/.clawdbot/clawdbot.json` env section or export in shell.

**"401 Unauthorized"** — Check PAPERLESS_TOKEN is valid. Regenerate in Paperless UI if needed.

**"Connection refused"** — Verify Paperless is running and URL is correct (include port).

**Upload fails silently** — Check Paperless logs; file may be duplicate or unsupported format.
