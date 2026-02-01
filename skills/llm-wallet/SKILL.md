---
name: llm_wallet
description: Manage crypto wallets and make x402 micropayments with USDC stablecoins on Polygon
homepage: https://github.com/x402/llm-wallet-mcp
metadata: {"openclaw": {"emoji": "💰", "requires": {"bins": ["node"]}, "install": [{"id": "node", "kind": "node", "package": "llm-wallet-mcp", "bins": ["llm-wallet-mcp"], "label": "Install LLM Wallet MCP (node)"}]}}
---

# LLM Wallet - Crypto Wallet & x402 Micropayments

Use `llm-wallet` commands to manage crypto wallets and make micropayments to paid APIs using USDC stablecoins on Polygon blockchain.

**Default Network**: Polygon Testnet (polygon-amoy) - safe for testing
**Facilitator**: https://x402-amoy.polygon.technology

## Quick Start

```bash
# Create wallet
llm-wallet create

# Check balance
llm-wallet balance

# Set spending limits (recommended)
llm-wallet set-limit --per-tx 0.10 --daily 5.00

# View transaction history
llm-wallet history
```

## Wallet Management

### Create Wallet
```bash
llm-wallet create [--label <name>]
```
Creates a new HD wallet with encryption. Returns wallet address.

**Example:**
```bash
llm-wallet create --label "agent-wallet"
```

### Import Wallet
```bash
llm-wallet import --private-key <key> [--label <name>]
```
Import existing wallet from private key.

### Check Balance
```bash
llm-wallet balance
```
Shows USDC balance and native token balance on current network.

### Transaction History
```bash
llm-wallet history
```
View all transactions and payments made from this wallet.

## Spending Limits

### Set Limits
```bash
llm-wallet set-limit --per-tx <amount> --daily <amount>
```
Set per-transaction and daily spending caps in USDC.

**Example:**
```bash
llm-wallet set-limit --per-tx 0.10 --daily 5.00
```

### Check Limits
```bash
llm-wallet get-limits
```
View current spending limits and daily usage.

## x402 Payments

### Make Payment
```bash
llm-wallet pay <url> [--method GET|POST] [--body <json>]
```
Make x402 micropayment to a paid API endpoint.

**⚠️ IMPORTANT: Always ask user for approval before making payments!**

**Example:**
```bash
# Ask user: "I need to make a payment to https://api.example.com/weather. Cost: $0.001 USDC. Approve?"
llm-wallet pay "https://api.example.com/weather?location=London"
```

**Workflow:**
1. Check if payment is needed: `llm-wallet check-payment <url>`
2. Show user: URL, estimated cost, current limits
3. Wait for user approval
4. Execute: `llm-wallet pay <url>`
5. Confirm completion and show transaction ID

### Check Payment (Pre-flight)
```bash
llm-wallet check-payment <url>
```
Checks if wallet can afford payment without executing it.

## Dynamic API Registration

### Register API
```bash
llm-wallet register-api <url> --name <tool_name>
```
Register a paid API endpoint as a reusable tool.

**Example:**
```bash
llm-wallet register-api "https://api.example.com/weather" --name weather_api
```

### List Registered APIs
```bash
llm-wallet list-apis
```
Show all registered API tools.

### Call Registered API
```bash
llm-wallet call-api <tool_name> [--params <json>]
```
Execute a registered API tool. Requires approval if payment needed.

**Example:**
```bash
# Ask user for approval first if cost > 0
llm-wallet call-api weather_api --params '{"location": "London"}'
```

### Unregister API
```bash
llm-wallet unregister-api <tool_name>
```
Remove a registered API tool.

## Seller Tools (Advanced)

### Verify Payment
```bash
llm-wallet verify-payment --header <x-payment-header> --requirements <json>
```
Verify incoming payment from a buyer (seller-side).

### Create Payment Requirements
```bash
llm-wallet create-requirements --price <amount> --pay-to <address> --url <resource-url>
```
Generate payment requirements for a protected resource.

## Safety Rules

1. **Network Default**: Always uses polygon-amoy (testnet) unless configured otherwise
2. **Approval Required**: Always ask user before making payments
3. **Spending Limits**: Check limits before payment attempts
4. **Transaction Logging**: All payments are logged with timestamps
5. **Encryption**: Wallets are encrypted with AES-256-GCM

## Configuration

### Environment Variables
- `WALLET_ENCRYPTION_KEY` - Wallet encryption key (32+ chars, auto-generated if missing)
- `WALLET_NETWORK` - Network selection (default: `polygon-amoy` | `polygon`)
- `FACILITATOR_URL` - Custom facilitator URL (auto-configured)
- `WALLET_MAX_TX_AMOUNT` - Per-transaction limit override
- `WALLET_DAILY_LIMIT` - Daily limit override

### Network Info
- **Polygon Testnet (Amoy)**: Chain ID 80002, Facilitator: https://x402-amoy.polygon.technology
- **Polygon Mainnet**: Chain ID 137, Facilitator: https://x402.polygon.technology

## Common Workflows

### First Time Setup
```bash
# 1. Create wallet
llm-wallet create --label "my-agent"

# 2. Set spending limits
llm-wallet set-limit --per-tx 0.10 --daily 5.00

# 3. Check balance (will be 0 initially)
llm-wallet balance

# 4. Fund wallet with testnet USDC
# User needs to: visit https://faucet.polygon.technology/
```

### Making a Payment
```bash
# 1. Pre-check payment
llm-wallet check-payment "https://api.example.com/weather?location=London"

# 2. Show user: URL, cost estimate, current limits
# 3. Ask user: "Approve payment of $0.001 USDC to https://api.example.com/weather?"

# 4. If approved, execute payment
llm-wallet pay "https://api.example.com/weather?location=London"

# 5. Confirm and show transaction ID
llm-wallet history
```

### Registering a Paid API
```bash
# 1. Register the API
llm-wallet register-api "https://api.example.com/translate" --name translate_api

# 2. List available APIs
llm-wallet list-apis

# 3. Call the API (with approval)
llm-wallet call-api translate_api --params '{"text": "hello", "to": "es"}'

# 4. View payment in history
llm-wallet history
```

## Error Handling

- **Insufficient Balance**: Show error and guide user to faucet (testnet) or funding instructions (mainnet)
- **Payment Rejected**: Transaction reverted, check error message for details
- **Limit Exceeded**: Show current limits and daily usage, suggest increasing limits
- **Network Timeout**: Retry with exponential backoff (max 3 attempts)

## References

See `references/` folder for:
- `x402-protocol.md` - x402 payment protocol overview
- `wallet-setup.md` - Detailed wallet setup guide
- `examples.md` - More usage examples

## Notes

- All amounts are in USDC (6 decimals)
- Default network is testnet for safety
- Testnet USDC has no real value
- Always verify network before mainnet usage
- Keep encryption key secure (never share or commit)
