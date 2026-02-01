---
name: Better Polymarket
description: Query Polymarket prediction markets - check odds, trending markets, search events, track prices, list markets by volume.
homepage: https://polymarket.com
metadata: {"clawdbot":{"emoji":"📊"}}
---

# Better Polymarket

Query [Polymarket](https://polymarket.com) prediction markets. Check odds, find trending markets, search events, get single market/event by slug, list active markets by volume (aligned with Gamma API usage as in PolyEdge).

## Commands

```bash
# Trending/active events (by 24h volume)
python3 {baseDir}/scripts/polymarket.py trending

# Search markets
python3 {baseDir}/scripts/polymarket.py search "trump"
python3 {baseDir}/scripts/polymarket.py search "bitcoin"

# Get specific event by slug (event = group of markets)
python3 {baseDir}/scripts/polymarket.py event "fed-decision-in-october"

# Get single market by slug (one binary market; polymarket.com/market/xxx)
python3 {baseDir}/scripts/polymarket.py market "will-trump-win-2024"

# List active markets (by volume; like PolyEdge FetchMarkets)
python3 {baseDir}/scripts/polymarket.py markets
python3 {baseDir}/scripts/polymarket.py markets --closed   # include closed markets
python3 {baseDir}/scripts/polymarket.py markets --order volumeNum --limit 10

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
- "Show me Polymarket market by slug will-trump-win-2024"
- "List top active markets by volume on Polymarket"

## Output

- **Events**: title, total volume, list of markets with Yes price, event link.
- **Markets**: question, Yes/No prices, volume, end date, resolution source when present, market link.
- **markets** command: same as single market format, ordered by volume (or specified order).

## API

Uses the public Gamma API (no auth required for reading), same surface as PolyEdge:
- Base URL: `https://gamma-api.polymarket.com`
- Endpoints: `/events`, `/events/slug/:slug`, `/markets`, `/markets/slug/:slug`, `/search`
- Params: `limit`, `offset`, `order`, `ascending`, `closed`, `active`
- Docs: https://docs.polymarket.com

## Note

This is read-only. Trading requires wallet authentication (not implemented).
