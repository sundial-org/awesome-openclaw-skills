#!/bin/bash

# Maestro Bitcoin API Comprehensive Wrapper
# Supports all 7 API services with 119 endpoints
# Usage: ./call_maestro.sh <command> [args...]

set -e

# Configuration
API_KEY="${MAESTRO_API_KEY}"
NETWORK="${MAESTRO_NETWORK:-mainnet}"

if [ "$NETWORK" = "testnet" ]; then
  BASE_URL="https://xbt-testnet.gomaestro-api.org/v0"
else
  BASE_URL="https://xbt-mainnet.gomaestro-api.org/v0"
fi

if [ -z "$API_KEY" ]; then
  echo "Error: MAESTRO_API_KEY environment variable is not set."
  exit 1
fi

# Helper function for GET requests
maestro_get() {
  local endpoint="$1"
  curl -s -H "api-key: $API_KEY" "${BASE_URL}${endpoint}"
}

# Helper function for POST requests
maestro_post() {
  local endpoint="$1"
  local data="$2"
  local content_type="${3:-application/json}"
  curl -s -X POST \
    -H "api-key: $API_KEY" \
    -H "Content-Type: $content_type" \
    -d "$data" \
    "${BASE_URL}${endpoint}"
}

# Helper function for PUT requests
maestro_put() {
  local endpoint="$1"
  local data="$2"
  curl -s -X PUT \
    -H "api-key: $API_KEY" \
    -H "Content-Type: application/json" \
    -d "$data" \
    "${BASE_URL}${endpoint}"
}

# Helper function for DELETE requests
maestro_delete() {
  local endpoint="$1"
  curl -s -X DELETE \
    -H "api-key: $API_KEY" \
    "${BASE_URL}${endpoint}"
}

command=$1
shift

