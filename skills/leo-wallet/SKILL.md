---
name: leo-wallet
description: Interact with Aleo blockchain - check balances, view transactions, and explore the privacy-focused network. Works with Leo Wallet addresses.
metadata: {"openclaw":{"requires":{"bins":["snarkos"]},"install":[{"id":"aleo","kind":"shell","command":"curl -sSf https://raw.githubusercontent.com/AleoHQ/snarkOS/mainnet/install.sh | bash","bins":["snarkos"],"label":"Install snarkOS CLI"}]}}
---

# Leo Wallet CLI

## Setup

Install snarkOS:
```bash
curl -sSf https://raw.githubusercontent.com/AleoHQ/snarkOS/mainnet/install.sh | bash
```

Install Leo (development):
```bash
curl -sSf https://raw.githubusercontent.com/AleoHQ/leo/mainnet/install.sh | bash
```

## Check Balance via API

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/program/credits.aleo/mapping/account/ADDRESS" | \
python3 -c "import sys; print(sys.stdin.read())"
```

## Get Latest Block

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/latest/block" | python3 -m json.tool
```

## Block Height

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/latest/height"
```

## Get Transaction

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/transaction/TX_ID" | python3 -m json.tool
```

## Get Block by Height

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/block/BLOCK_HEIGHT" | python3 -m json.tool
```

## Program Info

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/program/credits.aleo" | python3 -m json.tool
```

## List Program Mappings

```bash
curl -s "https://api.explorer.aleo.org/v1/testnet3/program/credits.aleo/mappings" | python3 -m json.tool
```

## Network Stats

```bash
python3 -c "
import urllib.request
import json

base = 'https://api.explorer.aleo.org/v1/testnet3'
height = urllib.request.urlopen(f'{base}/latest/height').read().decode()
print(f'Latest Block: {height}')
"
```

## Using snarkOS

Start a client node:
```bash
snarkos start --client
```

Get peer info:
```bash
snarkos developer get-peer-count
```

## Leo CLI (Development)

Create new project:
```bash
leo new my_program
```

Build program:
```bash
leo build
```

Run program:
```bash
leo run main
```

## Address Format

- Aleo addresses start with `aleo1`
- Length: 63 characters
- Example: aleo1rhgdu77hgyqd3xjj8ucu3jj9r2krwz6mnzyd80gncr5fxcwlh5rsvzp9dx

## View Key Types

| Type | Prefix | Purpose |
|------|--------|---------|
| Address | aleo1 | Public identifier |
| View Key | AViewKey1 | Decrypt incoming |
| Private Key | APrivateKey1 | Full control |

## Explorer APIs

| Network | Base URL |
|---------|----------|
| Testnet3 | https://api.explorer.aleo.org/v1/testnet3 |
| Mainnet | https://api.explorer.aleo.org/v1/mainnet (when live) |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| /latest/block | Latest block |
| /latest/height | Current height |
| /block/{height} | Block by height |
| /transaction/{id} | Transaction details |
| /program/{id} | Program source |
| /program/{id}/mappings | Program state |

## Notes

- Aleo is privacy-focused; not all data is publicly visible
- Testnet3 is current test network
- Credits are the native currency
- Programs are written in Leo language
- Zero-knowledge proofs enable private transactions
- Mainnet launch expected - check aleo.org for updates
