---
name: tronlink
description: Work with TronLink wallet - manage TRX and TRC-20 tokens, stake for energy/bandwidth, vote for super representatives, and interact with TRON dApps.
metadata: {"openclaw":{"requires":{"bins":["python3"]},"install":[{"id":"python","kind":"pip","package":"tronpy","bins":[],"label":"Install tronpy (pip)"}]}}
---

# TronLink Wallet

## Installation

- Chrome: https://chrome.google.com/webstore/detail/tronlink/ibnejdfjmmkpcnlpebklmnkoeoihofec
- Mobile: iOS App Store / Google Play

## Supported Assets

| Type | Examples |
|------|----------|
| Native | TRX |
| TRC-20 | USDT, USDC, JST, BTT |
| TRC-10 | Legacy tokens |
| TRC-721 | NFTs |

## Check Balance (CLI)

TRX balance:
```bash
python3 -c "
from tronpy import Tron
client = Tron()
balance = client.get_account_balance('YOUR_TRONLINK_ADDRESS')
print(f'{balance} TRX')"
```

Via API:
```bash
curl -s "https://api.trongrid.io/v1/accounts/YOUR_ADDRESS" | \
python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['data'][0].get('balance',0)/1e6:.2f} TRX\")"
```

## TRC-20 Token Balance

USDT:
```bash
python3 -c "
from tronpy import Tron
client = Tron()
contract = client.get_contract('TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t')
balance = contract.functions.balanceOf('YOUR_ADDRESS')
print(f'{balance / 1e6:.2f} USDT')"
```

## Import TRC-20 Token

Assets → Add Token → Custom

Common TRC-20 contracts:
```
USDT: TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t
USDC: TEkxiTehnzSmSe2XqrBj4w32RUN966rdz8
BTT: TAFjULxiVgT4qWk6UZwjqwZXTSaGaqnVp4
JST: TCFLL5dx5ZJdKnWuesXxi1VPwjLVmWZZy9
WIN: TLa2f6VPqDgRE67v1736s7bJ8Ray5wYjU7
SUN: TSSMHYeV2uE9qYH95DqyoCuNCzEL1NvU3S
```

## Resources: Energy & Bandwidth

Check resources:
```bash
python3 -c "
from tronpy import Tron
client = Tron()
res = client.get_account_resource('YOUR_ADDRESS')
print(f\"Free Bandwidth: {res.get('freeNetUsed', 0)} / {res.get('freeNetLimit', 1500)}\")
print(f\"Energy: {res.get('EnergyUsed', 0)} / {res.get('EnergyLimit', 0)}\")"
```

Via API:
```bash
curl -s "https://api.trongrid.io/v1/accounts/YOUR_ADDRESS/resources" | python3 -m json.tool
```

## Freeze TRX for Resources

In TronLink: Resources → Freeze

| Freeze For | Get |
|------------|-----|
| Bandwidth | Free transactions |
| Energy | Smart contract calls |

Minimum freeze: 1 TRX
Lock period: 14 days (Stake 2.0)

## Vote for Super Representatives

Resources → Vote → Select SR

Check votes:
```bash
curl -s "https://api.trongrid.io/v1/accounts/YOUR_ADDRESS" | \
python3 -c "
import sys, json
d = json.load(sys.stdin)
votes = d['data'][0].get('votes', [])
for v in votes:
    print(f\"{v['vote_address']}: {v['vote_count']} votes\")"
```

## Transaction History

```bash
curl -s "https://api.trongrid.io/v1/accounts/YOUR_ADDRESS/transactions?limit=10" | \
python3 -c "
import sys, json
data = json.load(sys.stdin)
for tx in data.get('data', []):
    txid = tx['txID'][:16]
    type = tx.get('raw_data', {}).get('contract', [{}])[0].get('type', 'Unknown')
    print(f'{txid}... | {type}')"
```

TRC-20 transfers:
```bash
curl -s "https://api.trongrid.io/v1/accounts/YOUR_ADDRESS/transactions/trc20?limit=10" | python3 -m json.tool
```

## Network Settings

Settings → Node Settings

Default: https://api.trongrid.io

Custom nodes:
```
TronGrid: https://api.trongrid.io
Nile Testnet: https://nile.trongrid.io
Shasta Testnet: https://api.shasta.trongrid.io
```

## Connected dApps

Settings → Connected Sites → Manage

## Export Account

Settings → Export → Enter password

## dApp Browser (Mobile)

Discover → Browse dApps

Popular TRON dApps:
- JustLend (lending)
- SunSwap (DEX)
- JUST (stablecoin)

## Transaction Fees

| Operation | Cost |
|-----------|------|
| TRX transfer | ~1 Bandwidth |
| TRC-20 transfer | ~15,000 Energy |
| Contract call | Varies |

## Troubleshooting

**Not enough bandwidth:**
```bash
# Check bandwidth
curl -s "https://api.trongrid.io/v1/accounts/YOUR_ADDRESS/resources" | \
python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"Bandwidth: {d.get('freeNetLimit',0) - d.get('freeNetUsed',0)}\")"
```
Solution: Wait (regenerates) or freeze TRX

**Not enough energy:**
Solution: Freeze TRX for Energy or pay TRX for transaction

**Token not showing:**
Assets → Add Token → Paste contract address

**Transaction pending:**
```bash
# Check transaction
python3 -c "
from tronpy import Tron
client = Tron()
tx = client.get_transaction('TX_HASH')
print(tx)"
```

## Address Format

- Base58Check encoding
- Starts with 'T'
- 34 characters
- Example: TJYeasTPa6gpBZWqTcP4u1Q7bhLMWBL7ox

## Notes

- TronLink is official TRON wallet
- Free bandwidth: 1500/day (regenerates)
- Energy needed for smart contracts
- Stake 2.0: 14-day unlock period
- Voting rewards from Super Representatives
- Mobile has built-in dApp browser