case "$command" in

  # ========================================
  # BLOCKCHAIN INDEXER API
  # ========================================

  # Address Operations
  "get-balance")
    maestro_get "/addresses/$1/balance"
    ;;
  "get-utxos")
    maestro_get "/addresses/$1/utxos"
    ;;
  "get-address-txs")
    maestro_get "/addresses/$1/txs"
    ;;
  "get-address-activity")
    maestro_get "/addresses/$1/activity"
    ;;
  "get-address-stats")
    maestro_get "/addresses/$1/statistics"
    ;;
  "get-balance-history")
    maestro_get "/addresses/$1/balance/historical?height=$2"
    ;;
  "get-address-runes")
    maestro_get "/addresses/$1/runes"
    ;;
  "get-address-rune-activity")
    maestro_get "/addresses/$1/runes/activity"
    ;;
  "get-address-rune-utxos")
    maestro_get "/addresses/$1/runes/utxos"
    ;;
  "get-address-brc20")
    maestro_get "/addresses/$1/brc20"
    ;;
  "get-address-brc20-transfers")
    maestro_get "/addresses/$1/brc20/transfer_inscriptions"
    ;;
  "get-address-inscriptions")
    maestro_get "/addresses/$1/inscriptions"
    ;;
  "get-address-inscription-activity")
    maestro_get "/addresses/$1/inscriptions/activity"
    ;;

  # Block Operations
  "get-block")
    maestro_get "/blocks/$1"
    ;;
  "get-block-txs")
    maestro_get "/blocks/$1/transactions"
    ;;
  "get-block-inscriptions")
    maestro_get "/blocks/$1/inscriptions/activity"
    ;;

  # Transaction Operations
  "get-tx")
    maestro_get "/transactions/$1"
    ;;
  "get-tx-metaprotocols")
    maestro_get "/transactions/$1/metaprotocols"
    ;;
  "get-tx-output")
    maestro_get "/transactions/$1/outputs/$2"
    ;;
  "get-tx-inscriptions")
    maestro_get "/transactions/$1/inscriptions/activity"
    ;;

  # BRC20 Operations
  "list-brc20")
    maestro_get "/assets/brc20"
    ;;
  "get-brc20")
    maestro_get "/assets/brc20/$1"
    ;;
  "get-brc20-holders")
    maestro_get "/assets/brc20/$1/holders"
    ;;

  # Runes Operations
  "list-runes")
    maestro_get "/assets/runes"
    ;;
  "get-rune")
    maestro_get "/assets/runes/$1"
    ;;
  "get-rune-activity")
    maestro_get "/assets/runes/$1/activity"
    ;;
  "get-rune-holders")
    maestro_get "/assets/runes/$1/holders"
    ;;
  "get-rune-utxos")
    maestro_get "/assets/runes/$1/utxos"
    ;;

  # Inscriptions Operations
  "get-inscription")
    maestro_get "/assets/inscriptions/$1"
    ;;
  "get-inscription-content")
    maestro_get "/assets/inscriptions/$1/content_body"
    ;;
  "get-inscription-activity")
    maestro_get "/assets/inscriptions/$1/activity"
    ;;
  "get-inscription-metadata")
    maestro_get "/assets/inscriptions/$1/metadata"
    ;;
  "get-inscription-collection")
    maestro_get "/assets/inscriptions/$1/collection"
    ;;
  "get-collection")
    maestro_get "/assets/collections/$1/metadata"
    ;;
  "get-collection-stats")
    maestro_get "/assets/collections/$1/stats"
    ;;
  "get-collection-inscriptions")
    maestro_get "/assets/collections/$1/inscriptions"
    ;;

  # ========================================
  # ESPLORA API
  # ========================================

  "esplora-address-info")
    maestro_get "/esplora/address/$1"
    ;;
  "esplora-address-txs")
    maestro_get "/esplora/address/$1/txs"
    ;;
  "esplora-address-txs-chain")
    maestro_get "/esplora/address/$1/txs/chain"
    ;;
  "esplora-address-txs-mempool")
    maestro_get "/esplora/address/$1/txs/mempool"
    ;;
  "esplora-address-utxos")
    maestro_get "/esplora/address/$1/utxo"
    ;;
  "esplora-block")
    maestro_get "/esplora/block/$1"
    ;;
  "esplora-block-header")
    maestro_get "/esplora/block/$1/header"
    ;;
  "esplora-block-status")
    maestro_get "/esplora/block/$1/status"
    ;;
  "esplora-block-txs")
    maestro_get "/esplora/block/$1/txs/${2:-0}"
    ;;
  "esplora-block-txids")
    maestro_get "/esplora/block/$1/txids"
    ;;
  "esplora-block-txid")
    maestro_get "/esplora/block/$1/txid/$2"
    ;;
  "esplora-block-raw")
    maestro_get "/esplora/block/$1/raw"
    ;;
  "esplora-blocks")
    maestro_get "/esplora/blocks/$1"
    ;;
  "esplora-block-height")
    maestro_get "/esplora/block-height/$1"
    ;;
  "esplora-tip-height")
    maestro_get "/esplora/blocks/tip/height"
    ;;
  "esplora-tip-hash")
    maestro_get "/esplora/blocks/tip/hash"
    ;;
  "esplora-mempool")
    maestro_get "/esplora/mempool"
    ;;
  "esplora-mempool-txids")
    maestro_get "/esplora/mempool/txids"
    ;;
  "esplora-mempool-recent")
    maestro_get "/esplora/mempool/recent"
    ;;
  "esplora-tx")
    maestro_get "/esplora/tx/$1"
    ;;
  "esplora-tx-hex")
    maestro_get "/esplora/tx/$1/hex"
    ;;
  "esplora-tx-merkleblock")
    maestro_get "/esplora/tx/$1/merkleblock-proof"
    ;;
  "esplora-tx-merkle")
    maestro_get "/esplora/tx/$1/merkle-proof"
    ;;
  "esplora-tx-outspend")
    maestro_get "/esplora/tx/$1/outspend/$2"
    ;;
  "esplora-tx-outspends")
    maestro_get "/esplora/tx/$1/outspends"
    ;;
  "esplora-tx-raw")
    maestro_get "/esplora/tx/$1/raw"
    ;;
  "esplora-tx-rbf")
    maestro_get "/esplora/tx/$1/rbf"
    ;;
  "esplora-tx-status")
    maestro_get "/esplora/tx/$1/status"
    ;;
  "esplora-broadcast")
    maestro_post "/esplora/tx" "$1" "text/plain"
    ;;

  # ========================================
  # NODE RPC API
  # ========================================

  "rpc-get-latest-block")
    maestro_get "/rpc/block/latest"
    ;;
  "rpc-get-latest-height"|"get-latest-height")
    maestro_get "/rpc/block/latest/height"
    ;;
  "rpc-get-block-range")
    maestro_get "/rpc/block/range/$1/$2"
    ;;
  "rpc-get-recent-blocks")
    maestro_get "/rpc/block/recent/${1:-10}"
    ;;
  "rpc-get-block")
    maestro_get "/rpc/block/$1"
    ;;
  "rpc-get-block-miner")
    maestro_get "/rpc/block/$1/miner"
    ;;
  "rpc-get-block-volume")
    maestro_get "/rpc/block/$1/volume"
    ;;
  "rpc-get-info"|"get-info")
    maestro_get "/rpc/general/info"
    ;;
  "rpc-get-mempool-info"|"get-mempool-info")
    maestro_get "/rpc/mempool/info"
    ;;
  "rpc-get-mempool-txs")
    maestro_get "/rpc/mempool/transactions"
    ;;
  "rpc-get-mempool-tx")
    maestro_get "/rpc/mempool/transactions/$1"
    ;;
  "rpc-get-mempool-ancestors")
    maestro_get "/rpc/mempool/transactions/$1/ancestors"
    ;;
  "rpc-get-mempool-descendants")
    maestro_get "/rpc/mempool/transactions/$1/descendants"
    ;;
  "rpc-get-tx")
    maestro_get "/rpc/transaction/$1"
    ;;
  "rpc-get-tx-hex")
    maestro_get "/rpc/transaction/$1/hex"
    ;;
  "rpc-get-recent-txs")
    maestro_get "/rpc/transaction/recent/${1:-10}"
    ;;
  "rpc-decode-tx")
    maestro_post "/rpc/transaction/decode" "{\"transaction_hex\":\"$1\"}"
    ;;
  "rpc-decode-psbt")
    maestro_post "/rpc/transaction/psbt/decode" "{\"psbt\":\"$1\"}"
    ;;
  "rpc-tx-from-hex")
    maestro_post "/rpc/transaction/hex" "{\"transaction_hex\":\"$1\"}"
    ;;
  "rpc-tx-batch")
    maestro_post "/rpc/transaction/batch" "$1"
    ;;
  "rpc-broadcast-tx"|"broadcast-tx")
    maestro_post "/rpc/transaction/submit" "{\"transaction_hex\":\"$1\"}"
    ;;
  "rpc-estimate-fee"|"estimate-fee")
    maestro_get "/rpc/transaction/estimatefee/${1:-6}"
    ;;

  # ========================================
  # EVENT MANAGER API
  # ========================================

  "event-healthcheck")
    maestro_get "/eventmanager/healthcheck"
    ;;
  "event-list-triggers")
    maestro_get "/eventmanager/triggers"
    ;;
  "event-create-trigger")
    maestro_post "/eventmanager/triggers" "$1"
    ;;
  "event-get-trigger")
    maestro_get "/eventmanager/triggers/$1"
    ;;
  "event-update-trigger")
    maestro_put "/eventmanager/triggers/$1" "$2"
    ;;
  "event-delete-trigger")
    maestro_delete "/eventmanager/triggers/$1"
    ;;
  "event-trigger-options")
    maestro_get "/eventmanager/triggers/trigger-condition-options"
    ;;
  "event-list-logs")
    maestro_get "/eventmanager/logs"
    ;;
  "event-get-log")
    maestro_get "/eventmanager/logs/$1"
    ;;

  # ========================================
  # MARKET PRICE API
  # ========================================

  "market-btc-price")
    maestro_get "/markets/prices/$1"
    ;;
  "market-btc-price-batch")
    maestro_post "/markets/prices/batch" "$1"
    ;;
  "market-rune-price")
    maestro_get "/markets/prices/runes/$1/$2"
    ;;
  "market-rune-price-batch")
    maestro_post "/markets/prices/runes/batch" "$1"
    ;;
  "market-list-dexs")
    maestro_get "/markets/dexs"
    ;;
  "market-list-runes")
    maestro_get "/markets/runes"
    ;;
  "market-ohlc")
    maestro_get "/markets/dexs/ohlc/$1/$2"
    ;;
  "market-trades")
    maestro_get "/markets/dexs/trades/$1/$2"
    ;;

  # ========================================
  # MEMPOOL MONITORING API
  # ========================================

  "mempool-get-balance")
    maestro_get "/mempool/addresses/$1/balance"
    ;;
  "mempool-get-utxos")
    maestro_get "/mempool/addresses/$1/utxos"
    ;;
  "mempool-get-runes")
    maestro_get "/mempool/addresses/$1/runes"
    ;;
  "mempool-get-rune-utxos")
    maestro_get "/mempool/addresses/$1/runes/utxos"
    ;;
  "mempool-get-fee-rates")
    maestro_get "/mempool/fee_rates"
    ;;
  "mempool-get-rune-holders")
    maestro_get "/mempool/assets/runes/$1/holders"
    ;;
  "mempool-broadcast")
    maestro_post "/mempool/transactions/send" "{\"transaction_hex\":\"$1\"}"
    ;;
  "mempool-get-tx-meta")
    maestro_get "/mempool/transactions/$1/metaprotocols"
    ;;
  "mempool-get-tx-output")
    maestro_get "/mempool/transactions/$1/outputs/$2"
    ;;

  # ========================================
  # WALLET API
  # ========================================

  "wallet-get-activity")
    maestro_get "/wallet/addresses/$1/activity"
    ;;
  "wallet-get-meta-activity")
    maestro_get "/wallet/addresses/$1/activity/metaprotocols"
    ;;
  "wallet-get-balance-history")
    maestro_get "/wallet/addresses/$1/balance/historical?height=$2"
    ;;
  "wallet-get-inscription-activity")
    maestro_get "/wallet/addresses/$1/inscriptions/activity"
    ;;
  "wallet-get-rune-activity")
    maestro_get "/wallet/addresses/$1/runes/activity"
    ;;
  "wallet-get-stats")
    maestro_get "/wallet/addresses/$1/statistics"
    ;;

  # ========================================
  # HELP
  # ========================================

  "help"|"--help"|"-h"|"")
    cat <<EOF
