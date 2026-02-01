---
name: polymarket-trader
description: Query Polymarket prediction markets - trending events, crypto, politics, sports, and search
homepage: https://polymarket.com
user-invocable: true
metadata: {"moltbot":{"emoji":"🔮","requires":{"env":["UNIFAI_AGENT_API_KEY","GOOGLE_API_KEY"]},"primaryEnv":"UNIFAI_AGENT_API_KEY"}}
---

# Polymarket Trader

Query Polymarket, the leading decentralized prediction market on Polygon blockchain.

## About Polymarket

Polymarket is a decentralized prediction market platform where users can trade on the outcomes of real-world events. It operates on the Polygon blockchain using USDC.e for settlements.

## Commands

### Trending Events
```bash
python3 {baseDir}/scripts/polymarket.py trending
```
Get currently trending prediction events.

### Crypto Markets
```bash
python3 {baseDir}/scripts/polymarket.py crypto
```
Get cryptocurrency-related prediction markets.

### Politics Markets
```bash
python3 {baseDir}/scripts/polymarket.py politics
```
Get political prediction markets.

### Search Markets
```bash
python3 {baseDir}/scripts/polymarket.py search "<query>"
```
Search markets by keyword.

### Category Markets
```bash
python3 {baseDir}/scripts/polymarket.py category <name>
```
Get markets by category (trending, new, politics, crypto, tech, culture, sports, world, economy).

## Output Format

Results include:
- Event/market title
- YES/NO prices (probability)
- Trading volume
- Liquidity
- End date

## Categories

| Category | Description |
|----------|-------------|
| trending | Most popular markets |
| new | Recently created markets |
| politics | Political events and elections |
| crypto | Cryptocurrency predictions |
| tech | Technology sector events |
| culture | Entertainment and culture |
| sports | Sports outcomes |
| world | Global events |
| economy | Economic indicators |

## Example Usage

**User**: "What's trending on Polymarket?"

**Assistant**: I'll fetch the trending events from Polymarket.

```bash
python3 {baseDir}/scripts/polymarket.py trending
```

**User**: "Search for Bitcoin markets"

**Assistant**: Let me search Polymarket for Bitcoin-related markets.

```bash
python3 {baseDir}/scripts/polymarket.py search "bitcoin"
```

## Requirements

- `UNIFAI_AGENT_API_KEY` - UnifAI SDK key for Polymarket tools
- `GOOGLE_API_KEY` - Gemini API key for LLM processing

## API Information

- **Data Source**: UnifAI Polymarket tools (toolkit ID: 127)
- **Available Tools**: search, getEventsByCategory, getPrices, getOrderBooks
- **Rate Limits**: UnifAI API rate limits apply

## Notes

- This tool is read-only (trading requires wallet authentication)
- Prices shown as decimals (0.75 = 75% probability)
- Markets settle on Polygon blockchain
- USDC.e used for trading
- Not available in restricted jurisdictions
