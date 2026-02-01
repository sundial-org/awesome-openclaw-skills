#!/bin/bash
# ShapeScale Extensions for Stripe CLI
# Usage: ./shapescale-ext.sh <command> [args...]

set -e

# Load base config
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PRESETS_PATH="${SHAPESCALE_PRESETS_PATH:-$SCRIPT_DIR/../config/shapescale-presets.json}"

if [ -f "$PRESETS_PATH" ]; then
    # Parse JSON using basic tools (jq preferred)
    if command -v jq &> /dev/null; then
        read_json() {
            cat "$PRESETS_PATH" | jq -r "$1" 2>/dev/null || echo ""
        }
    else
        # Fallback: simple grep-based extraction
        read_json() {
            grep "\"$1\"" "$PRESETS_PATH" | sed 's/.*: *"\([^"]*\)".*/\1/' | head -1
        }
    fi
else
    echo "⚠️  Warning: shapescale-presets.json not found at $PRESETS_PATH"
    echo "   Run without ShapeScale extensions or create the config file."
    exit 1
fi

# Helper for format_output
format_output() {
    local output="$1"
    local status="$2"
    if [ "$status" = "success" ]; then
        echo "✅ $output"
    else
        echo "❌ $output"
    fi
}

COMMAND="$1"
shift || true

# Stripe authentication check
check_auth() {
    if [ -z "$STRIPE_SECRET_KEY" ]; then
        echo "❌ Error: STRIPE_SECRET_KEY not set"
        exit 1
    fi
    export STRIPE_SECRET_KEY
}

