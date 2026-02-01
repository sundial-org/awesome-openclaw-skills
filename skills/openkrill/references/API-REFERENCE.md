# x402 API Reference

Complete API documentation for the x402 payments skill.

## thirdweb x402 API

### fetchWithPayment

Wrap any API call with automatic x402 payment handling.

**Endpoint:** `POST https://api.thirdweb.com/v1/payments/x402/fetch`

#### Request

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| `x-secret-key` | Yes | thirdweb project secret key |
| `Content-Type` | Yes | `application/json` |

**Query Parameters:**
| Parameter | Required | Type | Description |
|-----------|----------|------|-------------|
| `url` | Yes | string | Target API URL to call |
| `method` | Yes | string | HTTP method (GET, POST, PUT, DELETE) |
| `from` | No | string | Wallet address for payment (uses project default if omitted) |
| `maxValue` | No | string | Maximum payment amount in wei |
| `asset` | No | string | Payment token address (defaults to USDC) |
| `chainId` | No | string | Chain ID (e.g., "eip155:8453" for Base) |

**Body:** JSON payload to pass through to the target API

#### Response

**Success (200):**
```json
{
  "message": "Returns the final result from the API call"
}
```

**Errors:**
| Status | Description |
|--------|-------------|
| 400 | Bad request - invalid URL or parameters |
| 401 | Unauthorized - invalid or missing secret key |
| 402 | Payment required - insufficient balance |
| 500 | Server error |

#### Example

```bash
curl -X POST "https://api.thirdweb.com/v1/payments/x402/fetch?url=https://api.browserbase.com/v1/sessions&method=POST" \
  -H "Content-Type: application/json" \
  -H "x-secret-key: YOUR_SECRET_KEY" \
  -d '{"browserSettings": {"viewport": {"width": 1920, "height": 1080}}}'
```

---

### Server Wallets

#### Create/Retrieve Wallet

**Endpoint:** `POST https://api.thirdweb.com/v1/wallets/server`

**Headers:**
| Header | Required | Description |
|--------|----------|-------------|
| `x-secret-key` | Yes | thirdweb project secret key |
| `Content-Type` | Yes | `application/json` |

**Body:**
```json
{
  "identifier": "unique-wallet-identifier"
}
```

**Response:**
```json
{
  "result": {
    "address": "0x...",
    "userId": "...",
    "createdAt": "2024-01-01T00:00:00.000Z",
    "profiles": [
      {
        "type": "server",
        "identifier": "unique-wallet-identifier"
      }
    ]
  }
}
```

#### List Wallets

**Endpoint:** `GET https://api.thirdweb.com/v1/wallets/server`

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | number | 50 | Number of wallets to return |
| `page` | number | 1 | Page number |

**Response:**
```json
{
  "result": {
    "pagination": {
      "hasMore": false,
      "limit": 50,
      "page": 1
    },
    "wallets": [
      {
        "address": "0x...",
        "createdAt": "2024-01-01T00:00:00.000Z",
        "profiles": [...]
      }
    ]
  }
}
```

---

## x402 Protocol

### How It Works

1. Client makes request to x402-compatible API
2. API returns `402 Payment Required` with payment requirements:
   ```
   HTTP/1.1 402 Payment Required
   X-Payment-Address: 0x...
   X-Payment-Amount: 1000000
   X-Payment-Token: 0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913
   X-Payment-Chain: 8453
   ```
3. Client signs payment authorization using ERC-2612 or ERC-3009
4. Client retries request with payment header:
   ```
   X-PAYMENT: <signed-payment-data>
   ```
5. API verifies and settles payment on-chain
6. API returns requested resource

### Payment Headers

**Request Headers:**
| Header | Description |
|--------|-------------|
| `X-PAYMENT` | Signed payment authorization |
| `PAYMENT-SIGNATURE` | Alternative header name |

**Response Headers (402):**
| Header | Description |
|--------|-------------|
| `X-Payment-Address` | Recipient wallet address |
| `X-Payment-Amount` | Payment amount in token's smallest unit |
| `X-Payment-Token` | Payment token contract address |
| `X-Payment-Chain` | Chain ID for payment |

---

## Supported Chains

