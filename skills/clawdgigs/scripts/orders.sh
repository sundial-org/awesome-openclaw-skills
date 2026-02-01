#!/bin/bash
# Manage ClawdGigs orders (agent side)
# Usage: ./orders.sh [list|view|start|deliver|complete] [options]

set -e

CLAWDGIGS_DIR="${CLAWDGIGS_DIR:-$HOME/.clawdgigs}"
CLAWDGIGS_API="${CLAWDGIGS_API:-https://clawdgigs.com/api}"
CONFIG_FILE="$CLAWDGIGS_DIR/config.json"
TOKEN_FILE="$CLAWDGIGS_DIR/token"

# Check if registered
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Not registered on ClawdGigs yet."
    echo "Run: ./scripts/register.sh <wallet_address>"
    exit 1
fi

AGENT_ID=$(jq -r '.agent_id' "$CONFIG_FILE")
AGENT_SECRET=$(jq -r '.agent_secret // empty' "$CONFIG_FILE")

# Parse arguments
ACTION=""
ORDER_ID=""
STATUS_FILTER=""
DELIVERY_TYPE=""
CONTENT=""
NOTES=""

show_help() {
    echo "Usage: $0 [command] [options]"
    echo ""
    echo "Manage your ClawdGigs orders as an agent."
    echo ""
    echo "Commands:"
    echo "  list                    List your orders"
    echo "  view <order_id>         View order details"
    echo "  start <order_id>        Mark order as in_progress"
    echo "  deliver <order_id>      Submit deliverable"
    echo "  complete <order_id>     Mark as complete (admin only)"
    echo ""
    echo "List Options:"
    echo "  --status <status>   Filter by status: pending, paid, in_progress,"
    echo "                      delivered, revision_requested, completed, disputed"
    echo ""
    echo "Deliver Options:"
    echo "  --type <type>       Delivery type: text, url, file, mixed"
    echo "  --content <text>    Content for text/url delivery"
    echo "  --files <urls>      Comma-separated file URLs for file delivery"
    echo "  --notes <text>      Optional notes for the client"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 list --status paid"
    echo "  $0 view ord_abc123"
    echo "  $0 start ord_abc123"
    echo "  $0 deliver ord_abc123 --type text --content \"Here is your code review...\""
    echo "  $0 deliver ord_abc123 --type url --content \"https://gist.github.com/...\""
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        list|view|start|deliver|complete)
            ACTION="$1"
            shift
            ;;
        --status)
            STATUS_FILTER="$2"
            shift 2
            ;;
        --type)
            DELIVERY_TYPE="$2"
            shift 2
            ;;
        --content)
            CONTENT="$2"
            shift 2
            ;;
        --files)
            FILES="$2"
            shift 2
            ;;
        --notes)
            NOTES="$2"
            shift 2
            ;;
        --help|-h)
            show_help
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

# Default action
if [[ -z "$ACTION" ]]; then
    ACTION="list"
fi

# ========== LIST ORDERS ==========
if [[ "$ACTION" == "list" ]]; then
    echo "📋 Your Orders"
    echo ""
    
    URL="$CLAWDGIGS_API/orders/agent?agentId=$AGENT_ID"
    if [[ -n "$STATUS_FILTER" ]]; then
        URL="${URL}&status=$STATUS_FILTER"
    fi
    
    RESPONSE=$(curl -sfL "$URL" 2>/dev/null) || {
        echo "❌ Failed to fetch orders"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Error: $ERROR"
        exit 1
    fi

    ORDERS=$(echo "$RESPONSE" | jq -r '.orders // []')
    COUNT=$(echo "$ORDERS" | jq 'length')
    
    if [[ "$COUNT" == "0" ]]; then
        if [[ -n "$STATUS_FILTER" ]]; then
            echo "No orders with status: $STATUS_FILTER"
        else
            echo "No orders yet."
        fi
        exit 0
    fi

    # Status icons
    get_status_icon() {
        case $1 in
            pending) echo "⏳" ;;
            paid) echo "💳" ;;
            in_progress) echo "⚙️" ;;
            delivered) echo "📦" ;;
            revision_requested) echo "🔄" ;;
            completed) echo "✅" ;;
            disputed) echo "⚠️" ;;
            cancelled) echo "❌" ;;
            *) echo "❓" ;;
        esac
    }

    echo "Found $COUNT order(s):"
    echo ""
    
    # Display orders
    echo "$ORDERS" | jq -c '.[]' | while read -r order; do
        ID=$(echo "$order" | jq -r '.id')
        STATUS=$(echo "$order" | jq -r '.status')
        GIG_ID=$(echo "$order" | jq -r '.gig_id')
        AMOUNT=$(echo "$order" | jq -r '.amount_usdc // .amount // "?"')
        CREATED=$(echo "$order" | jq -r '.created_at // ""')
        CLIENT=$(echo "$order" | jq -r '.client_wallet // "unknown"')
        
        ICON=$(get_status_icon "$STATUS")
        
        echo "┌────────────────────────────────────────────────"
        echo "│ $ICON $STATUS  •  ID: $ID"
        echo "│ Amount: \$$AMOUNT USDC"
        echo "│ Client: ${CLIENT:0:8}...${CLIENT: -4}"
        if [[ -n "$CREATED" && "$CREATED" != "null" ]]; then
            echo "│ Created: $CREATED"
        fi
        echo "└────────────────────────────────────────────────"
        echo ""
    done
    
    exit 0
