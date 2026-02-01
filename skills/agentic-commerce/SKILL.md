---
name: purch-api
description: |
  AI-powered shopping API for product search and crypto checkout. Use this skill when:
  - Searching for products from Amazon and Shopify
  - Building shopping assistants or product recommendation features
  - Creating purchase orders with crypto (USDC on Solana or Base)
  - Integrating e-commerce checkout into applications
  - Signing and submitting blockchain transactions for purchases
---

# Purch Public API

Base URL: `https://api.purch.xyz`

## Rate Limits

60 requests/minute per IP. Headers in every response:
- `X-RateLimit-Limit`: Max requests per window
- `X-RateLimit-Remaining`: Requests left
- `X-RateLimit-Reset`: Seconds until reset

## Endpoints

### GET /search - Structured Product Search

Query products with filters.

```bash
curl "https://api.purch.xyz/search?q=headphones&priceMax=100"
```

**Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| q | string | Yes | Search query |
| priceMin | number | No | Minimum price |
| priceMax | number | No | Maximum price |
| brand | string | No | Filter by brand |
| page | number | No | Page number (default: 1) |

**Response:**
```json
{
  "products": [
    {
      "id": "B0CXYZ1234",
      "title": "Sony WH-1000XM5",
      "price": 348.00,
      "currency": "USD",
      "rating": 4.8,
      "reviewCount": 15420,
      "imageUrl": "https://...",
      "productUrl": "https://amazon.com/dp/B0CXYZ1234",
      "source": "amazon"
    }
  ],
  "totalResults": 20,
  "page": 1,
  "hasMore": true
}
```

### POST /shop - AI Shopping Assistant

Natural language product search. Returns 20+ products from both Amazon and Shopify.

```bash
curl -X POST "https://api.purch.xyz/shop" \
  -H "Content-Type: application/json" \
  -d '{"message": "comfortable running shoes under $100"}'
```

**Request Body:**
```json
{
  "message": "comfortable running shoes under $100",
  "context": {
    "priceRange": { "min": 0, "max": 100 },
    "preferences": ["comfortable", "breathable"]
  }
}
```

**Response:**
```json
{
  "reply": "Found 22 running shoes. Top pick: Nike Revolution 6 at $65...",
  "products": [
    {
      "asin": "B09XYZ123",
      "title": "Nike Revolution 6",
      "price": 65.00,
      "currency": "USD",
      "rating": 4.5,
      "reviewCount": 8420,
      "imageUrl": "https://...",
      "productUrl": "https://amazon.com/dp/B09XYZ123",
      "source": "amazon"
    },
    {
      "asin": "gid://shopify/p/abc123",
      "title": "Allbirds Tree Runners",
      "price": 98.00,
      "source": "shopify",
      "productUrl": "https://allbirds.com/products/tree-runners",
      "vendor": "Allbirds"
    }
  ]
}
```

### POST /buy - Create Purchase Order

Create an order and get a transaction to sign. **Chain is auto-detected from wallet format:**
- Solana wallet (base58): `7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU`
- Base/EVM wallet (0x): `0x1234567890abcdef1234567890abcdef12345678`

**Amazon Products (Solana)**:
```bash
curl -X POST "https://api.purch.xyz/buy" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0CXYZ1234",
    "email": "buyer@example.com",
    "walletAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "shippingAddress": {
      "name": "John Doe",
      "line1": "123 Main St",
      "line2": "Apt 4B",
      "city": "New York",
      "state": "NY",
      "postalCode": "10001",
      "country": "US",
      "phone": "+1-555-123-4567"
    }
  }'
```

**Amazon Products (Base)**:
```bash
curl -X POST "https://api.purch.xyz/buy" \
  -H "Content-Type: application/json" \
  -d '{
    "asin": "B0CXYZ1234",
    "email": "buyer@example.com",
    "walletAddress": "0x1234567890abcdef1234567890abcdef12345678",
    "shippingAddress": {
      "name": "John Doe",
      "line1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postalCode": "10001",
      "country": "US"
    }
  }'
```

**Shopify Products** - Use `productUrl` AND `variantId`:
```bash
curl -X POST "https://api.purch.xyz/buy" \
  -H "Content-Type: application/json" \
  -d '{
    "productUrl": "https://store.com/products/item-name",
    "variantId": "41913945718867",
    "email": "buyer@example.com",
    "walletAddress": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
    "shippingAddress": {
      "name": "John Doe",
      "line1": "123 Main St",
      "city": "New York",
      "state": "NY",
      "postalCode": "10001",
      "country": "US"
    }
  }'
```

**Response:**
```json
{
  "orderId": "550e8400-e29b-41d4-a716-446655440000",
  "status": "awaiting-payment",
  "serializedTransaction": "NwbtPCP62oXk5fmSrgT...",
  "product": {
    "title": "Sony WH-1000XM5",
    "imageUrl": "https://...",
    "price": { "amount": "348.00", "currency": "usdc" }
  },
  "totalPrice": { "amount": "348.00", "currency": "usdc" },
  "checkoutUrl": "https://www.crossmint.com/checkout/550e8400..."
}
```

