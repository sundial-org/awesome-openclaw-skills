# Bags Trading 📈

Get quotes and swap tokens on Solana.

**Base URL:** `https://public-api-v2.bags.fm/api/v1/`

---

## Prerequisites

1. **Authenticated** — Complete [AUTH.md](https://bags.fm/auth.md) first
2. **API Key** — Created via `/agent/dev/keys/create` or from [dev.bags.fm](https://dev.bags.fm)
3. **Wallet with tokens** — Tokens to swap and SOL for transaction fees

```bash
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')
BAGS_WALLET=$(cat ~/.config/bags/credentials.json | jq -r '.wallets[0]')
```

---

## Common Token Addresses

| Token | Mint Address |
|-------|--------------|
| SOL (Wrapped) | `So11111111111111111111111111111111111111112` |
| USDC | `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v` |
| USDT | `Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB` |

---

## Get a Quote

Retrieve expected output before executing a swap.

```bash
BAGS_INPUT_MINT="So11111111111111111111111111111111111111112"
BAGS_OUTPUT_MINT="EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
BAGS_AMOUNT=100000000  # Amount in smallest unit (lamports for SOL)

curl -s "https://public-api-v2.bags.fm/api/v1/trade/quote?\
inputMint=$BAGS_INPUT_MINT&\
outputMint=$BAGS_OUTPUT_MINT&\
amount=$BAGS_AMOUNT&\
slippageMode=auto" \
  -H "x-api-key: $BAGS_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "response": {
    "requestId": "req_abc123",
    "inAmount": "100000000",
    "outAmount": "15250000",
    "minOutAmount": "15097500",
    "priceImpactPct": "0.05",
    "slippageBps": 100,
    "routePlan": [
      {
        "venue": "Raydium",
        "inputMint": "So11111111111111111111111111111111111111112",
        "outputMint": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "inAmount": "100000000",
        "outAmount": "15250000"
      }
    ],
    "platformFee": {
      "amount": "50000",
      "feeBps": 5,
      "feeAccount": "..."
    }
  }
}
```

### Quote Parameters

| Parameter | Required | Description |
|-----------|----------|-------------|
| `inputMint` | ✅ | Token mint address you're swapping from |
| `outputMint` | ✅ | Token mint address you're swapping to |
| `amount` | ✅ | Amount in smallest unit (e.g., lamports) |
| `slippageMode` | ✅ | `auto` or `manual` |
| `slippageBps` | If manual | Slippage tolerance in basis points |

### Quote Response Fields

| Field | Description |
|-------|-------------|
| `requestId` | Unique identifier for this quote |
| `inAmount` | Input amount (what you're spending) |
| `outAmount` | Expected output amount |
| `minOutAmount` | Minimum output accounting for slippage |
| `priceImpactPct` | Price impact percentage |
| `slippageBps` | Slippage tolerance in basis points |
| `routePlan` | Array of swap legs through DEXs/pools |
| `platformFee` | Fee information (if applicable) |

---

## Slippage Modes

### Auto Slippage

Bags calculates appropriate slippage based on current market conditions.

```bash
slippageMode=auto
```

### Manual Slippage

Specify your own slippage tolerance.

```bash
slippageMode=manual&slippageBps=100
```

| slippageBps | Percentage |
|-------------|------------|
| 50 | 0.5% |
| 100 | 1% |
| 300 | 3% |
| 500 | 5% |
| 1000 | 10% |

---

## Execute a Swap

### Step 1: Get Quote

```bash
BAGS_QUOTE=$(curl -s "https://public-api-v2.bags.fm/api/v1/trade/quote?\
inputMint=$BAGS_INPUT_MINT&\
outputMint=$BAGS_OUTPUT_MINT&\
amount=$BAGS_AMOUNT&\
slippageMode=auto" \
  -H "x-api-key: $BAGS_API_KEY")

# Extract quote details
BAGS_OUT_AMOUNT=$(echo "$BAGS_QUOTE" | jq -r '.response.outAmount')
BAGS_MIN_OUT=$(echo "$BAGS_QUOTE" | jq -r '.response.minOutAmount')
BAGS_PRICE_IMPACT=$(echo "$BAGS_QUOTE" | jq -r '.response.priceImpactPct')
```

### Step 2: Create Swap Transaction

```bash
BAGS_SWAP_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/trade/swap" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"quoteResponse\": $(echo "$BAGS_QUOTE" | jq '.response'),
    \"userPublicKey\": \"$BAGS_WALLET\"
  }")
```

**Response:**
```json
{
  "success": true,
  "response": {
    "transaction": "base64_encoded_unsigned_transaction",
    "computeUnitLimit": 200000,
    "prioritizationFeeLamports": 5000,
    "lastValidBlockHeight": 123456789
  }
}
```

### Step 3: Sign Transaction

```bash
BAGS_UNSIGNED_TX=$(echo "$BAGS_SWAP_RESPONSE" | jq -r '.response.transaction')

# Export private key
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
  | jq -r '.response.privateKey')

# Sign transaction (requires sign-transaction.js from WALLETS.md)
BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_UNSIGNED_TX")

# Clear private key immediately
unset BAGS_PRIVATE_KEY
```

### Step 4: Submit Transaction

```bash
BAGS_RESULT=$(curl -s -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"sendTransaction\",
    \"params\": [\"$BAGS_SIGNED_TX\", {\"encoding\": \"base64\", \"skipPreflight\": false}]
  }")

BAGS_SIGNATURE=$(echo "$BAGS_RESULT" | jq -r '.result // empty')
BAGS_ERROR=$(echo "$BAGS_RESULT" | jq -r '.error.message // empty')
```

---

## Complete Swap Script

```bash
#!/bin/bash
# bags-swap.sh - Execute a token swap
# Usage: ./bags-swap.sh <input_mint> <output_mint> <amount>

set -e

BAGS_INPUT_MINT=$1
BAGS_OUTPUT_MINT=$2
BAGS_AMOUNT=$3

if [ -z "$BAGS_INPUT_MINT" ] || [ -z "$BAGS_OUTPUT_MINT" ] || [ -z "$BAGS_AMOUNT" ]; then
  echo "Usage: $0 <input_mint> <output_mint> <amount_in_smallest_unit>"
  exit 1
fi

# Load credentials
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')
BAGS_WALLET=$(cat ~/.config/bags/credentials.json | jq -r '.wallets[0]')

echo "📈 Bags Swap"
echo "============"
echo "Input:  $BAGS_INPUT_MINT"
echo "Output: $BAGS_OUTPUT_MINT"
echo "Amount: $BAGS_AMOUNT"
echo ""

# Step 1: Get quote
echo "🔍 Getting quote..."
BAGS_QUOTE=$(curl -s "https://public-api-v2.bags.fm/api/v1/trade/quote?\
inputMint=$BAGS_INPUT_MINT&\
outputMint=$BAGS_OUTPUT_MINT&\
amount=$BAGS_AMOUNT&\
slippageMode=auto" \
  -H "x-api-key: $BAGS_API_KEY")

if ! echo "$BAGS_QUOTE" | jq -e '.success == true' > /dev/null; then
  echo "❌ Quote failed: $(echo "$BAGS_QUOTE" | jq -r '.error')"
  exit 1
fi

BAGS_IN_AMOUNT=$(echo "$BAGS_QUOTE" | jq -r '.response.inAmount')
BAGS_OUT_AMOUNT=$(echo "$BAGS_QUOTE" | jq -r '.response.outAmount')
BAGS_MIN_OUT=$(echo "$BAGS_QUOTE" | jq -r '.response.minOutAmount')
BAGS_PRICE_IMPACT=$(echo "$BAGS_QUOTE" | jq -r '.response.priceImpactPct')
BAGS_SLIPPAGE=$(echo "$BAGS_QUOTE" | jq -r '.response.slippageBps')

echo "✓ Quote received"
echo "  In:           $BAGS_IN_AMOUNT"
echo "  Out:          $BAGS_OUT_AMOUNT"
echo "  Min out:      $BAGS_MIN_OUT"
echo "  Price impact: $BAGS_PRICE_IMPACT%"
echo "  Slippage:     $((BAGS_SLIPPAGE / 100)).$((BAGS_SLIPPAGE % 100))%"
echo ""

# Step 2: Create swap transaction
echo "🎯 Creating swap transaction..."
BAGS_SWAP_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/trade/swap" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"quoteResponse\": $(echo "$BAGS_QUOTE" | jq '.response'),
    \"userPublicKey\": \"$BAGS_WALLET\"
  }")

if ! echo "$BAGS_SWAP_RESPONSE" | jq -e '.success == true' > /dev/null; then
  echo "❌ Swap creation failed: $(echo "$BAGS_SWAP_RESPONSE" | jq -r '.error')"
  exit 1
fi

BAGS_UNSIGNED_TX=$(echo "$BAGS_SWAP_RESPONSE" | jq -r '.response.transaction')
echo "✓ Transaction created"
echo ""

# Step 3: Sign transaction
echo "🔑 Signing transaction..."
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
  | jq -r '.response.privateKey')

if [ -z "$BAGS_PRIVATE_KEY" ] || [ "$BAGS_PRIVATE_KEY" = "null" ]; then
  echo "❌ Failed to export private key"
  exit 1
fi

BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_UNSIGNED_TX")
unset BAGS_PRIVATE_KEY

if [ -z "$BAGS_SIGNED_TX" ]; then
  echo "❌ Failed to sign transaction"
  exit 1
fi

echo "✓ Transaction signed"
echo ""

# Step 4: Submit transaction
echo "📡 Submitting transaction..."
BAGS_RESULT=$(curl -s -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"sendTransaction\",
    \"params\": [\"$BAGS_SIGNED_TX\", {\"encoding\": \"base64\", \"skipPreflight\": false}]
  }")

BAGS_SIGNATURE=$(echo "$BAGS_RESULT" | jq -r '.result // empty')
BAGS_ERROR=$(echo "$BAGS_RESULT" | jq -r '.error.message // empty')

if [ -n "$BAGS_SIGNATURE" ]; then
  echo ""
  echo "✅ Swap submitted"
  echo "   Signature: $BAGS_SIGNATURE"
  echo "   Explorer:  https://solscan.io/tx/$BAGS_SIGNATURE"
else
  echo ""
  echo "❌ Swap failed: $BAGS_ERROR"
  exit 1
fi
```

---

## Quote-Only Script

Get a quote without executing:

```bash
#!/bin/bash
# bags-quote.sh - Get a swap quote
# Usage: ./bags-quote.sh <input_mint> <output_mint> <amount>

BAGS_INPUT_MINT=$1
BAGS_OUTPUT_MINT=$2
BAGS_AMOUNT=$3

if [ -z "$BAGS_INPUT_MINT" ] || [ -z "$BAGS_OUTPUT_MINT" ] || [ -z "$BAGS_AMOUNT" ]; then
  echo "Usage: $0 <input_mint> <output_mint> <amount>"
  exit 1
fi

BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')

BAGS_QUOTE=$(curl -s "https://public-api-v2.bags.fm/api/v1/trade/quote?\
inputMint=$BAGS_INPUT_MINT&\
outputMint=$BAGS_OUTPUT_MINT&\
amount=$BAGS_AMOUNT&\
slippageMode=auto" \
  -H "x-api-key: $BAGS_API_KEY")

if ! echo "$BAGS_QUOTE" | jq -e '.success == true' > /dev/null; then
  echo "❌ Quote failed: $(echo "$BAGS_QUOTE" | jq -r '.error')"
  exit 1
fi

echo "$BAGS_QUOTE" | jq '.response | {
  inAmount,
  outAmount,
  minOutAmount,
  priceImpactPct,
  slippageBps,
  routes: [.routePlan[].venue]
}'
```

---

## Error Handling

**Quote not available (400):**
```json
{
  "success": false,
  "error": "No route found for this pair"
}
```

**Insufficient balance (400):**
```json
{
  "success": false,
  "error": "Insufficient balance for swap"
}
```

**Invalid API key (401):**
```json
{
  "success": false,
  "error": "Invalid API key"
}
```

**Rate limited (429):**
```json
{
  "success": false,
  "error": "Rate limit exceeded"
}
```

**Transaction failure (on-chain):**
- Slippage exceeded — price moved beyond tolerance
- Blockhash expired — transaction took too long
- Insufficient SOL — not enough for transaction fees

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `BAGS_JWT_TOKEN` | JWT token for Agent API |
| `BAGS_API_KEY` | API key for Public API |
| `BAGS_WALLET` | Your wallet address |
| `BAGS_INPUT_MINT` | Token mint to swap from |
| `BAGS_OUTPUT_MINT` | Token mint to swap to |
| `BAGS_AMOUNT` | Amount in smallest unit |
| `BAGS_QUOTE` | Quote response object |
| `BAGS_OUT_AMOUNT` | Expected output amount |
| `BAGS_MIN_OUT` | Minimum output (with slippage) |
| `BAGS_PRICE_IMPACT` | Price impact percentage |
| `BAGS_SLIPPAGE` | Slippage in basis points |
| `BAGS_SWAP_RESPONSE` | Swap transaction response |
| `BAGS_UNSIGNED_TX` | Unsigned transaction (base64) |
| `BAGS_SIGNED_TX` | Signed transaction (base64) |
| `BAGS_PRIVATE_KEY` | Temporary private key (clear after use!) |
| `BAGS_SIGNATURE` | Transaction signature |

---

## Next Steps

- **Claim fees first** → See [FEES.md](https://bags.fm/fees.md)
- **Launch tokens** → See [LAUNCH.md](https://bags.fm/launch.md)
- **Check balances** → See [WALLETS.md](https://bags.fm/wallets.md)
