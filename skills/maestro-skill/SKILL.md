---
name: maestro-bitcoin
description: Comprehensive Bitcoin blockchain interaction via Maestro APIs. Supports 7 API services with 119 endpoints including blockchain indexing, Esplora compatibility, RPC access, event management, market prices, mempool monitoring, and wallet operations. Handles BTC transactions, UTXOs, addresses, blocks, metaprotocols (BRC20, Runes, Inscriptions/Ordinals), webhooks, and real-time data.
---

# Maestro Bitcoin Skill

A comprehensive skill for interacting with the Bitcoin blockchain through the Maestro API platform, providing access to 7 distinct API services with 119 total endpoints.

## Overview

This skill provides complete access to Maestro's Bitcoin API suite:

1. **Blockchain Indexer API** (37 endpoints) - Real-time UTXO data with metaprotocol support
2. **Esplora API** (29 endpoints) - Blockstream-compatible REST API
3. **Node RPC API** (24 endpoints) - JSON-RPC protocol access
4. **Event Manager API** (9 endpoints) - Real-time webhooks and monitoring
5. **Market Price API** (8 endpoints) - OHLC data and price analytics
6. **Mempool Monitoring API** (9 endpoints) - Mempool-aware operations
7. **Wallet API** (6 endpoints) - Address-level activity tracking

### Key Capabilities

- Query addresses, transactions, blocks, and UTXOs
- Broadcast transactions with multiple methods
- Track BRC20 tokens, Runes, and Inscriptions (Ordinals)
- Monitor mempool and estimate fees
- Set up webhooks for blockchain events
- Access market price data and DEX trading info
- Mempool-aware balance and UTXO queries
- Historical balance tracking
- Collection and metaprotocol statistics

## Configuration

### API Key Setup

This skill requires a Maestro API Key. Set the `MAESTRO_API_KEY` environment variable:

```bash
export MAESTRO_API_KEY="your_api_key_here"
```

Add to `~/.bashrc` or `~/.zshrc` for persistence:

```bash
echo 'export MAESTRO_API_KEY="your_api_key_here"' >> ~/.bashrc
source ~/.bashrc
```

### Getting an API Key

