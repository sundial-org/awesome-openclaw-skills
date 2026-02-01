---
name: portfolio-watcher
description: Monitor stock/crypto holdings, get price alerts, track portfolio performance
author: clawd-team
version: 1.0.0
triggers:
  - "check portfolio"
  - "stock price"
  - "crypto price"
  - "set price alert"
  - "portfolio performance"
---

# Portfolio Watcher

Monitor your investments through natural conversation. Real-time prices, alerts, and performance tracking.

## What it does

Tracks your stock and crypto holdings, fetches real-time prices, sends alerts when targets are hit, and calculates portfolio performance. No brokerage connection needed—just tell Clawd what you own.

## Usage

**Add holdings:**
```
"I own 50 shares of AAPL at $150"
"Add 0.5 BTC bought at $40,000"
"Track NVDA, bought 20 shares at $280"
```

**Check prices:**
```
"What's TSLA at?"
"Bitcoin price"
"Check all my stocks"
```

**Set alerts:**
```
"Alert me if AAPL hits $200"
"Notify when ETH drops below $2000"
"Remove MSFT alert"
```

**Portfolio overview:**
```
"How's my portfolio doing?"
"Total gains/losses"
"Best and worst performers"
```

## Supported Assets

- US stocks (NYSE, NASDAQ)
- Major cryptocurrencies
- ETFs
- International stocks (limited)

## Tips

- Include purchase price for accurate gain/loss tracking
- Say "update [ticker] to [shares] at [price]" to modify holdings
- Ask "portfolio allocation" for pie chart breakdown
- Prices update every few minutes (not real-time streaming)
- This is informational only—not financial advice
