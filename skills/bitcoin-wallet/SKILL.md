---
slug: breezclaw
name: BreezClaw
description: "Self-custodial Bitcoin and Lightning wallet for AI agents. Send and receive sats via Lightning Network, Spark, or on-chain Bitcoin. Use when: checking bitcoin balance, sending/receiving payments, generating Lightning invoices, managing wallet operations. Requires the BreezClaw plugin and a Breez API key."
version: 1.0.0
author: onesandzeros-nz
keywords: bitcoin, lightning, wallet, breez, spark, sats, payments, self-custodial, breezclaw
homepage: https://github.com/onesandzeros-nz/BreezClaw
---

# BreezClaw

Self-custodial Bitcoin and Lightning wallet for AI agents. Powered by Breez SDK Spark.

## Install

```bash
# Clone plugin
cd ~/.openclaw/extensions
git clone https://github.com/onesandzeros-nz/BreezClaw.git breezclaw

# Install dependencies and build
cd breezclaw
npm install
npm run build
```

## Configure

### 1. Get Breez API Key

Sign up at https://breez.technology/sdk/

### 2. Add to OpenClaw Config

Edit `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "entries": {
      "breezclaw": {
        "enabled": true,
        "config": {
          "breezApiKey": "YOUR_BREEZ_API_KEY",
          "network": "mainnet"
        }
      }
    }
  }
}
```

### 3. Restart

```bash
openclaw gateway restart
```

## Tools

| Tool | Description |
|------|-------------|
| `wallet_status` | Check wallet exists and connection state |
| `wallet_connect` | Connect or create wallet from mnemonic |
| `wallet_balance` | Get balance in sats and BTC |
| `wallet_receive` | Generate payment request |
| `wallet_prepare_send` | Prepare payment with fee estimate |
| `wallet_send` | Execute confirmed payment |
| `wallet_transactions` | List transaction history |
| `wallet_info` | Detailed wallet info |
| `wallet_backup` | Retrieve mnemonic (sensitive!) |
| `wallet_disconnect` | Clean disconnect |

## Receive Methods

- `spark` — Reusable Spark address (default)
- `spark_invoice` — Spark invoice with amount
- `lightning` — BOLT11 invoice
- `bitcoin` — On-chain address

## Payment Flow

**Always two-step:**

1. `wallet_prepare_send` → Show fees
2. User confirms → `wallet_send(confirmed=true)`

## Security

- Never expose mnemonic unless explicitly requested
- Always show fees before sending
- Require explicit confirmation for sends
- Wallet data: `~/.openclaw/breezclaw/`

## Examples

```
"What's my balance?" → wallet_balance

"Invoice for 1000 sats" → wallet_receive(method="lightning", amount_sats=1000)

"Send 500 sats to user@wallet.com" → resolve LNURL → wallet_prepare_send → confirm → wallet_send
```