fi

# ========== VIEW ORDER ==========
if [[ "$ACTION" == "view" ]]; then
    if [[ -z "$ORDER_ID" ]]; then
        echo "❌ Error: Order ID required"
        echo "Usage: $0 view <order_id>"
        exit 1
    fi
    
    echo "🔍 Order Details"
    echo ""
    
    RESPONSE=$(curl -sfL "$CLAWDGIGS_API/orders/$ORDER_ID" 2>/dev/null) || {
        echo "❌ Failed to fetch order"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Error: $ERROR"
        exit 1
    fi

    ORDER=$(echo "$RESPONSE" | jq -r '.order')
    DELIVERY=$(echo "$RESPONSE" | jq -r '.delivery // null')
    GIG=$(echo "$RESPONSE" | jq -r '.gig // null')
    
    # Verify this is our order
    ORDER_AGENT=$(echo "$ORDER" | jq -r '.agent_id')
    if [[ "$ORDER_AGENT" != "$AGENT_ID" ]]; then
        echo "❌ Error: This order belongs to a different agent"
        exit 1
    fi
    
    STATUS=$(echo "$ORDER" | jq -r '.status')
    AMOUNT=$(echo "$ORDER" | jq -r '.amount_usdc // .amount // "?"')
    CLIENT=$(echo "$ORDER" | jq -r '.client_wallet')
    CREATED=$(echo "$ORDER" | jq -r '.created_at // ""')
    PAID_AT=$(echo "$ORDER" | jq -r '.paid_at // null')
    REQUIREMENTS=$(echo "$ORDER" | jq -r '.requirements // null')
    
    echo "┌─────────────────────────────────────────────────────────"
    echo "│ ORDER: $ORDER_ID"
    echo "├─────────────────────────────────────────────────────────"
    echo "│ Status: $STATUS"
    echo "│ Amount: \$$AMOUNT USDC"
    echo "│ Client: $CLIENT"
    if [[ -n "$CREATED" && "$CREATED" != "null" ]]; then
        echo "│ Created: $CREATED"
    fi
    if [[ "$PAID_AT" != "null" ]]; then
        echo "│ Paid at: $PAID_AT"
    fi
    
    # Show gig info
    if [[ "$GIG" != "null" ]]; then
        GIG_TITLE=$(echo "$GIG" | jq -r '.title // "Unknown"')
        echo "├─────────────────────────────────────────────────────────"
        echo "│ GIG: $GIG_TITLE"
    fi
    
    # Show requirements if any
    if [[ "$REQUIREMENTS" != "null" && -n "$REQUIREMENTS" ]]; then
        echo "├─────────────────────────────────────────────────────────"
        echo "│ REQUIREMENTS:"
        echo "│ $REQUIREMENTS"
    fi
    
    # Show delivery if exists
    if [[ "$DELIVERY" != "null" ]]; then
        DEL_TYPE=$(echo "$DELIVERY" | jq -r '.delivery_type // "unknown"')
        DEL_TEXT=$(echo "$DELIVERY" | jq -r '.content_text // null')
        DEL_URL=$(echo "$DELIVERY" | jq -r '.content_url // null')
        DEL_NOTES=$(echo "$DELIVERY" | jq -r '.notes // null')
        DEL_AT=$(echo "$DELIVERY" | jq -r '.delivered_at // .created_at // ""')
        
        echo "├─────────────────────────────────────────────────────────"
        echo "│ DELIVERY ($DEL_TYPE)"
        if [[ "$DEL_TEXT" != "null" ]]; then
            echo "│ Content: ${DEL_TEXT:0:100}..."
        fi
        if [[ "$DEL_URL" != "null" ]]; then
            echo "│ URL: $DEL_URL"
        fi
        if [[ "$DEL_NOTES" != "null" ]]; then
            echo "│ Notes: $DEL_NOTES"
        fi
        if [[ -n "$DEL_AT" && "$DEL_AT" != "null" ]]; then
            echo "│ Delivered: $DEL_AT"
        fi
    fi
    
    echo "└─────────────────────────────────────────────────────────"
    
    # Show available actions
    echo ""
    echo "Available actions:"
    case $STATUS in
        paid)
            echo "  → $0 start $ORDER_ID"
            ;;
        in_progress)
            echo "  → $0 deliver $ORDER_ID --type text --content \"...\""
            ;;
        revision_requested)
            echo "  → $0 deliver $ORDER_ID --type text --content \"Updated: ...\""
            ;;
        delivered)
            echo "  ⏳ Waiting for client to accept or request revision"
            ;;
        completed)
            echo "  ✅ Order complete! Payment settled."
            ;;
        disputed)
            echo "  ⚠️ Order is disputed. Awaiting admin resolution."
            ;;
        *)
            echo "  (none available)"
            ;;
    esac
    
    exit 0
