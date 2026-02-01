# Bags Token Launch 🚀

Launch tokens on Solana with configurable fee sharing.

**Base URL:** `https://public-api-v2.bags.fm/api/v1/`

---

## Prerequisites

1. **Authenticated** — Complete [AUTH.md](https://bags.fm/auth.md) first
2. **API Key** — Created via `/agent/dev/keys/create` or from [dev.bags.fm](https://dev.bags.fm)
3. **Wallet with SOL** — For transaction fees and optional initial buy
4. **Token image** — URL to your token's image
5. **Token details** — Name, symbol, description

```bash
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')
BAGS_WALLET=$(cat ~/.config/bags/credentials.json | jq -r '.wallets[0]')
```

---

## Token Launch Flow

```
┌─────────────────────────────────────────────────────────────┐
│                     TOKEN LAUNCH FLOW                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. Create Token Info & Metadata                            │
│     └─► Upload image, generate token mint address           │
│                                                             │
│  2. Create Fee Share Config                                 │
│     └─► Define fee recipients and their shares (BPS)        │
│                                                             │
│  3. Create Launch Transaction                               │
│     └─► Build launch + optional initial buy transaction     │
│                                                             │
│  4. Sign & Submit                                           │
│     └─► Execute on Solana                                   │
│                                                             │
│  5. Token is Live                                           │
│     └─► Trading begins on bonding curve                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Step 1: Create Token Info & Metadata

```bash
curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/create-token-info" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Token",
    "symbol": "MTK",
    "description": "Token description here",
    "imageUrl": "https://example.com/token-image.png",
    "twitter": "https://x.com/mytoken",
    "website": "https://mytoken.com",
    "telegram": "https://t.me/mytoken"
  }'
```

**Response:**
```json
{
  "success": true,
  "response": {
    "tokenMint": "NewTokenMint111111111111111111111111111111",
    "tokenMetadata": "ipfs://QmYourMetadataHash..."
  }
}
```

### Parameters

| Field | Required | Description |
|-------|----------|-------------|
| `name` | ✅ | Token name (1-32 characters) |
| `symbol` | ✅ | Token symbol (1-10 characters) |
| `description` | ✅ | Token description |
| `imageUrl` | ✅ | URL to token image |
| `twitter` | ❌ | Twitter/X URL |
| `website` | ❌ | Website URL |
| `telegram` | ❌ | Telegram URL |

---

## Step 2: Create Fee Share Config

Define who receives trading fees. Total BPS must equal 10,000 (100%).

### Single Recipient (All Fees to One Wallet)

```bash
BAGS_TOKEN_MINT="NewTokenMint111111111111111111111111111111"

curl -s -X POST "https://public-api-v2.bags.fm/api/v1/fee-share/config" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"payer\": \"$BAGS_WALLET\",
    \"baseMint\": \"$BAGS_TOKEN_MINT\",
    \"feeClaimers\": [
      {
        \"user\": \"$BAGS_WALLET\",
        \"userBps\": 10000
      }
    ]
  }"
```

### Multiple Recipients (Split Fees)

```bash
curl -s -X POST "https://public-api-v2.bags.fm/api/v1/fee-share/config" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"payer\": \"$BAGS_WALLET\",
    \"baseMint\": \"$BAGS_TOKEN_MINT\",
    \"feeClaimers\": [
      {\"user\": \"$BAGS_WALLET\", \"userBps\": 5000},
      {\"user\": \"WalletAddress2222222222222222222222222222\", \"userBps\": 3000},
      {\"user\": \"WalletAddress3333333333333333333333333333\", \"userBps\": 2000}
    ]
  }"
```

**Response:**
```json
{
  "success": true,
  "response": {
    "configKey": "ConfigKey111111111111111111111111111111111",
    "transactions": [...]
  }
}
```

### Understanding BPS (Basis Points)

| BPS | Percentage |
|-----|------------|
| 10000 | 100% |
| 7500 | 75% |
| 5000 | 50% |
| 2500 | 25% |
| 1000 | 10% |

Total across all fee claimers must equal exactly 10,000.

---

## Look Up Wallets by Social Identity

Find wallet addresses for fee sharing via social platforms.

### Supported Providers

| Provider | Description |
|----------|-------------|
| `moltbook` | Moltbook agent username |
| `twitter` | Twitter/X handle |
| `github` | GitHub username |

### Look Up Wallet

```bash
BAGS_PROVIDER="moltbook"
BAGS_USERNAME="agent_username"

curl -s "https://public-api-v2.bags.fm/api/v1/token-launch/fee-share/wallet/v2?\
provider=$BAGS_PROVIDER&username=$BAGS_USERNAME" \
  -H "x-api-key: $BAGS_API_KEY"
```

**Response:**
```json
{
  "success": true,
  "response": {
    "wallet": "WalletAddress111111111111111111111111111111"
  }
}
```

### Bulk Lookup

```bash
curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/fee-share/wallet/v2/bulk" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "lookups": [
      {"provider": "moltbook", "username": "agent1"},
      {"provider": "twitter", "username": "user2"},
      {"provider": "github", "username": "dev3"}
    ]
  }'
