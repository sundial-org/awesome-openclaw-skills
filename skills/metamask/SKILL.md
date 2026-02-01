---
name: metamask
description: Work with MetaMask wallet - add custom networks, import ERC-20 tokens, manage permissions, configure gas settings, and integrate with dApps.
metadata: {"openclaw":{"requires":{"bins":["cast"]},"install":[{"id":"foundry","kind":"shell","command":"curl -L https://foundry.paradigm.xyz | bash && foundryup","bins":["cast"],"label":"Install Foundry (cast)"}]}}
---

# MetaMask Wallet

## Installation

- Chrome: https://chrome.google.com/webstore/detail/metamask/nkbihfbeogaeaoehlefnkodbefgpgknn
- Firefox: https://addons.mozilla.org/firefox/addon/ether-metamask/
- Mobile: iOS App Store / Google Play
- Flask (dev): https://metamask.io/flask/

## Add Popular Networks

Settings → Networks → Add Network

**Polygon:**
```
Network: Polygon Mainnet
RPC: https://polygon-rpc.com
Chain ID: 137
Symbol: MATIC
Explorer: https://polygonscan.com
```

**Arbitrum:**
```
Network: Arbitrum One
RPC: https://arb1.arbitrum.io/rpc
Chain ID: 42161
Symbol: ETH
Explorer: https://arbiscan.io
```

**Optimism:**
```
Network: Optimism
RPC: https://mainnet.optimism.io
Chain ID: 10
Symbol: ETH
Explorer: https://optimistic.etherscan.io
```

**Base:**
```
Network: Base
RPC: https://mainnet.base.org
Chain ID: 8453
Symbol: ETH
Explorer: https://basescan.org
```

**BSC:**
```
Network: BNB Smart Chain
RPC: https://bsc-dataseed.binance.org
Chain ID: 56
Symbol: BNB
Explorer: https://bscscan.com
```

**Avalanche:**
```
Network: Avalanche C-Chain
RPC: https://api.avax.network/ext/bc/C/rpc
Chain ID: 43114
Symbol: AVAX
Explorer: https://snowtrace.io
```

## Import ERC-20 Token

Assets → Import Token → Custom Token

Common tokens (Ethereum):
```
USDC: 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
USDT: 0xdAC17F958D2ee523a2206206994597C13D831ec7
DAI: 0x6B175474E89094C44Da98b954EescdeCB5BE3830
WETH: 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
LINK: 0x514910771AF9Ca656af840dff83E8264EcF986CA
UNI: 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
```

## Check Balance (CLI)

ETH balance:
```bash
cast balance YOUR_ADDRESS --ether --rpc-url https://eth.llamarpc.com
```

Token balance:
```bash
cast call 0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48 \
  "balanceOf(address)(uint256)" YOUR_ADDRESS \
  --rpc-url https://eth.llamarpc.com
```

## ENS Names

Resolve ENS:
```bash
cast resolve-name vitalik.eth --rpc-url https://eth.llamarpc.com
```

Reverse lookup:
```bash
cast lookup-address YOUR_ADDRESS --rpc-url https://eth.llamarpc.com
```

## Gas Settings

Settings → Advanced → Advanced Gas Controls

Check current gas:
```bash
cast gas-price --rpc-url https://eth.llamarpc.com | xargs -I {} cast --to-unit {} gwei
```

## Transaction History

Via Etherscan:
```
https://etherscan.io/address/YOUR_ADDRESS
```

Via CLI:
```bash
cast etherscan-source YOUR_ADDRESS --etherscan-api-key YOUR_KEY
```

## Connected Sites

Settings → Connected Sites → Manage permissions

## Account Management

Create account: Account menu → Create Account
Import: Account menu → Import Account

## Hardware Wallet

1. Connect Ledger/Trezor
2. Account menu → Connect Hardware Wallet
3. Select device and address

## Custom Nonce

Settings → Advanced → Customize transaction nonce

Get current nonce:
```bash
cast nonce YOUR_ADDRESS --rpc-url https://eth.llamarpc.com
```

## Speed Up / Cancel Transaction

Pending tx → Speed Up or Cancel

Replace with CLI:
```bash
# Check pending nonce
cast nonce YOUR_ADDRESS --rpc-url https://eth.llamarpc.com
```

## Export Account

Account menu → Account details → Export

## Network RPC Endpoints

| Network | Free RPC |
|---------|----------|
| Ethereum | https://eth.llamarpc.com |
| Polygon | https://polygon-rpc.com |
| Arbitrum | https://arb1.arbitrum.io/rpc |
| Optimism | https://mainnet.optimism.io |
| Base | https://mainnet.base.org |
| BSC | https://bsc-dataseed.binance.org |

## Troubleshooting

**Stuck transaction:**
```bash
# Get pending nonce
cast nonce YOUR_ADDRESS --pending --rpc-url https://eth.llamarpc.com
```
Then send 0 ETH to yourself with same nonce + higher gas

**Wrong token balance:**
Assets → Refresh list, or reimport token

**Network not connecting:**
Settings → Networks → Edit RPC URL

**Reset account:**
Settings → Advanced → Clear activity tab data

## MetaMask Snaps

Extend functionality with Snaps:
Settings → Snaps → Browse Snaps

Popular snaps:
- Transaction Insights
- Account Management
- Interoperability

## Mobile Sync

1. Mobile: Settings → Sync with Extension
2. Scan QR code from extension
3. Or use same recovery phrase

## Security Tips

- Never share recovery phrase
- Verify URLs before connecting
- Review permissions before approving
- Use hardware wallet for large amounts
- Enable phishing detection

## Notes

- MetaMask is EVM-only (Ethereum and compatible chains)
- Default network is Ethereum mainnet
- Supports EIP-1559 transactions
- Built-in swap via aggregators
- Mobile has built-in browser
