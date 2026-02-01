---
name: better-notion
description: Full CRUD for Notion pages, databases, and blocks. Create, read, update, delete, search, and query.
metadata: {"clawdbot":{"emoji":"📝"}}
---

# Notion

Use the Notion API for pages, data sources (databases), and blocks.

## Setup

```bash
mkdir -p ~/.config/notion
echo "ntn_your_key_here" > ~/.config/notion/api_key
```

Share target pages/databases with your integration in Notion UI.

## API Basics

```bash
NOTION_KEY=$(cat ~/.config/notion/api_key)
curl -X POST "https://api.notion.com/v1/..." \
  -H "Authorization: Bearer $NOTION_KEY" \
  -H "Notion-Version: 2025-09-03" \
  -H "Content-Type: application/json"
```

## Common Operations

```bash
# Search
curl -X POST "https://api.notion.com/v1/search" -d '{"query": "title"}'

# Get page
curl "https://api.notion.com/v1/pages/{page_id}"

# Get page blocks
curl "https://api.notion.com/v1/blocks/{page_id}/children"

# Create page in database
curl -X POST "https://api.notion.com/v1/pages" -d '{
  "parent": {"data_source_id": "xxx"},
  "properties": {"Name": {"title": [{"text": {"content": "Item"}}]}}
}'

# Query database
curl -X POST "https://api.notion.com/v1/data_sources/{id}/query" -d '{
  "filter": {"property": "Status", "select": {"equals": "Active"}}
}'

# Update page
curl -X PATCH "https://api.notion.com/v1/pages/{page_id}" -d '{
  "properties": {"Status": {"select": {"name": "Done"}}}
}'

# Add blocks
curl -X PATCH "https://api.notion.com/v1/blocks/{page_id}/children" -d '{
  "children": [{"type": "paragraph", "paragraph": {"rich_text": [{"text": {"content": "Text"}}]}}]
}'

# Delete page or block (moves to trash)
curl -X DELETE "https://api.notion.com/v1/blocks/{block_id}"

# Restore from trash (set archived to false)
curl -X PATCH "https://api.notion.com/v1/blocks/{block_id}" -d '{"archived": false}'
```

## Property Types

| Type | Format |
|------|--------|
| Title | `{"title": [{"text": {"content": "..."}}]}` |
| Text | `{"rich_text": [{"text": {"content": "..."}}]}` |
| Select | `{"select": {"name": "Option"}}` |
| Multi-select | `{"multi_select": [{"name": "A"}]}` |
| Date | `{"date": {"start": "2024-01-15"}}` |
| Checkbox | `{"checkbox": true}` |
| Number | `{"number": 42}` |
| URL | `{"url": "https://..."}` |

## 2025-09-03 API Notes

- Databases = "data sources" in API
- Use `data_source_id` for both creating pages and querying
- Get `data_source_id` from search results (the `id` field)
- Rate limit: ~3 req/sec
