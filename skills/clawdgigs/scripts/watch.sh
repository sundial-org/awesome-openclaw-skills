#!/bin/bash
# Watch for new ClawdGigs orders
# Usage: ./watch.sh [check|list|ack|webhook] [options]

set -e

CLAWDGIGS_DIR="${CLAWDGIGS_DIR:-$HOME/.clawdgigs}"
CLAWDGIGS_API="${CLAWDGIGS_API:-https://backend.benbond.dev/wp-json/app/v1}"
CONFIG_FILE="$CLAWDGIGS_DIR/config.json"
TOKEN_FILE="$CLAWDGIGS_DIR/token"
SEEN_FILE="$CLAWDGIGS_DIR/seen_orders.json"

# Handle --help before registration check
if [[ "$1" == "--help" || "$1" == "-h" ]]; then
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Watch for incoming ClawdGigs orders."
    echo ""
    echo "Commands:"
    echo "  check               Check for new pending orders (default)"
    echo "  list                List all orders (with --status filter)"
    echo "  ack <order_id>      Acknowledge an order (mark as seen)"
    echo "  clear               Clear seen orders list"
    echo "  webhook             Start webhook listener (experimental)"
    echo ""
    echo "Options:"
    echo "  --all, -a           Show all orders, not just new ones"
    echo "  --quiet, -q         Minimal output (for cron/heartbeat)"
    echo "  --json              Output as JSON"
    echo "  --status <status>   Filter by status: pending, processing, completed, cancelled"
    echo "  --port <port>       Webhook listener port (default: 8402)"
    echo "  --handler <script>  Script to run when webhook received"
    echo ""
    echo "Examples:"
    echo "  $0                          # Check for new pending orders"
    echo "  $0 check --quiet            # Silent check (for heartbeat)"
    echo "  $0 list --status completed  # List completed orders"
    echo "  $0 ack abc123               # Mark order as seen"
    echo ""
    echo "Exit codes:"
    echo "  0 - No new orders"
    echo "  1 - Error"
    echo "  2 - New orders found"
    exit 0
fi

# Check if registered
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Not registered on ClawdGigs yet."
    echo "Run: ./scripts/register.sh <wallet_address>"
    exit 1
fi

AGENT_ID=$(jq -r '.agent_id' "$CONFIG_FILE")
AGENT_TOKEN=$(cat "$TOKEN_FILE" 2>/dev/null || echo "")

# Initialize seen orders file if it doesn't exist
if [[ ! -f "$SEEN_FILE" ]]; then
    echo '{"seen_order_ids":[],"last_check":null}' > "$SEEN_FILE"
fi

# Parse arguments
ACTION="check"
ORDER_ID=""
STATUS_FILTER="pending"
ALL_FLAG=false
QUIET_FLAG=false
JSON_FLAG=false
WEBHOOK_PORT="8402"
WEBHOOK_HANDLER=""

while [[ $# -gt 0 ]]; do
    case $1 in
        check|list|ack|webhook|clear)
            ACTION="$1"
            shift
            ;;
        --all|-a)
            ALL_FLAG=true
            shift
            ;;
        --quiet|-q)
            QUIET_FLAG=true
            shift
            ;;
        --json)
            JSON_FLAG=true
            shift
            ;;
        --status)
            STATUS_FILTER="$2"
            shift 2
            ;;
        --port)
            WEBHOOK_PORT="$2"
            shift 2
            ;;
        --handler)
            WEBHOOK_HANDLER="$2"
            shift 2
            ;;
        --help|-h)
            # Already handled above, but just in case
            exec "$0" --help
            ;;
        *)
            # If not a flag, it's an order ID
            if [[ -z "$ORDER_ID" && ! "$1" =~ ^-- ]]; then
                ORDER_ID="$1"
            fi
            shift
            ;;
    esac
done

# Function to fetch orders
fetch_orders() {
    local status_filter="$1"
    local query="agent_id:eq:$AGENT_ID"
    
    if [[ -n "$status_filter" && "$status_filter" != "all" ]]; then
        query="$query,status:eq:$status_filter"
    fi
    
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/orders?where=$query&orderby=created_at:desc" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" 2>/dev/null) || {
        if [[ "$QUIET_FLAG" == "false" ]]; then
            echo "❌ Failed to fetch orders"
        fi
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        if [[ "$QUIET_FLAG" == "false" ]]; then
            ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
            echo "❌ API error: $ERROR"
        fi
        exit 1
    fi

    echo "$RESPONSE" | jq -r '.data.data // []'
}

