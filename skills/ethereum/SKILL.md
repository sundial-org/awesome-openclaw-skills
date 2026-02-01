---
name: ethereum
description: Interact with Ethereum blockchain - check ETH and ERC-20 balances, view transactions, gas prices, and ENS lookups. Works with MetaMask addresses.
metadata: {"openclaw":{"requires":{"bins":["cast"]},"install":[{"id":"foundry","kind":"shell","command":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["cast"],"label":"Install Foundry (cast)"}]}}
---

# Ethereum Wallet CLI

## Setup

Install Foundry (includes `cast`):
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Set RPC (optional):
```bash
export ETH_RPC_URL="https://eth.llamarpc.com"
```

## Check ETH Balance

```bash
cast balance <ADDRESS> --rpc-url https://eth.llamarpc.com
```

In ether (human readable):
```bash
cast balance <ADDRESS> --ether --rpc-url https://eth.llamarpc.com
```

## ENS Lookup

Resolve ENS to address:
```bash
cast resolve-name vitalik.eth --rpc-url https://eth.llamarpc.com
```

Reverse lookup (address to ENS):
```bash
cast lookup-address <ADDRESS> --rpc-url https://eth.llamarpc.com
```

## ERC-20 Token Balance

```bash
# USDC balance (6 decimals)
cast call 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  "balanceOf(address)(uint256)" <ADDRESS> \
  --rpc-url https://eth.llamarpc.com

# Format with decimals
cast call 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  "balanceOf(address)(uint256)" <ADDRESS> \
  --rpc-url https://eth.llamarpc.com | xargs -I {} cast --to-unit {} 6
```

## Token Info

```bash
# Token name
cast call <TOKEN_CONTRACT> "name()(string)" --rpc-url https://eth.llamarpc.com

# Token symbol
cast call <TOKEN_CONTRACT> "symbol()(string)" --rpc-url https://eth.llamarpc.com

# Decimals
cast call <TOKEN_CONTRACT> "decimals()(uint8)" --rpc-url https://eth.llamarpc.com

# Total supply
cast call <TOKEN_CONTRACT> "totalSupply()(uint256)" --rpc-url https://eth.llamarpc.com
```

## Transaction Info

```bash
cast tx <TX_HASH> --rpc-url https://eth.llamarpc.com
```

Transaction receipt:
```bash
cast receipt <TX_HASH> --rpc-url https://eth.llamarpc.com
```

## Gas Price

Current gas price:
```bash
cast gas-price --rpc-url https://eth.llamarpc.com
```

In gwei:
```bash
cast --to-unit $(cast gas-price --rpc-url https://eth.llamarpc.com) gwei
```

## Block Info

Latest block:
```bash
cast block latest --rpc-url https://eth.llamarpc.com
```

Specific block:
```bash
cast block 17000000 --rpc-url https://eth.llamarpc.com
```

## NFT (ERC-721) Owner

```bash
cast call <NFT_CONTRACT> "ownerOf(uint256)(address)" <TOKEN_ID> --rpc-url https://eth.llamarpc.com
```

## Account Nonce

```bash
cast nonce <ADDRESS> --rpc-url https://eth.llamarpc.com
```

## Chain Info

```bash
cast chain-id --rpc-url https://eth.llamarpc.com
```

## Common Token Contracts

| Token | Contract |
|-------|----------|
| USDC | 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 |
| USDT | 0xdAC17F958D2ee523a2206206994597C13D831ec7 |
| DAI | 0x6B175474E89094C44Da98b954EescdeCB5BE3830 |
| WETH | 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 |
| LINK | 0x514910771AF9Ca656af840dff83E8264EcF986CA |

## Public RPC Endpoints

| Provider | URL |
|----------|-----|
| LlamaRPC | https://eth.llamarpc.com |
| Ankr | https://rpc.ankr.com/eth |
| PublicNode | https://ethereum.publicnode.com |
| Cloudflare | https://cloudflare-eth.com |

## Notes

- Addresses are 0x-prefixed hex (42 characters)
- 1 ETH = 10^18 wei
- Gas prices fluctuate; check before transactions
- Rate limits apply on public RPCs
- Use `--rpc-url` or set `ETH_RPC_URL` environment variable
