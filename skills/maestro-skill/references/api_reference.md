# Maestro Bitcoin API Reference

Complete reference for all Maestro Bitcoin API endpoints across 7 services with 119 total endpoints.

## Table of Contents

1. [Authentication](#authentication)
2. [Base URLs](#base-urls)
3. [Common Patterns](#common-patterns)
4. [Blockchain Indexer API](#blockchain-indexer-api) (37 endpoints)
5. [Esplora API](#esplora-api) (29 endpoints)
6. [Node RPC API](#node-rpc-api) (24 endpoints)
7. [Event Manager API](#event-manager-api) (9 endpoints)
8. [Market Price API](#market-price-api) (8 endpoints)
9. [Mempool Monitoring API](#mempool-monitoring-api) (9 endpoints)
10. [Wallet API](#wallet-api) (6 endpoints)

---

## Authentication

All requests require the `api-key` header:

```bash
api-key: YOUR_PROJECT_API_KEY
```

Get your API key from [Maestro Dashboard](https://dashboard.gomaestro.org/signup).

---

## Base URLs

### Mainnet
```
https://xbt-mainnet.gomaestro-api.org/v0
```

### Testnet4
```
https://xbt-testnet.gomaestro-api.org/v0
```

**Important:** The `/v0` version prefix MUST be included in all API calls.

---

## Common Patterns

### Pagination

Cursor-based pagination for efficient data retrieval:

**Query Parameters:**
- `count` - Results per page (default: 100, min: 0)
- `cursor` - Pagination token from previous response
- `order` - Sort direction (`asc` or `desc`)

**Response:**
```json
{
  "data": [...],
  "next_cursor": "cursor_token_or_null"
}
```

### Filtering

**Block Height Range:**
- `from` - Return only items on or after specific height (int64)
- `to` - Return only items on or before specific height (int64)

**Ordering:**
- `order` - Sort direction: `asc` or `desc`

### Rate Limits

**Response Headers:**
- `X-RateLimit-Limit-Second` - Requests per second limit
- `X-RateLimit-Remaining-Second` - Remaining requests this second
- `X-Maestro-Credits-Limit` - Daily credit limit
- `X-Maestro-Credits-Remaining` - Remaining daily credits

### Status Codes

- `200` - Success
- `400` - Bad Request (malformed parameters)
- `404` - Not Found (entity not found on-chain)
- `429` - Too Many Requests (rate limit exceeded)
- `500` - Internal Server Error

---

## Blockchain Indexer API

**Base Path:** `/v0` (root)
**Endpoints:** 37

Real-time UTXO data with rollback protection and metaprotocol support (BRC20, Runes, Inscriptions).

### Addresses (14 endpoints)

#### GET `/addresses/{address}/activity`
Satoshi activity by address.

**Parameters:**
- `address` (path) - Bitcoin address
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction (asc/desc)
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh/activity?order=desc&count=50"
```

---

#### GET `/addresses/{address}/balance`
Current satoshi balance for an address.

**Parameters:**
- `address` (path) - Bitcoin address

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh/balance"
```

---

#### GET `/addresses/{address}/balance/historical`
Historical satoshi balance at specific block height.

**Parameters:**
- `address` (path) - Bitcoin address
- `height` (query) - Block height

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh/balance/historical?height=800000"
```

---

#### GET `/addresses/{address}/brc20`
BRC20 tokens held by an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/brc20/transfer_inscriptions`
BRC20 transfer inscriptions for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `ticker` (query) - Filter by BRC20 ticker
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/inscriptions`
Inscriptions held by an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/inscriptions/activity`
Inscription activity for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/runes`
Runes held by an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/runes/activity`
Rune activity for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `rune` (query) - Filter by specific rune ID
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/runes/utxos`
Rune UTXOs held by an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `rune` (query) - Filter by specific rune ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/statistics`
Address statistics including transaction count and balance.

**Parameters:**
- `address` (path) - Bitcoin address

---

#### GET `/addresses/{address}/txs`
Transactions for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/addresses/{address}/utxos`
UTXOs for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `filter_dust` (query) - Filter out dust UTXOs (boolean)
- `exclude_metaprotocols` (query) - Exclude metaprotocol UTXOs (boolean)
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh/utxos?filter_dust=true&exclude_metaprotocols=true"
```

---

### BRC20 (3 endpoints)

#### GET `/assets/brc20`
List all BRC20 tokens.

**Parameters:**
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/assets/brc20/{ticker}`
Information about a specific BRC20 token.

**Parameters:**
- `ticker` (path) - BRC20 token ticker (e.g., "ordi")

---

#### GET `/assets/brc20/{ticker}/holders`
Holders of a specific BRC20 token.

**Parameters:**
- `ticker` (path) - BRC20 token ticker
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

### Blocks (3 endpoints)

#### GET `/blocks/{height_or_hash}`
Block information by height or hash.

**Parameters:**
- `height_or_hash` (path) - Block height (integer) or hash (hex string)

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/blocks/800000"
```

---

#### GET `/blocks/{height_or_hash}/inscriptions/activity`
Inscription activity in a specific block.

**Parameters:**
- `height_or_hash` (path) - Block height or hash
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/blocks/{height_or_hash}/transactions`
Transactions in a specific block.

**Parameters:**
- `height_or_hash` (path) - Block height or hash
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

### Inscriptions (8 endpoints)

#### GET `/assets/collections/{collection_symbol}/inscriptions`
Inscription IDs for a collection.

**Parameters:**
- `collection_symbol` (path) - Collection symbol
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/assets/collections/{collection_symbol}/metadata`
Collection metadata.

**Parameters:**
- `collection_symbol` (path) - Collection symbol

---

#### GET `/assets/collections/{collection_symbol}/stats`
Collection statistics.

**Parameters:**
- `collection_symbol` (path) - Collection symbol

---

#### GET `/assets/inscriptions/{inscription_id}`
Inscription information.

**Parameters:**
- `inscription_id` (path) - Inscription ID

---

#### GET `/assets/inscriptions/{inscription_id}/activity`
Activity history for an inscription.

**Parameters:**
- `inscription_id` (path) - Inscription ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/assets/inscriptions/{inscription_id}/collection`
Collection metadata for an inscription.

**Parameters:**
- `inscription_id` (path) - Inscription ID

---

#### GET `/assets/inscriptions/{inscription_id}/content_body`
Content data for an inscription.

**Parameters:**
- `inscription_id` (path) - Inscription ID

---

#### GET `/assets/inscriptions/{inscription_id}/metadata`
Token metadata for an inscription.

**Parameters:**
- `inscription_id` (path) - Inscription ID

---

### Runes (5 endpoints)

#### GET `/assets/runes`
List all runes.

**Parameters:**
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/assets/runes/{rune}`
Information about a specific rune.

**Parameters:**
- `rune` (path) - Rune ID

---

#### GET `/assets/runes/{rune}/activity`
Activity history for a rune.

**Parameters:**
- `rune` (path) - Rune ID
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/assets/runes/{rune}/holders`
Holders of a specific rune.

**Parameters:**
- `rune` (path) - Rune ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/assets/runes/{rune}/utxos`
UTXOs containing a specific rune.

**Parameters:**
- `rune` (path) - Rune ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

### Transactions (4 endpoints)

#### GET `/transactions/{tx_hash}`
Transaction information.

**Parameters:**
- `tx_hash` (path) - Transaction hash

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/transactions/TX_HASH"
```

---

#### GET `/transactions/{tx_hash}/inscriptions/activity`
Inscription activity in a transaction.

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

#### GET `/transactions/{tx_hash}/metaprotocols`
Transaction with metaprotocol data (BRC20, Runes, Inscriptions).

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

#### GET `/transactions/{tx_hash}/outputs/{output_index}`
Specific transaction output information.

**Parameters:**
- `tx_hash` (path) - Transaction hash
- `output_index` (path) - Output index (integer)

---

## Esplora API

**Base Path:** `/v0/esplora`
**Endpoints:** 29

Blockstream-compatible Esplora REST API for lightweight blockchain access.

### Addresses (5 endpoints)

#### GET `/esplora/address/{address}`
Address information including balance and transaction count.

**Parameters:**
- `address` (path) - Bitcoin address

---

#### GET `/esplora/address/{address}/txs`
All transactions for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `after_txid` (query) - Get transactions after specific txid

---

#### GET `/esplora/address/{address}/txs/chain`
Confirmed transactions for an address.

**Parameters:**
- `address` (path) - Bitcoin address
- `last_seen_txid` (query) - Pagination marker

---

#### GET `/esplora/address/{address}/txs/mempool`
Mempool transactions for an address.

**Parameters:**
- `address` (path) - Bitcoin address

---

#### GET `/esplora/address/{address}/utxo`
UTXOs for an address.

**Parameters:**
- `address` (path) - Bitcoin address

---

### Blocks (11 endpoints)

#### GET `/esplora/block/{hash}`
Block information.

**Parameters:**
- `hash` (path) - Block hash

---

#### GET `/esplora/block/{hash}/header`
Block header in hex format.

**Parameters:**
- `hash` (path) - Block hash

---

#### GET `/esplora/block/{hash}/status`
Block status and confirmation count.

**Parameters:**
- `hash` (path) - Block hash

---

#### GET `/esplora/block/{hash}/txs/{start_index}`
Block transactions starting from index.

**Parameters:**
- `hash` (path) - Block hash
- `start_index` (path) - Starting transaction index

---

#### GET `/esplora/block/{hash}/txids`
All transaction IDs in a block.

**Parameters:**
- `hash` (path) - Block hash

---

#### GET `/esplora/block/{hash}/txid/{index}`
Transaction ID at specific index in block.

**Parameters:**
- `hash` (path) - Block hash
- `index` (path) - Transaction index

---

#### GET `/esplora/block/{hash}/raw`
Raw block data in hex format.

**Parameters:**
- `hash` (path) - Block hash

---

#### GET `/esplora/blocks/{start_height}`
10 blocks starting from height.

**Parameters:**
- `start_height` (path) - Starting block height

---

#### GET `/esplora/block-height/{height}`
Block hash at specific height.

**Parameters:**
- `height` (path) - Block height

---

#### GET `/esplora/blocks/tip/height`
Current blockchain tip height.

---

#### GET `/esplora/blocks/tip/hash`
Current blockchain tip hash.

---

### Mempool (3 endpoints)

#### GET `/esplora/mempool`
Mempool statistics.

---

#### GET `/esplora/mempool/txids`
All transaction IDs in mempool.

---

#### GET `/esplora/mempool/recent`
Recent mempool transactions (last 10).

---

### Transactions (10 endpoints)

#### GET `/esplora/tx/{txid}`
Transaction information.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/hex`
Transaction in hex format.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/merkleblock-proof`
Merkleblock proof for transaction.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/merkle-proof`
Merkle inclusion proof for transaction.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/outspend/{vout}`
Information about transaction output spend.

**Parameters:**
- `txid` (path) - Transaction ID
- `vout` (path) - Output index

---

#### GET `/esplora/tx/{txid}/outspends`
Spending status of all outputs.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/raw`
Raw transaction data in hex.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/rbf`
RBF (Replace-By-Fee) history timeline.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### GET `/esplora/tx/{txid}/status`
Transaction confirmation status.

**Parameters:**
- `txid` (path) - Transaction ID

---

#### POST `/esplora/tx`
Broadcast a signed transaction.

**Body:** Raw transaction hex (text/plain)

**Example:**
```bash
curl -X POST \
  -H "api-key: YOUR_KEY" \
  -H "Content-Type: text/plain" \
  -d "YOUR_SIGNED_TX_HEX" \
  "https://xbt-mainnet.gomaestro-api.org/v0/esplora/tx"
```

---

## Node RPC API

**Base Path:** `/v0/rpc`
**Endpoints:** 24

JSON-RPC protocol access for blockchain queries and transaction operations.

### Blocks (8 endpoints)

#### GET `/rpc/block/latest`
Latest block information.

---

#### GET `/rpc/block/latest/height`
Latest block height.

---

#### GET `/rpc/block/range/{start_height}/{end_height}`
Block range information.

**Parameters:**
- `start_height` (path) - Start block height
- `end_height` (path) - End block height

---

#### GET `/rpc/block/recent`
Recent block information.

---

#### GET `/rpc/block/recent/{count}`
Recent blocks by count.

**Parameters:**
- `count` (path) - Number of recent blocks

---

#### GET `/rpc/block/{height_or_hash}`
Block information by height or hash.

**Parameters:**
- `height_or_hash` (path) - Block height or hash

---

#### GET `/rpc/block/{height_or_hash}/miner`
Block miner information.

**Parameters:**
- `height_or_hash` (path) - Block height or hash

---

#### GET `/rpc/block/{height_or_hash}/volume`
Block transaction volume.

**Parameters:**
- `height_or_hash` (path) - Block height or hash

---

### General (1 endpoint)

#### GET `/rpc/general/info`
Blockchain information (network, blocks, difficulty, etc.).

---

### Mempool (5 endpoints)

#### GET `/rpc/mempool/info`
Mempool information and statistics.

---

#### GET `/rpc/mempool/transactions`
All transactions in mempool.

---

#### GET `/rpc/mempool/transactions/{tx_hash}`
Mempool transaction information.

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

#### GET `/rpc/mempool/transactions/{tx_hash}/ancestors`
Mempool transaction ancestors.

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

#### GET `/rpc/mempool/transactions/{tx_hash}/descendants`
Mempool transaction descendants.

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

### Transactions (10 endpoints)

#### POST `/rpc/transaction/batch`
Get information for multiple transactions.

**Body:**
```json
{
  "transaction_hashes": ["hash1", "hash2", ...]
}
```

---

#### POST `/rpc/transaction/decode`
Decode a transaction from hex.

**Body:**
```json
{
  "transaction_hex": "HEX_STRING"
}
```

---

#### GET `/rpc/transaction/estimatefee/{blocks}`
Estimate fee for confirmation in N blocks.

**Parameters:**
- `blocks` (path) - Target confirmation blocks

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/transaction/estimatefee/6"
```

---

#### POST `/rpc/transaction/hex`
Get transaction information from hex.

**Body:**
```json
{
  "transaction_hex": "HEX_STRING"
}
```

---

#### POST `/rpc/transaction/psbt/decode`
Decode a PSBT (Partially Signed Bitcoin Transaction).

**Body:**
```json
{
  "psbt": "BASE64_PSBT"
}
```

---

#### GET `/rpc/transaction/recent`
Recent transactions.

---

#### GET `/rpc/transaction/recent/{count}`
Recent transactions by count.

**Parameters:**
- `count` (path) - Number of recent transactions

---

#### POST `/rpc/transaction/submit`
Broadcast a signed transaction.

**Body:**
```json
{
  "transaction_hex": "YOUR_SIGNED_TX_HEX"
}
```

**Example:**
```bash
curl -X POST \
  -H "api-key: YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"transaction_hex": "YOUR_SIGNED_TX_HEX"}' \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/transaction/submit"
```

---

#### GET `/rpc/transaction/{tx_hash}`
Transaction information.

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

#### GET `/rpc/transaction/{tx_hash}/hex`
Transaction in hex format.

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

## Event Manager API

**Base Path:** `/v0/eventmanager`
**Endpoints:** 9

Real-time blockchain monitoring with programmable webhooks.

### Health (1 endpoint)

#### GET `/eventmanager/healthcheck`
Service health check.

---

### Logs (3 endpoints)

#### GET `/eventmanager/logs`
List all event logs.

**Parameters:**
- `trigger_id` (query) - Filter by trigger ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/eventmanager/logs/{id}`
Get specific event log details.

**Parameters:**
- `id` (path) - Event log ID

---

### Triggers (6 endpoints)

#### GET `/eventmanager/triggers`
List all event triggers.

**Parameters:**
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### POST `/eventmanager/triggers`
Create a new event trigger.

**Body:**
```json
{
  "name": "Trigger Name",
  "trigger_type": "address_activity",
  "conditions": {...},
  "webhook_url": "https://your-webhook.com/endpoint"
}
```

---

#### GET `/eventmanager/triggers/{id}`
Get trigger details.

**Parameters:**
- `id` (path) - Trigger ID

---

#### PUT `/eventmanager/triggers/{id}`
Update an existing trigger.

**Parameters:**
- `id` (path) - Trigger ID

**Body:** Updated trigger configuration

---

#### DELETE `/eventmanager/triggers/{id}`
Delete a trigger.

**Parameters:**
- `id` (path) - Trigger ID

---

#### GET `/eventmanager/triggers/trigger-condition-options`
List available trigger condition options.

---

## Market Price API

**Base Path:** `/v0/markets`
**Endpoints:** 8

OHLC data, trading pairs, and price analytics for BTC and Rune tokens.

### DEX (4 endpoints)

#### GET `/markets/dexs`
List supported DEX options.

---

#### GET `/markets/dexs/ohlc/{dex}/{symbol}`
OHLC data for a rune on a DEX.

**Parameters:**
- `dex` (path) - DEX identifier
- `symbol` (path) - Rune symbol
- `resolution` (query) - Time resolution (1m, 5m, 1h, 1d, etc.)
- `from` (query) - Start timestamp
- `to` (query) - End timestamp

---

#### GET `/markets/dexs/trades/{dex}/{symbol}`
Recent trades for a rune on a DEX.

**Parameters:**
- `dex` (path) - DEX identifier
- `symbol` (path) - Rune symbol
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/markets/runes`
Rune registry with market data.

**Parameters:**
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

### Prices (4 endpoints)

#### GET `/markets/prices/{timestamp}`
BTC price at specific timestamp.

**Parameters:**
- `timestamp` (path) - Unix timestamp

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/markets/prices/1672531200"
```

---

#### POST `/markets/prices/batch`
BTC prices for multiple timestamps.

**Body:**
```json
{
  "timestamps": [1672531200, 1672617600, ...]
}
```

---

#### GET `/markets/prices/runes/{rune_id}/{timestamp}`
Rune price at specific timestamp.

**Parameters:**
- `rune_id` (path) - Rune ID
- `timestamp` (path) - Unix timestamp

---

#### POST `/markets/prices/runes/batch`
Rune prices for multiple timestamps.

**Body:**
```json
{
  "rune_id": "RUNE_ID",
  "timestamps": [1672531200, 1672617600, ...]
}
```

---

## Mempool Monitoring API

**Base Path:** `/v0/mempool`
**Endpoints:** 9

Mempool-aware endpoints tracking pending transactions and network congestion.

### Addresses (4 endpoints)

#### GET `/mempool/addresses/{address}/balance`
Satoshi balance including pending transactions.

**Parameters:**
- `address` (path) - Bitcoin address

---

#### GET `/mempool/addresses/{address}/runes`
Runes by address (mempool-aware).

**Parameters:**
- `address` (path) - Bitcoin address
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/mempool/addresses/{address}/runes/utxos`
Rune UTXOs (mempool-aware).

**Parameters:**
- `address` (path) - Bitcoin address
- `rune` (query) - Filter by specific rune ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/mempool/addresses/{address}/utxos`
UTXOs including pending transactions.

**Parameters:**
- `address` (path) - Bitcoin address
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

### General (1 endpoint)

#### GET `/mempool/fee_rates`
Current mempool block fee rates.

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/mempool/fee_rates"
```

---

### Runes (1 endpoint)

#### GET `/mempool/assets/runes/{rune}/holders`
Rune holders (mempool-aware).

**Parameters:**
- `rune` (path) - Rune ID
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

### Transactions (3 endpoints)

#### POST `/mempool/transactions/send`
Broadcast transaction with propagation tracking.

**Body:**
```json
{
  "transaction_hex": "YOUR_SIGNED_TX_HEX"
}
```

---

#### GET `/mempool/transactions/{tx_hash}/metaprotocols`
Transaction with metaprotocols (mempool-aware).

**Parameters:**
- `tx_hash` (path) - Transaction hash

---

#### GET `/mempool/transactions/{tx_hash}/outputs/{output_index}`
Transaction output info (mempool-aware).

**Parameters:**
- `tx_hash` (path) - Transaction hash
- `output_index` (path) - Output index

---

## Wallet API

**Base Path:** `/v0/wallet`
**Endpoints:** 6

Address-level transaction activity with mempool awareness.

### Addresses (6 endpoints)

#### GET `/wallet/addresses/{address}/activity`
Wallet satoshi activity (mempool-aware).

**Parameters:**
- `address` (path) - Bitcoin address
- `mempool` (query) - Include mempool transactions (boolean)
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/wallet/addresses/{address}/activity/metaprotocols`
Metaprotocol activity (BRC20, Runes, Inscriptions).

**Parameters:**
- `address` (path) - Bitcoin address
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/wallet/addresses/{address}/balance/historical`
Historical satoshi balance.

**Parameters:**
- `address` (path) - Bitcoin address
- `height` (query) - Block height

---

#### GET `/wallet/addresses/{address}/inscriptions/activity`
Inscription activity (mempool-aware).

**Parameters:**
- `address` (path) - Bitcoin address
- `mempool` (query) - Include mempool transactions (boolean)
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/wallet/addresses/{address}/runes/activity`
Rune activity (mempool-aware).

**Parameters:**
- `address` (path) - Bitcoin address
- `rune` (query) - Filter by specific rune ID
- `mempool` (query) - Include mempool transactions (boolean)
- `from` (query) - Min block height
- `to` (query) - Max block height
- `order` (query) - Sort direction
- `count` (query) - Results per page
- `cursor` (query) - Pagination cursor

---

#### GET `/wallet/addresses/{address}/statistics`
Address statistics (mempool-aware).

**Parameters:**
- `address` (path) - Bitcoin address

---

## Additional Resources

- **Official Documentation:** https://docs.gomaestro.org/bitcoin
- **API Specifications:** https://github.com/maestro-org/maestro-api-specifications
- **Dashboard:** https://dashboard.gomaestro.org/signup
- **Documentation Index:** https://docs.gomaestro.org/llms.txt

---

## Summary

- **Total Services:** 7
- **Total Endpoints:** 119
- **Networks:** Mainnet, Testnet4
- **Authentication:** API Key (Header-based)
- **Pagination:** Cursor-based
- **Rate Limiting:** Two-tier (Daily + Per-second)
- **Metaprotocol Support:** BRC20, Runes, Inscriptions (Ordinals)