Maestro Bitcoin API Wrapper - Comprehensive Access to 119 Endpoints

Network: $NETWORK ($BASE_URL)

USAGE:
  ./call_maestro.sh <command> [args...]

BLOCKCHAIN INDEXER API (37 endpoints):

  Address Operations:
    get-balance <address>                    - Get address satoshi balance
    get-utxos <address>                      - Get address UTXOs
    get-address-txs <address>                - Get address transactions
    get-address-activity <address>           - Get address activity
    get-address-stats <address>              - Get address statistics
    get-balance-history <address> <height>   - Get historical balance
    get-address-runes <address>              - Get runes for address
    get-address-rune-activity <address>      - Get rune activity
    get-address-rune-utxos <address>         - Get rune UTXOs
    get-address-brc20 <address>              - Get BRC20 tokens
    get-address-brc20-transfers <address>    - Get BRC20 transfer inscriptions
    get-address-inscriptions <address>       - Get inscriptions
    get-address-inscription-activity <addr>  - Get inscription activity

  Block Operations:
    get-block <height_or_hash>               - Get block information
    get-block-txs <height_or_hash>           - Get block transactions
    get-block-inscriptions <height_or_hash>  - Get block inscription activity

  Transaction Operations:
    get-tx <tx_hash>                         - Get transaction info
    get-tx-metaprotocols <tx_hash>           - Get tx with metaprotocols
    get-tx-output <tx_hash> <index>          - Get tx output info
    get-tx-inscriptions <tx_hash>            - Get tx inscription activity

  BRC20 Operations:
    list-brc20                               - List all BRC20 tokens
    get-brc20 <ticker>                       - Get BRC20 token info
    get-brc20-holders <ticker>               - Get BRC20 holders

  Runes Operations:
    list-runes                               - List all runes
    get-rune <rune_id>                       - Get rune info
    get-rune-activity <rune_id>              - Get rune activity
    get-rune-holders <rune_id>               - Get rune holders
    get-rune-utxos <rune_id>                 - Get rune UTXOs

  Inscriptions Operations:
    get-inscription <id>                     - Get inscription info
    get-inscription-content <id>             - Get inscription content
    get-inscription-activity <id>            - Get inscription activity
    get-inscription-metadata <id>            - Get inscription metadata
    get-inscription-collection <id>          - Get inscription collection
    get-collection <symbol>                  - Get collection metadata
    get-collection-stats <symbol>            - Get collection stats
    get-collection-inscriptions <symbol>     - Get collection inscriptions