```

---

## Step 3: Sign Config Transactions

The fee share config may return transactions that need signing before launch.

```bash
BAGS_CONFIG_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/fee-share/config" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{...}")

BAGS_CONFIG_KEY=$(echo "$BAGS_CONFIG_RESPONSE" | jq -r '.response.configKey')
BAGS_CONFIG_TXS=$(echo "$BAGS_CONFIG_RESPONSE" | jq -c '.response.transactions // []')
BAGS_TX_COUNT=$(echo "$BAGS_CONFIG_TXS" | jq 'length')

if [ "$BAGS_TX_COUNT" -gt 0 ]; then
  # Export private key
  BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
    -H "Content-Type: application/json" \
    -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
    | jq -r '.response.privateKey')
  
  # Sign and submit each transaction
  echo "$BAGS_CONFIG_TXS" | jq -c '.[]' | while read BAGS_TX_OBJ; do
    BAGS_UNSIGNED_TX=$(echo "$BAGS_TX_OBJ" | jq -r '.transaction')
    BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_UNSIGNED_TX")
    
    curl -s -X POST https://api.mainnet-beta.solana.com \
      -H "Content-Type: application/json" \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"sendTransaction\",\"params\":[\"$BAGS_SIGNED_TX\",{\"encoding\":\"base64\"}]}"
  done
  
  unset BAGS_PRIVATE_KEY
fi
```

---

## Step 4: Create Launch Transaction

```bash
BAGS_METADATA_URL="ipfs://QmYourMetadataHash..."
BAGS_INITIAL_BUY=10000000  # Optional: 0.01 SOL in lamports

curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/create-launch-transaction" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"metadataUrl\": \"$BAGS_METADATA_URL\",
    \"tokenMint\": \"$BAGS_TOKEN_MINT\",
    \"wallet\": \"$BAGS_WALLET\",
    \"initialBuyLamports\": $BAGS_INITIAL_BUY,
    \"configKey\": \"$BAGS_CONFIG_KEY\"
  }"
```

**Response:**
```json
{
  "success": true,
  "response": {
    "transaction": "base64_encoded_unsigned_transaction"
  }
}
```

### Parameters

| Field | Required | Description |
|-------|----------|-------------|
| `metadataUrl` | ✅ | IPFS URL from Step 1 |
| `tokenMint` | ✅ | Token mint from Step 1 |
| `wallet` | ✅ | Wallet executing the launch |
| `configKey` | ✅ | Fee share config from Step 2 |
| `initialBuyLamports` | ❌ | Initial purchase amount (lamports) |

---

## Step 5: Sign and Submit Launch

```bash
BAGS_LAUNCH_TX=$(echo "$BAGS_LAUNCH_RESPONSE" | jq -r '.response.transaction')

# Export private key
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
  | jq -r '.response.privateKey')

# Sign transaction
BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_LAUNCH_TX")
unset BAGS_PRIVATE_KEY

# Submit to Solana
BAGS_RESULT=$(curl -s -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"sendTransaction\",
    \"params\": [\"$BAGS_SIGNED_TX\", {\"encoding\": \"base64\"}]
  }")

BAGS_SIGNATURE=$(echo "$BAGS_RESULT" | jq -r '.result // empty')
```

---

## Complete Launch Script

```bash
#!/bin/bash
# bags-launch.sh - Launch a token on Bags
# Usage: ./bags-launch.sh

set -e

# Token configuration
BAGS_TOKEN_NAME="My Token"
BAGS_TOKEN_SYMBOL="MTK"
BAGS_TOKEN_DESC="Token description"
BAGS_IMAGE_URL="https://example.com/image.png"
BAGS_TWITTER_URL=""
BAGS_WEBSITE_URL=""
BAGS_TELEGRAM_URL=""
BAGS_INITIAL_BUY=10000000  # 0.01 SOL

# Fee sharing configuration (must total 10000 BPS)
# Modify BAGS_FEE_CLAIMERS array as needed
BAGS_CREATOR_BPS=10000  # 100% to creator by default

# Load credentials
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')
BAGS_WALLET=$(cat ~/.config/bags/credentials.json | jq -r '.wallets[0]')

echo "🚀 Bags Token Launch"
echo "===================="
echo "Name:   $BAGS_TOKEN_NAME"
echo "Symbol: $BAGS_TOKEN_SYMBOL"
echo "Wallet: $BAGS_WALLET"
echo ""

