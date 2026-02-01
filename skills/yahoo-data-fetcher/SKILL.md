---
name: yahoo-data-fetcher
description: Fetch real-time stock quotes from Yahoo Finance.
user-invocable: true
metadata:
  moltbot:
    emoji: "📈"
    requires:
      bins: ["node"]
    homepage: https://query1.finance.yahoo.com/v7/finance/quote
---

# Yahoo Data Fetcher – Stock Quote

Get current stock price data from Yahoo Finance.

This skill fetches the latest market quote for one or more stock symbols and returns normalized JSON output.

---

## Command

### `/stock quote`

Fetch the latest quote for one or more stock symbols.

---

## Input

- `symbols` (string or array of strings)

Examples:
- `"AAPL"`
- `"AAPL MSFT TSLA"`
- `"AAPL,MSFT,TSLA"`
- `["AAPL", "MSFT"]`
- `{ "symbols": ["AAPL", "MSFT"] }`

---

## Output

For each symbol:

- `symbol` – stock ticker
- `price` – latest market price
- `change` – absolute price change
- `changePercent` – percentage change
- `currency` – trading currency
- `marketState` – market status (e.g. `REGULAR`, `CLOSED`)

Example output:

```json
[
  {
    "symbol": "AAPL",
    "price": 189.12,
    "change": 1.23,
    "changePercent": 0.65,
    "currency": "USD",
    "marketState": "REGULAR"
  }
]