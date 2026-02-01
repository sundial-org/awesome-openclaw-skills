---
name: phantom
description: Work with Phantom browser extension - add custom networks, import tokens, check connected dApps, troubleshoot issues, and manage Solana/Ethereum/Polygon accounts.
metadata: {"openclaw":{"requires":{"bins":["solana"]},"install":[{"id":"solana","kind":"shell","command":"sh -c \"$(curl -sSfL https://release.solana.com/stable/install)\"","bins":["solana"],"label":"Install Solana CLI"}]}}
---

# Phantom Wallet

## Installation

- Chrome: https://chrome.google.com/webstore/detail/phantom/bfnaelmomeimhlpmgjnjophhpkkoljpa
- Firefox: https://addons.mozilla.org/firefox/addon/phantom-app/
- Brave: Same as Chrome
- Mobile: iOS App Store / Google Play

## Supported Networks

| Network | Type | Native Asset |
|---------|------|--------------|
| Solana | Default | SOL |
| Ethereum | EVM | ETH |
| Polygon | EVM | MATIC |
| Base | EVM | ETH |

## Add Custom RPC (Solana)

Settings → Developer Settings → Change Network → Add Custom RPC

Popular RPCs:
```
Helius: https://mainnet.helius-rpc.com/?api-key=YOUR_KEY
QuickNode: https://YOUR_ENDPOINT.quiknode.pro/
Alchemy: https://solana-mainnet.g.alchemy.com/v2/YOUR_KEY
Triton: https://YOUR_PROJECT.triton.one/
```

## Add Custom Network (EVM)

Settings → Developer Settings → Add Network

Polygon:
```
Name: Polygon Mainnet
RPC: https://polygon-rpc.com
Chain ID: 137
Symbol: MATIC
Explorer: https://polygonscan.com
```

Arbitrum:
```
Name: Arbitrum One
RPC: https://arb1.arbitrum.io/rpc
Chain ID: 42161
Symbol: ETH
Explorer: https://arbiscan.io
```

## Import SPL Token

1. Go to token list
2. Click "Manage Token List"
3. Search or paste contract address
4. Enable token

Common SPL tokens:
```
USDC: EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v
USDT: Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB
RAY: 4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R
BONK: DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263
JUP: JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN
```

## Check Address Balance (CLI)

```bash
solana balance YOUR_PHANTOM_ADDRESS --url https://api.mainnet-beta.solana.com
```

All tokens:
```bash
spl-token accounts --owner YOUR_PHANTOM_ADDRESS --url mainnet-beta
```

## View Transaction History

Via Solscan:
```bash
open "https://solscan.io/account/YOUR_ADDRESS"
```

Via CLI:
```bash
solana transaction-history YOUR_ADDRESS --limit 20
```

## Export Account for CLI

In Phantom: Settings → Security → Export Private Key

Import to Solana CLI (careful with this!):
```bash
solana-keygen recover ASK
```

## Connected Apps Management

Settings → Connected Apps → View/Revoke connections

## Priority Fees

Settings → Transaction Settings → Priority Fee
- Normal: ~0.000005 SOL
- High: ~0.00005 SOL
- Turbo: ~0.0005 SOL

## Troubleshooting

**Transactions stuck:**
```bash
# Check transaction status
solana confirm TX_SIGNATURE -v
```

**Token not showing:**
1. Manage Token List → Search contract
2. Or import manually with address

**Wrong balance:**
Settings → Developer Settings → Reset Cache

**RPC issues:**
Try different RPC endpoint in Developer Settings

## Phantom Deep Links

```
# Open Phantom
phantom://

# Connect to dApp
phantom://browse/YOUR_DAPP_URL

# View transaction
phantom://tx/TX_SIGNATURE
```

## Mobile-Specific

- Face ID / Touch ID: Settings → Security
- Auto-lock: Settings → Security → Auto-Lock Timer
- Testnet: Settings → Developer Settings → Change Network

## Notes

- Phantom derives addresses from single recovery phrase
- Supports hardware wallets (Ledger)
- Built-in swap via Jupiter aggregator
- NFT gallery included
- Browser extension and mobile sync via recovery phrase
