---
name: bnb-chain
version: 0.1.0
description: Basic BNB Chain operations — check balances, send BNB, send BEP-20 tokens.
metadata: {"openclaw":{"emoji":"🟡","category":"blockchain","requires":{"bins":["node"]}}}
---

# BNB Chain Skill

Basic operations on BNB Chain (BSC). Check balances and send transactions.

## Setup

Requires Node.js and ethers.js:

```bash
cd ~/.openclaw/workspace/skills/bnb-chain && npm install ethers --silent
```

## Configuration

Store your private key securely. The skill reads from environment variable:

```bash
export BNB_PRIVATE_KEY="0x..."
```

Or pass it directly to the helper script.

## Usage

All operations use the helper script: `bnb.js`

### Check BNB Balance

```bash
node bnb.js balance <address>
```

Example:
```bash
node bnb.js balance 0x9787436458A36a9CC72364BaC18ba78fdEf83997
```

### Check BEP-20 Token Balance

```bash
node bnb.js token-balance <token_address> <wallet_address>
```

Example (USDT):
```bash
node bnb.js token-balance 0x55d398326f99059fF775485246999027B3197955 0x9787436458A36a9CC72364BaC18ba78fdEf83997
```

### Send BNB

```bash
node bnb.js send <to_address> <amount_bnb> [--key <private_key>]
```

Example:
```bash
node bnb.js send 0xRecipient 0.01 --key 0xYourPrivateKey
```

### Send BEP-20 Token

```bash
node bnb.js send-token <token_address> <to_address> <amount> [--key <private_key>]
```

Example (send 10 USDT):
```bash
node bnb.js send-token 0x55d398326f99059fF775485246999027B3197955 0xRecipient 10 --key 0xYourPrivateKey
```

### Get Wallet Address from Private Key

```bash
node bnb.js address <private_key>
```

### Get Transaction Details

```bash
node bnb.js tx <tx_hash>
```

## Common Token Addresses (BSC Mainnet)

| Token | Address |
|-------|---------|
| USDT | `0x55d398326f99059fF775485246999027B3197955` |
| USDC | `0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d` |
| BUSD | `0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56` |
| WBNB | `0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c` |

## RPC Endpoints

Default: `https://bsc-dataseed.binance.org/`

Alternatives:
- `https://bsc-dataseed1.binance.org/`
- `https://bsc-dataseed2.binance.org/`
- `https://bsc-dataseed3.binance.org/`
- `https://bsc-dataseed4.binance.org/`

## Security Notes

- **Never commit private keys** to git
- Use environment variables or secure storage
- Double-check recipient addresses before sending
- Start with small test amounts
