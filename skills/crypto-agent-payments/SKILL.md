# Crypto Wallets & Payments for AI Agents

Create wallets, transfer tokens, and enable payments between agents. Perfect for bug bounty programs, rewards systems, and agent-to-agent transactions.

## What This Enables

- **Create wallets** - Generate ERC20-compatible wallets with secure key storage
- **Transfer tokens** - Send ETH, USDC, or any ERC20 token to any address
- **Swap tokens** - Exchange tokens across 13 chains with best rates
- **Agent payments** - Bug bounties, rewards programs, automated payouts

## Quick Start

### 1. Install the MCP Server

Add to your Claude Desktop or Moltbot MCP config:

```json
{
  "mcpServers": {
    "onlyswaps": {
      "command": "npx",
      "args": ["-y", "@onlyswaps/mcp-server@latest"]
    }
  }
}
```

Restart your agent after adding.

### 2. Create a Wallet

```
Use setup_wallet to create a new wallet for me.
```

This generates a wallet and securely stores the private key in your environment.

### 3. Fund the Wallet

Send some ETH or tokens to your new wallet address for gas and transfers.

### 4. Make Transfers

```
Transfer 10 USDC to 0x123...abc on Base
```

## Available Tools

| Tool | Description |
|------|-------------|
| `setup_wallet` | Create a new wallet with encrypted key storage |
| `check_setup` | Verify wallet is configured and show balances |
| `transfer` | Send tokens to any address |
| `swap` | Exchange tokens with best rates across DEXs |
| `get_portfolio` | View all token balances |
| `approve_permit2` | Approve tokens for gasless swaps |

## Supported Chains

Ethereum, Base, Arbitrum, Optimism, Polygon, BNB Chain, Avalanche, Gnosis, Scroll, Linea, Blast, Mode, zkSync

## Use Cases

### Bug Bounty Payments
```
Transfer 500 USDC to 0xHunterAddress on Arbitrum as bug bounty payment
```

### Reward Distribution
```
Check my portfolio, then transfer 100 USDC to each of these addresses: 0x123, 0x456, 0x789
```

### Agent-to-Agent Payments
```
Swap 0.1 ETH to USDC on Base, then transfer to the agent's wallet
```

## Environment Variables

After `setup_wallet`, these are set automatically:
- `WALLET_ADDRESS` - Your wallet's public address
- `PRIVATE_KEY` - Encrypted private key (keep secure!)

## Security Notes

- Private keys are stored locally, never transmitted
- Use testnets first (Sepolia, Base Goerli) before mainnet
- Start with small amounts to verify everything works

## Links

- **npm**: [@onlyswaps/mcp-server](https://www.npmjs.com/package/@onlyswaps/mcp-server)
- **Docs**: [onlyswaps.fyi/skill.md](https://onlyswaps.fyi/skill.md)
- **GitHub**: [github.com/Delegueinu/onlyswaps](https://github.com/Delegueinu/onlyswaps)

---

Built by [OnlySwaps](https://onlyswaps.fyi) 🦞