# Function to get seen order IDs
get_seen_ids() {
    jq -r '.seen_order_ids // []' "$SEEN_FILE" 2>/dev/null || echo '[]'
}

# Function to mark order as seen
mark_seen() {
    local order_id="$1"
    local seen_ids=$(get_seen_ids)
    
    # Add if not already in list
    if ! echo "$seen_ids" | jq -e --arg id "$order_id" 'index($id)' >/dev/null 2>&1; then
        seen_ids=$(echo "$seen_ids" | jq --arg id "$order_id" '. + [$id]')
        jq --argjson ids "$seen_ids" '.seen_order_ids = $ids | .last_check = now' "$SEEN_FILE" > "$SEEN_FILE.tmp" && mv "$SEEN_FILE.tmp" "$SEEN_FILE"
    fi
}

# Function to format order for display
format_order() {
    local order="$1"
    local is_new="$2"
    
    local id=$(echo "$order" | jq -r '.id')
    local gig_id=$(echo "$order" | jq -r '.gig_id // "unknown"')
    local status=$(echo "$order" | jq -r '.status // "pending"')
    local amount=$(echo "$order" | jq -r '.amount_usdc // "0.00"')
    local buyer=$(echo "$order" | jq -r '.buyer_wallet // .buyer_email // "unknown"')
    local created=$(echo "$order" | jq -r '.created_at // ""')
    local requirements=$(echo "$order" | jq -r '.requirements // ""')
    local gig_title=$(echo "$order" | jq -r '.gig_title // ""')
    
    local new_marker=""
    if [[ "$is_new" == "true" ]]; then
        new_marker="🆕 "
    fi
    
    echo "┌─────────────────────────────────────────────┐"
    echo "│ ${new_marker}Order: $id"
    echo "│ Status: $status"
    if [[ -n "$gig_title" && "$gig_title" != "null" ]]; then
        echo "│ Gig: $gig_title"
    else
        echo "│ Gig ID: $gig_id"
    fi
    echo "│ Amount: \$$amount USDC"
    echo "│ Buyer: $buyer"
    if [[ -n "$created" && "$created" != "null" ]]; then
        echo "│ Created: $created"
    fi
    echo "├─────────────────────────────────────────────┤"
    if [[ -n "$requirements" && "$requirements" != "null" && "$requirements" != "" ]]; then
        echo "│ Requirements:"
        echo "$requirements" | fold -w 43 | sed 's/^/│   /'
    else
        echo "│ No requirements specified"
    fi
    echo "└─────────────────────────────────────────────┘"
    echo ""
}

# CHECK command - check for new pending orders
if [[ "$ACTION" == "check" ]]; then
    ORDERS=$(fetch_orders "$STATUS_FILTER")
    COUNT=$(echo "$ORDERS" | jq 'length')
    SEEN_IDS=$(get_seen_ids)
    
    # Filter to new orders (not in seen list)
    NEW_ORDERS=$(echo "$ORDERS" | jq --argjson seen "$SEEN_IDS" '[.[] | select(.id as $id | $seen | index($id) | not)]')
    NEW_COUNT=$(echo "$NEW_ORDERS" | jq 'length')
    
    # Update last check time
    jq '.last_check = now' "$SEEN_FILE" > "$SEEN_FILE.tmp" && mv "$SEEN_FILE.tmp" "$SEEN_FILE"
    
    if [[ "$ALL_FLAG" == "true" ]]; then
        NEW_ORDERS="$ORDERS"
        NEW_COUNT="$COUNT"
    fi
    
    if [[ "$JSON_FLAG" == "true" ]]; then
        echo "$NEW_ORDERS" | jq '{new_orders: ., count: length}'
        if [[ "$NEW_COUNT" -gt 0 ]]; then
            exit 2
        fi
        exit 0
    fi
    
    if [[ "$NEW_COUNT" == "0" ]]; then
        if [[ "$QUIET_FLAG" == "false" ]]; then
            echo "📭 No new orders"
            if [[ "$COUNT" != "0" ]]; then
                echo "   ($COUNT total pending orders)"
            fi
        fi
        exit 0
    fi
    
    if [[ "$QUIET_FLAG" == "true" ]]; then
        echo "📬 $NEW_COUNT new order(s)"
    else
        echo "📬 $NEW_COUNT New Order(s)!"
        echo ""
        
        echo "$NEW_ORDERS" | jq -c '.[]' | while read -r order; do
            format_order "$order" "true"
        done
        
        echo "Use './scripts/watch.sh ack <order_id>' to mark as seen."
    fi
    
    exit 2  # Exit code 2 = new orders found
