---
name: openkrill
description: Enable AI agents to make micropayments via x402 protocol. Use when purchasing browser sessions on Browserbase, scraping with Firecrawl, or any x402-compatible API. Handles wallet creation, funding, and automatic payment flows.
license: MIT
compatibility: Requires network access and thirdweb API key (THIRDWEB_SECRET_KEY environment variable)
metadata:
  author: emilankerwiik
  version: "1.2"
  openclaw:
    requires:
      env:
        - THIRDWEB_SECRET_KEY
    primaryEnv: THIRDWEB_SECRET_KEY
---

# OpenKrill - x402 Payments Skill

This skill enables AI agents to autonomously make micropayments using the x402 protocol. It handles wallet management, balance checking, and automatic payment flows when APIs return HTTP 402 Payment Required responses.

## When to Use This Skill

- **When asked "what services can I purchase?" or "what x402 APIs are available?"** - Query the Bazaar first!
- When purchasing browser automation sessions on Browserbase
- When performing web scraping tasks with Firecrawl
- When the agent needs to create an email address for signups or verification
- When interacting with any x402-compatible API
- When the user mentions micropayments, crypto payments, or paying for API access
- When you encounter a 402 Payment Required response
- **When discovering new x402-compatible services** via the Bazaar

> **TIP:** When a user or agent asks what services are available for purchase, always start by querying the Bazaar discovery endpoint. It provides a live, up-to-date catalog of 12,000+ x402-compatible services.

### Quick: Discover Available Services

```bash
# Query the Bazaar to see what's available (no auth required)
curl -s "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?type=http&limit=50"
```

## Prerequisites

Before using this skill, ensure:

1. **THIRDWEB_SECRET_KEY** environment variable is set with a valid thirdweb project secret key
2. The wallet has sufficient USDC balance on Base chain (or the target chain)
3. Network access to thirdweb API endpoints

## IMPORTANT: x402 Endpoint URLs & Service Types

### Two Types of x402 Support

| Type | Description | Example |
|------|-------------|---------|
| **True x402** | Fully keyless - no API keys needed, just pay and use | Browserbase |
| **Hybrid x402** | Requires API key/token + payment header | Firecrawl |

### x402 Endpoint Patterns

| Service | Standard API | x402 Endpoint | Type | Status |
|---------|-------------|---------------|------|--------|
| Browserbase | `api.browserbase.com` | `x402.browserbase.com` | True x402 | ✅ Works |
| Firecrawl | `api.firecrawl.dev/v1/search` | `api.firecrawl.dev/v1/x402/search` | Non-standard | ❌ Broken |

**Discovery tips:**
- Check for `x402.` subdomain (e.g., `x402.browserbase.com`)
- Check for `/x402/` in the path (e.g., `/v1/x402/search`)
- Hit the x402 root URL for endpoint listing (e.g., `curl https://x402.browserbase.com/`)

## Core Workflow

### Step 1: Check or Create Wallet

Use the thirdweb API directly (recommended):

```bash
curl -s -X POST https://api.thirdweb.com/v1/wallets/server \
  -H "Content-Type: application/json" \
  -H "x-secret-key: $THIRDWEB_SECRET_KEY" \
  -d '{"identifier": "x402-agent-wallet"}'
```

The response will include the wallet address. Store this for subsequent operations.

### Step 2: Make Payments with fetchWithPayment

Call the thirdweb x402 fetch API directly:

```bash
# Browserbase - Create browser session
curl -s -X POST "https://api.thirdweb.com/v1/payments/x402/fetch?url=https://x402.browserbase.com/browser/session/create&method=POST" \
  -H "Content-Type: application/json" \
  -H "x-secret-key: $THIRDWEB_SECRET_KEY" \
  -d '{"browserSettings": {"viewport": {"width": 1920, "height": 1080}}}'
```

### Step 3: Handle the Response

**Success:** The API returns the session data directly.

**Insufficient Funds:** If the wallet needs funding, the API returns:

```json
{
  "result": {
    "message": "This endpoint requires 0.002 USDC on chain id 8453...",
    "link": "https://thirdweb.com/pay?chain=8453&receiver=0x...&token=0x..."
  }
}
```

**When you receive a payment link, open it in the user's browser:**

- If browser automation is available (MCP, browser tool, etc.), use it to navigate to the link in a new tab
- Otherwise, display the link prominently and instruct the user to open it manually