ESPLORA API (29 endpoints):

  Address Operations:
    esplora-address-info <address>           - Get address info
    esplora-address-txs <address>            - Get address transactions
    esplora-address-txs-chain <address>      - Get confirmed transactions
    esplora-address-txs-mempool <address>    - Get mempool transactions
    esplora-address-utxos <address>          - Get address UTXOs

  Block Operations:
    esplora-block <hash>                     - Get block info
    esplora-block-header <hash>              - Get block header
    esplora-block-status <hash>              - Get block status
    esplora-block-txs <hash> [index]         - Get block transactions
    esplora-block-txids <hash>               - Get block tx IDs
    esplora-block-txid <hash> <index>        - Get tx ID by index
    esplora-block-raw <hash>                 - Get raw block data
    esplora-blocks <start_height>            - Get 10 blocks from height
    esplora-block-height <height>            - Get block hash by height
    esplora-tip-height                       - Get tip height
    esplora-tip-hash                         - Get tip hash

  Mempool Operations:
    esplora-mempool                          - Get mempool stats
    esplora-mempool-txids                    - Get mempool tx IDs
    esplora-mempool-recent                   - Get recent mempool txs

  Transaction Operations:
    esplora-tx <txid>                        - Get transaction info
    esplora-tx-hex <txid>                    - Get transaction hex
    esplora-tx-merkleblock <txid>            - Get merkleblock proof
    esplora-tx-merkle <txid>                 - Get merkle proof
    esplora-tx-outspend <txid> <vout>        - Get output spend info
    esplora-tx-outspends <txid>              - Get all output spends
    esplora-tx-raw <txid>                    - Get raw transaction
    esplora-tx-rbf <txid>                    - Get RBF history
    esplora-tx-status <txid>                 - Get tx status
    esplora-broadcast <hex>                  - Broadcast transaction

