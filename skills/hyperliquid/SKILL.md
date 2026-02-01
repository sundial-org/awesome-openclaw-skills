---
name: hyperliquid
description: Read-only Hyperliquid market data assistant (perps + spot optional) with support for natural-language requests and deterministic command parsing (terminal-style `hl ...` and slash-style `/hl ...`). Use to fetch quotes (mark/mid/oracle/funding/OI/volume), top movers, funding rankings, L2 order book, and candle snapshots via https://api.hyperliquid.xyz/info, and to format results for chat.
---

# Hyperliquid (read-only)

Implement read-only market-data queries for Hyperliquid using the **Info** HTTP endpoint:

- `POST https://api.hyperliquid.xyz/info`
- `Content-Type: application/json`

Prefer **HTTP snapshot** flows for v1. WebSocket streaming can be added later.

## Supported user input styles

Treat these as equivalent:

- Natural language: “Hyperliquid quote BTC”, “top movers 24h”, “book ETH”, “1h candles for SOL last 48”
- Terminal style: `hl quote BTC`, `hl movers --top 10 --window 24h`
- Slash style: `/hl quote BTC`, `/hl overview`

Parse `/hl` and `hl` first (deterministic). If no prefix, fall back to intent extraction from natural language.

## Canonical commands (v1)

Market data:
- `quote <coin>`: show mark/mid/oracle, 24h change (prevDayPx), 24h notional volume, open interest (perps), funding (perps), premium, impact prices
- `movers [--window 24h] [--top N]`: rank by 24h % change (markPx vs prevDayPx)
- `funding-top|funding-bottom [--n N]`: rank by funding (perps only)
- `book <coin>`: show top 20 levels per side (and spread)
- `candles <coin> --interval <1m|...|1M> (--last N | --start <ms> --end <ms>)`
- `overview`: concise dashboard: top movers, top funding, top OI, top volume

Account (read-only):
- `positions <HL:0x..|0x..|label>`: show perp positions + margin summary
- `balances <HL:0x..|0x..|label>`: show spot balances
- `orders <HL:0x..|0x..|label>`: show open orders
- `fills <HL:0x..|0x..|label> [--n N]`: show recent fills

Saved account aliases (stored locally in `~/.clawdbot/hyperliquid/config.json`):
- `account list`
- `account add "sub account 1" HL:0x... [--default]`
- `account remove "sub account 1"`
- `account default "sub account 1"`

Natural language equivalents should work too:
- “store this address HL:0x... as sub account 1”
- “show me positions of sub account 1”

## Data sources

Perpetuals:
- `metaAndAssetCtxs` (preferred): universe + asset contexts for all perps
- `l2Book`
- `candleSnapshot`

Spot (optional later):
- `spotMetaAndAssetCtxs`, `spotMeta`

See `references/hyperliquid-api.md` for request bodies and field meanings.

## Implementation guidance

Use the bundled scripts:

- `scripts/hyperliquid_api.mjs`: thin HTTP client + helpers (safe defaults, timeouts)
- `scripts/hyperliquid_chat.mjs`: parses user text into an intent + args, calls API helpers, and prints a compact chat-friendly response

When responding:
- Prefer short bullet output.
- Show units and timeframes.
- Handle missing fields gracefully (e.g., midPx sometimes null).

## Quick manual test

Run locally:

```bash
node skills/hyperliquid/scripts/hyperliquid_chat.mjs "hl quote BTC"
node skills/hyperliquid/scripts/hyperliquid_chat.mjs "/hl movers --top 5"
```
