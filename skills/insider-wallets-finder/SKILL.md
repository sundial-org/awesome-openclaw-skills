---
name: insider-wallets-finder
description: Find and analyze smart money addresses - discover early buyers, track successful traders, identify whale accumulation patterns, and research on-chain alpha.
metadata: {"openclaw":{"requires":{"bins":["python3"]},"install":[{"id":"python","kind":"pip","package":"requests","bins":[],"label":"Install requests (pip)"}]}}
---

# Insider Wallets Finder

## Overview

Identify profitable addresses by analyzing:
- Early token buyers
- Consistent profitable traders
- Whale accumulation patterns
- DEX trading patterns
- NFT flippers

## Find Early Buyers of Token

### Ethereum (ERC-20)

```bash
# Get first 100 transfers of a token
TOKEN="0xTokenContractAddress"
curl -s "https://api.etherscan.io/api?module=account&action=tokentx&contractaddress=${TOKEN}&page=1&offset=100&sort=asc&apikey=YourKey" | \
python3 -c "
import sys, json
from collections import Counter
data = json.load(sys.stdin)
buyers = Counter()
for tx in data.get('result', []):
    buyers[tx['to']] += 1
print('=== Early Buyers ===')
for addr, count in buyers.most_common(20):
    print(f'{addr} | {count} buys')"
```

### Solana (SPL Token)

```bash
# Find early holders using Birdeye API
curl -s "https://public-api.birdeye.so/public/token_holder?address=TOKEN_MINT&offset=0&limit=20" \
  -H "X-API-KEY: your-birdeye-key" | python3 -m json.tool
```

## Analyze Deployer Activity

```bash
# Find what else deployer created
DEPLOYER="0xDeployerAddress"
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=${DEPLOYER}&sort=desc&apikey=YourKey" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
contracts = []
for tx in data.get('result', []):
    if tx['to'] == '' and tx['contractAddress']:
        contracts.append(tx['contractAddress'])
print('Deployed contracts:')
for c in contracts[:10]:
    print(c)"
```

## Track Whale Accumulation

```bash
python3 << 'EOF'
import requests

TOKEN = "0xTokenAddress"
API_KEY = "YourEtherscanKey"

# Get top holders
url = f"https://api.etherscan.io/api?module=token&action=tokenholderlist&contractaddress={TOKEN}&page=1&offset=50&apikey={API_KEY}"
resp = requests.get(url).json()

print("=== Top Holders ===")
for holder in resp.get('result', [])[:20]:
    addr = holder['TokenHolderAddress']
    qty = float(holder['TokenHolderQuantity']) / 1e18
    print(f"{addr[:20]}... | {qty:,.2f}")
EOF
```

## Find Profitable DEX Traders

### Analyze Uniswap Trades

```bash
python3 << 'EOF'
import requests

# GraphQL query for top traders
query = """
{
  swaps(first: 100, orderBy: amountUSD, orderDirection: desc, where: {amountUSD_gt: "10000"}) {
    sender
    amountUSD
    token0 { symbol }
    token1 { symbol }
  }
}
"""

resp = requests.post(
    "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
    json={"query": query}
).json()

from collections import Counter
traders = Counter()
for swap in resp.get('data', {}).get('swaps', []):
    traders[swap['sender']] += float(swap['amountUSD'])

print("=== High Volume Traders ===")
for addr, vol in traders.most_common(10):
    print(f"{addr[:20]}... | ${vol:,.0f}")
EOF
```

## Solana DEX Analysis

### Find Raydium/Jupiter Traders

```bash
# Using Birdeye API
curl -s "https://public-api.birdeye.so/public/txs/token?address=TOKEN_MINT&tx_type=swap&limit=50" \
  -H "X-API-KEY: your-key" | \
python3 -c "
import sys, json
from collections import Counter
data = json.load(sys.stdin)
traders = Counter()
for tx in data.get('data', {}).get('items', []):
    traders[tx.get('owner', '')] += 1
print('Active Traders:')
for addr, count in traders.most_common(10):
    print(f'{addr[:20]}... | {count} trades')"
```

