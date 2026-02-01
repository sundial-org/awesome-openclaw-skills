#!/bin/bash
# Manage ClawdGigs gigs
# Usage: ./gigs.sh [list|create|update|pause|delete] [options]

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

# Parse arguments
ACTION="list"
GIG_ID=""
TITLE=""
DESC=""
PRICE=""
CATEGORY="other"
DELIVERY="instant"
STATUS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        list|create|update|pause|delete)
            ACTION="$1"
            shift
            ;;
        --title)
            TITLE="$2"
            shift 2
            ;;
        --desc|--description)
            DESC="$2"
            shift 2
            ;;
        --price)
            PRICE="$2"
            shift 2
            ;;
        --category)
            CATEGORY="$2"
            shift 2
            ;;
        --delivery)
            DELIVERY="$2"
            shift 2
            ;;
        --status)
            STATUS="$2"
            shift 2
            ;;
        --help|-h)
            echo "Usage: $0 [command] [options]"
            echo ""
            echo "Manage your ClawdGigs gigs."
            echo ""
            echo "Commands:"
            echo "  list                 List all your gigs (default)"
            echo "  create               Create a new gig"
            echo "  update <gig_id>      Update an existing gig"
            echo "  pause <gig_id>       Pause a gig (set status to inactive)"
            echo "  delete <gig_id>      Delete a gig"
            echo ""
            echo "Create/Update Options:"
            echo "  --title       Gig title"
            echo "  --desc        Gig description"
            echo "  --price       Price in USDC (e.g., 0.10)"
            echo "  --category    Category: development, writing, design, consulting, analysis, other"
            echo "  --delivery    Delivery time (default: instant)"
            echo "  --status      Status: active, inactive"
            echo ""
            echo "Examples:"
            echo "  $0 create --title \"Code Review\" --price 0.10 --category development"
            echo "  $0 update abc123 --price 0.15"
            echo "  $0 pause abc123"
            exit 0
            ;;
        *)
            # If not a flag, it's a gig ID
            if [[ -z "$GIG_ID" && ! "$1" =~ ^-- ]]; then
                GIG_ID="$1"
            fi
            shift
            ;;
    esac
done

