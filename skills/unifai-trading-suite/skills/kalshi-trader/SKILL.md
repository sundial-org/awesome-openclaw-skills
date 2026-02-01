---
name: kalshi-trader
description: Query Kalshi prediction markets - Fed rates, GDP, CPI, economics, and regulated event contracts
homepage: https://kalshi.com
user-invocable: true
metadata: {"moltbot":{"emoji":"🏛️","requires":{}}}
---

# Kalshi Trader

Query Kalshi, the CFTC-regulated US prediction market for economics, politics, and event contracts.

## About Kalshi

Kalshi is the first legal, regulated prediction market in the United States, approved by the CFTC. It offers event contracts on:
- Federal Reserve interest rate decisions
- GDP and economic indicators
- Inflation (CPI) data
- Political events
- Weather and natural events

## Commands

### Federal Reserve Markets
```bash
python3 {baseDir}/scripts/kalshi.py fed [limit]
```
Get Fed interest rate prediction markets (KXFED series).

### Economics Markets
```bash
python3 {baseDir}/scripts/kalshi.py economics [limit]
```
Get GDP, CPI, and other economics markets.

### Trending Markets
```bash
python3 {baseDir}/scripts/kalshi.py trending [limit]
```
Get high-volume trending markets.

### Search Markets
```bash
python3 {baseDir}/scripts/kalshi.py search "<query>" [limit]
```
Search markets by keyword.

### Get All Series
```bash
python3 {baseDir}/scripts/kalshi.py series
```
List all available market series.

## Output Format

Results include:
- Market title/question
- YES price (probability)
- Trading volume
- Market ticker
- Status (open/closed)

## Key Market Series

| Series | Description |
|--------|-------------|
| KXFED | Federal Reserve interest rate decisions |
| KXGDP | US GDP predictions |
| KXCPI | Consumer Price Index / Inflation |
| KXBTC | Bitcoin price brackets |

## Example Usage

**User**: "What are the Fed rate predictions?"

**Assistant**: I'll fetch the Federal Reserve markets from Kalshi.

```bash
python3 {baseDir}/scripts/kalshi.py fed
```

**User**: "Search for inflation markets"

**Assistant**: Let me search Kalshi for inflation-related markets.

```bash
python3 {baseDir}/scripts/kalshi.py search "inflation"
```

## API Information

- **Base URL**: `https://api.elections.kalshi.com/trade-api/v2`
- **Authentication**: Not required for read operations
- **Rate Limits**: Standard API rate limits apply
- **Documentation**: https://docs.kalshi.com

## Notes

- This tool is read-only (trading requires API key authentication)
- Prices shown as decimals (0.75 = 75% probability)
- Volume represents total contracts traded
- Markets settle to $1.00 (YES) or $0.00 (NO)
- US-regulated, available to US residents