## NFT Flipper Analysis

```bash
python3 << 'EOF'
import requests

# OpenSea API - find profitable flippers
collection = "boredapeyachtclub"
url = f"https://api.opensea.io/api/v1/events?collection_slug={collection}&event_type=successful&limit=50"

resp = requests.get(url, headers={"Accept": "application/json"}).json()

from collections import defaultdict
profits = defaultdict(float)

for event in resp.get('asset_events', []):
    seller = event.get('seller', {}).get('address', '')
    price = float(event.get('total_price', 0)) / 1e18
    profits[seller] += price

print("=== Top Sellers ===")
for addr, total in sorted(profits.items(), key=lambda x: -x[1])[:10]:
    print(f"{addr[:20]}... | {total:.2f} ETH")
EOF
```

## Cross-Reference Multiple Tokens

```bash
python3 << 'EOF'
import requests
from collections import Counter

API_KEY = "YourKey"
tokens = [
    "0xToken1",
    "0xToken2",
    "0xToken3"
]

all_early_buyers = Counter()

for token in tokens:
    url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={token}&page=1&offset=50&sort=asc&apikey={API_KEY}"
    resp = requests.get(url).json()

    for tx in resp.get('result', []):
        all_early_buyers[tx['to']] += 1

print("=== Addresses in Multiple Early Buys ===")
for addr, count in all_early_buyers.most_common(20):
    if count >= 2:
        print(f"{addr} | {count} tokens")
EOF
```

## Labeled Address Databases

### Check Known Addresses

```bash
# Etherscan labels
curl -s "https://api.etherscan.io/api?module=account&action=balance&address=ADDRESS&tag=latest&apikey=YourKey"
```

### Arkham Intelligence (API)

```bash
curl -s "https://api.arkhamintelligence.com/intelligence/address/ADDRESS" \
  -H "API-Key: your-arkham-key" | python3 -m json.tool
```

## Pattern Detection

### Find Addresses with Similar Behavior

```bash
python3 << 'EOF'
import requests
from datetime import datetime

TOKEN = "0xTokenAddress"
API_KEY = "YourKey"

# Get all transfers
url = f"https://api.etherscan.io/api?module=account&action=tokentx&contractaddress={TOKEN}&sort=asc&apikey={API_KEY}"
resp = requests.get(url).json()

# Group by timing
from collections import defaultdict
timing = defaultdict(list)

for tx in resp.get('result', []):
    block = int(tx['blockNumber'])
    timing[block // 100].append(tx['to'])  # Group by ~100 blocks

# Find coordinated buying
print("=== Potential Coordinated Buys ===")
for block_group, buyers in timing.items():
    if len(buyers) >= 3:
        unique = set(buyers)
        if len(unique) >= 3:
            print(f"Block ~{block_group * 100}: {len(unique)} unique buyers")
            for b in list(unique)[:5]:
                print(f"  {b}")
EOF
```

## Research Tools

| Tool | Purpose | Link |
|------|---------|------|
| Nansen | Labeled addresses | nansen.ai |
| Arkham | Intel platform | arkhamintelligence.com |
| Bubblemaps | Holder visualization | bubblemaps.io |
| DeBank | Portfolio tracking | debank.com |
| Dune | Custom queries | dune.com |
| Birdeye | Solana analytics | birdeye.so |

## Dune Analytics Queries

Find smart money on Dune:
```sql
-- Top profitable traders
SELECT
  trader,
  SUM(profit_usd) as total_profit,
  COUNT(*) as trade_count
FROM dex.trades
WHERE block_time > now() - interval '7 days'
GROUP BY trader
HAVING SUM(profit_usd) > 10000
ORDER BY total_profit DESC
LIMIT 50
```

## Notes

- All blockchain data is public
- Use for research and education
- Cross-reference multiple sources
- Patterns don't guarantee future performance
- Consider transaction fees in profit calculations
- Some "insiders" may be arbitrage bots
- Always verify findings manually