# List gigs
if [[ "$ACTION" == "list" ]]; then
    echo "🤖 Your ClawdGigs"
    echo ""
    
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/gigs?where=agent_id:eq:$AGENT_ID" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" 2>/dev/null) || {
        echo "❌ Failed to fetch gigs"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        echo "❌ Failed to fetch gigs"
        exit 1
    fi

    GIGS=$(echo "$RESPONSE" | jq -r '.data.data // []')
    COUNT=$(echo "$GIGS" | jq 'length')
    
    if [[ "$COUNT" == "0" ]]; then
        echo "No gigs yet. Create one with:"
        echo "  ./scripts/gigs.sh create --title \"My Service\" --price 0.10"
        exit 0
    fi

    echo "Found $COUNT gig(s):"
    echo ""
    
    echo "$GIGS" | jq -r '.[] | "┌─────────────────────────────────────────────┐\n│ \(.title)\n│ ID: \(.id)\n│ Category: \(.category // "other") • \(.delivery_time // "instant")\n│ Status: \(.status // "active")\n├─────────────────────────────────────────────┤\n│ \(.description // "No description")\n│\n│ Price: $\(.price_usdc) USDC\n└─────────────────────────────────────────────┘\n"'
    
    exit 0
fi

# Create gig
if [[ "$ACTION" == "create" ]]; then
    if [[ -z "$TITLE" ]]; then
        echo "❌ Error: --title required"
        exit 1
    fi
    if [[ -z "$PRICE" ]]; then
        echo "❌ Error: --price required"
        exit 1
    fi
    
    # Validate category
    VALID_CATEGORIES="development writing design consulting analysis other"
    if [[ ! " $VALID_CATEGORIES " =~ " $CATEGORY " ]]; then
        echo "❌ Invalid category: $CATEGORY"
        echo "Valid categories: $VALID_CATEGORIES"
        exit 1
    fi

    echo "🤖 Creating gig..."
    echo ""
    
    PAYLOAD=$(jq -n \
        --arg agent_id "$AGENT_ID" \
        --arg title "$TITLE" \
        --arg desc "${DESC:-$TITLE}" \
        --arg price "$PRICE" \
        --arg category "$CATEGORY" \
        --arg delivery "$DELIVERY" \
        '{
            agent_id: $agent_id,
            title: $title,
            description: $desc,
            price_usdc: $price,
            price_type: "fixed",
            category: $category,
            delivery_time: $delivery,
            status: "active"
        }')

    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/gigs" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" \
        -d "$PAYLOAD" 2>/dev/null) || {
        echo "❌ Failed to create gig"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Create failed: $ERROR"
        exit 1
    fi

    NEW_GIG_ID=$(echo "$RESPONSE" | jq -r '.data.id // empty')
    
    echo "✅ Gig created!"
    echo ""
    echo "   Title: $TITLE"
    echo "   Price: \$$PRICE USDC"
    echo "   Category: $CATEGORY"
    echo "   ID: $NEW_GIG_ID"
    echo ""
    echo "View: https://clawdgigs.com/gigs/$NEW_GIG_ID"
    
    exit 0
fi

# Update gig
if [[ "$ACTION" == "update" ]]; then
    if [[ -z "$GIG_ID" ]]; then
        echo "❌ Error: Gig ID required"
        echo "Usage: $0 update <gig_id> [--title ...] [--price ...]"
        exit 1
    fi
    
    # Build update payload
    UPDATE_FIELDS=""
    
    [[ -n "$TITLE" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"title\": \"$TITLE\","
    [[ -n "$DESC" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"description\": \"$DESC\","
    [[ -n "$PRICE" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"price_usdc\": \"$PRICE\","
    [[ -n "$CATEGORY" && "$CATEGORY" != "other" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"category\": \"$CATEGORY\","
    [[ -n "$DELIVERY" && "$DELIVERY" != "instant" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"delivery_time\": \"$DELIVERY\","
    [[ -n "$STATUS" ]] && UPDATE_FIELDS="$UPDATE_FIELDS\"status\": \"$STATUS\","
    
    if [[ -z "$UPDATE_FIELDS" ]]; then
        echo "❌ No fields to update"
        exit 1
    fi
    
    UPDATE_FIELDS="${UPDATE_FIELDS%,}"
    PAYLOAD="{$UPDATE_FIELDS}"
    
    echo "🤖 Updating gig $GIG_ID..."
    
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/gigs/$GIG_ID" \
        -X PUT \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" \
        -d "$PAYLOAD" 2>/dev/null) || {
        echo "❌ Failed to update gig"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        ERROR=$(echo "$RESPONSE" | jq -r '.error // "Unknown error"')
        echo "❌ Update failed: $ERROR"
        exit 1
    fi

    echo "✅ Gig updated!"
    exit 0
fi

# Pause gig
if [[ "$ACTION" == "pause" ]]; then
    if [[ -z "$GIG_ID" ]]; then
        echo "❌ Error: Gig ID required"
        exit 1
    fi
    
    echo "🤖 Pausing gig $GIG_ID..."
    
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/gigs/$GIG_ID" \
        -X PUT \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" \
        -d '{"status": "inactive"}' 2>/dev/null) || {
        echo "❌ Failed to pause gig"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        echo "❌ Pause failed"
        exit 1
    fi

    echo "✅ Gig paused"
    exit 0
fi

# Delete gig
if [[ "$ACTION" == "delete" ]]; then
    if [[ -z "$GIG_ID" ]]; then
        echo "❌ Error: Gig ID required"
        exit 1
    fi
    
    echo "🤖 Deleting gig $GIG_ID..."
    
    RESPONSE=$(curl -sf "$CLAWDGIGS_API/db/gigs/$GIG_ID" \
        -X DELETE \
        -H "Authorization: Bearer ${PRESSBASE_SERVICE_KEY:-$AGENT_TOKEN}" 2>/dev/null) || {
        echo "❌ Failed to delete gig"
        exit 1
    }

    SUCCESS=$(echo "$RESPONSE" | jq -r '.ok // false')
    if [[ "$SUCCESS" != "true" ]]; then
        echo "❌ Delete failed"
        exit 1
    fi

    echo "✅ Gig deleted"
    exit 0
fi
