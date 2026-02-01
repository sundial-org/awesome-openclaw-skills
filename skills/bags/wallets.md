# Bags Wallet Management 💛

List your Solana wallets and export private keys for transaction signing.

**Base URL:** `https://public-api-v2.bags.fm/api/v1/agent/`

---

## Prerequisites

You must be authenticated first. See [AUTH.md](https://bags.fm/auth.md).

Load your credentials:
```bash
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_API_KEY=$(cat ~/.config/bags/credentials.json | jq -r '.api_key')
```

---

## List Your Wallets

Retrieve all Solana wallet addresses associated with your agent account.

```bash
curl -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/list \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\"}"
```

**Response:**
```json
{
  "success": true,
  "response": [
    "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "9aE8nCfL3Gq2kXzPvRtYhNsD4mWjB5cFp7KvUeHoJ2Lx"
  ]
}
```

Save your wallets to credentials:
```bash
BAGS_WALLETS=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/list \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\"}" | jq -r '.response')

# Update credentials file
jq --argjson wallets "$BAGS_WALLETS" '.wallets = $wallets' \
  ~/.config/bags/credentials.json > ~/.config/bags/credentials.json.tmp \
  && mv ~/.config/bags/credentials.json.tmp ~/.config/bags/credentials.json
```

---

## Export Private Key

⚠️ **SECURITY WARNING:** Private keys give full control over your wallet. Handle with extreme care.

```bash
BAGS_WALLET_ADDRESS="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"

curl -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{
    \"token\": \"$BAGS_JWT_TOKEN\",
    \"walletAddress\": \"$BAGS_WALLET_ADDRESS\"
  }"
```

**Response:**
```json
{
  "success": true,
  "response": {
    "privateKey": "5Jd7Eu8VMkr9eQaKoH1Nwm..."
  }
}
```

The `privateKey` is Base58 encoded — standard Solana format.

---

## Using Your Private Key

### Option 1: Solana CLI (Recommended for Simple Operations)

Install Solana CLI:
```bash
sh -c "$(curl -sSfL https://release.anza.xyz/stable/install)"
```

Make sure to use the Anza release of the Solana CLI, and read help for the latest features.
```bash
USAGE:
    solana [FLAGS] [OPTIONS] <SUBCOMMAND>

FLAGS:
    -h, --help                           Prints help information
        --no-address-labels              Do not use address labels in the output
        --skip-preflight                 Skip the preflight check when sending transactions
        --skip-seed-phrase-validation    Skip validation of seed phrases. Use this if your phrase does not use the BIP39
                                         official English word list
        --use-quic                       Use QUIC when sending transactions.
        --use-tpu-client                 Use TPU client when sending transactions.
        --use-udp                        Use UDP when sending transactions.
    -V, --version                        Prints version information
    -v, --verbose                        Show additional information
```

Create a keypair file from your private key:
```bash
# Export the key (temporary use only)
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET_ADDRESS\"}" \
  | jq -r '.response.privateKey')

# Convert to keypair file format (JSON array of bytes)
echo "$BAGS_PRIVATE_KEY" | base58 -d | xxd -p | fold -w2 | paste -sd',' | sed 's/^/[/;s/$/]/' > ~/.config/bags/keypair.json

# Set permissions
chmod 600 ~/.config/bags/keypair.json

# Clear from memory immediately
unset BAGS_PRIVATE_KEY

# Verify it works
solana address -k ~/.config/bags/keypair.json
```

Use for transfers:
```bash
solana transfer <RECIPIENT> <AMOUNT> --keypair ~/.config/bags/keypair.json
```

Check balance:
```bash
solana balance --keypair ~/.config/bags/keypair.json
```

### Option 2: Programmatic Signing (For Complex Transactions)

For signing claim transactions or other complex operations, you'll need to sign programmatically.

**Using Node.js:**

Create `sign-transaction.js`:
```javascript
// sign-transaction.js
const { Keypair, VersionedTransaction } = require('@solana/web3.js');
const bs58 = require('bs58');

const privateKeyBase58 = process.argv[2];
const transactionBase64 = process.argv[3];

const keypair = Keypair.fromSecretKey(bs58.decode(privateKeyBase58));
const transaction = VersionedTransaction.deserialize(
  Buffer.from(transactionBase64, 'base64')
);
transaction.sign([keypair]);

console.log(Buffer.from(transaction.serialize()).toString('base64'));
```

Run:
```bash
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET_ADDRESS\"}" \
  | jq -r '.response.privateKey')

BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_UNSIGNED_TX")

# Clear private key immediately
unset BAGS_PRIVATE_KEY
```

**Using Python:**

Create `sign_transaction.py`:
```python
# sign_transaction.py
import sys
import base64
import base58
from solders.keypair import Keypair
from solders.transaction import VersionedTransaction

private_key_b58 = sys.argv[1]
tx_base64 = sys.argv[2]

keypair = Keypair.from_bytes(base58.b58decode(private_key_b58))
tx = VersionedTransaction.from_bytes(base64.b64decode(tx_base64))
tx.sign([keypair])

print(base64.b64encode(bytes(tx)).decode())
```

### Option 3: Submit Signed Transaction to RPC

After signing, submit to Solana:
```bash
curl -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"sendTransaction\",
    \"params\": [
      \"$BAGS_SIGNED_TX\",
      {\"encoding\": \"base64\", \"skipPreflight\": false}
    ]
  }"
```

---

## Check Wallet Balance

### Using Solana RPC (Recommended)

```bash
BAGS_WALLET_ADDRESS="7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU"

curl -s -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{
    \"jsonrpc\": \"2.0\",
    \"id\": 1,
    \"method\": \"getBalance\",
    \"params\": [\"$BAGS_WALLET_ADDRESS\"]
  }"
```

**Response:**
```json
{
  "jsonrpc": "2.0",
  "result": {
    "context": {"slot": 123456789},
    "value": 1500000000
  },
  "id": 1
}
```

Note: `value` is in lamports (1 SOL = 1,000,000,000 lamports).

### Convert to SOL

```bash
BAGS_BALANCE_LAMPORTS=$(curl -s -X POST https://api.mainnet-beta.solana.com \
  -H "Content-Type: application/json" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"getBalance\",\"params\":[\"$BAGS_WALLET_ADDRESS\"]}" \
  | jq '.result.value')

BAGS_BALANCE_SOL=$(echo "scale=4; $BAGS_BALANCE_LAMPORTS / 1000000000" | bc)
echo "Balance: $BAGS_BALANCE_SOL SOL"
```

### Using Solana CLI (Recommended if you are on CLI)

```bash
solana balance $BAGS_WALLET_ADDRESS
```

---

## Security Best Practices

### ✅ DO:
- Export keys only when needed for signing
- Delete keypair files after use: `rm ~/.config/bags/keypair.json`
- Use `chmod 600` on any file containing keys
- Clear private keys from environment: `unset BAGS_PRIVATE_KEY`
- Verify transaction details before signing
- Keep JWT token and API key separate from private keys

### ❌ DON'T:
- Log private keys to console or files
- Store private keys in credentials.json
- Share private keys with anyone or any service
- Commit keys to version control
- Keep keypair files around longer than necessary
- Use private keys in scripts without clearing them after

---

## Error Handling

**Invalid token (400):**
```json
{
  "success": false,
  "response": "Invalid token"
}
```
→ Re-authenticate via [AUTH.md](https://bags.fm/auth.md)

**Wallet not found (400):**
```json
{
  "success": false,
  "response": "Wallet not found for this agent"
}
```
→ Check wallet address is correct and belongs to your account

**Rate limited (429):**
```json
{
  "success": false,
  "response": "Too many requests. Please try again later."
}
```
→ Wait and retry with exponential backoff

---

## Complete Wallet Status Script

```bash
#!/bin/bash
# bags-wallet-status.sh - Check all wallet balances

set -e

# Load credentials
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')

echo "💛 Bags Wallet Status"
echo "====================="

# Get wallets
BAGS_WALLETS_RESPONSE=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/list \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\"}")

if ! echo "$BAGS_WALLETS_RESPONSE" | jq -e '.success == true' > /dev/null; then
  echo "❌ Failed to fetch wallets: $(echo "$BAGS_WALLETS_RESPONSE" | jq -r '.response')"
  exit 1
fi

BAGS_WALLETS=$(echo "$BAGS_WALLETS_RESPONSE" | jq -r '.response[]')
BAGS_TOTAL_LAMPORTS=0

for BAGS_WALLET in $BAGS_WALLETS; do
  BAGS_BALANCE=$(curl -s -X POST https://api.mainnet-beta.solana.com \
    -H "Content-Type: application/json" \
    -d "{
      \"jsonrpc\": \"2.0\",
      \"id\": 1,
      \"method\": \"getBalance\",
      \"params\": [\"$BAGS_WALLET\"]
    }" | jq -r '.result.value')
  
  BAGS_SOL=$(echo "scale=4; $BAGS_BALANCE / 1000000000" | bc)
  BAGS_TOTAL_LAMPORTS=$((BAGS_TOTAL_LAMPORTS + BAGS_BALANCE))
  
  echo ""
  echo "📍 Wallet: $BAGS_WALLET"
  echo "   Balance: $BAGS_SOL SOL"
done

BAGS_TOTAL_SOL=$(echo "scale=4; $BAGS_TOTAL_LAMPORTS / 1000000000" | bc)

echo ""
echo "====================="
echo "💰 Total: $BAGS_TOTAL_SOL SOL"
```

---

## Sign and Submit Transaction Script

```bash
#!/bin/bash
# bags-sign-submit.sh - Sign and submit a transaction
# Usage: ./bags-sign-submit.sh <unsigned_tx_base64>

set -e

BAGS_UNSIGNED_TX=$1

if [ -z "$BAGS_UNSIGNED_TX" ]; then
  echo "Usage: $0 <unsigned_tx_base64>"
  exit 1
fi

# Load credentials
BAGS_JWT_TOKEN=$(cat ~/.config/bags/credentials.json | jq -r '.jwt_token')
BAGS_WALLET_ADDRESS=$(cat ~/.config/bags/credentials.json | jq -r '.wallets[0]')

echo "🔐 Bags Transaction Signer"
echo "=========================="

# Export private key (temporary)
echo "📤 Exporting private key..."
BAGS_PRIVATE_KEY=$(curl -s -X POST https://public-api-v2.bags.fm/api/v1/agent/wallet/export \
  -H "Content-Type: application/json" \
  -d "{\"token\": \"$BAGS_JWT_TOKEN\", \"walletAddress\": \"$BAGS_WALLET_ADDRESS\"}" \
  | jq -r '.response.privateKey')

if [ -z "$BAGS_PRIVATE_KEY" ] || [ "$BAGS_PRIVATE_KEY" = "null" ]; then
  echo "❌ Failed to export private key"
  exit 1
fi

# Sign transaction
echo "✍️  Signing transaction..."
BAGS_SIGNED_TX=$(node sign-transaction.js "$BAGS_PRIVATE_KEY" "$BAGS_UNSIGNED_TX")

# Clear private key immediately
unset BAGS_PRIVATE_KEY

if [ -z "$BAGS_SIGNED_TX" ]; then
  echo "❌ Failed to sign transaction"
  exit 1
fi

# Submit transaction
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
  echo "✅ Transaction submitted!"
  echo "   Signature: $BAGS_SIGNATURE"
  echo "   Explorer: https://solscan.io/tx/$BAGS_SIGNATURE"
else
  echo ""
  echo "❌ Transaction failed: $BAGS_ERROR"
  exit 1
fi
```

---

## Environment Variables Reference

All Bags wallet scripts use these prefixed variables:

| Variable | Description |
|----------|-------------|
| `BAGS_JWT_TOKEN` | JWT token for Agent API authentication |
| `BAGS_API_KEY` | API key for Public API authentication |
| `BAGS_WALLET_ADDRESS` | Current wallet address being used |
| `BAGS_WALLETS` | Array of all wallet addresses |
| `BAGS_PRIVATE_KEY` | Temporary private key (clear after use!) |
| `BAGS_UNSIGNED_TX` | Unsigned transaction (base64) |
| `BAGS_SIGNED_TX` | Signed transaction (base64) |
| `BAGS_BALANCE_LAMPORTS` | Wallet balance in lamports |
| `BAGS_BALANCE_SOL` | Wallet balance in SOL |

---

## Next Steps

After managing your wallets, you can:

1. **Check claimable fees** → See [FEES.md](https://bags.fm/fees.md)
2. **Trade tokens** → See [TRADING.md](https://bags.fm/trading.md)
3. **Launch tokens** → See [LAUNCH.md](https://bags.fm/launch.md)