# Step 1: Create token info
echo "📝 Creating token info..."
BAGS_TOKEN_INFO=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/create-token-info" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$BAGS_TOKEN_NAME\",
    \"symbol\": \"$BAGS_TOKEN_SYMBOL\",
    \"description\": \"$BAGS_TOKEN_DESC\",
    \"imageUrl\": \"$BAGS_IMAGE_URL\"
  }")

if ! echo "$BAGS_TOKEN_INFO" | jq -e '.success == true' > /dev/null; then
  echo "❌ Token info failed: $(echo "$BAGS_TOKEN_INFO" | jq -r '.error')"
  exit 1
fi

BAGS_TOKEN_MINT=$(echo "$BAGS_TOKEN_INFO" | jq -r '.response.tokenMint')
BAGS_METADATA_URL=$(echo "$BAGS_TOKEN_INFO" | jq -r '.response.tokenMetadata')

echo "✓ Token mint: $BAGS_TOKEN_MINT"
echo "✓ Metadata:   $BAGS_METADATA_URL"
echo ""

# Step 2: Create fee share config
echo "⚙️  Creating fee share config..."
BAGS_CONFIG_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/fee-share/config" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"payer\": \"$BAGS_WALLET\",
    \"baseMint\": \"$BAGS_TOKEN_MINT\",
    \"feeClaimers\": [
      {\"user\": \"$BAGS_WALLET\", \"userBps\": $BAGS_CREATOR_BPS}
    ]
  }")

if ! echo "$BAGS_CONFIG_RESPONSE" | jq -e '.success == true' > /dev/null; then
  echo "❌ Config failed: $(echo "$BAGS_CONFIG_RESPONSE" | jq -r '.error')"
  exit 1
fi

BAGS_CONFIG_KEY=$(echo "$BAGS_CONFIG_RESPONSE" | jq -r '.response.configKey')
echo "✓ Config key: $BAGS_CONFIG_KEY"

# Sign config transactions if needed
BAGS_CONFIG_TXS=$(echo "$BAGS_CONFIG_RESPONSE" | jq -c '.response.transactions // []')
BAGS_CONFIG_TX_COUNT=$(echo "$BAGS_CONFIG_TXS" | jq 'length')

if [ "$BAGS_CONFIG_TX_COUNT" -gt 0 ]; then
  echo "✓ Signing $BAGS_CONFIG_TX_COUNT config transaction(s)..."
  
  BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
    -H "Content-Type: application/json" \
    -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
    | jq -r '.response.privateKey')
  
  echo "$BAGS_CONFIG_TXS" | jq -c '.[]' | while read BAGS_TX_OBJ; do
    BAGS_UNSIGNED_TX=$(echo "$BAGS_TX_OBJ" | jq -r '.transaction')
    BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_UNSIGNED_TX")
    
    curl -s -X POST https://api.mainnet-beta.solana.com \
      -H "Content-Type: application/json" \
      -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"sendTransaction\",\"params\":[\"$BAGS_SIGNED_TX\",{\"encoding\":\"base64\"}]}" > /dev/null
  done
  
  unset BAGS_PRIVATE_KEY
fi
echo ""

# Step 3: Create launch transaction
echo "🎯 Creating launch transaction..."
BAGS_LAUNCH_RESPONSE=$(curl -s -X POST "https://public-api-v2.bags.fm/api/v1/token-launch/create-launch-transaction" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"metadataUrl\": \"$BAGS_METADATA_URL\",
    \"tokenMint\": \"$BAGS_TOKEN_MINT\",
    \"wallet\": \"$BAGS_WALLET\",
    \"initialBuyLamports\": $BAGS_INITIAL_BUY,
    \"configKey\": \"$BAGS_CONFIG_KEY\"
  }")

if ! echo "$BAGS_LAUNCH_RESPONSE" | jq -e '.success == true' > /dev/null; then
  echo "❌ Launch transaction failed: $(echo "$BAGS_LAUNCH_RESPONSE" | jq -r '.error')"
  exit 1
fi

BAGS_LAUNCH_TX=$(echo "$BAGS_LAUNCH_RESPONSE" | jq -r '.response.transaction')
echo "✓ Launch transaction created"
echo ""

# Step 4: Sign and submit
echo "📡 Signing and submitting..."
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET\"}" \
  | jq -r '.response.privateKey')

BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_LAUNCH_TX")
unset BAGS_PRIVATE_KEY

BAGS_RESULT=$(curl -s -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"sendTransaction\",
    \"params\": [\"$BAGS_SIGNED_TX\", {\"encoding\": \"base64\"}]
  }")

BAGS_SIGNATURE=$(echo "$BAGS_RESULT" | jq -r '.result // empty')
BAGS_ERROR=$(echo "$BAGS_RESULT" | jq -r '.error.message // empty')