## CLI Scripts

This skill includes ready-to-use CLI scripts for all endpoints. Available in Python and TypeScript/Bun.

**Dependencies (Solana):**
```bash
# Python
pip install solana solders base58

# TypeScript/Bun
bun add @solana/web3.js bs58
```

**Dependencies (Base/EVM):**
```bash
# TypeScript/Bun
bun add viem
```

### Search Products

```bash
# Python
python scripts/search.py "wireless headphones" --price-max 100
python scripts/search.py "running shoes" --brand Nike --page 2

# TypeScript
bun run scripts/search.ts "wireless headphones" --price-max 100
```

### AI Shopping Assistant

```bash
# Python
python scripts/shop.py "comfortable running shoes under $100"

# TypeScript
bun run scripts/shop.ts "wireless headphones with good noise cancellation"
```

### Create Order (without signing)

```bash
# Amazon by ASIN
python scripts/buy.py --asin B0CXYZ1234 --email buyer@example.com \
  --wallet 7xKXtg... --address "John Doe,123 Main St,New York,NY,10001,US"

# Shopify product
bun run scripts/buy.ts --url "https://store.com/products/item" --variant 41913945718867 \
  --email buyer@example.com --wallet 7xKXtg... --address "John Doe,123 Main St,NYC,NY,10001,US"
```

Address format: `Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]`

### Create Order AND Sign Transaction (Solana)

End-to-end purchase flow - creates order and signs/submits the Solana transaction:

```bash
# Python
python scripts/buy_and_sign.py --asin B0CXYZ1234 --email buyer@example.com \
  --wallet 7xKXtg... --private-key 5abc123... \
  --address "John Doe,123 Main St,New York,NY,10001,US"

# TypeScript
bun run scripts/buy_and_sign.ts --url "https://store.com/products/item" --variant 41913945718867 \
  --email buyer@example.com --wallet 7xKXtg... --private-key 5abc123... \
  --address "John Doe,123 Main St,NYC,NY,10001,US"
```

### Create Order AND Sign Transaction (Base)

End-to-end purchase flow using Base/EVM wallet:

```bash
bun run scripts/buy_and_sign_base.ts --asin B0CXYZ1234 --email buyer@example.com \
  --wallet 0x1234567890abcdef1234567890abcdef12345678 \
  --private-key 0xabc123... \
  --address "John Doe,123 Main St,New York,NY,10001,US"
```

### Sign Transaction Only (Solana)

If you already have a `serializedTransaction` from the `/buy` endpoint:

```bash
# Python
python scripts/sign_transaction.py "<serialized_tx>" "<private_key_base58>"

# TypeScript
bun run scripts/sign_transaction.ts "<serialized_tx>" "<private_key_base58>"
```

### Sign Transaction Only (Base)

```bash
bun run scripts/sign_transaction_base.ts "<serialized_tx_hex>" "<private_key_hex>"
```

**Output (Solana):**
```
✅ Transaction successful!
   Signature: 5UfgJ3vN...
   Explorer:  https://solscan.io/tx/5UfgJ3vN...
```

**Output (Base):**
```
✅ Transaction successful!
   Hash:     0x1234...
   Explorer: https://basescan.org/tx/0x1234...
```

## Signing Transactions Programmatically

For custom integrations without using the bundled scripts:

### JavaScript/TypeScript

```typescript
import { Connection, Transaction, clusterApiUrl } from "@solana/web3.js";
import bs58 from "bs58";

async function signAndSendTransaction(
  serializedTransaction: string,
  wallet: { signTransaction: (tx: Transaction) => Promise<Transaction> }
) {
  // Decode the base58 transaction
  const transactionBuffer = bs58.decode(serializedTransaction);
  const transaction = Transaction.from(transactionBuffer);

  // Sign with user's wallet (e.g., Phantom, Solflare)
  const signedTransaction = await wallet.signTransaction(transaction);

  // Send to Solana network
  const connection = new Connection(clusterApiUrl("mainnet-beta"));
  const signature = await connection.sendRawTransaction(
    signedTransaction.serialize()
  );

  // Confirm transaction
  await connection.confirmTransaction(signature, "confirmed");

  return signature;
}
```

### React with Wallet Adapter

```typescript
import { useWallet, useConnection } from "@solana/wallet-adapter-react";
import { Transaction } from "@solana/web3.js";
import bs58 from "bs58";

function CheckoutButton({ serializedTransaction }: { serializedTransaction: string }) {
  const { signTransaction, publicKey } = useWallet();
  const { connection } = useConnection();

  const handlePayment = async () => {
    if (!signTransaction || !publicKey) {
      throw new Error("Wallet not connected");
    }

    // Decode and sign
    const tx = Transaction.from(bs58.decode(serializedTransaction));
    const signed = await signTransaction(tx);

    // Send and confirm
    const sig = await connection.sendRawTransaction(signed.serialize());
    await connection.confirmTransaction(sig, "confirmed");

    console.log("Payment complete:", sig);
  };

  return <button onClick={handlePayment}>Pay with USDC</button>;
}
```

