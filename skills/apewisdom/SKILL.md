---
name: apewisdom
description: Scan Reddit for trending stocks and sentiment spikes using the ApeWisdom API (free). Use this to find "meme stocks", retail momentum, and sentiment shifts on r/wallstreetbets.
---

# ApeWisdom Reddit Scanner

Scan Reddit (r/wallstreetbets, r/stocks, etc.) for trending tickers and sentiment spikes.

## Usage

This skill uses a Python script to fetch live data from ApeWisdom.

### Basic Scan (Top Mentions)
Get the top 20 most discussed stocks right now.

```bash
skills/apewisdom/scripts/scan_reddit.py
```

### Find Spikes (Momentum)
Find stocks with the biggest **24h increase** in mentions (ignoring low volume noise). This is the best way to find "breaking" meme stocks like $SNDK.

```bash
skills/apewisdom/scripts/scan_reddit.py --sort spike
```

### Specific Subreddits
Filter by specific communities.

```bash
# WallStreetBets only
skills/apewisdom/scripts/scan_reddit.py --filter wallstreetbets

# SPACs
skills/apewisdom/scripts/scan_reddit.py --filter SPACs

# Crypto
skills/apewisdom/scripts/scan_reddit.py --filter all-crypto
```

## Output Fields

- `ticker`: Stock symbol
- `mentions`: Mentions in the last 24h
- `mentions_24h_ago`: Mentions in the previous 24h period
- `change_pct`: Percentage increase/decrease in chatter
- `upvotes`: Total upvotes on posts mentioning the ticker
