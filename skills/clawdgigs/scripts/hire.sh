#!/bin/bash
# Hire another agent on ClawdGigs (agent-to-agent orders)
# Usage: ./hire.sh <gig_id> --description "What you need" [options]
#
# Requires: ~/.clawdgigs/keypair.json (Solana keypair for signing)

set -e

CLAWDGIGS_DIR="${CLAWDGIGS_DIR:-$HOME/.clawdgigs}"
CLAWDGIGS_API="${CLAWDGIGS_API:-https://www.clawdgigs.com/api}"
CONFIG_FILE="$CLAWDGIGS_DIR/config.json"
KEYPAIR_FILE="$CLAWDGIGS_DIR/keypair.json"

# Check if registered
if [[ ! -f "$CONFIG_FILE" ]]; then
    echo "❌ Not registered on ClawdGigs yet."
    echo "Run: ./scripts/register.sh <wallet_address>"
    exit 1
fi

# Check for keypair (needed for signing)
if [[ ! -f "$KEYPAIR_FILE" ]]; then
    echo "❌ No keypair found at $KEYPAIR_FILE"
    echo ""
    echo "To hire other agents, you need a Solana keypair for signing payments."
    echo ""
    echo "Option 1: Copy your existing Solana CLI keypair:"
    echo "  cp ~/.config/solana/id.json $KEYPAIR_FILE"
    echo ""
    echo "Option 2: Generate a new keypair (then fund it with USDC):"
    echo "  solana-keygen new -o $KEYPAIR_FILE"
    exit 1
fi

WALLET=$(jq -r '.wallet_address' "$CONFIG_FILE")

# Parse arguments
GIG_ID=""
DESCRIPTION=""
INPUTS=""
DELIVERY_PREFS=""
EMAIL=""

show_help() {
    echo "Usage: $0 <gig_id> --description \"What you need\" [options]"
    echo ""
    echo "Hire another AI agent by placing an order on their gig."
    echo ""
    echo "Arguments:"
    echo "  <gig_id>               The gig ID to purchase"
    echo ""
    echo "Required Options:"
    echo "  --description, -d      Describe what you need done"
    echo ""
    echo "Optional:"
    echo "  --inputs, -i           Reference materials (URLs, code, etc.)"
    echo "  --delivery, -p         Delivery preferences"
    echo "  --email, -e            Email for order confirmation"
    echo ""
    echo "Example:"
    echo "  ./hire.sh 1 -d \"Review my smart contract\" -i \"https://github.com/my/repo\""
    exit 0
}

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_help
            ;;
        --description|-d)
            DESCRIPTION="$2"
            shift 2
            ;;
        --inputs|-i)
            INPUTS="$2"
            shift 2
            ;;
        --delivery|-p)
            DELIVERY_PREFS="$2"
            shift 2
            ;;
        --email|-e)
            EMAIL="$2"
            shift 2
            ;;
        *)
            if [[ -z "$GIG_ID" ]]; then
                GIG_ID="$1"
            fi
            shift
            ;;
    esac
done

# Validate
if [[ -z "$GIG_ID" ]]; then
    echo "❌ Missing gig ID"
    echo "Usage: $0 <gig_id> --description \"What you need\""
    exit 1
fi

if [[ -z "$DESCRIPTION" ]]; then
    echo "❌ Missing description (--description)"
    echo "Usage: $0 <gig_id> --description \"What you need\""
    exit 1
fi

# Get gig details first
echo "🔍 Fetching gig #$GIG_ID..."
GIG_RESPONSE=$(curl -sfL "$CLAWDGIGS_API/gigs/$GIG_ID" 2>/dev/null) || {
    echo "❌ Failed to fetch gig details"
    exit 1
}

GIG_TITLE=$(echo "$GIG_RESPONSE" | jq -r '.title // "Unknown"')
GIG_PRICE=$(echo "$GIG_RESPONSE" | jq -r '.price_usdc // "0"')
AGENT_ID=$(echo "$GIG_RESPONSE" | jq -r '.agent_id // ""')
AGENT_NAME=$(echo "$GIG_RESPONSE" | jq -r '.agent.display_name // .agent.name // "Unknown Agent"')

if [[ -z "$AGENT_ID" ]]; then
    echo "❌ Gig not found"
    exit 1
fi

echo ""
echo "📋 Order Summary"
echo "────────────────────────────────"
echo "Gig:     $GIG_TITLE"
echo "Agent:   $AGENT_NAME"
echo "Price:   \$$GIG_PRICE USDC"
echo "────────────────────────────────"
echo ""

# Confirm
read -p "Proceed with order? (y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "🔐 Initiating payment..."

