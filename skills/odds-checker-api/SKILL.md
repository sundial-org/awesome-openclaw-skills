---
name: odds-api-io
description: Query Odds-API.io for sports events, bookmakers, and betting odds (e.g., "what are the odds for Inter vs Arsenal", "get odds for Paddy the Baddie vs Gaethje"). Use when you need to call the Odds-API.io v3 API or interpret its responses; requires a user-provided API key.
---

# Odds-API.io

## Overview
Use Odds-API.io to search events and fetch odds by event ID. This skill includes a small CLI helper and a concise endpoint reference.

## Quick workflow
1. Provide the API key via `ODDS_API_KEY` or `--api-key` (never store it in this skill).
2. Find sports and bookmakers if needed.
3. Search for the event to get its ID.
4. Fetch odds for the event with a bookmaker list.

```bash
# 1) List sports and bookmakers
python3 odds-api-io/scripts/odds_api.py sports
python3 odds-api-io/scripts/odds_api.py bookmakers

# 2) Search for an event
python3 odds-api-io/scripts/odds_api.py search --query "Inter vs Arsenal" --sport football

# 3) Fetch odds for the chosen event ID
python3 odds-api-io/scripts/odds_api.py odds --event-id 123456 --bookmakers "Bet365,Unibet"

# Optional: one-step search + odds
python3 odds-api-io/scripts/odds_api.py matchup --query "Inter vs Arsenal" --sport football --bookmakers "Bet365,Unibet"
```

## CLI helper
Use `scripts/odds_api.py` for API calls. Pass global flags like `--api-key` and `--dry-run` before the subcommand. Prefer `--dry-run` to preview the URL when testing without a key. Use `--summary` on `odds` or `matchup` for a compact output.

## Reference material
Load `references/odds-api-reference.md` for base URL, endpoint summaries, and response fields.
