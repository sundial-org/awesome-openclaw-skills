# MAESTRO BITCOIN API - COMPLETE DOCUMENTATION SUMMARY

## Table of Contents
1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base URLs](#base-urls)
4. [API Services](#api-services)
5. [Common Patterns](#common-patterns)
6. [All Endpoints by Service](#all-endpoints-by-service)
7. [Common Use Cases](#common-use-cases)

---

## Overview

Maestro provides a comprehensive Bitcoin API platform with 7 distinct services and 119 total endpoints covering:

- **Blockchain Indexer API** (37 endpoints) - Real-time UTXO data with metaprotocol support
- **Esplora API** (29 endpoints) - Blockstream-compatible REST API
- **Node RPC API** (24 endpoints) - JSON-RPC protocol access
- **Event Manager API** (9 endpoints) - Real-time monitoring with webhooks
- **Market Price API** (8 endpoints) - OHLC data and price analytics
- **Mempool Monitoring API** (9 endpoints) - Mempool-aware endpoints
- **Wallet API** (6 endpoints) - Address-level transaction tracking

---

## Authentication

### Method
API Key in HTTP Header

### Header Format
```
api-key: <your_project_api_key>
```

### Getting Your API Key
1. Sign up at https://dashboard.gomaestro.org/signup
2. Create a new project
3. Select Bitcoin as the blockchain
4. Select your network (Mainnet or Testnet)
5. Copy the API key from your project dashboard

### Important Notes
- Each API key is specific to a project and network
- Keep your API key private and never share it publicly
- API keys must be included in all requests

---

## Base URLs

### Mainnet
```
https://xbt-mainnet.gomaestro-api.org/v0
```

### Testnet (Testnet4)
```
https://xbt-testnet.gomaestro-api.org/v0
```

### Important
- The `/v0` version prefix MUST be included in all API calls
- Different services have different path prefixes (see API Services section)

---

## API Services

### 1. Blockchain Indexer API
**Base Path:** `/v0` (root)  
**Endpoints:** 37

Provides real-time UTXO data with rollback protection and comprehensive metaprotocol support including:
- BRC-20 tokens
- Runes
- Inscriptions (Ordinals)

**Key Features:**
- Real-time data with rollback protection
- Comprehensive UTXO indexing
- Address statistics and activity tracking
- Historical balance queries
- Metaprotocol data extraction

**Categories:**
- Addresses (14 endpoints)
- BRC20 (3 endpoints)
- Blocks (3 endpoints)
- Inscriptions (8 endpoints)
- Runes (5 endpoints)
- Transactions (4 endpoints)

---

### 2. Esplora API
**Base Path:** `/v0/esplora`  
**Endpoints:** 29

Blockstream-compatible Esplora REST API for lightweight Bitcoin blockchain access.

**Key Features:**
- Fast block, transaction, and address queries
- Compatible with existing Esplora clients
- Raw transaction and block data
- Merkle proof generation
- RBF (Replace-By-Fee) tracking

**Categories:**
- Addresses (5 endpoints)
- Blocks (11 endpoints)
- Mempool (3 endpoints)
- Transactions (10 endpoints)

---

### 3. Node RPC API
**Base Path:** `/v0/rpc`  
**Endpoints:** 24

JSON-RPC protocol access for blockchain queries and transaction operations.

**Key Features:**
- Block and blockchain information queries
- Mempool transaction analysis
- Transaction broadcasting and decoding
- Fee estimation
- PSBT (Partially Signed Bitcoin Transaction) support

**Categories:**
- Blocks (8 endpoints)
- General (1 endpoint)
- Mempool (5 endpoints)
- Transactions (10 endpoints)

---

### 4. Event Manager API
**Base Path:** `/v0/eventmanager`  
**Endpoints:** 9

Real-time blockchain monitoring with programmable webhooks and customizable event notifications.

**Key Features:**
- Programmable webhook triggers
- Granular event monitoring
- Event log tracking
- Customizable trigger conditions

**Categories:**
- Health (1 endpoint)
- Logs (3 endpoints)
- Triggers (6 endpoints)

---

### 5. Market Price API
**Base Path:** `/v0/markets`  
**Endpoints:** 8

OHLC data, trading pairs, and real-time price analytics for Bitcoin and Rune tokens.

**Key Features:**
- Historical BTC price data
- Rune token prices
- OHLC (Open, High, Low, Close) data
- DEX trading data
- Batch price queries

**Categories:**
- DEX (4 endpoints)
- Prices (4 endpoints)

---

### 6. Mempool Monitoring API
**Base Path:** `/v0/mempool`  
**Endpoints:** 9

Mempool-aware endpoints tracking pending transactions and real-time network congestion.

**Key Features:**
- Real-time fee rate data
- Mempool-aware UTXO queries
- Pending transaction tracking
- Metaprotocol data for unconfirmed transactions

**Categories:**
- Addresses (4 endpoints)
- General (1 endpoint)
- Runes (1 endpoint)
- Transactions (3 endpoints)

---

### 7. Wallet API
**Base Path:** `/v0/wallet`  
**Endpoints:** 6

Detailed address-level transaction activity with satoshi tracking, inscription monitoring, and rune balance management.

**Key Features:**
- Mempool-aware activity tracking
- Historical balance queries
- Metaprotocol activity monitoring
- Address statistics

**Categories:**
- Addresses (6 endpoints)

---

## Common Patterns

### Pagination

Maestro uses cursor-based pagination for efficient data retrieval.

**Query Parameters:**
- `count` - Results per page (default: 100, min: 0)
- `cursor` - Pagination token from previous response
- `order` - Sort direction (`asc` or `desc`)

**Response:**
- `data` - Array of results
- `next_cursor` - Token for next page (null when no more data)

**Example:**
```bash
# First page
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/utxos?count=50&order=desc"

# Next page (use next_cursor from previous response)
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/utxos?count=50&order=desc&cursor=CURSOR_VALUE"
```

---

### Filtering

**Block Height Range:**
- `from` - Return only items on or after a specific height (int64)
- `to` - Return only items on or before a specific height (int64)

**Ordering:**
- `order` - Sort direction: `asc` (ascending) or `desc` (descending)

**Example:**
```bash
curl -H "api-key: YOUR_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/activity?from=800000&to=850000&order=asc"
```

---

### Rate Limits

Maestro implements two-tier rate limiting:

**1. Daily Tier:**
- Credit limits based on subscription tier
- Tracked via `X-Maestro-Credits-*` headers

**2. Per-Second Tier:**
- Request caps per second (e.g., Artist plan = 10 req/sec)
- Tracked via `X-RateLimit-*` headers

**Response Headers:**
```
X-RateLimit-Limit-Second: 10
X-RateLimit-Remaining-Second: 8
X-Maestro-Credits-Limit: 1000000
X-Maestro-Credits-Remaining: 999500
```

---

### Response Status Codes

- **2xx** - Success
  - `200` - OK - Requested data returned successfully
- **4xx** - Client Errors
  - `400` - Bad Request - Malformed query parameters
  - `404` - Not Found - Requested entity not found on-chain
  - `429` - Too Many Requests - Rate limit exceeded
- **5xx** - Server Errors
  - `500` - Internal Server Error - Server-side failure

---

## All Endpoints by Service

### BLOCKCHAIN INDEXER API (37 endpoints)

#### Addresses (14 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/addresses/{address}/activity` | Satoshi activity by address |
| GET | `/addresses/{address}/balance` | Satoshi balance by address |
| GET | `/addresses/{address}/balance/historical` | Historical satoshi balance |
| GET | `/addresses/{address}/brc20` | BRC20 tokens by address |
| GET | `/addresses/{address}/brc20/transfer_inscriptions` | BRC20 transfer inscriptions |
| GET | `/addresses/{address}/inscriptions` | Inscriptions by address |
| GET | `/addresses/{address}/inscriptions/activity` | Inscription activity by address |
| GET | `/addresses/{address}/runes` | Runes by address |
| GET | `/addresses/{address}/runes/activity` | Rune activity by address |
| GET | `/addresses/{address}/runes/utxos` | Rune UTxOs by address |
| GET | `/addresses/{address}/runes/{rune}` | Rune UTxOs by address and rune (deprecated) |
| GET | `/addresses/{address}/statistics` | Address statistics |
| GET | `/addresses/{address}/txs` | Transactions by address |
| GET | `/addresses/{address}/utxos` | UTxOs by address |

#### BRC20 (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets/brc20` | List all BRC20 tokens |
| GET | `/assets/brc20/{ticker}` | BRC20 token info |
| GET | `/assets/brc20/{ticker}/holders` | BRC20 token holders |

#### Blocks (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/blocks/{height_or_hash}` | Block information |
| GET | `/blocks/{height_or_hash}/inscriptions/activity` | Inscription activity by block |
| GET | `/blocks/{height_or_hash}/transactions` | Transactions by block |

#### Inscriptions (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets/collections/{collection_symbol}/inscriptions` | Inscription IDs by collection |
| GET | `/assets/collections/{collection_symbol}/metadata` | Collection metadata |
| GET | `/assets/collections/{collection_symbol}/stats` | Collection statistics |
| GET | `/assets/inscriptions/{inscription_id}` | Inscription info |
| GET | `/assets/inscriptions/{inscription_id}/activity` | Activity by inscription |
| GET | `/assets/inscriptions/{inscription_id}/collection` | Collection metadata by inscription |
| GET | `/assets/inscriptions/{inscription_id}/content_body` | Content by inscription ID |
| GET | `/assets/inscriptions/{inscription_id}/metadata` | Token metadata by inscription |

#### Runes (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/assets/runes` | List all runes |
| GET | `/assets/runes/{rune}` | Rune info |
| GET | `/assets/runes/{rune}/activity` | Activity by rune |
| GET | `/assets/runes/{rune}/holders` | Holders by rune |
| GET | `/assets/runes/{rune}/utxos` | UTxOs by rune |

#### Transactions (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/transactions/{tx_hash}` | Transaction info |
| GET | `/transactions/{tx_hash}/inscriptions/activity` | Inscription activity by transaction |
| GET | `/transactions/{tx_hash}/metaprotocols` | Transaction with metaprotocols |
| GET | `/transactions/{tx_hash}/outputs/{output_index}` | Transaction output info |

---

### ESPLORA API (29 endpoints)

#### Addresses (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/esplora/address/{address}` | Address information |
| GET | `/esplora/address/{address}/txs` | Address transactions |
| GET | `/esplora/address/{address}/txs/chain` | Address transactions chain |
| GET | `/esplora/address/{address}/txs/mempool` | Address transactions mempool |
| GET | `/esplora/address/{address}/utxo` | Address UTXOs |

#### Blocks (11 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/esplora/block/{hash}` | Block information |
| GET | `/esplora/block/{hash}/header` | Block header |
| GET | `/esplora/block/{hash}/status` | Block status |
| GET | `/esplora/block/{hash}/txs/{start_index}` | Block transactions |
| GET | `/esplora/block/{hash}/txids` | Block transaction IDs |
| GET | `/esplora/block/{hash}/txid/{index}` | Block transaction ID by index |
| GET | `/esplora/block/{hash}/raw` | Raw block data |
| GET | `/esplora/blocks/{start_height}` | Blocks from height |
| GET | `/esplora/block-height/{height}` | Block by height |
| GET | `/esplora/blocks/tip/height` | Block tip height |
| GET | `/esplora/blocks/tip/hash` | Block tip hash |

#### Mempool (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/esplora/mempool` | Mempool information |
| GET | `/esplora/mempool/txids` | Mempool transaction IDs |
| GET | `/esplora/mempool/recent` | Recent mempool transactions |

#### Transactions (10 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/esplora/tx/{txid}` | Transaction information |
| GET | `/esplora/tx/{txid}/hex` | Transaction hex |
| GET | `/esplora/tx/{txid}/merkleblock-proof` | Transaction merkleblock proof |
| GET | `/esplora/tx/{txid}/merkle-proof` | Transaction merkle proof |
| GET | `/esplora/tx/{txid}/outspend/{vout}` | Transaction outspend |
| GET | `/esplora/tx/{txid}/outspends` | Transaction outspends |
| GET | `/esplora/tx/{txid}/raw` | Raw transaction data |
| GET | `/esplora/tx/{txid}/rbf` | Transaction RBF timeline |
| GET | `/esplora/tx/{txid}/status` | Transaction status |
| POST | `/esplora/tx` | Broadcast transaction |

---

### NODE RPC API (24 endpoints)

#### Blocks (8 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rpc/block/latest` | Latest block |
| GET | `/rpc/block/latest/height` | Latest block height |
| GET | `/rpc/block/range/{start_height}/{end_height}` | Block range info |
| GET | `/rpc/block/recent` | Recent block info |
| GET | `/rpc/block/recent/{count}` | Recent blocks by count |
| GET | `/rpc/block/{height_or_hash}` | Block info |
| GET | `/rpc/block/{height_or_hash}/miner` | Block miner info |
| GET | `/rpc/block/{height_or_hash}/volume` | Block volume |

#### General (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rpc/general/info` | Blockchain info |

#### Mempool (5 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/rpc/mempool/info` | Mempool info |
| GET | `/rpc/mempool/transactions` | Mempool transactions |
| GET | `/rpc/mempool/transactions/{tx_hash}` | Mempool transaction info |
| GET | `/rpc/mempool/transactions/{tx_hash}/ancestors` | Mempool transaction ancestors |
| GET | `/rpc/mempool/transactions/{tx_hash}/descendants` | Mempool transaction descendants |

#### Transactions (10 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/rpc/transaction/batch` | Transaction info batch |
| POST | `/rpc/transaction/decode` | Decode transaction |
| GET | `/rpc/transaction/estimatefee/{blocks}` | Estimate fee |
| POST | `/rpc/transaction/hex` | Transaction info from hex |
| POST | `/rpc/transaction/psbt/decode` | Decode PSBT |
| GET | `/rpc/transaction/recent` | Recent transactions |
| GET | `/rpc/transaction/recent/{count}` | Recent transactions by count |
| POST | `/rpc/transaction/submit` | Send transaction |
| GET | `/rpc/transaction/{tx_hash}` | Transaction info |
| GET | `/rpc/transaction/{tx_hash}/hex` | Transaction hex |

---

### EVENT MANAGER API (9 endpoints)

#### Health (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/eventmanager/healthcheck` | Health check |

#### Logs (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/eventmanager/logs/{id}` | Get event log |
| GET | `/eventmanager/logs` | List event logs |

#### Triggers (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/eventmanager/triggers` | List triggers |
| POST | `/eventmanager/triggers` | Create trigger |
| GET | `/eventmanager/triggers/{id}` | Get trigger |
| PUT | `/eventmanager/triggers/{id}` | Update trigger |
| DELETE | `/eventmanager/triggers/{id}` | Delete trigger |
| GET | `/eventmanager/triggers/trigger-condition-options` | List trigger condition options |

---

### MARKET PRICE API (8 endpoints)

#### DEX (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/markets/dexs` | Supported DEX options |
| GET | `/markets/dexs/ohlc/{dex}/{symbol}` | Rune OHLC data |
| GET | `/markets/dexs/trades/{dex}/{symbol}` | Rune trades for DEX |
| GET | `/markets/runes` | Rune registry |

#### Prices (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/markets/prices/batch` | BTC prices by timestamp (batch) |
| POST | `/markets/prices/runes/batch` | Rune prices by timestamp (batch) |
| GET | `/markets/prices/runes/{rune_id}/{timestamp}` | Rune price by timestamp |
| GET | `/markets/prices/{timestamp}` | BTC price by timestamp |

---

### MEMPOOL MONITORING API (9 endpoints)

#### Addresses (4 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mempool/addresses/{address}/balance` | Satoshi balance (mempool-aware) |
| GET | `/mempool/addresses/{address}/runes` | Runes by address (mempool-aware) |
| GET | `/mempool/addresses/{address}/runes/utxos` | Rune UTxOs (mempool-aware) |
| GET | `/mempool/addresses/{address}/utxos` | UTxOs (mempool-aware) |

#### General (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mempool/fee_rates` | Mempool block fee rates |

#### Runes (1 endpoint)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/mempool/assets/runes/{rune}/holders` | Holders by rune (mempool-aware) |

#### Transactions (3 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/mempool/transactions/send` | Transaction propagator |
| GET | `/mempool/transactions/{tx_hash}/metaprotocols` | Transaction with metaprotocols (mempool-aware) |
| GET | `/mempool/transactions/{tx_hash}/outputs/{output_index}` | Transaction output info (mempool-aware) |

---

### WALLET API (6 endpoints)

#### Addresses (6 endpoints)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/wallet/addresses/{address}/activity` | Wallet satoshi activity (mempool-aware) |
| GET | `/wallet/addresses/{address}/activity/metaprotocols` | Metaprotocol activity |
| GET | `/wallet/addresses/{address}/balance/historical` | Historical satoshi balance |
| GET | `/wallet/addresses/{address}/inscriptions/activity` | Inscription activity (mempool-aware) |
| GET | `/wallet/addresses/{address}/runes/activity` | Rune activity (mempool-aware) |
| GET | `/wallet/addresses/{address}/statistics` | Address statistics (mempool-aware) |

---

## Common Use Cases

### 1. Query Address Balance

```bash
# Get current balance
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qcx7ys0ahvtfqcc63sfn6axls0qrhkadnslpd94/balance"

# Get mempool-aware balance (includes pending transactions)
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/mempool/addresses/bc1qcx7ys0ahvtfqcc63sfn6axls0qrhkadnslpd94/balance"
```

### 2. Get Address UTXOs

```bash
# Get all UTXOs
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qcx7ys0ahvtfqcc63sfn6axls0qrhkadnslpd94/utxos"

# Filter out dust and exclude metaprotocols
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/bc1qcx7ys0ahvtfqcc63sfn6axls0qrhkadnslpd94/utxos?filter_dust=true&exclude_metaprotocols=true"

# Mempool-aware UTXOs (includes pending)
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/mempool/addresses/bc1qcx7ys0ahvtfqcc63sfn6axls0qrhkadnslpd94/utxos"
```

### 3. Get Transaction Information

```bash
# Basic transaction info
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/transactions/TX_HASH"

# Transaction with metaprotocols (BRC20, Runes, Inscriptions)
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/transactions/TX_HASH/metaprotocols"

# Using Esplora API
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/esplora/tx/TX_HASH"
```

### 4. Get Block Information

```bash
# By height or hash
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/blocks/800000"

# Latest block
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/block/latest"

# Latest block height
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/block/latest/height"
```

### 5. Get Mempool Information

```bash
# Mempool info
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/mempool/info"

# Fee rates
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/mempool/fee_rates"

# Estimate fee for confirmation in N blocks
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/transaction/estimatefee/6"
```

### 6. Broadcast Transaction

```bash
# Using RPC API
curl -X POST \
  -H "api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"transaction_hex": "YOUR_SIGNED_TX_HEX"}' \
  "https://xbt-mainnet.gomaestro-api.org/v0/rpc/transaction/submit"

# Using Esplora API
curl -X POST \
  -H "api-key: YOUR_API_KEY" \
  -H "Content-Type: text/plain" \
  -d "YOUR_SIGNED_TX_HEX" \
  "https://xbt-mainnet.gomaestro-api.org/v0/esplora/tx"

# Using Mempool Monitoring API (with propagation tracking)
curl -X POST \
  -H "api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"transaction_hex": "YOUR_SIGNED_TX_HEX"}' \
  "https://xbt-mainnet.gomaestro-api.org/v0/mempool/transactions/send"
```

### 7. Query BRC20 Tokens

```bash
# List all BRC20 tokens
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/brc20"

# Get BRC20 token info
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/brc20/ordi"

# Get BRC20 tokens for an address
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/brc20"

# Get BRC20 holders
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/brc20/ordi/holders"
```

### 8. Query Runes

```bash
# List all runes
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/runes"

# Get rune info
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/runes/RUNE_ID"

# Get runes for an address
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/runes"

# Get rune UTXOs for an address
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/runes/utxos?rune=RUNE_ID"

# Get rune holders
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/runes/RUNE_ID/holders"
```

### 9. Query Inscriptions (Ordinals)

```bash
# Get inscriptions for an address
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/inscriptions"

# Get inscription info
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/inscriptions/INSCRIPTION_ID"

# Get inscription content
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/inscriptions/INSCRIPTION_ID/content_body"

# Get collection info
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/assets/collections/COLLECTION_SYMBOL/metadata"
```

### 10. Query Address Activity

```bash
# Get satoshi activity
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/activity?order=desc&count=50"

# Get rune activity
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/runes/activity?order=desc"

# Get inscription activity
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/addresses/ADDRESS/inscriptions/activity?order=desc"

# Wallet API - mempool-aware activity
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/wallet/addresses/ADDRESS/activity?mempool=true"
```

### 11. Get Market Price Data

```bash
# Get current BTC price
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/markets/prices/$(date +%s)"

# Get historical BTC price
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/markets/prices/1672531200"

# Get rune price
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/markets/prices/runes/RUNE_ID/$(date +%s)"

# Get OHLC data for a rune
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/markets/dexs/ohlc/DEX/SYMBOL?resolution=1h&from=1672531200&to=1672617600"
```

### 12. Create Event Triggers (Webhooks)

```bash
# List all triggers
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/eventmanager/triggers"

# Create a trigger
curl -X POST \
  -H "api-key: YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Address Activity Monitor",
    "trigger_type": "address_activity",
    "conditions": {...},
    "webhook_url": "https://your-webhook.com/endpoint"
  }' \
  "https://xbt-mainnet.gomaestro-api.org/v0/eventmanager/triggers"

# Get trigger logs
curl -H "api-key: YOUR_API_KEY" \
  "https://xbt-mainnet.gomaestro-api.org/v0/eventmanager/logs?trigger_id=TRIGGER_ID"
```

---

## Additional Resources

- **Official Documentation:** https://docs.gomaestro.org/bitcoin
- **API Specifications:** https://github.com/maestro-org/maestro-api-specifications
- **Dashboard:** https://dashboard.gomaestro.org/signup
- **Documentation Index:** https://docs.gomaestro.org/llms.txt

---

## Summary Statistics

- **Total Services:** 7
- **Total Endpoints:** 119
- **Networks Supported:** Mainnet, Testnet4
- **Authentication:** API Key (Header-based)
- **Pagination:** Cursor-based
- **Rate Limiting:** Two-tier (Daily + Per-second)
- **Metaprotocol Support:** BRC20, Runes, Inscriptions (Ordinals)

