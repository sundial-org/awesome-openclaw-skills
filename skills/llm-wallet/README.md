# LLM Wallet Skill for OpenClaw

Enable OpenClaw agents to own crypto wallets and make x402 micropayments with USDC stablecoins.

## What This Skill Does

- **Wallet Management**: Create, import, and manage HD wallets with encryption
- **Check Balance**: View USDC and native token balances
- **Spending Limits**: Set per-transaction and daily spending caps
- **x402 Payments**: Make micropayments to paid APIs using USDC
- **Dynamic APIs**: Register paid APIs as reusable tools
- **Transaction History**: Track all payments and transactions

## Installation

### Prerequisites
- Node.js 20+
- OpenClaw installed

### Install Skill

**Option 1: Via ClawHub (Recommended)**
```bash
clawhub install llm-wallet
```

**Option 2: Manual Installation**
```bash
# Clone or copy this skill directory to your workspace
cp -r skills/llm-wallet ~/.openclaw/workspace/skills/

# Install MCP server
npm install -g llm-wallet-mcp
```

### Add to PATH
```bash
# Add to your shell profile (~/.bashrc, ~/.zshrc)
export PATH="/Users/agada/openclaw/skills/llm-wallet/bin:$PATH"
```

## Quick Start

### 1. Create Wallet
```bash
llm-wallet create --label "my-agent-wallet"
```

### 2. Set Spending Limits
```bash
llm-wallet set-limit --per-tx 0.10 --daily 5.00
```

### 3. Fund Wallet (Testnet)
Visit: https://faucet.polygon.technology/
- Select "USDC" token
- Select "Polygon Amoy" network
- Paste your wallet address
- Request testnet USDC (free)

### 4. Check Balance
```bash
llm-wallet balance
```

### 5. Make Payment (with Agent)
```
User: "What's the weather in London?"

Agent: "I'll check the weather API. Cost: $0.001 USDC. Approve?"

User: "Yes"

Agent executes: llm-wallet pay "https://api.weather.com/current?location=London"
```

## Usage in OpenClaw

### Agent Workflow

The agent will automatically:
1. Detect when paid APIs are needed
2. Check cost via `llm-wallet check-payment`
3. Ask user for approval
4. Execute payment via `llm-wallet pay`
5. Return API response with transaction confirmation

### Example Conversation

```
User: Translate "hello" to Spanish using a paid translation API

Agent: I found a translation API. The cost is $0.002 USDC.
       Your limits: $0.10 per transaction, $4.98 remaining today.
       Approve this payment?

User: Yes, approved

Agent: [Executes: llm-wallet pay "https://api.translate.com/v1?text=hello&to=es"]
       Translation: "hola"
       Payment completed: 0.002 USDC
       Transaction: 0xabc123...
       Remaining daily limit: $4.978
```

## Commands Available to Agents

### Wallet Commands
- `llm-wallet create` - Create new wallet
- `llm-wallet balance` - Check USDC balance
- `llm-wallet history` - View transactions

### Payment Commands
- `llm-wallet check-payment <url>` - Pre-check cost
- `llm-wallet pay <url>` - Make payment (requires approval!)
- `llm-wallet set-limit --per-tx <amt> --daily <amt>` - Set limits

### API Management
- `llm-wallet register-api <url> --name <tool>` - Register API
- `llm-wallet list-apis` - Show registered APIs
- `llm-wallet call-api <tool> --params <json>` - Call API

## Configuration

### Environment Variables

```bash
# Network (default: polygon-amoy testnet)
export WALLET_NETWORK="polygon-amoy"

# Encryption key (auto-generated if not set)
export WALLET_ENCRYPTION_KEY="your-secure-32-char-key-here"

# Custom facilitator (optional)
export FACILITATOR_URL="https://x402-amoy.polygon.technology"

# Storage directory (default: ~/.llm-wallet)
export STORAGE_DIR="$HOME/.llm-wallet"
```

### OpenClaw Config

Add to `~/.openclaw/config.json5`:

```json5
{
  "skills": {
    "entries": {
      "llm_wallet": {
        "enabled": true,
        "env": {
          "WALLET_NETWORK": "polygon-amoy",
          "WALLET_ENCRYPTION_KEY": "${WALLET_ENCRYPTION_KEY}"
        }
      }
    }
  }
}
```

## Security

### Default Safety Measures
1. **Network**: Defaults to testnet (polygon-amoy)
2. **Approvals**: Agent always asks before payments
3. **Spending Limits**: Per-transaction and daily caps
4. **Encryption**: Wallets encrypted with AES-256-GCM
5. **Logging**: All transactions logged with timestamps

### Best Practices
- Start with testnet (polygon-amoy)
- Set conservative spending limits
- Review transaction history regularly
- Never commit encryption keys to git
- Test thoroughly before mainnet use

## Networks

### Polygon Testnet (Amoy) - Default
- **Chain ID**: 80002
- **Facilitator**: https://x402-amoy.polygon.technology
- **USDC**: 0x41E94Eb019C0762f9Bfcf9Fb1E58725BfB0e7582
- **Faucet**: https://faucet.polygon.technology/
- **Safe for testing** (no real money)

### Polygon Mainnet
- **Chain ID**: 137
- **Facilitator**: https://x402.polygon.technology
- **USDC**: 0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359
- **⚠️ Real money** - use with caution

## Documentation

- **SKILL.md** - Complete command reference
- **references/x402-protocol.md** - x402 payment protocol overview
- **references/wallet-setup.md** - Detailed setup guide
- **references/examples.md** - Usage examples and workflows

## Troubleshooting

### Command Not Found
```bash
# Check if llm-wallet is in PATH
which llm-wallet

# If not, add to PATH:
export PATH="/Users/agada/openclaw/skills/llm-wallet/bin:$PATH"
```

### MCP Server Not Found
```bash
npm install -g llm-wallet-mcp
# or
npx llm-wallet-mcp
```

### Insufficient Balance
```bash
# Check balance
llm-wallet balance

# Fund via testnet faucet
# Visit: https://faucet.polygon.technology/
```

### Payment Failed
```bash
# Check limits
llm-wallet get-limits

# Check history for errors
llm-wallet history

# Verify network configuration
echo $WALLET_NETWORK  # Should be "polygon-amoy"
```

## Examples

See `references/examples.md` for complete workflows including:
- First time user setup
- Making payments with approval
- Registering and using paid APIs
- Monitoring usage and limits
- Error handling scenarios

## Support

- **GitHub**: https://github.com/x402/llm-wallet-mcp
- **x402 Protocol**: https://www.x402.org/
- **OpenClaw Docs**: https://docs.openclaw.ai/
- **ClawHub**: https://clawhub.com/

## License

MIT License - See LICENSE file for details

## Contributing

Contributions welcome! Please:
1. Test on polygon-amoy testnet
2. Include examples in PR description
3. Update documentation as needed
4. Follow OpenClaw skill conventions

## Version

**v1.0.0** - Initial release with core wallet and x402 payment functionality
