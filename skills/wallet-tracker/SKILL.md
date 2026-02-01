---
name: wallet-tracker
description: Track blockchain addresses in real-time - monitor whale movements, get alerts on transactions, analyze portfolio changes across Ethereum, Solana, and other chains.
metadata: {"openclaw":{"requires":{"bins":["python3"]},"install":[{"id":"python","kind":"pip","package":"requests","bins":[],"label":"Install requests (pip)"}]}}
---

# Wallet Tracker

## Overview

Monitor blockchain addresses for:
- Large transactions (whale alerts)
- Portfolio changes
- Token transfers
- NFT movements
- DeFi interactions

## Ethereum Tracking

### Watch Address Transactions

```bash
# Using Etherscan API
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=ADDRESS&startblock=0&endblock=99999999&sort=desc&apikey=YourApiKey" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for tx in data.get('result', [])[:10]:
    val = int(tx['value']) / 1e18
    print(f\"{tx['hash'][:16]}... | {val:.4f} ETH | {tx['to'][:16]}...\")"
```

### Monitor ERC-20 Transfers

```bash
curl -s "https://api.etherscan.io/api?module=account&action=tokentx&address=ADDRESS&sort=desc&apikey=YourApiKey" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for tx in data.get('result', [])[:10]:
    val = int(tx['value']) / 10**int(tx['tokenDecimal'])
    print(f\"{tx['tokenSymbol']}: {val:.2f} | {tx['to'][:16]}...\")"
```

### Real-time Monitoring Script

```python
#!/usr/bin/env python3
import requests
import time

ADDRESS = "0x..." # Address to track
API_KEY = "YourEtherscanApiKey"
INTERVAL = 60  # Check every 60 seconds

last_block = 0

while True:
    url = f"https://api.etherscan.io/api?module=account&action=txlist&address={ADDRESS}&startblock={last_block}&sort=asc&apikey={API_KEY}"
    resp = requests.get(url).json()

    for tx in resp.get('result', []):
        block = int(tx['blockNumber'])
        if block > last_block:
            val = int(tx['value']) / 1e18
            direction = "IN" if tx['to'].lower() == ADDRESS.lower() else "OUT"
            print(f"[{direction}] {val:.4f} ETH | TX: {tx['hash'][:20]}...")
            last_block = block

    time.sleep(INTERVAL)
```

## Solana Tracking

### Recent Transactions

```bash
curl -s -X POST https://api.mainnet-beta.solana.com -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getSignaturesForAddress",
  "params": ["ADDRESS", {"limit": 10}]
}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for sig in data.get('result', []):
    print(f\"{sig['signature'][:32]}... | Block: {sig.get('slot')}\")"
```

### Monitor SOL Balance Changes

```bash
python3 -c "
import requests
import time

address = 'YOUR_ADDRESS'
last_balance = 0

while True:
    resp = requests.post('https://api.mainnet-beta.solana.com', json={
        'jsonrpc': '2.0',
        'id': 1,
        'method': 'getBalance',
        'params': [address]
    }).json()

    balance = resp['result']['value'] / 1e9
    if balance != last_balance:
        diff = balance - last_balance
        print(f'Balance: {balance:.4f} SOL | Change: {diff:+.4f}')
        last_balance = balance

    time.sleep(30)"
```

### Track SPL Token Transfers

```bash
curl -s -X POST https://api.mainnet-beta.solana.com -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getTokenAccountsByOwner",
  "params": [
    "ADDRESS",
    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
    {"encoding": "jsonParsed"}
  ]
}' | python3 -c "
import sys, json
data = json.load(sys.stdin)
for acc in data.get('result', {}).get('value', []):
    info = acc['account']['data']['parsed']['info']
    amount = float(info['tokenAmount']['uiAmount'] or 0)
    mint = info['mint'][:16]
    print(f'{mint}... | {amount:.4f}')"
```

## Multi-Chain Portfolio Tracker

```python
#!/usr/bin/env python3
import requests

def get_eth_balance(address):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&apikey=YourKey"
    resp = requests.get(url).json()
    return int(resp['result']) / 1e18

def get_sol_balance(address):
    resp = requests.post('https://api.mainnet-beta.solana.com', json={
        'jsonrpc': '2.0', 'id': 1,
        'method': 'getBalance',
        'params': [address]
    }).json()
    return resp['result']['value'] / 1e9

# Track multiple addresses
wallets = {
    'eth': ['0xAddress1', '0xAddress2'],
    'sol': ['SolAddress1', 'SolAddress2']
}

print("=== Portfolio ===")
for addr in wallets['eth']:
    bal = get_eth_balance(addr)
    print(f"ETH {addr[:10]}...: {bal:.4f} ETH")

for addr in wallets['sol']:
    bal = get_sol_balance(addr)
    print(f"SOL {addr[:10]}...: {bal:.4f} SOL")
```

## Webhook Alerts (Using Alchemy)

```bash
# Create webhook via Alchemy API
curl -X POST "https://dashboard.alchemy.com/api/create-webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "network": "ETH_MAINNET",
    "webhook_type": "ADDRESS_ACTIVITY",
    "webhook_url": "https://your-server.com/webhook",
    "addresses": ["0xAddress1", "0xAddress2"]
  }'
```

## Whale Alert Integration

Track large movements:
```bash
# Top ETH holders recent activity
curl -s "https://api.etherscan.io/api?module=account&action=txlist&address=0x00000000219ab540356cBB839Cbe05303d7705Fa&sort=desc&apikey=YourKey" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for tx in data.get('result', [])[:5]:
    val = int(tx['value']) / 1e18
    if val > 100:
        print(f'WHALE: {val:.2f} ETH | {tx[\"hash\"][:20]}...')"
```

## Tracking Services (Free Tiers)

| Service | Chains | Features |
|---------|--------|----------|
| Etherscan | ETH, L2s | TX history, API |
| Solscan | Solana | Full history |
| DeBank | Multi-chain | Portfolio view |
| Zapper | EVM chains | DeFi tracking |
| Nansen | Multi | Whale labels |

## API Endpoints

| Chain | Endpoint |
|-------|----------|
| Ethereum | https://api.etherscan.io/api |
| Polygon | https://api.polygonscan.com/api |
| BSC | https://api.bscscan.com/api |
| Arbitrum | https://api.arbiscan.io/api |
| Solana | https://api.mainnet-beta.solana.com |

## Notes

- Most APIs have rate limits (5 req/sec free tier)
- Paid APIs offer WebSocket for real-time
- Consider using dedicated tracking services for production
- All blockchain data is public
- Use responsibly for research purposes