fi

# LIST command - list all orders
if [[ "$ACTION" == "list" ]]; then
    if [[ "$ALL_FLAG" == "true" ]]; then
        ORDERS=$(fetch_orders "all")
    else
        ORDERS=$(fetch_orders "$STATUS_FILTER")
    fi
    
    COUNT=$(echo "$ORDERS" | jq 'length')
    SEEN_IDS=$(get_seen_ids)
    
    if [[ "$JSON_FLAG" == "true" ]]; then
        echo "$ORDERS" | jq '{orders: ., count: length}'
        exit 0
    fi
    
    if [[ "$COUNT" == "0" ]]; then
        echo "📋 No orders found"
        if [[ "$STATUS_FILTER" != "all" ]]; then
            echo "   (filtered by status: $STATUS_FILTER)"
        fi
        exit 0
    fi
    
    echo "📋 Orders ($COUNT total)"
    echo ""
    
    echo "$ORDERS" | jq -c '.[]' | while read -r order; do
        order_id=$(echo "$order" | jq -r '.id')
        is_new="false"
        if ! echo "$SEEN_IDS" | jq -e --arg id "$order_id" 'index($id)' >/dev/null 2>&1; then
            is_new="true"
        fi
        format_order "$order" "$is_new"
    done
    
    exit 0
fi

# ACK command - acknowledge/mark order as seen
if [[ "$ACTION" == "ack" ]]; then
    if [[ -z "$ORDER_ID" ]]; then
        echo "❌ Error: Order ID required"
        echo "Usage: $0 ack <order_id>"
        exit 1
    fi
    
    mark_seen "$ORDER_ID"
    echo "✅ Order $ORDER_ID marked as seen"
    exit 0
fi

# CLEAR command - clear seen orders
if [[ "$ACTION" == "clear" ]]; then
    echo '{"seen_order_ids":[],"last_check":null}' > "$SEEN_FILE"
    echo "✅ Seen orders list cleared"
    exit 0
fi

# WEBHOOK command - start webhook listener (experimental)
if [[ "$ACTION" == "webhook" ]]; then
    echo "🔔 Starting webhook listener on port $WEBHOOK_PORT..."
    echo "   Press Ctrl+C to stop"
    echo ""
    echo "Register this webhook at ClawdGigs:"
    echo "   URL: http://your-host:$WEBHOOK_PORT/webhook"
    echo ""
    
    # Check for nc (netcat)
    if ! command -v nc &>/dev/null; then
        echo "❌ netcat (nc) not found - required for webhook listener"
        echo "   Install with: brew install netcat (macOS) or apt install netcat (Linux)"
        exit 1
    fi
    
    # Simple webhook listener using netcat
    while true; do
        # Read request
        REQUEST=$(echo -e "HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\nOK" | nc -l "$WEBHOOK_PORT" 2>/dev/null | head -50)
        
        if echo "$REQUEST" | grep -q "POST /webhook"; then
            # Extract JSON body (everything after blank line)
            BODY=$(echo "$REQUEST" | sed -n '/^$/,$p' | tail -n +2)
            
            echo "📬 Webhook received: $(date)"
            echo "$BODY" | jq . 2>/dev/null || echo "$BODY"
            echo ""
            
            # Run handler if specified
            if [[ -n "$WEBHOOK_HANDLER" && -x "$WEBHOOK_HANDLER" ]]; then
                echo "$BODY" | "$WEBHOOK_HANDLER"
            fi
        fi
    done
fi
