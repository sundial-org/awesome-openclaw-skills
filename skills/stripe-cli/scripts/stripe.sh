#!/bin/bash
# Stripe CLI Wrapper - Universal Commands
# Usage: ./stripe.sh <command> [args...]

set -e

# Load environment
STRIPE_SECRET_KEY="${STRIPE_SECRET_KEY:-}"
if [ -z "$STRIPE_SECRET_KEY" ]; then
    # Try 1Password
    STRIPE_SECRET_KEY=$(op read "op://Stripe/Secret Key" --vault Personal 2>/dev/null || echo "")
fi

if [ -z "$STRIPE_SECRET_KEY" ]; then
    echo "❌ Error: STRIPE_SECRET_KEY not set. Run 'stripe login' or set the environment variable."
    exit 1
fi

export STRIPE_SECRET_KEY

COMMAND="$1"
shift || true

# Helper function to format output as JSON for agent consumption
format_output() {
    local output="$1"
    local status="$2"
    
    if [ "$status" = "success" ]; then
        echo "✅ $output"
    else
        echo "❌ $output"
    fi
}

case "$COMMAND" in
    "customer")
        SUBCOMMAND="$1"
        shift
        case "$SUBCOMMAND" in
            "create")
                NAME="$1"
                EMAIL="$2"
                if [ -z "$NAME" ]; then
                    echo "Usage: stripe customer create <name> [email]"
                    exit 1
                fi
                # Build command safely without eval
                if [ -n "$EMAIL" ]; then
                    RESULT=$(stripe customers create --description "$NAME" --email "$EMAIL" 2>&1)
                else
                    RESULT=$(stripe customers create --description "$NAME" 2>&1)
                fi
                if [ $? -eq 0 ]; then
                    format_output "$RESULT" "success"
                else
                    format_output "$RESULT" "error"
                fi
                ;;
            "list")
                LIMIT="${1:-10}"
                stripe customers list --limit "$LIMIT" 2>&1
                ;;
            "get")
                CUSTOMER_ID="$1"
                if [ -z "$CUSTOMER_ID" ]; then
                    echo "Usage: stripe customer get <customer_id>"
                    exit 1
                fi
                stripe customers retrieve "$CUSTOMER_ID" 2>&1
                ;;
            *)
                echo "Unknown customer command: $SUBCOMMAND"
                echo "Usage: stripe customer <create|list|get>"
                ;;
        esac
        ;;
        
    "payment")
        SUBCOMMAND="$1"
        shift
        case "$SUBCOMMAND" in
            "create")
                AMOUNT="$1"
                CURRENCY="${2:-usd}"
                if [ -z "$AMOUNT" ]; then
                    echo "Usage: stripe payment create <amount_in_cents> [currency]"
                    exit 1
                fi
                RESULT=$(stripe payment_intents create --amount "$AMOUNT" --currency "$CURRENCY" 2>&1)
                if [ $? -eq 0 ]; then
                    format_output "$RESULT" "success"
                else
                    format_output "$RESULT" "error"
                fi
                ;;
            "list")
                LIMIT="${1:-10}"
                stripe payment_intents list --limit "$LIMIT" 2>&1
                ;;
            "get")
                PAYMENT_ID="$1"
                if [ -z "$PAYMENT_ID" ]; then
                    echo "Usage: stripe payment get <payment_intent_id>"
                    exit 1
                fi
                stripe payment_intents retrieve "$PAYMENT_ID" 2>&1
                ;;
            "refund")
                PAYMENT_ID="$1"
                if [ -z "$PAYMENT_ID" ]; then
                    echo "Usage: stripe payment refund <payment_intent_id>"
                    exit 1
                fi
                stripe refunds create --payment-intent "$PAYMENT_ID" 2>&1
                ;;
            *)
                echo "Unknown payment command: $SUBCOMMAND"
                echo "Usage: stripe payment <create|list|get|refund>"
                ;;
        esac
        ;;
        
    "webhook")
        SUBCOMMAND="$1"
        shift
        case "$SUBCOMMAND" in
            "listen")
                DURATION="${1:-30}"
                ENDPOINT="${STRIPE_WEBHOOK_ENDPOINT:-http://localhost:4242}"
                echo "🔌 Listening for webhooks for ${DURATION}s, forwarding to $ENDPOINT..."
                stripe listen --forward-to "$ENDPOINT" --timeout "$DURATION" 2>&1
                ;;
            "trigger")
                EVENT="$1"
                if [ -z "$EVENT" ]; then
                    echo "Usage: stripe webhook trigger <event_type>"
                    echo "Examples: payment_intent.succeeded, charge.refunded, customer.subscription.created"
                    exit 1
                fi
                echo "🎯 Triggering $EVENT event..."
                stripe trigger "$EVENT" 2>&1
                ;;
            "resend")
                EVENT_ID="$1"
                if [ -z "$EVENT_ID" ]; then
                    echo "Usage: stripe webhook resend <event_id>"
                    exit 1
                fi
                stripe events resend "$EVENT_ID" 2>&1
                ;;
            *)
                echo "Unknown webhook command: $SUBCOMMAND"
                echo "Usage: stripe webhook <listen|trigger|resend>"
                ;;
        esac
        ;;
        
    "api")
        METHOD="$1"
        RESOURCE="$2"
        shift 2
        case "$METHOD" in
            "get")
                stripe get "$RESOURCE" "$@" 2>&1
                ;;
            "post")
                stripe post "$RESOURCE" "$@" 2>&1
                ;;
            "delete")
                stripe delete "$RESOURCE" "$@" 2>&1
                ;;
            *)
                echo "Usage: stripe api <get|post|delete> <resource> [args]"
                ;;
        esac
        ;;
        
    "version")
        stripe version 2>&1
        ;;
        
    "help"|"")
        echo "Stripe CLI Wrapper for Clawdbot"
        echo ""
        echo "Commands:"
        echo "  customer create <name> [email]  - Create a customer"
        echo "  customer list [limit]           - List customers"
        echo "  customer get <id>               - Get customer details"
        echo ""
        echo "  payment create <amount> [curr]  - Create payment intent"
        echo "  payment list [limit]            - List payment intents"
        echo "  payment get <id>                - Get payment details"
        echo "  payment refund <id>             - Refund payment"
        echo ""
        echo "  webhook listen [seconds]        - Listen for webhooks"
        echo "  webhook trigger <event>         - Trigger test event"
        echo "  webhook resend <event_id>       - Resend event"
        echo ""
        echo "  api <get|post|delete> <res>     - Generic API call"
        echo ""
        echo "Environment:"
        echo "  STRIPE_SECRET_KEY               - Your Stripe secret key"
        echo "  STRIPE_WEBHOOK_ENDPOINT         - Webhook forwarding URL"
        ;;
        
    *)
        echo "Unknown command: $COMMAND"
        echo "Run 'stripe help' for usage"
        ;;
esac