| Chain | Chain ID | USDC Address | Notes |
|-------|----------|--------------|-------|
| Base | 8453 | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` | Recommended |
| Base Sepolia | 84532 | `0x036CbD53842c5426634e7929541eC2318f3dCF7e` | Testnet |
| Arbitrum | 42161 | `0xaf88d065e77c8cC2239327C5EDb3A432268e5831` | Alternative |
| Ethereum | 1 | `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48` | Higher fees |

---

## TypeScript SDK

If using thirdweb SDK directly:

```typescript
import { createThirdwebClient } from "thirdweb";
import { facilitator, settlePayment } from "thirdweb/x402";

const client = createThirdwebClient({ 
  secretKey: process.env.THIRDWEB_SECRET_KEY 
});

// For server-side x402 facilitation
const thirdwebX402Facilitator = facilitator({
  client,
  serverWalletAddress: "0xYourWalletAddress",
});
```

---

## Error Codes

| Code | Name | Description | Solution |
|------|------|-------------|----------|
| 400 | Bad Request | Invalid parameters | Check URL and method |
| 401 | Unauthorized | Invalid API key | Verify THIRDWEB_SECRET_KEY |
| 402 | Payment Required | Payment needed or failed | Fund wallet with USDC |
| 403 | Forbidden | Access denied | Check permissions |
| 404 | Not Found | Endpoint not found | Verify URL |
| 429 | Rate Limited | Too many requests | Add delay between requests |
| 500 | Server Error | Internal error | Retry or contact support |

---

## Rate Limits

- Default: 100 requests per minute
- With payment: Limits may vary by service
- Retry with exponential backoff on 429 errors

---

## x402 Bazaar Discovery API

The Bazaar is a machine-readable catalog for discovering x402-compatible API endpoints.

### Discovery Endpoint

**Endpoint:** `GET {facilitator_url}/discovery/resources`

**Available Facilitators:**
| Facilitator | URL |
|-------------|-----|
| Default | `https://x402.org/facilitator` |
| CDP (Coinbase) | `https://api.cdp.coinbase.com/platform/v2/x402` |

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | - | Filter by protocol type (e.g., `"http"`) |
| `limit` | number | 20 | Number of resources to return (max: 100) |
| `offset` | number | 0 | Offset for pagination |

#### Response Schema

```json
{
  "x402Version": 2,
  "items": [
    {
      "resource": "https://api.example.com/endpoint",
      "type": "http",
      "x402Version": 1,
      "accepts": [
        {
          "scheme": "exact",
          "network": "eip155:8453",
          "amount": "1000",
          "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          "payTo": "0x..."
        }
      ],
      "lastUpdated": "2024-01-15T12:30:00.000Z",
      "metadata": {
        "description": "Service description",
        "mimeType": "application/json",
        "input": { ... },
        "output": { ... }
      }
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 42
  }
}
```

#### Discovered Resource Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `resource` | string | Yes | The resource URL being monetized |
| `type` | string | Yes | Resource type (currently `"http"`) |
| `x402Version` | number | Yes | Protocol version supported |
| `accepts` | array | Yes | Array of PaymentRequirements |
| `lastUpdated` | string | Yes | ISO 8601 timestamp |
| `metadata` | object | No | Additional metadata (description, schemas) |

#### Payment Option Fields

| Field | Type | Description |
|-------|------|-------------|
| `scheme` | string | Payment scheme (e.g., `"exact"`) |
| `network` | string | Blockchain network (e.g., `"eip155:8453"` for Base) |
| `amount` | string | Payment amount in smallest unit |
| `asset` | string | Token contract address |
| `payTo` | string | Recipient wallet address |

#### Example

```bash
# Query the Bazaar for HTTP services
curl -s "https://x402.org/facilitator/discovery/resources?type=http&limit=20"

# Using CDP facilitator
curl -s "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?type=http&limit=20"
```

---

## Resources

- [x402 Protocol Specification](https://x402.org)
- [x402 Bazaar Documentation](https://docs.cdp.coinbase.com/x402/bazaar)
- [thirdweb Documentation](https://portal.thirdweb.com/x402)
- [thirdweb Playground](https://playground.thirdweb.com/x402)
- [Agent Skills Specification](https://agentskills.io/specification)