NODE RPC API (24 endpoints):

  Block Operations:
    rpc-get-latest-block                     - Get latest block
    rpc-get-latest-height                    - Get latest block height
    get-latest-height                        - (alias)
    rpc-get-block-range <start> <end>        - Get block range
    rpc-get-recent-blocks [count]            - Get recent blocks
    rpc-get-block <height_or_hash>           - Get block info
    rpc-get-block-miner <height_or_hash>     - Get block miner
    rpc-get-block-volume <height_or_hash>    - Get block volume

  General:
    rpc-get-info                             - Get blockchain info
    get-info                                 - (alias)

  Mempool Operations:
    rpc-get-mempool-info                     - Get mempool info
    get-mempool-info                         - (alias)
    rpc-get-mempool-txs                      - Get mempool transactions
    rpc-get-mempool-tx <tx_hash>             - Get mempool tx info
    rpc-get-mempool-ancestors <tx_hash>      - Get tx ancestors
    rpc-get-mempool-descendants <tx_hash>    - Get tx descendants

  Transaction Operations:
    rpc-get-tx <tx_hash>                     - Get transaction info
    rpc-get-tx-hex <tx_hash>                 - Get transaction hex
    rpc-get-recent-txs [count]               - Get recent transactions
    rpc-decode-tx <hex>                      - Decode transaction
    rpc-decode-psbt <psbt>                   - Decode PSBT
    rpc-tx-from-hex <hex>                    - Get tx info from hex
    rpc-tx-batch <json>                      - Get batch tx info
    rpc-broadcast-tx <hex>                   - Broadcast transaction
    broadcast-tx <hex>                       - (alias)
    rpc-estimate-fee [blocks]                - Estimate fee (default: 6)
    estimate-fee [blocks]                    - (alias)

