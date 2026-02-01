# Maestro Bitcoin API - Usage Examples

Comprehensive examples for common use cases across all 7 API services.

## Table of Contents

1. [Address Operations](#address-operations)
2. [Block Operations](#block-operations)
3. [Transaction Operations](#transaction-operations)
4. [Metaprotocol Queries](#metaprotocol-queries)
5. [Mempool Operations](#mempool-operations)
6. [Market Data](#market-data)
7. [Event Management](#event-management)
8. [Wallet Tracking](#wallet-tracking)

---

## Address Operations

### Get Address Balance

```bash
# Standard balance
./scripts/call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Mempool-aware balance (includes pending transactions)
./scripts/call_maestro.sh mempool-get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Historical balance at specific block
./scripts/call_maestro.sh get-balance-history bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh 800000
```

### Get Address UTXOs

```bash
# Standard UTXOs
./scripts/call_maestro.sh get-utxos bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Mempool-aware UTXOs (includes pending)
./scripts/call_maestro.sh mempool-get-utxos bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Using Esplora API
./scripts/call_maestro.sh esplora-address-utxos bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Get Address Transactions

```bash
# Standard transactions
./scripts/call_maestro.sh get-address-txs bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# All transactions (Esplora)
./scripts/call_maestro.sh esplora-address-txs bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Only confirmed transactions (Esplora)
./scripts/call_maestro.sh esplora-address-txs-chain bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Only mempool transactions (Esplora)
./scripts/call_maestro.sh esplora-address-txs-mempool bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Get Address Activity

```bash
# Satoshi activity
./scripts/call_maestro.sh get-address-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Wallet activity (mempool-aware)
./scripts/call_maestro.sh wallet-get-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Metaprotocol activity
./scripts/call_maestro.sh wallet-get-meta-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Get Address Statistics

```bash
# Standard statistics
./scripts/call_maestro.sh get-address-stats bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Mempool-aware statistics
./scripts/call_maestro.sh wallet-get-stats bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Using Esplora API
./scripts/call_maestro.sh esplora-address-info bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

---

## Block Operations

### Get Latest Block Information

```bash
# Latest block
./scripts/call_maestro.sh rpc-get-latest-block

# Latest block height
./scripts/call_maestro.sh get-latest-height

# Using Esplora API
./scripts/call_maestro.sh esplora-tip-height
./scripts/call_maestro.sh esplora-tip-hash
```

### Get Block by Height or Hash

```bash
# By height (Blockchain Indexer)
./scripts/call_maestro.sh get-block 800000

# By hash (Blockchain Indexer)
./scripts/call_maestro.sh get-block 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054

# Using RPC API
./scripts/call_maestro.sh rpc-get-block 800000

# Using Esplora API
./scripts/call_maestro.sh esplora-block 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054
```

### Get Block Transactions

```bash
# Blockchain Indexer
./scripts/call_maestro.sh get-block-txs 800000

# Esplora API - all transaction IDs
./scripts/call_maestro.sh esplora-block-txids 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054

# Esplora API - paginated transactions
./scripts/call_maestro.sh esplora-block-txs 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054 0
```

### Get Block Range

```bash
# Get multiple blocks
./scripts/call_maestro.sh rpc-get-block-range 800000 800010

# Get recent blocks
./scripts/call_maestro.sh rpc-get-recent-blocks 5

# Get 10 blocks from height (Esplora)
./scripts/call_maestro.sh esplora-blocks 800000
```

### Get Block Details

```bash
# Block miner information
./scripts/call_maestro.sh rpc-get-block-miner 800000

# Block transaction volume
./scripts/call_maestro.sh rpc-get-block-volume 800000

# Block header (Esplora)
./scripts/call_maestro.sh esplora-block-header 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054

# Block status (Esplora)
./scripts/call_maestro.sh esplora-block-status 00000000000000000002a7c4c1e48d76c5a37902165a270156b7a8d72728a054
```

---

## Transaction Operations

### Get Transaction Information

```bash
# Blockchain Indexer
./scripts/call_maestro.sh get-tx 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# With metaprotocol data (BRC20, Runes, Inscriptions)
./scripts/call_maestro.sh get-tx-metaprotocols 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# Using RPC API
./scripts/call_maestro.sh rpc-get-tx 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# Using Esplora API
./scripts/call_maestro.sh esplora-tx 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

### Get Transaction Hex

```bash
# RPC API
./scripts/call_maestro.sh rpc-get-tx-hex 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# Esplora API
./scripts/call_maestro.sh esplora-tx-hex 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# Raw transaction (Esplora)
./scripts/call_maestro.sh esplora-tx-raw 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

### Get Transaction Output Information

```bash
# Specific output
./scripts/call_maestro.sh get-tx-output 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b 0

# Mempool-aware output
./scripts/call_maestro.sh mempool-get-tx-output 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b 0

# Output spend status (Esplora)
./scripts/call_maestro.sh esplora-tx-outspend 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b 0

# All output spends (Esplora)
./scripts/call_maestro.sh esplora-tx-outspends 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

### Broadcast Transaction

```bash
# Using RPC API
./scripts/call_maestro.sh broadcast-tx 0200000001...

# Using Esplora API
./scripts/call_maestro.sh esplora-broadcast 0200000001...

# Using Mempool API (with propagation tracking)
./scripts/call_maestro.sh mempool-broadcast 0200000001...
```

### Decode Transaction

```bash
# Decode from hex
./scripts/call_maestro.sh rpc-decode-tx 0200000001...

# Get transaction info from hex
./scripts/call_maestro.sh rpc-tx-from-hex 0200000001...

# Decode PSBT
./scripts/call_maestro.sh rpc-decode-psbt cHNidP8BAH...
```

### Get Transaction Proofs

```bash
# Merkle proof (Esplora)
./scripts/call_maestro.sh esplora-tx-merkle 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# Merkleblock proof (Esplora)
./scripts/call_maestro.sh esplora-tx-merkleblock 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

---

## Metaprotocol Queries

### BRC20 Tokens

```bash
# List all BRC20 tokens
./scripts/call_maestro.sh list-brc20

# Get specific BRC20 token info
./scripts/call_maestro.sh get-brc20 ordi

# Get BRC20 holders
./scripts/call_maestro.sh get-brc20-holders ordi

# Get BRC20 tokens for an address
./scripts/call_maestro.sh get-address-brc20 bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get BRC20 transfer inscriptions
./scripts/call_maestro.sh get-address-brc20-transfers bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Runes

```bash
# List all runes
./scripts/call_maestro.sh list-runes

# Get rune information
./scripts/call_maestro.sh get-rune 840000:1

# Get rune activity
./scripts/call_maestro.sh get-rune-activity 840000:1

# Get rune holders
./scripts/call_maestro.sh get-rune-holders 840000:1

# Get rune UTXOs
./scripts/call_maestro.sh get-rune-utxos 840000:1

# Get runes for an address
./scripts/call_maestro.sh get-address-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get rune activity for address
./scripts/call_maestro.sh get-address-rune-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get rune UTXOs for address
./scripts/call_maestro.sh get-address-rune-utxos bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Mempool-aware rune queries
./scripts/call_maestro.sh mempool-get-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
./scripts/call_maestro.sh mempool-get-rune-utxos bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
./scripts/call_maestro.sh mempool-get-rune-holders 840000:1
```

### Inscriptions (Ordinals)

```bash
# Get inscription info
./scripts/call_maestro.sh get-inscription 1234567i0

# Get inscription content
./scripts/call_maestro.sh get-inscription-content 1234567i0

# Get inscription activity
./scripts/call_maestro.sh get-inscription-activity 1234567i0

# Get inscription metadata
./scripts/call_maestro.sh get-inscription-metadata 1234567i0

# Get inscription collection
./scripts/call_maestro.sh get-inscription-collection 1234567i0

# Get inscriptions for an address
./scripts/call_maestro.sh get-address-inscriptions bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get inscription activity for address
./scripts/call_maestro.sh get-address-inscription-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Wallet inscription activity (mempool-aware)
./scripts/call_maestro.sh wallet-get-inscription-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Collections

```bash
# Get collection metadata
./scripts/call_maestro.sh get-collection bitcoin-frogs

# Get collection statistics
./scripts/call_maestro.sh get-collection-stats bitcoin-frogs

# Get all inscriptions in collection
./scripts/call_maestro.sh get-collection-inscriptions bitcoin-frogs
```

---

## Mempool Operations

### Get Mempool Information

```bash
# Mempool info and statistics
./scripts/call_maestro.sh get-mempool-info

# Mempool stats (Esplora)
./scripts/call_maestro.sh esplora-mempool

# Current fee rates
./scripts/call_maestro.sh mempool-get-fee-rates

# Estimate fee for confirmation in N blocks
./scripts/call_maestro.sh estimate-fee 6
./scripts/call_maestro.sh estimate-fee 1
./scripts/call_maestro.sh estimate-fee 24
```

### Get Mempool Transactions

```bash
# All mempool transactions (RPC)
./scripts/call_maestro.sh rpc-get-mempool-txs

# Mempool transaction IDs (Esplora)
./scripts/call_maestro.sh esplora-mempool-txids

# Recent mempool transactions (Esplora)
./scripts/call_maestro.sh esplora-mempool-recent

# Specific mempool transaction
./scripts/call_maestro.sh rpc-get-mempool-tx 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

### Mempool Transaction Relationships

```bash
# Get transaction ancestors
./scripts/call_maestro.sh rpc-get-mempool-ancestors 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b

# Get transaction descendants
./scripts/call_maestro.sh rpc-get-mempool-descendants 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

### RBF (Replace-By-Fee) Tracking

```bash
# Get RBF history timeline
./scripts/call_maestro.sh esplora-tx-rbf 4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b
```

---

## Market Data

### Bitcoin Price

```bash
# Current BTC price (use current timestamp)
./scripts/call_maestro.sh market-btc-price $(date +%s)

# Historical BTC price
./scripts/call_maestro.sh market-btc-price 1672531200

# Batch price query
./scripts/call_maestro.sh market-btc-price-batch '{"timestamps": [1672531200, 1672617600, 1672704000]}'
```

### Rune Price

```bash
# Current rune price
./scripts/call_maestro.sh market-rune-price 840000:1 $(date +%s)

# Historical rune price
./scripts/call_maestro.sh market-rune-price 840000:1 1672531200

# Batch rune price query
./scripts/call_maestro.sh market-rune-price-batch '{"rune_id": "840000:1", "timestamps": [1672531200, 1672617600]}'
```

### DEX Data

```bash
# List supported DEXs
./scripts/call_maestro.sh market-list-dexs

# Get rune registry
./scripts/call_maestro.sh market-list-runes

# Get OHLC data for a rune
./scripts/call_maestro.sh market-ohlc unisat DOG

# Get recent trades
./scripts/call_maestro.sh market-trades unisat DOG
```

---

## Event Management

### Managing Triggers (Webhooks)

```bash
# Health check
./scripts/call_maestro.sh event-healthcheck

# List all triggers
./scripts/call_maestro.sh event-list-triggers

# Get trigger condition options
./scripts/call_maestro.sh event-trigger-options

# Create a trigger
./scripts/call_maestro.sh event-create-trigger '{
  "name": "Address Activity Monitor",
  "trigger_type": "address_activity",
  "conditions": {
    "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "min_value": 10000000
  },
  "webhook_url": "https://your-webhook.com/endpoint"
}'

# Get trigger details
./scripts/call_maestro.sh event-get-trigger trigger_id_here

# Update trigger
./scripts/call_maestro.sh event-update-trigger trigger_id_here '{
  "name": "Updated Monitor",
  "conditions": {
    "address": "bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh",
    "min_value": 50000000
  }
}'

# Delete trigger
./scripts/call_maestro.sh event-delete-trigger trigger_id_here
```

### Event Logs

```bash
# List all event logs
./scripts/call_maestro.sh event-list-logs

# Get specific event log
./scripts/call_maestro.sh event-get-log log_id_here
```

---

## Wallet Tracking

### Wallet Activity

```bash
# Get wallet satoshi activity
./scripts/call_maestro.sh wallet-get-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get metaprotocol activity
./scripts/call_maestro.sh wallet-get-meta-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get inscription activity
./scripts/call_maestro.sh wallet-get-inscription-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Get rune activity
./scripts/call_maestro.sh wallet-get-rune-activity bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Historical Balance

```bash
# Get balance at specific block height
./scripts/call_maestro.sh wallet-get-balance-history bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh 800000

# Using Blockchain Indexer
./scripts/call_maestro.sh get-balance-history bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh 800000
```

---

## Advanced Examples

### Batch Operations

```bash
# Get multiple transaction info at once
./scripts/call_maestro.sh rpc-tx-batch '{
  "transaction_hashes": [
    "4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
  ]
}'
```

### Comparing Standard vs Mempool-Aware Queries

```bash
# Standard balance (confirmed only)
./scripts/call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Mempool-aware balance (includes pending)
./scripts/call_maestro.sh mempool-get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Standard runes (confirmed only)
./scripts/call_maestro.sh get-address-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

# Mempool-aware runes (includes pending)
./scripts/call_maestro.sh mempool-get-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh
```

### Using Different APIs for Same Data

```bash
ADDRESS="bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh"

# Get UTXOs using different APIs
./scripts/call_maestro.sh get-utxos $ADDRESS              # Blockchain Indexer
./scripts/call_maestro.sh esplora-address-utxos $ADDRESS  # Esplora
./scripts/call_maestro.sh mempool-get-utxos $ADDRESS      # Mempool Monitoring

# Get transaction info using different APIs
TX_HASH="4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"
./scripts/call_maestro.sh get-tx $TX_HASH                 # Blockchain Indexer
./scripts/call_maestro.sh rpc-get-tx $TX_HASH             # RPC
./scripts/call_maestro.sh esplora-tx $TX_HASH             # Esplora
```

### Monitoring Transaction Lifecycle

```bash
TX_HASH="4a5e1e4baab89f3a32518a88c31bc87f618f76673e2cc77ab2127b7afdeda33b"

# Check if transaction is in mempool
./scripts/call_maestro.sh rpc-get-mempool-tx $TX_HASH

# Get transaction status
./scripts/call_maestro.sh esplora-tx-status $TX_HASH

# Check RBF history
./scripts/call_maestro.sh esplora-tx-rbf $TX_HASH

# Once confirmed, get full transaction info
./scripts/call_maestro.sh get-tx $TX_HASH

# Get block it was confirmed in
./scripts/call_maestro.sh esplora-tx $TX_HASH
```

---

## Tips and Best Practices

### Choosing the Right API

- **Blockchain Indexer**: Best for metaprotocol data (BRC20, Runes, Inscriptions)
- **Esplora**: Best for Blockstream compatibility and raw data
- **Node RPC**: Best for detailed blockchain queries and fee estimation
- **Mempool Monitoring**: Best for real-time pending transaction tracking
- **Wallet API**: Best for address-level activity tracking with mempool awareness
- **Event Manager**: Best for setting up automated notifications
- **Market Price**: Best for price feeds and DEX data

### Performance Tips

1. Use mempool-aware endpoints only when you need pending transaction data
2. Use cursor-based pagination for large result sets
3. Monitor rate limit headers in responses
4. Cache blockchain data that doesn't change (confirmed transactions, blocks)
5. Use batch endpoints when querying multiple items

### Error Handling

```bash
# Check if API key is set
if [ -z "$MAESTRO_API_KEY" ]; then
  echo "Error: MAESTRO_API_KEY not set"
  exit 1
fi

# Check response status
RESPONSE=$(./scripts/call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh)
if echo "$RESPONSE" | grep -q "error"; then
  echo "API Error: $RESPONSE"
  exit 1
fi
```

---

## Additional Resources

- [API Reference](api_reference.md): Complete endpoint documentation
- [SKILL.md](../SKILL.md): Skill overview and configuration
- [Official Documentation](https://docs.gomaestro.org/bitcoin): Maestro Bitcoin docs
- [Dashboard](https://dashboard.gomaestro.org): Manage API keys and projects