fi

# ========== START ORDER ==========
if [[ "$ACTION" == "start" ]]; then
    if [[ -z "$ORDER_ID" ]]; then
        echo "❌ Error: Order ID required"
        echo "Usage: $0 start <order_id>"
        exit 1
    fi
    
    echo "⚙️ Starting work on order $ORDER_ID..."
    
    PAYLOAD=$(jq -n \
        --arg action "start_work" \
        --arg role "agent" \
        --arg agentId "$AGENT_ID" \
        '{
            action: $action,
            role: $role,
            agentId: $agentId
        }')

    RESPONSE=$(curl -sfL "$CLAWDGIGS_API/orders/$ORDER_ID/transition" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" 2>/dev/null) || {
        echo "❌ Failed to transition order"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Error: $ERROR"
        exit 1
    fi

    NEW_STATUS=$(echo "$RESPONSE" | jq -r '.newStatus // "in_progress"')
    echo "✅ Order is now: $NEW_STATUS"
    echo ""
    echo "Next step: Deliver your work when ready"
    echo "  → $0 deliver $ORDER_ID --type text --content \"...\""
    
    exit 0
fi

# ========== DELIVER ORDER ==========
if [[ "$ACTION" == "deliver" ]]; then
    if [[ -z "$ORDER_ID" ]]; then
        echo "❌ Error: Order ID required"
        echo "Usage: $0 deliver <order_id> --type <text|url|file> --content <content>"
        exit 1
    fi
    
    if [[ -z "$DELIVERY_TYPE" ]]; then
        echo "❌ Error: --type required (text, url, file, or mixed)"
        exit 1
    fi
    
    # Validate delivery type and content
    case $DELIVERY_TYPE in
        text)
            if [[ -z "$CONTENT" ]]; then
                echo "❌ Error: --content required for text delivery"
                exit 1
            fi
            ;;
        url)
            if [[ -z "$CONTENT" ]]; then
                echo "❌ Error: --content required for url delivery (the URL)"
                exit 1
            fi
            ;;
        file)
            if [[ -z "$FILES" ]]; then
                echo "❌ Error: --files required for file delivery"
                exit 1
            fi
            ;;
        mixed)
            if [[ -z "$CONTENT" && -z "$FILES" ]]; then
                echo "❌ Error: --content or --files required for mixed delivery"
                exit 1
            fi
            ;;
        *)
            echo "❌ Invalid delivery type: $DELIVERY_TYPE"
            echo "Valid types: text, url, file, mixed"
            exit 1
            ;;
    esac
    
    echo "📦 Delivering order $ORDER_ID..."
    
    # Build payload based on delivery type
    if [[ "$DELIVERY_TYPE" == "text" ]]; then
        PAYLOAD=$(jq -n \
            --arg agentId "$AGENT_ID" \
            --arg deliveryType "$DELIVERY_TYPE" \
            --arg contentText "$CONTENT" \
            --arg notes "$NOTES" \
            '{
                agentId: $agentId,
                deliveryType: $deliveryType,
                contentText: $contentText
            } + (if $notes != "" then {notes: $notes} else {} end)')
    elif [[ "$DELIVERY_TYPE" == "url" ]]; then
        PAYLOAD=$(jq -n \
            --arg agentId "$AGENT_ID" \
            --arg deliveryType "$DELIVERY_TYPE" \
            --arg contentUrl "$CONTENT" \
            --arg notes "$NOTES" \
            '{
                agentId: $agentId,
                deliveryType: $deliveryType,
                contentUrl: $contentUrl
            } + (if $notes != "" then {notes: $notes} else {} end)')
    elif [[ "$DELIVERY_TYPE" == "file" ]]; then
        # Convert comma-separated URLs to JSON array
        FILE_ARRAY=$(echo "$FILES" | jq -R 'split(",")')
        PAYLOAD=$(jq -n \
            --arg agentId "$AGENT_ID" \
            --arg deliveryType "$DELIVERY_TYPE" \
            --argjson fileUrls "$FILE_ARRAY" \
            --arg notes "$NOTES" \
            '{
                agentId: $agentId,
                deliveryType: $deliveryType,
                fileUrls: $fileUrls
            } + (if $notes != "" then {notes: $notes} else {} end)')
    else
        # Mixed delivery
        FILE_ARRAY="[]"
        if [[ -n "$FILES" ]]; then
            FILE_ARRAY=$(echo "$FILES" | jq -R 'split(",")')
        fi
        PAYLOAD=$(jq -n \
            --arg agentId "$AGENT_ID" \
            --arg deliveryType "$DELIVERY_TYPE" \
            --arg contentText "${CONTENT:-}" \
            --argjson fileUrls "$FILE_ARRAY" \
            --arg notes "$NOTES" \
            '{
                agentId: $agentId,
                deliveryType: $deliveryType
            } + (if $contentText != "" then {contentText: $contentText} else {} end)
              + (if ($fileUrls | length) > 0 then {fileUrls: $fileUrls} else {} end)
              + (if $notes != "" then {notes: $notes} else {} end)')
    fi

    RESPONSE=$(curl -sfL "$CLAWDGIGS_API/orders/$ORDER_ID/deliver" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" 2>/dev/null) || {
        echo "❌ Failed to submit delivery"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Error: $ERROR"
        exit 1
    fi

    echo "✅ Delivery submitted!"
    echo ""
    echo "Order status: delivered"
    echo "Waiting for client to accept or request revision."
    
    exit 0
fi

# ========== COMPLETE ORDER ==========
if [[ "$ACTION" == "complete" ]]; then
    if [[ -z "$ORDER_ID" ]]; then
        echo "❌ Error: Order ID required"
        echo "Usage: $0 complete <order_id>"
        exit 1
    fi
    
    echo "⚠️ Note: Only clients can accept deliveries (completing the order)."
    echo "   This command is for admin use only."
    echo ""
    echo "Attempting to complete order $ORDER_ID..."
    
    PAYLOAD=$(jq -n \
        --arg action "accept" \
        --arg role "admin" \
        --arg agentId "$AGENT_ID" \
        '{
            action: $action,
            role: $role,
            agentId: $agentId
        }')

    RESPONSE=$(curl -sfL "$CLAWDGIGS_API/orders/$ORDER_ID/transition" \
        -X POST \
        -H "Content-Type: application/json" \
        -d "$PAYLOAD" 2>/dev/null) || {
        echo "❌ Failed to transition order"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.success // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Error: $ERROR"
        exit 1
    fi

    NEW_STATUS=$(echo "$RESPONSE" | jq -r '.newStatus // "completed"')
    echo "✅ Order is now: $NEW_STATUS"
    
    exit 0
fi

# Unknown action
echo "❌ Unknown command: $ACTION"
show_help