This opens thirdweb's payment page where users can fund the wallet.

## API Reference

### fetchWithPayment Endpoint

**URL:** `https://api.thirdweb.com/v1/payments/x402/fetch`

**Method:** POST

**Query Parameters:**
| Parameter | Required | Description |
|-----------|----------|-------------|
| `url` | Yes | Target API URL to call |
| `method` | Yes | HTTP method (GET, POST, etc.) |
| `from` | No | Wallet address for payment (uses default project wallet if omitted) |
| `maxValue` | No | Maximum payment amount in wei |
| `asset` | No | Payment token address (defaults to USDC) |
| `chainId` | No | Chain ID for payment (e.g., "eip155:8453" for Base) |

**Headers:**
- `x-secret-key`: Your thirdweb project secret key (required)
- `Content-Type`: application/json

## Supported x402 Services

### Browserbase

**x402 Endpoint:** `https://x402.browserbase.com`  
**Pricing:** $0.12/hour (paid in USDC on Base)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/browser/session/create` | POST | Create a browser session |
| `/browser/session/:id/status` | GET | Check session status |
| `/browser/session/:id/extend` | POST | Add more time |
| `/browser/session/:id` | DELETE | Terminate session |

```bash
curl -s -X POST "https://api.thirdweb.com/v1/payments/x402/fetch?url=https://x402.browserbase.com/browser/session/create&method=POST" \
  -H "Content-Type: application/json" \
  -H "x-secret-key: $THIRDWEB_SECRET_KEY" \
  -d '{"browserSettings": {"viewport": {"width": 1920, "height": 1080}}}'
```

### Firecrawl (Non-Standard x402 - NOT RECOMMENDED)

**x402 Endpoint:** `https://api.firecrawl.dev/v1/x402/search`  
**Pricing:** $0.01/request  
**Status:** ⚠️ Incomplete implementation - cannot be used with thirdweb

> **WARNING:** Firecrawl's x402 implementation is non-standard and currently unusable for automated agents:
> 
> 1. Returns `401 Unauthorized` instead of `402 Payment Required`
> 2. Doesn't include payment details (payTo address, asset, amount) in response
> 3. Documentation says to use `X-Payment: {{paymentHeader}}` but doesn't explain how to generate it
> 
> **Comparison with proper x402 (Browserbase):**
> - Browserbase: Returns 402 with `x402Version`, `accepts`, `payTo`, `asset` → thirdweb can auto-pay
> - Firecrawl: Returns 401 with just `{"error":"Unauthorized"}` → no payment info provided

| Endpoint | Method | Status |
|----------|--------|--------|
| `/v1/x402/search` | POST | ❌ Non-functional for agents |

**Recommended alternatives:**
1. **Firecrawl MCP** - If available in your environment (uses standard API key)
2. **Browserbase + scraping script** - True x402, fully keyless
3. **Standard Firecrawl API** - With subscription/API key

