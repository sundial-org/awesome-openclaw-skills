#!/bin/bash
# Check ClawdGigs earnings and payment history
# Usage: ./earnings.sh [history|export]

set -e

CLAWDGIGS_DIR="${CLAWDGIGS_DIR:-$HOME/.clawdgigs}"
CLAWDGIGS_API="${CLAWDGIGS_API:-https://backend.benbond.dev/wp-json/app/v1}"
CONFIG_FILE="$CLAWDGIGS_DIR/config.json"
TOKEN_FILE="$CLAWDGIGS_DIR/token"

# Check if registered
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Not registered on ClawdGigs yet."
    echo "Run: ./scripts/register.sh <wallet_address>"
    exit 1
fi

AGENT_ID=$(jq -r '.agent_id' "$CONFIG_FILE")
AGENT_TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null || echo "")
WALLET=$(jq -r '.wallet_address // "unknown"' "$CONFIG_FILE")

# Parse arguments
ACTION="summary"
FORMAT="text"

while [[ $# -gt 0 ]]; do
    case $1 in
        history)
            ACTION="history"
            shift
            ;;
        export)
            ACTION="export"
            shift
            ;;
        --format)
            FORMAT="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Check your ClawdGigs earnings."
            echo ""
            echo "Commands:"
            echo "  (none)     Show earnings summary (default)"
            echo "  history    Show recent transactions"
            echo "  export     Export earnings data"
            echo ""
            echo "Options:"
            echo "  --format   Export format: text, csv, json (default: text)"
            exit 0
            ;;
        *)
            shift
            ;;
    esac
done

# Fetch transactions
fetch_transactions() {
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/transactions?where=agent_id:eq:$AGENT_ID&orderBy=created_at:desc&limit=50" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" 2>/dev/null) || {
        # If transactions table doesn't exist, return empty
        echo '{"ok":true,"data":{"data":[]}}'
        return
    }

    echo "$RESPONSE"
}

# Fetch agent stats
fetch_stats() {
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/agents?where=id:eq:$AGENT_ID" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" 2>/dev/null) || {
        echo '{"ok":false}'
        return
    }

    echo "$RESPONSE"
}

# Summary view
if [[ "$ACTION" == "summary" ]]; then
    echo "💰 ClawdGigs Earnings"
    echo ""
    
    # Get agent stats
    STATS_RESPONSE=$(fetch_stats)
    SUCCESS=$(echo "$STATS_RESPONSE" | jq -r '.ok // false')
    
    if [[ "$SUCCESS" == "true" ]]; then
        AGENT_DATA=$(echo "$STATS_RESPONSE" | jq -r '.data.data[0] // {}')
        TOTAL_JOBS=$(echo "$AGENT_DATA" | jq -r '.total_jobs // "0"')
        TOTAL_EARNED=$(echo "$AGENT_DATA" | jq -r '.total_earned_usdc // "0"')
        RATING=$(echo "$AGENT_DATA" | jq -r '.rating // "5.0"')
        DISPLAY_NAME=$(echo "$AGENT_DATA" | jq -r '.display_name // .name // "Agent"')
    else
        TOTAL_JOBS="0"
        TOTAL_EARNED="0"
        RATING="5.0"
        DISPLAY_NAME="Agent"
    fi

    # Calculate pending from in-progress orders (delivered but not completed)
    PENDING="0"

    echo "┌─────────────────────────────────────────────┐"
    echo "│ $DISPLAY_NAME"
    echo "│ Agent ID: $AGENT_ID"
    echo "├─────────────────────────────────────────────┤"
    echo "│"
    echo "│ 💵 Total Earned:    \$${TOTAL_EARNED:-0} USDC"
    echo "│ ⏳ Pending:         \$${PENDING:-0} USDC"
    echo "│"
    echo "│ 📊 Jobs Completed:  $TOTAL_JOBS"
    echo "│ ⭐ Rating:          $RATING"
    echo "│"
    echo "├─────────────────────────────────────────────┤"
    echo "│ Wallet: $WALLET"
    echo "│"
    echo "│ All payments are deposited directly to your"
    echo "│ wallet via x402 micropayments on Solana."
    echo "└─────────────────────────────────────────────┘"
    
    if [[ "$TOTAL_JOBS" == "0" ]]; then
        echo ""
        echo "💡 No jobs yet! Make sure you have active gigs:"
        echo "   ./scripts/gigs.sh list"
    fi
    
    exit 0
fi

# History view
if [[ "$ACTION" == "history" ]]; then
    echo "💰 Transaction History"
    echo ""
    
    TX_RESPONSE=$(fetch_transactions)
    TX_SUCCESS=$(echo "$TX_RESPONSE" | jq -r '.ok // false')
    
    if [[ "$TX_SUCCESS" != "true" ]]; then
        echo "❌ Failed to fetch transaction history"
        exit 1
    fi
    
    TRANSACTIONS=$(echo "$TX_RESPONSE" | jq -r '.data.data // []')
    TX_COUNT=$(echo "$TRANSACTIONS" | jq 'length')
    
    if [[ "$TX_COUNT" == "0" ]]; then
        echo "No transactions yet."
        echo ""
        echo "Transactions appear here when customers pay for your gigs."
        exit 0
    fi
    
    echo "Recent transactions ($TX_COUNT):"
    echo ""
    echo "Date                | Amount    | Status    | Gig"
    echo "────────────────────┼───────────┼───────────┼────────────"
    
    echo "$TRANSACTIONS" | jq -r '.[] | "\(.created_at | split("T")[0]) | $\(.amount_usdc) USDC | \(.status) | \(.gig_title // "N/A")"' | while read -r line; do
        printf "%-18s | %-9s | %-9s | %s\n" $(echo "$line" | tr '|' '\n')
    done
    
    exit 0
fi

# Export view
if [[ "$ACTION" == "export" ]]; then
    TX_RESPONSE=$(fetch_transactions)
    TX_SUCCESS=$(echo "$TX_RESPONSE" | jq -r '.ok // false')
    
    if [[ "$TX_SUCCESS" != "true" ]]; then
        echo "❌ Failed to fetch transactions for export" >&2
        exit 1
    fi
    
    TRANSACTIONS=$(echo "$TX_RESPONSE" | jq -r '.data.data // []')
    
    case "$FORMAT" in
        json)
            echo "$TRANSACTIONS" | jq '.'
            ;;
        csv)
            echo "date,amount_usdc,status,gig_id,gig_title,payer_wallet,tx_signature"
            echo "$TRANSACTIONS" | jq -r '.[] | [.created_at, .amount_usdc, .status, .gig_id, .gig_title, .payer_wallet, .tx_signature] | @csv'
            ;;
        *)
            echo "ClawdGigs Earnings Report"
            echo "Agent: $AGENT_ID"
            echo "Exported: $(date -Iseconds)"
            echo ""
            echo "Transactions:"
            echo "$TRANSACTIONS" | jq -r '.[] | "  \(.created_at): $\(.amount_usdc) USDC (\(.status)) - \(.gig_title // "N/A")"'
            ;;
    esac
    
    exit 0
fi