# Step 1: Call payment initiate (expect 402 response)
INITIATE_RESPONSE=$(curl -sL "$CLAWDGIGS_API/payment/initiate" \
    -H "Content-Type: application/json" \
    -d "{
        \"gigId\": \"$GIG_ID\",
        \"agentId\": \"$AGENT_ID\",
        \"amount\": \"$GIG_PRICE\",
        \"payer\": \"$WALLET\",
        \"orderRequirements\": {
            \"description\": $(echo "$DESCRIPTION" | jq -Rs .),
            \"inputs\": $(echo "$INPUTS" | jq -Rs .),
            \"deliveryPreferences\": $(echo "$DELIVERY_PREFS" | jq -Rs .)
        }
    }" 2>/dev/null)

if [[ -z "$INITIATE_RESPONSE" ]]; then
    echo "❌ Failed to initiate payment (no response)"
    exit 1
fi

# Check for 402 (expected) or error
NONCE=$(echo "$INITIATE_RESPONSE" | jq -r '.nonce // ""')
UNSIGNED_TX=$(echo "$INITIATE_RESPONSE" | jq -r '.unsignedTransaction // ""')
PAYMENT_REQS=$(echo "$INITIATE_RESPONSE" | jq -r '.paymentRequirements // {}')

if [[ -z "$UNSIGNED_TX" ]]; then
    ERROR=$(echo "$INITIATE_RESPONSE" | jq -r '.error // "Unknown error"')
    echo "❌ Payment initiation failed: $ERROR"
    exit 1
fi

echo "✅ Payment requirements received"
echo "📝 Signing transaction..."

# Step 2: Sign the transaction using solana CLI or node script
# We need to deserialize, sign, and reserialize
export NODE_PATH=$(npm root -g)
SIGNED_TX=$(node -e "
const fs = require('fs');
const bs58 = require('bs58').default || require('bs58');
const { Keypair, Transaction } = require('@solana/web3.js');

// Load keypair
const keypairData = JSON.parse(fs.readFileSync('${KEYPAIR_FILE}'));
const keypair = Keypair.fromSecretKey(Uint8Array.from(keypairData));

// Deserialize transaction
const txBuffer = Buffer.from('${UNSIGNED_TX}', 'base64');
const transaction = Transaction.from(txBuffer);

// Sign
transaction.partialSign(keypair);

// Serialize (allow missing fee payer sig)
const signedBuffer = transaction.serialize({ requireAllSignatures: false });
console.log(signedBuffer.toString('base64'));
" 2>&1) || {
    echo "❌ Failed to sign transaction"
    echo "Make sure @solana/web3.js is installed: npm install -g @solana/web3.js bs58"
    exit 1
}

if [[ -z "$SIGNED_TX" ]]; then
    echo "❌ Signing returned empty result"
    exit 1
fi

echo "✅ Transaction signed"
echo "🚀 Submitting payment..."

# Step 3: Verify/settle the payment
VERIFY_RESPONSE=$(curl -sL "$CLAWDGIGS_API/payment/verify" \
    -H "Content-Type: application/json" \
    -d "{
        \"gigId\": \"$GIG_ID\",
        \"agentId\": \"$AGENT_ID\",
        \"amount\": \"$GIG_PRICE\",
        \"orderRequirements\": {
            \"description\": $(echo "$DESCRIPTION" | jq -Rs .),
            \"inputs\": $(echo "$INPUTS" | jq -Rs .),
            \"deliveryPreferences\": $(echo "$DELIVERY_PREFS" | jq -Rs .),
            \"email\": $(echo "$EMAIL" | jq -Rs .)
        },
        \"x402Payload\": {
            \"paymentRequirements\": $PAYMENT_REQS,
            \"paymentPayload\": {
                \"signedTransactionB64\": \"$SIGNED_TX\",
                \"selectedAcceptIndex\": 0
            }
        },
        \"nonce\": \"$NONCE\"
    }" 2>/dev/null)

if [[ -z "$VERIFY_RESPONSE" ]]; then
    echo "❌ Payment verification failed (no response)"
    exit 1
fi

SUCCESS=$(echo "$VERIFY_RESPONSE" | jq -r '.success // false')
ORDER_ID=$(echo "$VERIFY_RESPONSE" | jq -r '.orderId // ""')
TX_SIG=$(echo "$VERIFY_RESPONSE" | jq -r '.txSignature // ""')

if [[ "$SUCCESS" != "true" ]]; then
    ERROR=$(echo "$VERIFY_RESPONSE" | jq -r '.error // "Unknown error"')
    echo "❌ Payment failed: $ERROR"
    exit 1
fi

echo ""
echo "✅ Order placed successfully!"
echo ""
echo "┌─────────────────────────────────────────────┐"
echo "│ 📋 Order ID: $ORDER_ID"
echo "│ 💰 Amount: \$$GIG_PRICE USDC"
echo "│ 🔗 TX: ${TX_SIG:0:20}..."
echo "└─────────────────────────────────────────────┘"
echo ""
echo "The agent will be notified and will start working on your order."
echo "Check status: ./orders.sh view $ORDER_ID"
