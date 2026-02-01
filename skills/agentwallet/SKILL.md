---
name: Agent Wallet
description: Give your AI agent its own blockchain wallet without ever exposing private keys.
---

# Agent Wallet - Give Your Agent a Wallet with Policies

AgentWallet gives your AI agent its own blockchain wallet -- without ever exposing private keys. You create a wallet, set spending policies, and your agent can transfer tokens and interact with smart contracts within the boundaries you define.

**The agent never sees the private key.** All transactions are executed server-side through a smart account. The wallet owner controls what the agent can do via configurable policies.

## Configuration

- **Base API URL:** Use the `SAFESKILLS_API_URL` environment variable if set, otherwise default to `https://safeskill-production.up.railway.app`
- **Frontend URL:** Use the `SAFESKILLS_FRONTEND_URL` environment variable if set, otherwise default to `https://safeskill-production.up.railway.app`

All API requests require a Bearer token (the API key returned when creating a wallet).

```
Authorization: Bearer <API_KEY>
```

## Quick Start

### 1. Create a Wallet

Create a new smart account wallet for your agent. This generates a private key server-side (you never see it), creates a ZeroDev smart account, and returns an API key for the agent plus a claim URL for the wallet owner.

```bash
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/secrets" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "EVM_WALLET",
    "memo": "My agent wallet",
    "chainId": 11155111
  }'
```

Response includes:
- `apiKey` -- store this securely; use it as the Bearer token for all future requests
- `claimUrl` -- share this with the user so they can claim the wallet and set policies
- `address` -- the smart account address

After creating, tell the user:
> "Here is your wallet claim URL: `<claimUrl>`. Use this to claim ownership, set spending policies, and monitor your agent's wallet activity."

### 2. Get Wallet Address

```bash
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/address" \
  -H "Authorization: Bearer <API_KEY>"
```

### 3. Check Balances

```bash
# Native balance only
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/balance" \
  -H "Authorization: Bearer <API_KEY>"

# With ERC-20 tokens
curl -X GET "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/balance?tokens=0xTokenAddr1,0xTokenAddr2" \
  -H "Authorization: Bearer <API_KEY>"
```

### 4. Transfer ETH or Tokens

```bash
# Transfer native ETH
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/transfer" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipientAddress",
    "amount": "0.01"
  }'

# Transfer ERC-20 token
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/transfer" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xRecipientAddress",
    "amount": "100",
    "token": "0xTokenContractAddress"
  }'
```

### 5. Send Arbitrary Transaction

Interact with any smart contract by sending custom calldata.

```bash
curl -X POST "${SAFESKILLS_API_URL:-https://safeskill-production.up.railway.app}/api/skills/evm-wallet/send-transaction" \
  -H "Authorization: Bearer <API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{
    "to": "0xContractAddress",
    "data": "0xCalldata",
    "value": "0"
  }'
```

## Policies

The wallet owner controls what the agent can do by setting policies via the claim URL. If a transaction violates a policy, the API will reject it or require human approval via Telegram.

| Policy | What it does |
|--------|-------------|
| **Address allowlist** | Only allow transfers/calls to specific addresses |
| **Token allowlist** | Only allow transfers of specific ERC-20 tokens |
| **Function allowlist** | Only allow calling specific contract functions (by 4-byte selector) |
| **Spending limit (per tx)** | Max USD value per transaction |
| **Spending limit (daily)** | Max USD value per rolling 24 hours |
| **Spending limit (weekly)** | Max USD value per rolling 7 days |
| **Require approval** | Every transaction needs human approval via Telegram |
| **Approval threshold** | Transactions above a USD amount need human approval |

If no policies are set, all actions are allowed by default. Once the owner claims the wallet and adds policies, the agent operates within those boundaries.

## Important Notes

- **Never try to access raw secret values.** The private key stays server-side -- that's the whole point.
- Always store the API key from wallet creation -- it's the only way to authenticate.
- Always share the claim URL with the user after creating a wallet.
- The default chain ID `11155111` is Ethereum Sepolia testnet. Adjust as needed.
- If a transaction is rejected, it may be blocked by a policy. Tell the user to check their policy settings via the claim URL.
- If a transaction requires approval, it will return `status: "pending_approval"`. The wallet owner will receive a Telegram notification to approve or deny.