### Python (with solana-py)

```python
import base58
from solana.rpc.api import Client
from solana.transaction import Transaction
from solders.keypair import Keypair

def sign_and_send(serialized_tx: str, keypair: Keypair) -> str:
    # Decode base58 transaction
    tx_bytes = base58.b58decode(serialized_tx)
    transaction = Transaction.deserialize(tx_bytes)

    # Sign
    transaction.sign(keypair)

    # Send
    client = Client("https://api.mainnet-beta.solana.com")
    result = client.send_transaction(transaction)

    return result.value  # transaction signature
```

## Signing Base/EVM Transactions

For Base chain orders, the `serializedTransaction` is an EVM transaction that needs to be signed with an EVM wallet.

### TypeScript with viem

```typescript
import { createWalletClient, http, parseTransaction } from "viem";
import { base } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";

async function signAndSendBaseTransaction(
  serializedTransaction: string,
  privateKey: `0x${string}`
) {
  const account = privateKeyToAccount(privateKey);

  const client = createWalletClient({
    account,
    chain: base,
    transport: http(),
  });

  // Parse and send the serialized transaction
  const tx = parseTransaction(serializedTransaction as `0x${string}`);
  const hash = await client.sendTransaction(tx);

  console.log("Transaction hash:", hash);
  console.log("Explorer: https://basescan.org/tx/" + hash);

  return hash;
}
```

### React with wagmi

```typescript
import { useSendTransaction } from "wagmi";
import { parseTransaction } from "viem";

function CheckoutButton({ serializedTransaction }: { serializedTransaction: string }) {
  const { sendTransaction } = useSendTransaction();

  const handlePayment = async () => {
    const tx = parseTransaction(serializedTransaction as `0x${string}`);
    sendTransaction(tx);
  };

  return <button onClick={handlePayment}>Pay with USDC on Base</button>;
}
```

## Complete Checkout Flow (Solana)

```typescript
// 1. Search for products
const searchResponse = await fetch("https://api.purch.xyz/shop", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "wireless headphones under $100" })
});
const { products, reply } = await searchResponse.json();

// 2. User selects a product, create order (Solana wallet)
const orderResponse = await fetch("https://api.purch.xyz/buy", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    asin: products[0].asin,
    email: "buyer@example.com",
    walletAddress: wallet.publicKey.toBase58(), // Solana address
    shippingAddress: {
      name: "John Doe",
      line1: "123 Main St",
      city: "New York",
      state: "NY",
      postalCode: "10001",
      country: "US"
    }
  })
});
const { orderId, serializedTransaction, checkoutUrl } = await orderResponse.json();

// 3. Sign and send Solana transaction
const tx = Transaction.from(bs58.decode(serializedTransaction));
const signed = await wallet.signTransaction(tx);
const signature = await connection.sendRawTransaction(signed.serialize());
await connection.confirmTransaction(signature, "confirmed");

console.log(`Order ${orderId} paid. Tx: ${signature}`);
```

## Complete Checkout Flow (Base)

```typescript
import { parseTransaction } from "viem";

// 1. Search for products
const searchResponse = await fetch("https://api.purch.xyz/shop", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ message: "wireless headphones under $100" })
});
const { products } = await searchResponse.json();

// 2. User selects a product, create order (EVM wallet)
const orderResponse = await fetch("https://api.purch.xyz/buy", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    asin: products[0].asin,
    email: "buyer@example.com",
    walletAddress: "0x1234...", // Base/EVM address - chain auto-detected
    shippingAddress: {
      name: "John Doe",
      line1: "123 Main St",
      city: "New York",
      state: "NY",
      postalCode: "10001",
      country: "US"
    }
  })
});
const { orderId, serializedTransaction } = await orderResponse.json();

// 3. Sign and send Base transaction
const tx = parseTransaction(serializedTransaction as `0x${string}`);
const hash = await walletClient.sendTransaction(tx);

console.log(`Order ${orderId} paid. Tx: ${hash}`);
```

## Fallback: Browser Checkout

If wallet signing fails or isn't available, redirect to `checkoutUrl` for browser-based payment:

```typescript
if (!wallet.connected) {
  window.open(checkoutUrl, "_blank");
}
```

## Error Handling

All endpoints return errors as:
```json
{
  "code": "VALIDATION_ERROR",
  "message": "Invalid email format",
  "details": { "field": "email" }
}
```

Common error codes:
- `VALIDATION_ERROR` (400) - Invalid request parameters
- `NOT_FOUND` (404) - Product not found
- `RATE_LIMITED` (429) - Too many requests
- `INTERNAL_ERROR` (500) - Server error
