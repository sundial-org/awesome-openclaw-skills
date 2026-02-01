---
name: wallapop-cli
description: Use the wallapop CLI to search listings, fetch item details, view user profiles, and list categories. Apply when a user asks for Wallapop marketplace data or when you need CLI commands and flags for wallapop-cli usage.
compatibility: Requires wallapop-cli installed (Node.js 18+), network access to api.wallapop.com, and optional WALLAPOP_ACCESS_TOKEN for non-search endpoints.
---

## Purpose
Provide concise, correct commands for using wallapop-cli.

## When to use
- User asks how to search Wallapop listings from the terminal.
- User needs CLI flags for filtering search (price, location, category, limit).
- User needs item or user lookup commands.
- User needs JSON output for scripting.

## Commands
### Search listings
```
wallapop search "<query>" [--lat <lat>] [--lng <lng>] [--min-price <n>] [--max-price <n>] [--category <id>] [--limit <n>]
```
Notes:
- Defaults to configured location if `--lat/--lng` omitted.
- `--limit` trims results locally.

### Item details
```
wallapop item <item_id>
```

### User profile
```
wallapop user <user_id>
```

### Categories
```
wallapop categories
```

### JSON output (all commands)
Add the global flag `--json`:
```
wallapop --json search "laptop"
wallapop --json item abc123
```

## Configuration
- Location defaults can be set via env vars:
  - `WALLAPOP_LAT`
  - `WALLAPOP_LNG`
- Optional auth token for non-search endpoints:
  - `WALLAPOP_ACCESS_TOKEN`

## Output expectations
- Search: table or JSON array of results with id, title, price, distance, and user.
- Item: table or JSON with title, description, taxonomy, user, images.
- User: table or JSON with profile fields.
- Categories: table or JSON list of category ids and names.

## Examples (safe placeholders)
```
wallapop search "camera" --min-price 50 --max-price 200
wallapop search "chair" --lat 40.0 --lng -3.0 --limit 5
wallapop item abc123
wallapop user user123
wallapop --json categories
```

## Error handling
- Non-zero exit code on failure.
- For scripted use, prefer `--json` and handle errors by checking exit code.