Reference: [Firecrawl x402 docs](https://docs.firecrawl.dev/x402/search)

### Mail.tm (Disposable Email)

**Base URL:** `https://api.mail.tm`  
**Pricing:** Free (no x402 payment required)

Mail.tm allows agents to create email addresses for signups and receive verification emails.

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/domains` | GET | No | Get available email domains |
| `/accounts` | POST | No | Create an email account |
| `/token` | POST | No | Get authentication token |
| `/messages` | GET | Yes | List all messages |
| `/messages/:id` | GET | Yes | Get full message content |
| `/me` | GET | Yes | Get account info |

#### Create Email Account

```bash
# 1. Get available domain
DOMAIN=$(curl -s https://api.mail.tm/domains | jq -r '.["hydra:member"][0].domain')

# 2. Create account with unique address
curl -s -X POST https://api.mail.tm/accounts \
  -H "Content-Type: application/json" \
  -d '{"address": "agent-'$(date +%s)'@'"$DOMAIN"'", "password": "SecurePass123!"}'
```

#### Get Token and Check Messages

```bash
# Get auth token
TOKEN=$(curl -s -X POST https://api.mail.tm/token \
  -H "Content-Type: application/json" \
  -d '{"address": "YOUR_EMAIL", "password": "YOUR_PASSWORD"}' | jq -r '.token')

# List messages
curl -s https://api.mail.tm/messages -H "Authorization: Bearer $TOKEN"

# Read specific message
curl -s https://api.mail.tm/messages/MESSAGE_ID -H "Authorization: Bearer $TOKEN"
```

**Important:** Store email credentials (address, password, token) for later use. Consider saving to `.agent-emails.json` (gitignored).

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Invalid or missing THIRDWEB_SECRET_KEY | Check environment variable |
| 402 Payment Required | Insufficient balance | Auto-open payment link (see above) |
| 400 Bad Request | Invalid URL or method | Verify request parameters |
| 404 Not Found | Wrong endpoint | Check x402-specific endpoint (e.g., `x402.browserbase.com`) |
| 500 Server Error | thirdweb or target API issue | Retry or check service status |

## Common Mistakes

1. **Using wrong subdomain**: `api.browserbase.com` vs `x402.browserbase.com`
2. **Using wrong path**: `/v1/sessions` vs `/browser/session/create`
3. **Not checking for payment links**: Always parse response for `link` field

## Discovering x402 Endpoints

There are two ways to discover x402-compatible services:

### Method 1: x402 Bazaar (Recommended)

The x402 Bazaar is a machine-readable catalog that helps AI agents discover x402-compatible API endpoints programmatically.

#### Query the Bazaar Discovery Endpoint

```bash
# Using the default facilitator (x402.org)
curl -s "https://x402.org/facilitator/discovery/resources?type=http&limit=20"

# Using CDP facilitator (Coinbase)
curl -s "https://api.cdp.coinbase.com/platform/v2/x402/discovery/resources?type=http&limit=20"
```

#### Using the Discovery Script

```bash
# Discover available services
npx ts-node scripts/discover-services.ts

# With pagination
npx ts-node scripts/discover-services.ts --limit 50 --offset 0

# Use CDP facilitator
npx ts-node scripts/discover-services.ts --facilitator "https://api.cdp.coinbase.com/platform/v2/x402"

# Output as JSON for programmatic use
npx ts-node scripts/discover-services.ts --json
```

#### Response Format

```json
{
  "x402Version": 2,
  "items": [
    {
      "resource": "https://x402.browserbase.com/browser/session/create",
      "type": "http",
      "x402Version": 1,
      "accepts": [
        {
          "scheme": "exact",
          "network": "eip155:8453",
          "amount": "2000",
          "asset": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
          "payTo": "0x..."
        }
      ],
      "lastUpdated": "2024-01-15T12:30:00.000Z",
      "metadata": {
        "description": "Create a browser session",
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

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `type` | string | - | Filter by protocol type (e.g., `"http"`) |
| `limit` | number | 20 | Number of resources to return (max: 100) |
| `offset` | number | 0 | Offset for pagination |

### Method 2: Manual Discovery

When encountering a new service that might support x402:

#### 1. Check for x402 Subdomain

```bash
# Try the x402 subdomain - often has an info page
curl -s https://x402.SERVICE.com/

# Example: Browserbase lists all endpoints at root
curl -s https://x402.browserbase.com/
```

#### 2. Check for /x402/ Path Prefix

```bash
# Some services use path prefix instead of subdomain
curl -s -I https://api.SERVICE.com/v1/x402/endpoint
```

#### 3. Test for 402 Response

```bash
# A true x402 endpoint returns 402 Payment Required (not 401)
curl -s -i -X POST https://x402.SERVICE.com/endpoint \
  -H "Content-Type: application/json" \
  -d '{}' 2>&1 | head -5
```

**Expected for true x402:**
```
HTTP/2 402
x-payment-required: ...
```

**If you see 401 Unauthorized:** The service uses hybrid x402 (needs API key + payment).

#### 4. Check Service Documentation

Look for x402/payments documentation:
- `docs.SERVICE.com/x402/`
- `docs.SERVICE.com/payments/`
- Search for "x402" or "402" in their docs

## Additional Resources

- See [references/API-REFERENCE.md](references/API-REFERENCE.md) for complete API documentation
- See [references/SERVICES.md](references/SERVICES.md) for x402-compatible service examples

## Links

- [x402 Protocol](https://x402.org)
- [x402 Bazaar Discovery](https://docs.cdp.coinbase.com/x402/bazaar)
- [thirdweb x402 Documentation](https://portal.thirdweb.com/x402)
- [Browserbase x402 Docs](https://docs.browserbase.com/integrations/x402/introduction)
