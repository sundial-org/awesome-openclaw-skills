---
name: tron
description: Interact with TRON blockchain - check TRX balances, view TRC-20 tokens, transactions, and account resources. Works with TronLink addresses.
metadata: {"openclaw":{"requires":{"bins":["python3"]},"install":[{"id":"python","kind":"pip","package":"tronpy","bins":[],"label":"Install tronpy (pip)"}]}}
---

# TRON Wallet CLI

## Setup

Install tronpy:
```bash
pip install tronpy
```

## Check TRX Balance

```bash
python3 -c "
from tronpy import Tron
client = Tron()
balance = client.get_account_balance('ADDRESS')
print(f'{balance} TRX')"
```

## Account Info

```bash
python3 -c "
from tronpy import Tron
import json
client = Tron()
acc = client.get_account('ADDRESS')
print(json.dumps(acc, indent=2))"
```

## Account Resources (Energy & Bandwidth)

```bash
python3 -c "
from tronpy import Tron
client = Tron()
res = client.get_account_resource('ADDRESS')
print(f\"Bandwidth: {res.get('freeNetLimit', 0)}\")
print(f\"Energy: {res.get('EnergyLimit', 0)}\")"
```

## TRC-20 Token Balance

```bash
python3 -c "
from tronpy import Tron
from tronpy.contract import Contract

client = Tron()
# USDT TRC-20 contract
contract = client.get_contract('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
balance = contract.functions.balanceOf('ADDRESS')
decimals = contract.functions.decimals()
print(f'{balance / 10**decimals} USDT')"
```

## Token Info

```bash
python3 -c "
from tronpy import Tron
client = Tron()
contract = client.get_contract('CONTRACT_ADDRESS')
print(f\"Name: {contract.functions.name()}\")
print(f\"Symbol: {contract.functions.symbol()}\")
print(f\"Decimals: {contract.functions.decimals()}\")
print(f\"Total Supply: {contract.functions.totalSupply()}\")"
```

## Transaction History (via API)

```bash
curl -s "https://api.trongrid.io/v1/accounts/ADDRESS/transactions?limit=10" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for tx in data.get('data', []):
    print(f\"{tx['txID'][:16]}... | {tx.get('raw_data', {}).get('contract', [{}])[0].get('type', 'Unknown')}\")"
```

## TRC-20 Transfers

```bash
curl -s "https://api.trongrid.io/v1/accounts/ADDRESS/transactions/trc20?limit=10" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for tx in data.get('data', []):
    val = int(tx.get('value', 0)) / 10**int(tx.get('token_info', {}).get('decimals', 6))
    sym = tx.get('token_info', {}).get('symbol', '?')
    print(f\"{tx['transaction_id'][:16]}... | {val:.2f} {sym}\")"
```

## Get Transaction

```bash
python3 -c "
from tronpy import Tron
import json
client = Tron()
tx = client.get_transaction('TX_HASH')
print(json.dumps(tx, indent=2))"
```

## Current Block

```bash
python3 -c "
from tronpy import Tron
client = Tron()
block = client.get_latest_block()
print(f\"Block: {block['block_header']['raw_data']['number']}\")"
```

## Check if Contract

```bash
python3 -c "
from tronpy import Tron
client = Tron()
try:
    contract = client.get_contract('ADDRESS')
    print('This is a contract')
    print(f'Name: {contract.name}')
except:
    print('This is a regular account')"
```

## Using TronGrid API

Account info:
```bash
curl -s "https://api.trongrid.io/v1/accounts/ADDRESS" | python3 -m json.tool
```

Account balance:
```bash
curl -s "https://api.trongrid.io/v1/accounts/ADDRESS" | \
python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['data'][0].get('balance',0)/1e6:.2f} TRX\")"
```

## Common TRC-20 Contracts

| Token | Contract |
|-------|----------|
| USDT | TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t |
| USDC | TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8 |
| WTRX | TNUC9Qb1rRpS5CbWLmNMxXBjyFoydXjWFR |
| BTT | TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4 |
| JST | TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9 |

## Address Format

- TRON uses Base58Check encoding
- Addresses start with 'T'
- Length: 34 characters
- Example: TJYeasTPa6gpBZWqTcP4u1Q7bhLMWBL7ox

## Notes

- 1 TRX = 1,000,000 SUN
- Free bandwidth: 1500 per day
- Energy needed for smart contract calls
- TronGrid API has rate limits
- Use Shasta testnet for testing
