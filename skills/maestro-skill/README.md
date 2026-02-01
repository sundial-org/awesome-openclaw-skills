# Maestro Bitcoin Skill

A comprehensive skill for interacting with the Bitcoin blockchain through the Maestro API platform. Provides complete access to 7 distinct API services with 119 total endpoints covering all aspects of Bitcoin blockchain interaction.

## Overview

This skill enables agents to interact with the Bitcoin blockchain via [Maestro's comprehensive API suite](https://docs.gomaestro.org/bitcoin), including:

- **Blockchain Indexer API** (37 endpoints) - Real-time UTXO data with metaprotocol support
- **Esplora API** (29 endpoints) - Blockstream-compatible REST API
- **Node RPC API** (24 endpoints) - JSON-RPC protocol access
- **Event Manager API** (9 endpoints) - Real-time webhooks and monitoring
- **Market Price API** (8 endpoints) - OHLC data and price analytics
- **Mempool Monitoring API** (9 endpoints) - Mempool-aware operations
- **Wallet API** (6 endpoints) - Address-level activity tracking

### Key Features

✅ **Complete API Coverage** - All 119 endpoints across 7 services
✅ **Metaprotocol Support** - BRC20 tokens, Runes, Inscriptions (Ordinals)
✅ **Mempool Awareness** - Real-time pending transaction tracking
✅ **Event-Driven** - Webhook support for blockchain events
✅ **Market Data** - BTC and Rune price feeds, DEX trading data
✅ **Multi-Network** - Support for both mainnet and testnet4
✅ **Comprehensive Docs** - Detailed API reference and examples

## Quick Start

### 1. Get an API Key

Sign up at [Maestro Dashboard](https://dashboard.gomaestro.org/signup) and create a Bitcoin project to get your API key.

### 2. Configure Environment

```bash
# Set your API key
export MAESTRO_API_KEY="your_api_key_here"

# Optional: Set network (defaults to mainnet)
export MAESTRO_NETWORK="mainnet"  # or "testnet"
```

### 3. Run Commands

```bash
# Get latest block height
./scripts/call_maestro.sh get-latest-height

# Get address balance
./scripts/call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# List all BRC20 tokens
./scripts/call_maestro.sh list-brc20

# Get mempool fee rates
./scripts/call_maestro.sh mempool-get-fee-rates

# View all available commands
./scripts/call_maestro.sh help
```

## What You Can Do

### Address Operations
- Query balances (standard and mempool-aware)
- Get UTXOs and transaction history
- Track address activity and statistics
- Historical balance queries

### Transaction Operations
- Get transaction details with metaprotocol data
- Broadcast transactions (3 different methods)
- Decode transactions and PSBTs
- Track transaction lifecycle from mempool to confirmation

### Block Operations
- Query blocks by height or hash
- Get block transactions and metadata
- Track miner information and block volume
- Query block ranges

### Metaprotocol Support
- **BRC20 Tokens**: List, query, and track BRC20 tokens and holders
- **Runes**: Query runes, holders, activity, and UTXOs
- **Inscriptions (Ordinals)**: Get inscriptions, collections, and content

### Mempool Monitoring
- Real-time fee rate estimation
- Mempool-aware balance and UTXO queries
- Track pending transactions
- Monitor mempool congestion

### Market Data
- BTC price feeds (current and historical)
- Rune token prices
- OHLC data for DEX trading
- Trading pair information

### Event Management
- Set up webhooks for blockchain events
- Monitor address activity
- Track confirmations
- Custom trigger conditions

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation and usage guide
- **[API Reference](references/api_reference.md)** - Detailed documentation for all 119 endpoints
- **[Examples](references/examples.md)** - Real-world usage examples and patterns
- **[Official Maestro Docs](https://docs.gomaestro.org/bitcoin)** - Maestro Bitcoin documentation

## Available Commands

The skill provides 119+ commands organized across 7 API services:

### Blockchain Indexer (37 endpoints)
```bash
# Address operations
get-balance, get-utxos, get-address-txs, get-address-activity, get-address-stats
get-balance-history, get-address-runes, get-address-rune-activity, get-address-rune-utxos
get-address-brc20, get-address-inscriptions, get-address-inscription-activity

# Block operations
get-block, get-block-txs, get-block-inscriptions

# Transaction operations
get-tx, get-tx-metaprotocols, get-tx-output, get-tx-inscriptions

# BRC20 operations
list-brc20, get-brc20, get-brc20-holders

# Runes operations
list-runes, get-rune, get-rune-activity, get-rune-holders, get-rune-utxos

# Inscriptions operations
get-inscription, get-inscription-content, get-inscription-activity
get-collection, get-collection-stats, get-collection-inscriptions
```

### Esplora API (29 endpoints)
```bash
esplora-address-info, esplora-address-txs, esplora-address-utxos
esplora-block, esplora-block-txs, esplora-tip-height
esplora-tx, esplora-tx-hex, esplora-broadcast, esplora-mempool
# ... and 19 more
```

### Node RPC API (24 endpoints)
```bash
rpc-get-latest-block, rpc-get-latest-height, rpc-get-info
rpc-get-mempool-info, rpc-get-tx, rpc-decode-tx
rpc-broadcast-tx, rpc-estimate-fee
# ... and 16 more
```

### Event Manager API (9 endpoints)
```bash
event-list-triggers, event-create-trigger, event-get-trigger
event-delete-trigger, event-list-logs, event-get-log
```

### Market Price API (8 endpoints)
```bash
market-btc-price, market-rune-price, market-list-dexs
market-list-runes, market-ohlc, market-trades
```

### Mempool Monitoring API (9 endpoints)
```bash
mempool-get-balance, mempool-get-utxos, mempool-get-runes
mempool-get-fee-rates, mempool-broadcast, mempool-get-tx-meta
```

### Wallet API (6 endpoints)
```bash
wallet-get-activity, wallet-get-meta-activity, wallet-get-balance-history
wallet-get-inscription-activity, wallet-get-rune-activity, wallet-get-stats
```

Run `./scripts/call_maestro.sh help` for the complete list with descriptions.

## Examples

### Basic Queries

```bash
# Get latest block height
./scripts/call_maestro.sh get-latest-height

# Get address balance
./scripts/call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get transaction details
./scripts/call_maestro.sh get-tx 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

### Metaprotocol Queries

```bash
# List all BRC20 tokens
./scripts/call_maestro.sh list-brc20

# Get BRC20 token info
./scripts/call_maestro.sh get-brc20 ordi

# Get runes for an address
./scripts/call_maestro.sh get-address-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get inscription content
./scripts/call_maestro.sh get-inscription-content 1234567i0
```

### Mempool Operations

```bash
# Get mempool-aware balance (includes pending)
./scripts/call_maestro.sh mempool-get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get current fee rates
./scripts/call_maestro.sh mempool-get-fee-rates

# Estimate fee for 6 block confirmation
./scripts/call_maestro.sh estimate-fee 6
```

### Market Data

```bash
# Get current BTC price
./scripts/call_maestro.sh market-btc-price $(date +%s)

# Get rune price
./scripts/call_maestro.sh market-rune-price 840000:1 $(date +%s)

# List supported DEXs
./scripts/call_maestro.sh market-list-dexs
```

### Event Management

```bash
# Create a webhook for address activity
./scripts/call_maestro.sh event-create-trigger '{
  "name": "Address Activity Monitor",
  "trigger_type": "address_activity",
  "conditions": {
    "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"
  },
  "webhook_url": "https://your-webhook.com/endpoint"
}'

# List all triggers
./scripts/call_maestro.sh event-list-triggers
```

See [examples.md](references/examples.md) for more comprehensive examples.

## Architecture

### File Structure

```
maestro-skill/
├── SKILL.md                    # Main skill documentation
├── README.md                   # This file
├── scripts/
│   └── call_maestro.sh        # Comprehensive wrapper script (119+ commands)
└── references/
    ├── api_reference.md       # Complete API documentation
    └── examples.md            # Usage examples and patterns
```

### API Services

The skill is organized around Maestro's 7 API services:

1. **Blockchain Indexer** - Primary data source with metaprotocol support
2. **Esplora** - Blockstream-compatible REST API for compatibility
3. **Node RPC** - Direct node access with JSON-RPC protocol
4. **Event Manager** - Webhook and event-driven architecture
5. **Market Price** - Price feeds and trading data
6. **Mempool Monitoring** - Real-time mempool awareness
7. **Wallet** - Address-level activity tracking

## Configuration

### Environment Variables

- `MAESTRO_API_KEY` (required) - Your Maestro API key
- `MAESTRO_NETWORK` (optional) - Network: `mainnet` (default) or `testnet`

### Persistent Configuration

Add to `~/.bashrc` or `~/.zshrc`:

```bash
export MAESTRO_API_KEY="your_api_key_here"
export MAESTRO_NETWORK="mainnet"
```

## Rate Limits

Maestro implements two-tier rate limiting:

- **Daily Tier**: Credit limits based on subscription tier
- **Per-Second Tier**: Request caps per second (e.g., 10 req/sec for Artist plan)

Monitor rate limit headers in responses:
- `X-RateLimit-Limit-Second`
- `X-RateLimit-Remaining-Second`
- `X-Maestro-Credits-Limit`
- `X-Maestro-Credits-Remaining`

## Network Support

### Mainnet (default)
```bash
export MAESTRO_NETWORK="mainnet"
# Base URL: https://xbt-mainnet.gomaestro-api.org/v0
```

### Testnet4
```bash
export MAESTRO_NETWORK="testnet"
# Base URL: https://xbt-testnet.gomaestro-api.org/v0
```

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

## Resources

- **Maestro Dashboard**: https://dashboard.gomaestro.org
- **Official Documentation**: https://docs.gomaestro.org/bitcoin
- **API Specifications**: https://github.com/maestro-org/maestro-api-specifications
- **Maestro MCP Server**: https://github.com/maestro-org/maestro-mcp-server

## License

This skill is provided as-is for use with the Maestro API platform.

## Support

For issues or questions:
- Check the [API Reference](references/api_reference.md)
- Review [Examples](references/examples.md)
- Visit [Maestro Documentation](https://docs.gomaestro.org/bitcoin)
- Contact Maestro support through the dashboard

---

Built with ❤️ for the Bitcoin ecosystem using [Maestro APIs](https://www.gomaestro.org)
