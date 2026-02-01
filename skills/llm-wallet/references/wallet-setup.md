# LLM Wallet Setup Guide

## Installation

### Prerequisites
- Node.js 20+
- npm or pnpm

### Install LLM Wallet MCP
```bash
npm install -g llm-wallet-mcp
```

Or via npx (no install needed):
```bash
npx llm-wallet-mcp
```

## First Time Setup

### 1. Create Wallet
```bash
llm-wallet create --label "my-agent-wallet"
```

**Output:**
```json
{
  "success": true,
  "address": "0x742d35Cc6635C0532925a3b8D2A0a7e3E4b1b4e4",
  "label": "my-agent-wallet",
  "network": "polygon-amoy"
}
```

**Important**: Save this address! You'll need it to fund the wallet.

### 2. Set Spending Limits (Recommended)
```bash
llm-wallet set-limit --per-tx 0.10 --daily 5.00
```

This sets:
- Max $0.10 per transaction
- Max $5.00 per day

### 3. Fund Your Wallet

#### Testnet (polygon-amoy)
1. Visit: https://faucet.polygon.technology/
2. Select "USDC" token
3. Select "Polygon Amoy" network
4. Paste your wallet address
5. Request testnet USDC (free, no real value)

#### Mainnet (polygon)
1. **⚠️ Use real money carefully!**
2. Send USDC to your wallet address via:
   - Centralized exchange (Coinbase, Binance)
   - DEX (Uniswap)
   - Bridge from Ethereum

### 4. Verify Balance
```bash
llm-wallet balance
```

**Output:**
```json
{
  "address": "0x742d35...",
  "network": "polygon-amoy",
  "usdc": "10.000000",
  "native": "0.5"
}
```

## Configuration

### Environment Variables

Create `.env` file or export:
```bash
export WALLET_ENCRYPTION_KEY="your-32-char-encryption-key-here-secure"
export WALLET_NETWORK="polygon-amoy"  # or "polygon" for mainnet
```

**Auto-Generation**: If `WALLET_ENCRYPTION_KEY` is not set, one will be generated automatically.

### Network Selection

**Testnet (Default - Recommended)**
```bash
export WALLET_NETWORK="polygon-amoy"
```

**Mainnet (Use with Caution)**
```bash
export WALLET_NETWORK="polygon"
```

## Security Best Practices

### 1. Encryption Key
- Generate secure 32+ character key
- Never commit to git
- Store in environment variable or secure vault
- Example generation:
  ```bash
  openssl rand -hex 32
  ```

### 2. Spending Limits
- Always set limits before making payments
- Start conservative (per-tx: $0.10, daily: $5.00)
- Monitor usage regularly
- Adjust based on needs

### 3. Network Safety
- **Always test on polygon-amoy first**
- Testnet USDC has no real value
- Verify network before mainnet usage
- Double-check facilitator URL

### 4. Wallet Backup
- Wallet storage: `~/.llm-wallet/`
- Backup this directory (encrypted)
- Or export/save private key securely
- Test restore procedure

## Troubleshooting

### "llm-wallet-mcp not found"
```bash
npm install -g llm-wallet-mcp
# or
npm install llm-wallet-mcp
```

### "Insufficient balance"
- Check balance: `llm-wallet balance`
- Fund via faucet (testnet) or exchange (mainnet)
- Verify network matches funding source

### "Payment exceeds limit"
- Check limits: `llm-wallet get-limits`
- Increase limits: `llm-wallet set-limit --per-tx 1.00 --daily 10.00`
- View usage: `llm-wallet history`

### "Wallet not found"
- Create wallet: `llm-wallet create`
- Or import: `llm-wallet import --private-key <key>`

### "Network timeout"
- Check internet connection
- Verify RPC URL (auto-configured)
- Try again (automatic retry logic)

## Multi-Wallet Management

### Create Named Wallets
```bash
llm-wallet create --label "production"
llm-wallet create --label "testing"
llm-wallet create --label "development"
```

### List Wallets
```bash
llm-wallet list-wallets
```

### Switch Active Wallet
```bash
llm-wallet set-active --label "production"
```

## Network Information

### Polygon Testnet (Amoy)
- Chain ID: 80002
- RPC: https://rpc-amoy.polygon.technology
- USDC: 0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582
- Facilitator: https://x402-amoy.polygon.technology
- Faucet: https://faucet.polygon.technology/

### Polygon Mainnet
- Chain ID: 137
- RPC: https://polygon-rpc.com
- USDC: 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359
- Facilitator: https://x402.polygon.technology
- Explorer: https://polygonscan.com/

## Support

- GitHub: https://github.com/x402/llm-wallet-mcp
- Discord: https://discord.gg/x402
- Docs: https://docs.x402.org/
