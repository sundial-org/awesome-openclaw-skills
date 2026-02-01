---
name: miniflux-news
description: Fetch and triage the latest unread RSS/news entries from a Miniflux instance via its REST API using an API token. Use when the user asks to get the latest Miniflux unread items, list recent entries with titles/links, or generate short summaries of specific Miniflux entries. Includes a bundled script to query Miniflux (/v1/entries and /v1/entries/{id}) using credentials from ~/.config/clawdbot/miniflux-news.json (or MINIFLUX_URL and MINIFLUX_TOKEN overrides).
---

# Miniflux News

Use the bundled script to fetch entries, then format a clean list and optionally write summaries.

## Setup (credentials)

This skill reads Miniflux credentials from a local config file by default.

### Config file (recommended)

Path:
- `~/.config/clawdbot/miniflux-news.json`

Format:
```json
{
  "url": "https://your-miniflux.example",
  "token": "<api-token>"
}
```

Create/update it using the script:

```bash
python3 skills/miniflux-news/scripts/miniflux.py configure \
  --url "https://your-miniflux.example" \
  --token "<api-token>"
```

### Environment variables (override)

You can override the config file (useful for CI):

```bash
export MINIFLUX_URL="https://your-miniflux.example"
export MINIFLUX_TOKEN="<api-token>"
```

Token scope: Miniflux API token with read access.

## Fetch latest entries

List latest unread items (default):

```bash
python3 skills/miniflux-news/scripts/miniflux.py entries --limit 20
```

Filter by category (by name):

```bash
python3 skills/miniflux-news/scripts/miniflux.py entries --category "News" --limit 20
```

If you need machine-readable output:

```bash
python3 skills/miniflux-news/scripts/miniflux.py entries --limit 50 --json
```

### Response formatting

- Return a tight bullet list: **[id] title — feed** + link.
- Ask how many the user wants summarized (e.g., “summarize 3” or “summarize ids 123,124”).

## View full content

Show the full article content stored in Miniflux (useful for reading or for better summaries):

```bash
python3 skills/miniflux-news/scripts/miniflux.py entry 123 --full --format text
```

If you want the raw HTML as stored by Miniflux:

```bash
python3 skills/miniflux-news/scripts/miniflux.py entry 123 --full --format html
```

## Categories

List categories:

```bash
python3 skills/miniflux-news/scripts/miniflux.py categories
```

## Mark entries as read (explicit only)

This skill **must never** mark anything as read implicitly. Only do it when the user explicitly asks to mark specific ids as read.

Mark specific ids as read:

```bash
python3 skills/miniflux-news/scripts/miniflux.py mark-read 123 124 --confirm
```

Mark all unread entries in a category as read (still explicit, requires `--confirm`; includes a safety `--limit`):

```bash
python3 skills/miniflux-news/scripts/miniflux.py mark-read-category "News" --confirm --limit 500
```

## Summarize entries

Fetch full content for a specific entry id (machine-readable):

```bash
python3 skills/miniflux-news/scripts/miniflux.py entry 123 --json
```

Summarization rules:
- Prefer 3–6 bullets max.
- Lead with the “so what” in 1 sentence.
- If content is empty or truncated, say so and summarize from title + available snippet.
- Don’t invent facts; quote key numbers/names if present.

## Troubleshooting

- If the script says missing credentials: set `MINIFLUX_URL`/`MINIFLUX_TOKEN` or create `~/.config/clawdbot/miniflux-news.json`.
- If you get HTTP 401: token is wrong/expired.
- If you get HTTP 404: base URL is wrong (should be the Miniflux web root).