case "$COMMAND" in
    "clinic")
        SUBCOMMAND="$1"
        shift
        check_auth
        case "$SUBCOMMAND" in
            "create")
                CLINIC_NAME="$1"
                TEMPLATE="${2:-standard}"
                if [ -z "$CLINIC_NAME" ]; then
                    echo "Usage: shapescale clinic create <name> [template]"
                    exit 1
                fi
                
                # Get preset values
                DEPOSIT=$(read_json "${TEMPLATE}.deposit" ".clinic_templates")
                TERMS=$(read_json "${TEMPLATE}.terms" ".clinic_templates")
                
                echo "🏥 Creating clinic: $CLINIC_NAME (template: $TEMPLATE, deposit: $DEPOSIT)"
                
                # Create customer with clinic metadata
                RESULT=$(stripe customers create \
                    --description "Clinic: $CLINIC_NAME" \
                    --metadata "type=clinic,template=$TEMPLATE,terms=$TERMS" \
                    2>&1)
                
                if [ $? -eq 0 ]; then
                    CUSTOMER_ID=$(echo "$RESULT" | grep -o '"id": "[^"]*"' | head -1 | sed 's/"id": "\(.*\)"/\1/')
                    echo "✅ Clinic created: $CUSTOMER_ID"
                    [ -n "$DEPOSIT" ] && echo "   Deposit: $DEPOSIT cents | Terms: $TERMS"
                else
                    echo "❌ Failed to create clinic: $RESULT"
                fi
                ;;
            "list")
                echo "🏥 Listing clinic customers..."
                stripe customers list --limit 100 --metadata "type=clinic" 2>&1
                ;;
            *)
                echo "Usage: shapescale clinic <create|list>"
                ;;
        esac
        ;;
        
    "subscription")
        SUBCOMMAND="$1"
        shift
        check_auth
        case "$SUBCOMMAND" in
            "create")
                CUSTOMER_ID="$1"
                PLAN="$2"
                if [ -z "$CUSTOMER_ID" ] || [ -z "$PLAN" ]; then
                    echo "Usage: shapescale subscription create <customer_id> <plan>"
                    echo "Available plans: monthly, annual"
                    exit 1
                fi
                
                # Get plan values
                AMOUNT=$(read_json "${PLAN}.amount" ".subscription_plans")
                INTERVAL=$(read_json "${PLAN}.interval" ".subscription_plans")
                
                echo "📅 Creating $PLAN subscription for customer $CUSTOMER_ID"
                
                # Create price and subscription
                PRICE_RESULT=$(stripe prices create \
                    --unit-amount "$AMOUNT" \
                    --currency "usd" \
                    --recurring "interval=$INTERVAL" \
                    --product "default" \
                    2>&1)
                
                if [ $? -eq 0 ]; then
                    PRICE_ID=$(echo "$PRICE_RESULT" | grep -o '"id": "[^"]*"' | head -1 | sed 's/"id": "\(.*\)"/\1/')
                    SUB_RESULT=$(stripe subscriptions create \
                        --customer "$CUSTOMER_ID" \
                        --price "$PRICE_ID" \
                        2>&1)
                    
                    format_output "$SUB_RESULT" "success" || format_output "$SUB_RESULT" "error"
                else
                    echo "❌ Failed to create subscription: $PRICE_RESULT"
                fi
                ;;
            "list")
                CUSTOMER_ID="$1"
                if [ -z "$CUSTOMER_ID" ]; then
                    echo "Usage: shapescale subscription list <customer_id>"
                    exit 1
                fi
                echo "📅 Subscriptions for customer $CUSTOMER_ID"
                stripe subscriptions list --customer "$CUSTOMER_ID" 2>&1
                ;;
            "cancel")
                SUBSCRIPTION_ID="$1"
                if [ -z "$SUBSCRIPTION_ID" ]; then
                    echo "Usage: shapescale subscription cancel <subscription_id>"
                    exit 1
                fi
                echo "🛑 Canceling subscription $SUBSCRIPTION_ID"
                stripe subscriptions cancel "$SUBSCRIPTION_ID" 2>&1
                ;;
            *)
                echo "Usage: shapescale subscription <create|list|cancel>"
                ;;
        esac
        ;;
        
    "invoice")
        SUBCOMMAND="$1"
        shift
        check_auth
        case "$SUBCOMMAND" in
            "generate")
                CUSTOMER_ID="$1"
                ORDER_ID="$2"
                if [ -z "$CUSTOMER_ID" ]; then
                    echo "Usage: shapescale invoice generate <customer_id> [order_id]"
                    exit 1
                fi
                
                TAX_RATE=$(read_json "tax_rate" ".")
                CURRENCY=$(read_json "default_currency" ".")
                
                echo "📄 Generating invoice for customer $CUSTOMER_ID"
                [ -n "$ORDER_ID" ] && echo "   Order: $ORDER_ID"
                
                # Create invoice item
                INVOICE_ITEM=$(stripe invoice-items create \
                    --customer "$CUSTOMER_ID" \
                    --amount 0 \
                    --currency "$CURRENCY" \
                    --description "ShapeScale Order $ORDER_ID" \
                    2>&1)
                
                # Create and finalize invoice
                INVOICE=$(stripe invoices create \
                    --customer "$CUSTOMER_ID" \
                    --auto-advance \
                    2>&1)
                
                format_output "$INVOICE" "success" || format_output "$INVOICE" "error"
                ;;
            *)
                echo "Usage: shapescale invoice generate <customer_id> [order_id]"
                ;;
        esac
        ;;
        
    "order")
        SUBCOMMAND="$1"
        shift
        check_auth
        case "$SUBCOMMAND" in
            "status")
                ORDER_ID="$1"
                if [ -z "$ORDER_ID" ]; then
                    echo "Usage: shapescale order status <order_id>"
                    exit 1
                fi
                
                echo "📦 Checking order status: $ORDER_ID"
                
                # Look up by metadata
                RESULT=$(stripe payment-intents list --limit 100 2>&1)
                
                # Find payment with matching order metadata
                MATCH=$(echo "$RESULT" | grep -A 5 "\"metadata\"" | grep -B 5 "\"order_id\": \"$ORDER_ID\"" || echo "")
                
                if [ -n "$MATCH" ]; then
                    echo "✅ Found payment for order $ORDER_ID"
                    echo "$MATCH" | head -20
                else
                    echo "⚠️  No payment found for order $ORDER_ID"
                    echo "   Make sure payments are tagged with: metadata: { order_id: '$ORDER_ID' }"
                fi
                ;;
            *)
                echo "Usage: shapescale order status <order_id>"
                ;;
        esac
        ;;
        
    "help"|"")
        echo "ShapeScale Stripe Extensions"
        echo ""
        echo "Commands:"
        echo "  clinic create <name> [template]  - Create clinic customer"
        echo "  clinic list                       - List clinic customers"
        echo ""
        echo "  subscription create <cus_id> <plan> - Create subscription"
        echo "  subscription list <cus_id>          - List subscriptions"
        echo "  subscription cancel <sub_id>        - Cancel subscription"
        echo ""
        echo "  invoice generate <cus_id> [order]  - Generate invoice"
        echo "  order status <order_id>            - Check order payment status"
        echo ""
        echo "Configuration:"
        echo "  SHAPESCALE_PRESETS_PATH - Path to shapescale-presets.json"
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        echo "Run 'shapescale help' for usage"
        ;;
esac
