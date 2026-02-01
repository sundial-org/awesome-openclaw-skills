---
name: solflare
description: Work with Solflare wallet - manage Solana assets, staking, custom RPC setup, hardware wallet integration, and NFT management.
metadata: {"openclaw":{"requires":{"bins":["solana"]},"install":[{"id":"solana","kind":"shell","command":"sh -c \"$(curl -sSfL https://release.solana.com/stable/install)\"","bins":["solana"],"label":"Install Solana CLI"}]}}
---

# Solflare Wallet

## Installation

- Web: https://solflare.com/access
- Chrome: https://chrome.google.com/webstore/detail/solflare-wallet/bhhhlbepdkbapadjdnnojkbgioiodbic
- Mobile: iOS App Store / Google Play

## Supported Features

| Feature | Supported |
|---------|-----------|
| Solana | Yes |
| SPL Tokens | Yes |
| NFTs | Yes |
| Staking | Yes (built-in) |
| Ledger | Yes |
| dApp Browser | Yes |

## Configure Custom RPC

Settings → Network → Custom RPC

Recommended RPCs:
```
Helius: https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
QuickNode: https://YOUR_ENDPOINT.solana-mainnet.quiknode.pro/
Triton: https://YOUR_PROJECT.triton.one/
GenesysGo: https://ssc-dao.genesysgo.net/
```

## Staking SOL

1. Portfolio → Staking → Stake
2. Choose validator or use Solflare's stake pool
3. Enter amount
4. Confirm transaction

Check stake via CLI:
```bash
solana stakes YOUR_ADDRESS --url mainnet-beta
```

## View Stake Accounts

```bash
solana stake-account YOUR_STAKE_ACCOUNT_ADDRESS --url mainnet-beta
```

List all stakes:
```bash
curl -s -X POST https://api.mainnet-beta.solana.com -H "Content-Type: application/json" -d '{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "getProgramAccounts",
  "params": [
    "Stake11111111111111111111111111111111111111",
    {
      "encoding": "jsonParsed",
      "filters": [
        {"memcmp": {"offset": 12, "bytes": "YOUR_ADDRESS"}}
      ]
    }
  ]
}'
```

## Import Tokens

Portfolio → Manage Token List → Add Token

Paste contract address:
```
USDC: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
USDT: Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB
mSOL: mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So
stSOL: 7dHbWXmci3dT8UFYWYZweBLXgycu7Y3iL6trKn1Y7ARj
```

## Check Balances (CLI)

SOL balance:
```bash
solana balance YOUR_SOLFLARE_ADDRESS
```

Token balances:
```bash
spl-token accounts --owner YOUR_SOLFLARE_ADDRESS
```

## NFT Management

Portfolio → NFTs tab

View NFTs via CLI:
```bash
# Install metaboss
cargo install metaboss

# List NFTs
metaboss snapshot mints -c YOUR_ADDRESS -o nfts.json
```

## Hardware Wallet (Ledger)

1. Install Solana app on Ledger
2. In Solflare: Add Wallet → Hardware Wallet → Ledger
3. Connect and select address

Check Ledger address:
```bash
solana-keygen pubkey usb://ledger
```

## Transaction History

Via Solscan:
```
https://solscan.io/account/YOUR_ADDRESS
```

Via CLI:
```bash
solana transaction-history YOUR_ADDRESS --limit 10
```

## Priority Fees

Settings → Priority Fee
- Market: Dynamic based on network
- Custom: Set exact amount in lamports

## Collectibles (NFTs)

View metadata:
```bash
metaboss decode mint -a NFT_MINT_ADDRESS
```

## Connected dApps

Settings → Connected Apps → Manage

## Export for CLI Usage

Settings → Export → Show recovery phrase

Create keypair file:
```bash
solana-keygen recover -o ~/my-solflare.json
```

## Troubleshooting

**Staking not showing:**
```bash
# Verify stake accounts
solana stakes YOUR_ADDRESS
```

**Transaction failed:**
```bash
# Check recent blockhash
solana block-time $(solana slot)
```

**Token balance wrong:**
```bash
# Get actual balance
spl-token balance TOKEN_MINT --owner YOUR_ADDRESS
```

## Solflare vs Phantom

| Feature | Solflare | Phantom |
|---------|----------|---------|
| Chains | Solana only | Multi-chain |
| Staking UI | Advanced | Basic |
| Ledger | Full support | Full support |
| Web version | Yes | No |
| Validators | Choose any | Limited |

## Notes

- Solflare is Solana-focused (no EVM chains)
- Built-in staking with validator selection
- Web version works without extension
- Supports Ledger and Keystone hardware wallets
- Professional staking analytics
- NFT bulk management features
