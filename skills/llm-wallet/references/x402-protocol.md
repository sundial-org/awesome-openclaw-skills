# x402 Protocol Overview

## What is x402?

x402 is an open payment protocol developed by Coinbase that enables instant, automatic cryptocurrency micropayments directly over HTTP. It uses the HTTP 402 Payment Required status code to create a universal payment mechanism for the internet.

## How It Works

### Payment Flow

1. **Client Request (No Payment)**
   ```
   GET /api/weather?location=London
   ```

2. **Server Response: 402 Payment Required**
   ```json
   {
     "x402Version": 1,
     "error": "X-PAYMENT header is required",
     "accepts": [{
       "scheme": "exact",
       "network": "polygon-amoy",
       "maxAmountRequired": "1000",  // 0.001 USDC
       "payTo": "0xCA3953e536bDA86D1F152eEfA8aC7b0C82b6eC00",
       "resource": "https://api.example.com/weather"
     }]
   }
   ```

3. **Client Creates Signed Payment**
   - Creates EIP-712 signed message with payment authorization
   - Signs with wallet private key
   - Encodes as X-PAYMENT header

4. **Client Retries with Payment**
   ```
   GET /api/weather?location=London
   X-PAYMENT: <base64-encoded-signed-payment>
   ```

5. **Server Verifies & Settles**
   - Verifies payment with facilitator
   - Executes on-chain USDC transfer
   - Returns data + transaction receipt

## Key Components

### Facilitator
A trusted service that:
- Verifies payment authorizations
- Executes on-chain settlements
- Prevents double-spending
- Tracks nonces

**Facilitator URLs:**
- Testnet: https://x402-amoy.polygon.technology
- Mainnet: https://x402.polygon.technology

### Payment Token: USDC
- Stablecoin pegged to USD
- 6 decimal places (1 USDC = 1,000,000 atomic units)
- Fast, cheap transactions on Polygon Layer 2

### Networks
- **Polygon Amoy (Testnet)**: Chain ID 80002, safe for testing
- **Polygon (Mainnet)**: Chain ID 137, real money

## Payment Authorization (EIP-712)

The signed payment contains:
```typescript
{
  from: '0x742d...',        // Buyer wallet
  to: '0xCA39...',          // Seller wallet
  value: '1000',            // Amount (0.001 USDC)
  validAfter: 1738367445,   // Start timestamp
  validBefore: 1738367505,  // End timestamp (~60s)
  nonce: 'uuid',            // Prevents replay
  signature: { v, r, s }    // Cryptographic signature
}
```

## Security Model

- Payment is an **authorization**, not immediate transfer
- Two-phase: **Verify** (fast, off-chain) → **Settle** (on-chain)
- Time-limited (typically 60 seconds)
- Nonce prevents replay attacks
- Requires facilitator to execute

## Use Cases

1. **Paid APIs** - Pay per request ($0.001 - $1.00)
2. **Content Paywalls** - Unlock articles, data, media
3. **AI Agent Services** - Autonomous payments
4. **Metered Services** - Pay for compute, storage, bandwidth

## Benefits

- **No Accounts** - No registration, API keys, or OAuth
- **True Micropayments** - Economically viable at $0.0001+
- **AI Agent Native** - Perfect for autonomous payments
- **Open Standard** - Built on HTTP, EIP-712, blockchain

## Resources

- Website: https://www.x402.org/
- Docs: https://docs.cdp.coinbase.com/x402/welcome
- GitHub: https://github.com/coinbase/x402
