---
name: solana
description: Interact with Solana blockchain - check balances, view transactions, monitor NFTs, and explore account data. Works with Phantom and Solflare addresses.
metadata: {"openclaw":{"requires":{"bins":["solana"]},"install":[{"id":"solana","kind":"shell","command":"sh -c \"$(curl -sSfL https://release.solana.com/stable/install)\"","bins":["solana"],"label":"Install Solana CLI"}]}}
---

# Solana Wallet CLI

## Setup

Install Solana CLI:
```bash
sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
```

Set mainnet RPC:
```bash
solana config set --url https://api.mainnet-beta.solana.com
```

## Check Balance

SOL balance:
```bash
solana balance <ADDRESS>
```

In lamports:
```bash
solana balance <ADDRESS> --lamports
```

## View Account Info

```bash
solana account <ADDRESS>
```

Detailed JSON output:
```bash
solana account <ADDRESS> --output json
```

## Transaction History

Recent transactions:
```bash
solana transaction-history <ADDRESS> --limit 10
```

Transaction details:
```bash
solana confirm <SIGNATURE> -v
```

## Token Balances (SPL Tokens)

List all tokens:
```bash
spl-token accounts --owner <ADDRESS>
```

Specific token balance:
```bash
spl-token balance <TOKEN_MINT> --owner <ADDRESS>
```

## NFT & Token Info

Using Metaboss (NFT tool):
```bash
# Install
cargo install metaboss

# Get NFT metadata
metaboss decode mint -a <NFT_MINT_ADDRESS>
```

## Stake Accounts

View stake:
```bash
solana stakes <ADDRESS>
```

## Using Public RPC Endpoints

```bash
# Mainnet
solana config set --url https://api.mainnet-beta.solana.com

# Devnet (testing)
solana config set --url https://api.devnet.solana.com

# Custom RPC
solana config set --url https://your-rpc-provider.com
```

## Quick Balance Check (curl)

```bash
curl -X POST https://api.mainnet-beta.solana.com -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getBalance",
  "params": ["<ADDRESS>"]
}' | python3 -c "import sys,json; d=json.load(sys.stdin); print(f\"{d['result']['value']/1e9:.4f} SOL\")"
```

## Get Token Accounts (curl)

```bash
curl -X POST https://api.mainnet-beta.solana.com -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getTokenAccountsByOwner",
  "params": [
    "<ADDRESS>",
    {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
    {"encoding": "jsonParsed"}
  ]
}'
```

## Monitor Address

Watch for changes:
```bash
watch -n 5 "solana balance <ADDRESS>"
```

## Common Addresses

| Name | Address |
|------|---------|
| SOL Mint | So11111111111111111111111111111111111111112 |
| USDC | EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v |
| USDT | Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB |

## Notes

- Addresses are base58 encoded public keys
- 1 SOL = 1,000,000,000 lamports
- RPC rate limits apply on public endpoints
- For heavy usage, consider paid RPC providers (Helius, QuickNode, Alchemy)
