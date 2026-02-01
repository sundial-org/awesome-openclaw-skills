# Hyperliquid Skill (Clawdbot)

Read-only Hyperliquid assistant for market data + account views.

- Supports **natural language**, **terminal-style** (`hl ...`), and **slash-style** (`/hl ...`).
- Uses Hyperliquid **Info** endpoint: `POST https://api.hyperliquid.xyz/info`
- **No trading**, no private keys.

## Features

### Market data (perps)
- Quotes: mark/mid/oracle, 24h change, 24h notional volume, open interest, funding, premium, impact prices
- Movers (24h)
- Funding rankings (top/bottom)
- L2 order book (top levels)
- Candle snapshots (common intervals)
- Overview dashboard

### Account (read-only)
Given an EVM address (master or sub-account), you can view:
- Perp positions + margin summary
- Spot balances
- Open orders
- Recent fills

> Note: Use the address that actually owns the account/positions. Using an **agent wallet** address may return empty results.

## Usage

### Natural language examples
- “What are the top movers on Hyperliquid today?”
- “Hyperliquid quote BTC”
- “Show me the order book for ETH”
- “Give me 1h candles for SOL for the last 48 bars”
- “Show my Hyperliquid positions HL:0x….”

### Terminal / slash commands

#### Market
- `hl quote BTC`
- `/hl movers --top 10`
- `hl funding-top --n 10`
- `hl funding-bottom --n 10`
- `hl book ETH`
- `hl candles SOL --interval 1h --last 48`
- `hl overview`

#### Account (read-only)
- `hl positions HL:0x...`
- `hl balances HL:0x...`
- `hl orders HL:0x...`
- `hl fills HL:0x... --n 10`

## Saved account aliases (recommended)

Accounts are stored locally in:

- `~/.clawdbot/hyperliquid/config.json`

### Add / list / remove
- `hl account add "sub account 1" HL:0x... --default`
- `hl account list`
- `hl account remove "sub account 1"`
- `hl account default "sub account 1"`

### Use by label
- `hl positions "sub account 1"`
- `hl balances "sub account 1"`
- `hl orders "sub account 1"`
- `hl fills "sub account 1" --n 5`

If a default account is set, you can omit the argument:
- `hl positions`

## Local dev

Run the chat script directly:

```bash
node scripts/hyperliquid_chat.mjs "hl quote BTC"
node scripts/hyperliquid_chat.mjs "What are the top movers on Hyperliquid today?"
node scripts/hyperliquid_chat.mjs "hl positions HL:0x..."
```

## Files

- `SKILL.md` — skill instructions/triggering
- `scripts/hyperliquid_api.mjs` — HTTP client + helpers
- `scripts/hyperliquid_chat.mjs` — parser + command dispatcher + formatting
- `scripts/hyperliquid_config.mjs` — saved account aliases
- `references/hyperliquid-api.md` — API notes