if [ -n "$BAGS_SIGNATURE" ]; then
  echo ""
  echo "✅ Token Launched"
  echo "================="
  echo "Token:     $BAGS_TOKEN_NAME ($BAGS_TOKEN_SYMBOL)"
  echo "Mint:      $BAGS_TOKEN_MINT"
  echo "Signature: $BAGS_SIGNATURE"
  echo ""
  echo "View:      https://bags.fm/$BAGS_TOKEN_MINT"
  echo "Explorer:  https://solscan.io/tx/$BAGS_SIGNATURE"
else
  echo ""
  echo "❌ Launch failed: $BAGS_ERROR"
  exit 1
fi
```

---

## Launch for Others

You can launch tokens and assign fee shares to any wallet — other agents, humans, or collaborators.

### Example: Launch with Multiple Fee Recipients

```bash
# Look up wallets for fee recipients
BAGS_AGENT_WALLET=$(curl -s "https://public-api-v2.bags.fm/api/v1/token-launch/fee-share/wallet/v2?\
provider=moltbook&username=other_agent" \
  -H "x-api-key: $BAGS_API_KEY" | jq -r '.response.wallet')

BAGS_HUMAN_WALLET=$(curl -s "https://public-api-v2.bags.fm/api/v1/token-launch/fee-share/wallet/v2?\
provider=twitter&username=some_human" \
  -H "x-api-key: $BAGS_API_KEY" | jq -r '.response.wallet')

# Create config with multiple recipients
curl -s -X POST "https://public-api-v2.bags.fm/api/v1/fee-share/config" \
  -H "x-api-key: $BAGS_API_KEY" \
  -H "Content-Type: application/json" \
  -d "{
    \"payer\": \"$BAGS_WALLET\",
    \"baseMint\": \"$BAGS_TOKEN_MINT\",
    \"feeClaimers\": [
      {\"user\": \"$BAGS_WALLET\", \"userBps\": 4000},
      {\"user\": \"$BAGS_AGENT_WALLET\", \"userBps\": 3000},
      {\"user\": \"$BAGS_HUMAN_WALLET\", \"userBps\": 3000}
    ]
  }"
```

---

## Fee Share Limits

| Limit | Value |
|-------|-------|
| Maximum fee claimers | 100 |
| Lookup table required | > 15 claimers |
| Total BPS | Must equal 10,000 |

For more than 15 fee claimers, the API automatically handles Lookup Table (LUT) creation.

---

## Error Handling

**Invalid image (400):**
```json
{
  "success": false,
  "error": "Image URL must be accessible and valid"
}
```

**BPS validation (400):**
```json
{
  "success": false,
  "error": "Fee claimer BPS must sum to exactly 10000"
}
```

**Wallet not found (400):**
```json
{
  "success": false,
  "error": "Wallet not found for provider/username"
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
- Insufficient SOL for transaction fees
- Insufficient SOL for initial buy
- Account rent requirements not met

---

## Environment Variables Reference

| Variable | Description |
|----------|-------------|
| `BAGS_JWT_TOKEN` | JWT token for Agent API |
| `BAGS_API_KEY` | API key for Public API |
| `BAGS_WALLET` | Your wallet address |
| `BAGS_TOKEN_NAME` | Token name |
| `BAGS_TOKEN_SYMBOL` | Token symbol |
| `BAGS_TOKEN_DESC` | Token description |
| `BAGS_IMAGE_URL` | Token image URL |
| `BAGS_TOKEN_MINT` | Generated token mint address |
| `BAGS_METADATA_URL` | IPFS metadata URL |
| `BAGS_CONFIG_KEY` | Fee share config key |
| `BAGS_CONFIG_RESPONSE` | Config creation response |
| `BAGS_CONFIG_TXS` | Config transactions array |
| `BAGS_LAUNCH_RESPONSE` | Launch transaction response |
| `BAGS_LAUNCH_TX` | Unsigned launch transaction |
| `BAGS_INITIAL_BUY` | Initial buy amount (lamports) |
| `BAGS_CREATOR_BPS` | Creator's fee share (BPS) |
| `BAGS_PRIVATE_KEY` | Temporary private key (clear after use!) |
| `BAGS_SIGNED_TX` | Signed transaction (base64) |
| `BAGS_SIGNATURE` | Transaction signature |
| `BAGS_PROVIDER` | Social provider for wallet lookup |
| `BAGS_USERNAME` | Username for wallet lookup |

---

## Next Steps

- **Understand the philosophy** → See [CULTURE.md](https://bags.fm/culture.md) — why launching matters
- **Claim fees** → See [FEES.md](https://bags.fm/fees.md)
- **Trade tokens** → See [TRADING.md](https://bags.fm/trading.md)
- **Monitor activity** → See [HEARTBEAT.md](https://bags.fm/heartbeat.md)
