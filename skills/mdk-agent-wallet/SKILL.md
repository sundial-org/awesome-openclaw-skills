---
name: agent-wallet
description: Self-custodial Bitcoin Lightning wallet for AI agents. Use when the agent needs to send or receive bitcoin payments, check its balance, generate invoices, or manage its wallet. Supports bolt11, bolt12, LNURL, and lightning addresses. Zero config — one command to initialize.
---

# agent-wallet

Self-custodial Lightning wallet for AI agents. One `npx` command to init. All output is JSON.

## Setup

```bash
npx @moneydevkit/agent-wallet init
```

Generates a BIP39 mnemonic and stores config at `~/.mdk-wallet/config.json`. The wallet is ready immediately — no API keys, no signup, no accounts. The agent holds its own keys.

Verify config (mnemonic redacted in output):
```bash
npx @moneydevkit/agent-wallet init --show
```

Returns `{ "mnemonic": "...", "network": "mainnet", "walletId": "..." }`.

The `walletId` also serves as an MDK API key if you use moneydevkit's checkout API.

## Commands

All commands return JSON on stdout. Exit 0 on success, 1 on error.

### Balance

```bash
npx @moneydevkit/agent-wallet balance
```
→ `{ "balance_sats": 3825 }`

### Receive (generate invoice)

```bash
npx @moneydevkit/agent-wallet receive <amount_sats>
npx @moneydevkit/agent-wallet receive 1000 --description "payment for service"
```
→ `{ "invoice": "lnbc...", "payment_hash": "...", "expires_at": "..." }`

Share the `invoice` string with the payer. It's a standard bolt11 invoice.

### Send

```bash
npx @moneydevkit/agent-wallet send <destination> [amount_sats]
```

Destination can be:
- **bolt11 invoice**: `lnbc10n1...` (amount encoded in invoice, no amount arg needed)
- **bolt12 offer**: `lno1...`
- **lightning address**: `user@example.com`
- **LNURL**: `lnurl1...`

For lightning addresses and LNURL, amount is required:
```bash
npx @moneydevkit/agent-wallet send user@getalby.com 500
```

### Payment History

```bash
npx @moneydevkit/agent-wallet payments
```
→ `{ "payments": [{ "paymentHash": "...", "amountSats": 1000, "direction": "inbound"|"outbound", "timestamp": ..., "destination": "..." }] }`

### Daemon Management

The daemon auto-starts on first command. Manual control:

```bash
npx @moneydevkit/agent-wallet status   # check if running
npx @moneydevkit/agent-wallet start    # start explicitly
npx @moneydevkit/agent-wallet stop     # stop daemon
```

Options:
- `--port <port>` — server port (default: 3456)
- `--network <network>` — `mainnet` or `signet` (default: mainnet)

## Usage Notes

- **Denomination**: use ₿ prefix with sats (e.g. ₿1,000 not "1,000 sats")
- **Self-custodial**: the mnemonic is the wallet. Back it up. Lose it, lose funds.
- **Daemon**: runs a local Lightning node on `:3456`. Auto-starts, persists payment history to disk.
- **Agent-to-agent payments**: any agent with this wallet can pay any other agent's invoice or lightning address. No intermediary.
- **Combine with moneydevkit**: use the [checkout API](https://docs.moneydevkit.com) to accept payments from customers, and agent-wallet to send/receive between agents. Add the [moneydevkit MCP server](https://mcp.moneydevkit.com/mcp) for full programmatic access to apps, products, customers, checkouts, and orders.