EVENT MANAGER API (9 endpoints):

    event-healthcheck                        - Health check
    event-list-triggers                      - List all triggers
    event-create-trigger <json>              - Create trigger
    event-get-trigger <id>                   - Get trigger details
    event-update-trigger <id> <json>         - Update trigger
    event-delete-trigger <id>                - Delete trigger
    event-trigger-options                    - Get trigger options
    event-list-logs                          - List event logs
    event-get-log <id>                       - Get event log

MARKET PRICE API (8 endpoints):

    market-btc-price <timestamp>             - Get BTC price
    market-btc-price-batch <json>            - Get BTC prices batch
    market-rune-price <rune_id> <timestamp>  - Get rune price
    market-rune-price-batch <json>           - Get rune prices batch
    market-list-dexs                         - List supported DEXs
    market-list-runes                        - Get rune registry
    market-ohlc <dex> <symbol>               - Get OHLC data
    market-trades <dex> <symbol>             - Get trades

MEMPOOL MONITORING API (9 endpoints):

    mempool-get-balance <address>            - Get balance (mempool-aware)
    mempool-get-utxos <address>              - Get UTXOs (mempool-aware)
    mempool-get-runes <address>              - Get runes (mempool-aware)
    mempool-get-rune-utxos <address>         - Get rune UTXOs (mempool-aware)
    mempool-get-fee-rates                    - Get current fee rates
    mempool-get-rune-holders <rune>          - Get rune holders (mempool-aware)
    mempool-broadcast <hex>                  - Broadcast with tracking
    mempool-get-tx-meta <tx_hash>            - Get tx metaprotocols
    mempool-get-tx-output <tx_hash> <index>  - Get tx output

WALLET API (6 endpoints):

    wallet-get-activity <address>            - Get wallet activity
    wallet-get-meta-activity <address>       - Get metaprotocol activity
    wallet-get-balance-history <addr> <h>    - Get historical balance
    wallet-get-inscription-activity <addr>   - Get inscription activity
    wallet-get-rune-activity <address>       - Get rune activity
    wallet-get-stats <address>               - Get address statistics

CONFIGURATION:
  MAESTRO_API_KEY      - Your Maestro API key (required)
  MAESTRO_NETWORK      - Network: mainnet or testnet (default: mainnet)

EXAMPLES:
  # Get latest block height
  ./call_maestro.sh get-latest-height

  # Get address balance
  ./call_maestro.sh get-balance bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

  # Get mempool info
  ./call_maestro.sh get-mempool-info

  # Estimate fee for 6 blocks
  ./call_maestro.sh estimate-fee 6

  # List all BRC20 tokens
  ./call_maestro.sh list-brc20

  # Get runes for address
  ./call_maestro.sh get-address-runes bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh

For more information:
  - API Reference: references/api_reference.md
  - Official Docs: https://docs.gomaestro.org/bitcoin
EOF
    ;;

  *)
    echo "Unknown command: $command"
    echo "Run './call_maestro.sh help' for usage information."
    exit 1
    ;;
esac