1. Sign up at [Maestro Dashboard](https://dashboard.gomaestro.org/signup)
2. Create a new project
3. Select Bitcoin as the blockchain
4. Select your network (Mainnet or Testnet4)
5. Copy the API key from your project dashboard

### Network Configuration

The skill supports both mainnet and testnet. Set `MAESTRO_NETWORK` to switch:

```bash
# Use mainnet (default)
export MAESTRO_NETWORK="mainnet"

# Use testnet4
export MAESTRO_NETWORK="testnet"
```

## Usage

### Primary Interface: Shell Script

The main interface is through `scripts/call_maestro.sh`, which provides access to all 7 API services.

#### Quick Examples

```bash
# Get latest block height
./scripts/call_maestro.sh get-latest-height

# Get address balance
./scripts/call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get address UTXOs
./scripts/call_maestro.sh get-utxos bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get transaction details
./scripts/call_maestro.sh get-tx <tx_hash>

# Broadcast transaction
./scripts/call_maestro.sh broadcast-tx <hex_tx>

# Get mempool info
./scripts/call_maestro.sh get-mempool-info

# Estimate fee for 6 blocks
./scripts/call_maestro.sh estimate-fee 6

# Get BRC20 tokens
./scripts/call_maestro.sh list-brc20

# Get runes for address
./scripts/call_maestro.sh get-address-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Available Commands by Service

#### Blockchain Indexer Commands

**Address Operations:**
- `get-balance <address>` - Get address satoshi balance
- `get-utxos <address>` - Get address UTXOs
- `get-address-txs <address>` - Get address transactions
- `get-address-activity <address>` - Get address satoshi activity
- `get-address-stats <address>` - Get address statistics
- `get-balance-history <address>` - Get historical balance
- `get-address-runes <address>` - Get runes for address
- `get-address-rune-activity <address>` - Get rune activity
- `get-address-rune-utxos <address>` - Get rune UTXOs
- `get-address-brc20 <address>` - Get BRC20 tokens for address
- `get-address-inscriptions <address>` - Get inscriptions for address
- `get-address-inscription-activity <address>` - Get inscription activity

**Block Operations:**
- `get-block <height_or_hash>` - Get block information
- `get-block-txs <height_or_hash>` - Get transactions in block
- `get-block-inscriptions <height_or_hash>` - Get inscription activity in block

**Transaction Operations:**
- `get-tx <tx_hash>` - Get transaction information
- `get-tx-metaprotocols <tx_hash>` - Get transaction with metaprotocols
- `get-tx-output <tx_hash> <index>` - Get transaction output info
- `get-tx-inscriptions <tx_hash>` - Get inscription activity in transaction

**BRC20 Operations:**
- `list-brc20` - List all BRC20 tokens
- `get-brc20 <ticker>` - Get BRC20 token info
- `get-brc20-holders <ticker>` - Get BRC20 token holders

**Runes Operations:**
- `list-runes` - List all runes
- `get-rune <rune_id>` - Get rune information
- `get-rune-activity <rune_id>` - Get rune activity
- `get-rune-holders <rune_id>` - Get rune holders
- `get-rune-utxos <rune_id>` - Get rune UTXOs

**Inscriptions Operations:**
- `get-inscription <inscription_id>` - Get inscription info
- `get-inscription-content <inscription_id>` - Get inscription content
- `get-inscription-activity <inscription_id>` - Get inscription activity
- `get-collection <collection_symbol>` - Get collection metadata
- `get-collection-stats <collection_symbol>` - Get collection statistics
- `get-collection-inscriptions <collection_symbol>` - Get collection inscriptions

#### Esplora API Commands

- `esplora-address-info <address>` - Get address information
- `esplora-address-txs <address>` - Get address transactions
- `esplora-address-utxos <address>` - Get address UTXOs
- `esplora-block <hash>` - Get block information
- `esplora-block-txs <hash>` - Get block transactions
- `esplora-tx <txid>` - Get transaction information
- `esplora-tx-hex <txid>` - Get transaction hex
- `esplora-broadcast <tx_hex>` - Broadcast transaction
- `esplora-mempool` - Get mempool information
- `esplora-tip-height` - Get blockchain tip height

#### Node RPC Commands

- `rpc-get-latest-block` - Get latest block
- `rpc-get-latest-height` - Get latest block height
- `rpc-get-block <height_or_hash>` - Get block info
- `rpc-get-block-miner <height_or_hash>` - Get block miner info
- `rpc-get-info` - Get blockchain info
- `rpc-get-mempool-info` - Get mempool info
- `rpc-get-mempool-txs` - Get mempool transactions
- `rpc-get-mempool-tx <tx_hash>` - Get mempool transaction info
- `rpc-get-tx <tx_hash>` - Get transaction info
- `rpc-decode-tx <hex>` - Decode transaction
- `rpc-broadcast-tx <hex>` - Broadcast transaction
- `rpc-estimate-fee <blocks>` - Estimate fee

#### Event Manager Commands

- `event-list-triggers` - List all event triggers
- `event-create-trigger <json>` - Create event trigger
- `event-get-trigger <id>` - Get trigger details
- `event-delete-trigger <id>` - Delete trigger
- `event-list-logs` - List event logs
- `event-get-log <id>` - Get event log details

#### Market Price Commands

- `market-btc-price <timestamp>` - Get BTC price at timestamp
- `market-rune-price <rune_id> <timestamp>` - Get rune price
- `market-list-dexs` - List supported DEXs
- `market-list-runes` - Get rune registry
- `market-ohlc <dex> <symbol>` - Get OHLC data for rune
- `market-trades <dex> <symbol>` - Get trades for rune

#### Mempool Monitoring Commands

- `mempool-get-balance <address>` - Get balance (mempool-aware)
- `mempool-get-utxos <address>` - Get UTXOs (mempool-aware)
- `mempool-get-runes <address>` - Get runes (mempool-aware)
- `mempool-get-rune-utxos <address>` - Get rune UTXOs (mempool-aware)
- `mempool-get-fee-rates` - Get mempool block fee rates
- `mempool-broadcast <hex>` - Broadcast with propagation tracking
- `mempool-get-tx-meta <tx_hash>` - Get tx metaprotocols (mempool-aware)

#### Wallet API Commands

- `wallet-get-activity <address>` - Get wallet activity (mempool-aware)
- `wallet-get-meta-activity <address>` - Get metaprotocol activity
- `wallet-get-balance-history <address>` - Get historical balance
- `wallet-get-inscription-activity <address>` - Get inscription activity
- `wallet-get-rune-activity <address>` - Get rune activity
- `wallet-get-stats <address>` - Get address statistics (mempool-aware)

### References

- [API Reference](references/api_reference.md): Complete endpoint documentation
- [Examples](references/examples.md): Common use case examples
- [Official Docs](https://docs.gomaestro.org/bitcoin): Maestro documentation

## Features

### Metaprotocol Support

Full support for Bitcoin metaprotocols:
- **BRC20 Tokens**: Query tokens, holders, and balances
- **Runes**: Track rune balances, activity, and UTXOs
- **Inscriptions (Ordinals)**: Query inscriptions, collections, and content

### Mempool Awareness

Several endpoints offer mempool-aware queries that include pending transactions:
- Balance queries
- UTXO queries
- Rune and inscription tracking
- Transaction metaprotocols

### Event-Driven Architecture

Set up webhooks to monitor:
- Address activity
- Block confirmations
- Transaction events
- Metaprotocol operations

### Rate Limiting

Maestro implements two-tier rate limiting:
- Daily credit limits based on subscription
- Per-second request caps

Check rate limit headers in responses:
- `X-RateLimit-Limit-Second`
- `X-RateLimit-Remaining-Second`
- `X-Maestro-Credits-Limit`
- `X-Maestro-Credits-Remaining`

## Notes

- All endpoints require valid API key authentication
- The `/v0` version prefix must be included in all API calls
- Cursor-based pagination is available for listing endpoints
- Block height filtering available via `from` and `to` parameters
- Support for both mainnet and testnet4 networks
- Comprehensive error handling with standard HTTP status codes
