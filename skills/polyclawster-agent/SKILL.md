---
name: polyclawster-agent
description: Trade on Polymarket prediction markets. Non-custodial — your agent generates a Polygon wallet locally, signs orders with its own private key, and submits via polyclawster.com relay (geo-bypass). Private key never leaves your machine.
metadata:
  {
    "openclaw": {
      "requires": { "bins": ["node"] },
      "permissions": {
        "network": [
          "polyclawster.com",
          "polygon-rpc.com"
        ],
        "fs": {
          "write": ["~/.polyclawster/config.json"],
          "read":  ["~/.polyclawster/config.json"]
        }
      },
      "credentials": [
        {
          "key": "POLYCLAWSTER_API_KEY",
          "description": "Agent API key (auto-generated at setup, stored in ~/.polyclawster/config.json). Not a private key — just for polyclawster.com portfolio/demo API.",
          "required": false
        }
      ]
    }
  }
---

# polyclawster-agent

Trade on [Polymarket](https://polymarket.com) prediction markets with your OpenClaw agent.

## How to use with OpenClaw

After installing this skill, just talk to your agent naturally:

```
"Set me up to trade Polymarket in demo mode"
→ runs: node scripts/setup.js --auto

"Browse crypto markets on Polymarket"
→ runs: node scripts/browse.js "crypto"

"Place a $2 demo bet on bitcoin reaching 100k"
→ runs: node scripts/trade.js --market "bitcoin-100k" --side YES --amount 2 --demo

"Show my Polymarket balance"
→ runs: node scripts/balance.js

"Auto-trade Polymarket every hour with score above 8"
→ sets up OpenClaw cron: node scripts/auto.js --min-score 8 --max-bet 5 --demo
```

Your agent understands the skill context and can chain commands — e.g. browse → pick market → trade.

## OpenClaw Cron Setup

Ask your agent to set up autonomous trading:

> *"Run polyclawster auto-trade every 30 minutes in demo mode"*

Or set up manually — tell your agent:

```
Create a cron job that runs every 30 minutes:
  node /path/to/polyclawster/scripts/auto.js --demo --min-score 7 --max-bet 5
```

The agent will handle the cron setup via the `cron` tool automatically.

## Architecture — Non-Custodial

**Your private key stays on your machine. Always.**

```
Your Agent Container:
  ├─ generates wallet locally (ethers.Wallet.createRandom())
  ├─ signs orders locally (EIP-712 with private key)
  ├─ signs requests locally (HMAC with api_secret)
  └─ private key: ~/.polyclawster/config.json (chmod 600) only

polyclawster.com:
  ├─ stores: wallet_address, demo_balance, trade_history
  ├─ does NOT store: private key, CLOB api_secret
  ├─ /api/clob-relay: geo-bypass proxy → clob.polymarket.com (Tokyo)
  ├─ /api/signals: AI-scored trading opportunities
  └─ /api/agents: portfolio, leaderboard, TMA visibility

Polymarket CLOB:
  └─ receives already-signed orders, verifies EIP-712 signature
```

## Quick Start

### 1. Setup (generates wallet locally)
```bash
node scripts/setup.js --auto
```

### 2. Browse markets
```bash
node scripts/browse.js "bitcoin"
node scripts/browse.js "election" --min-volume 100000
```

### 3. Demo trade (free $10 balance)
```bash
node scripts/trade.js --market "bitboy-convicted" --side YES --amount 2 --demo
```

### 4. Check balance & open positions
```bash
node scripts/balance.js
```

### 5. Live trading (after depositing USDC to your wallet)
```bash
node scripts/approve.js         # one-time USDC approval (~0.01 POL gas)
node scripts/trade.js --market "bitboy-convicted" --side YES --amount 10
```

### 6. Auto-trade on AI signals
```bash
node scripts/auto.js --dry-run                         # preview
node scripts/auto.js --demo --min-score 7 --max-bet 5  # demo mode
node scripts/auto.js --min-score 8 --max-bet 10        # live mode
```

## Security Model

| What | Where stored | Who can see it |
|------|-------------|----------------|
| Private key | `~/.polyclawster/config.json` (chmod 600) | Only your machine |
| CLOB api_secret | `~/.polyclawster/config.json` | Only your machine |
| CLOB api_key | `~/.polyclawster/config.json` | Your machine + Polymarket |
| Wallet address | polyclawster.com + Polygon chain | Public |
| Trade history | polyclawster.com Supabase | polyclawster.com |

## Scripts Reference

| Script | Description |
|--------|-------------|
| `setup.js --auto` | Generate wallet, derive CLOB creds, register |
| `setup.js --derive-clob` | Re-derive CLOB credentials |
| `setup.js --info` | Show current config |
| `approve.js` | One-time on-chain USDC approval for live trading |
| `approve.js --check` | Check approval status (no tx) |
| `browse.js [topic]` | Search Polymarket markets |
| `trade.js --market X --side YES --amount N` | Live trade (locally signed) |
| `trade.js ... --demo` | Demo trade |
| `balance.js` | Portfolio & balance |
| `sell.js --list` | List open positions |
| `sell.js --bet-id N` | Close a position |
| `auto.js` | Autonomous trading loop on AI signals |
| `auto.js --dry-run` | Simulate without trading |
| `link.js PC-XXXXX` | Link to TMA account |

## Agent Dashboard

After setup: `https://polyclawster.com/a/YOUR_AGENT_ID`

Built by [Virix Labs](https://virixlabs.com) · [polyclawster.com](https://polyclawster.com)
