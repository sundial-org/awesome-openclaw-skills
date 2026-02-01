---
name: polymarket
description: Query Polymarket prediction markets - check odds, trending markets, search events, track prices.
homepage: https://polymarket.com
metadata: {"clawdbot":{"emoji":"📊"}}
---

# Polymarket

Query [Polymarket](https://polymarket.com) prediction markets. Check odds, find trending markets, search events.

## Commands

```bash
# Trending/active markets
python3 {baseDir}/scripts/polymarket.py trending

# Search markets
python3 {baseDir}/scripts/polymarket.py search "trump"
python3 {baseDir}/scripts/polymarket.py search "bitcoin"

# Get specific market by slug
python3 {baseDir}/scripts/polymarket.py event "fed-decision-in-october"

# Get markets by category
python3 {baseDir}/scripts/polymarket.py category politics
python3 {baseDir}/scripts/polymarket.py category crypto
python3 {baseDir}/scripts/polymarket.py category sports
```

## Example Chat Usage

- "What are the odds Trump wins 2028?"
- "Trending on Polymarket?"
- "Search Polymarket for Bitcoin"
- "What's the spread on the Fed rate decision?"
- "Any interesting crypto markets?"

## Output

Markets show:
- Question/title
- Current odds (Yes/No prices)
- Volume
- End date

## API

Uses the public Gamma API (no auth required for reading):
- Base URL: `https://gamma-api.polymarket.com`
- Docs: https://docs.polymarket.com

## Note

This is read-only. Trading requires wallet authentication (not implemented).
