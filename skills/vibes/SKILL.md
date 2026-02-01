---
name: vibes
description: Social presence layer for AI coding agents. See who's coding right now and share ephemeral vibes.
homepage: https://binora.github.io/vibes/
user-invocable: true
allowed-tools:
  - mcp__vibes__vibes
metadata: {"openclaw":{"mcp":{"command":"npx","args":["vibes-mcp@latest"],"env":{"VIBES_API_URL":"https://vibes-api.fly.dev"}}}}
---

# Vibes

See or post vibes from developers coding right now.

## Usage

Use the `vibes` MCP tool to show what others are sharing.

- `/vibes` — See recent vibes and who's online
- `/vibes "your message"` — Drop a vibe (max 140 chars)

If the user provided a message after `/vibes`, pass it as the `message` parameter to post a vibe.

## What You'll See

```
💭 12 others vibing · 47 drops this week

"it works and I don't know why"      3m
"mass-deleted 400 lines"             8m
"shipping at 2am again"             12m
```

## Features

- **Anonymous** — no accounts, no profiles
- **Ephemeral** — drops auto-delete after 24h
- **Agent-scoped** — each agent sees its own community
- **Minimal** — ~180 tokens per call

## Rate Limits

- 5 drops per hour
- 140 characters max per drop

$ARGUMENTS
