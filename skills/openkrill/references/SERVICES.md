# x402-Compatible Services

This document lists services that accept micropayments via the x402 protocol.

**IMPORTANT:** x402-enabled services often use a different subdomain than their standard API. Always check for `x402.` prefixed endpoints!

## Discovering Services via x402 Bazaar

The **x402 Bazaar** is the recommended way to discover x402-compatible endpoints programmatically:

```bash
# Query the Bazaar for available services
npx ts-node scripts/discover-services.ts

# Or query directly via curl
curl -s "https://x402.org/facilitator/discovery/resources?type=http&limit=20"
```

The Bazaar provides:
- **Real-time discovery** of available x402 endpoints
- **Pricing information** (amount, network, asset)
- **Schema information** for inputs/outputs
- **Pagination** for browsing large catalogs

See the [Bazaar documentation](https://docs.cdp.coinbase.com/x402/bazaar) for more details.

---

## Browserbase

**Website:** https://browserbase.com  
**Documentation:** https://docs.browserbase.com/integrations/x402/introduction

### Overview

Browserbase is a cloud browser automation platform that enables agents to spin up headless browsers for web scraping, testing, and automation tasks. With x402 integration, agents can pay per browser session without API keys or billing setup.

### x402 Endpoint

**Base URL:** `https://x402.browserbase.com` (NOT `api.browserbase.com`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/browser/session/create` | POST | Create a browser session |
| `/browser/session/:id/status` | GET | Check session status |
| `/browser/session/:id/extend` | POST | Add more time |
| `/browser/session/:id` | DELETE | Terminate session |

#### Create Session
```
POST https://x402.browserbase.com/browser/session/create
```

Creates a new browser session.

**Request Body:**
```json
{
  "browserSettings": {
    "viewport": {
      "width": 1920,
      "height": 1080
    }
  }
}
```

**Response:**
```json
{
  "id": "session_abc123",
  "status": "running",
  "connectUrl": "wss://...",
  "debuggerUrl": "https://..."
}
```

#### Get Session Status
```
GET https://x402.browserbase.com/browser/session/{sessionId}/status
```

#### Extend Session
```
POST https://x402.browserbase.com/browser/session/{sessionId}/extend
```

#### Terminate Session
```
DELETE https://x402.browserbase.com/browser/session/{sessionId}
```

### Pricing

- **Rate:** $0.12/hour (paid in USDC on Base)
- Minimum purchase: ~0.002 USDC (5 minutes)

| Duration | Cost (USDC) |
|----------|-------------|
| 5 min | $0.01 |
| 15 min | $0.03 |
| 30 min | $0.06 |
| 60 min | $0.12 |

### Example Usage

```bash
curl -s -X POST "https://api.thirdweb.com/v1/payments/x402/fetch?url=https://x402.browserbase.com/browser/session/create&method=POST" \
  -H "Content-Type: application/json" \
  -H "x-secret-key: $THIRDWEB_SECRET_KEY" \
  -d '{"browserSettings": {"viewport": {"width": 1920, "height": 1080}}}'
```

### Use Cases

- Web scraping and data extraction
- Automated testing
- Screenshot generation
- Form filling automation
- Monitoring website changes

---

## Firecrawl (Non-Standard x402 - NOT RECOMMENDED)

**Website:** https://firecrawl.dev  
**Documentation:** https://docs.firecrawl.dev/x402/search

### Overview

Firecrawl is a web scraping and search API that extracts structured data from websites.

### ⚠️ WARNING: Incomplete x402 Implementation

Firecrawl's x402 implementation is **non-standard and currently unusable** for automated agents:

| Issue | Firecrawl | Standard x402 (Browserbase) |
|-------|-----------|---------------------------|
| Response code | `401 Unauthorized` | `402 Payment Required` |
| Payment info | ❌ Not provided | ✅ `payTo`, `asset`, `amount` |
| Auto-payment | ❌ Impossible | ✅ thirdweb handles it |
| Docs explain header? | ❌ Just says `{{paymentHeader}}` | ✅ Client generates from 402 response |

**The problem:** Their docs say to use `X-Payment: {{paymentHeader}}` but:
1. They return 401, not 402
2. They don't provide payment details in the response
3. They don't document how to generate the payment header

### x402 Endpoint (Non-Functional)

**Base URL:** `https://api.firecrawl.dev/v1/x402/`

| Endpoint | Method | Status |
|----------|--------|--------|
| `/v1/x402/search` | POST | ❌ Cannot be used by agents |

**Limitations:**
- `limit` capped at 10 results (vs 100 for subscription)

### Standard Endpoints (Subscription-based)

These are NOT x402-enabled:

#### Search
```
POST https://api.firecrawl.dev/v1/search
```

#### Scrape
```
POST https://api.firecrawl.dev/v1/scrape
```

**Request Body:**
```json
{
  "url": "https://example.com/page",
  "formats": ["markdown", "html"],
  "onlyMainContent": true
}
```

#### Crawl
```
POST https://api.firecrawl.dev/v1/crawl
```

**Request Body:**
```json
{
  "url": "https://example.com",
  "limit": 50,
  "maxDepth": 3
}
```

### Pricing

- **x402 Search:** $0.01/request
- Experimental - pricing may change

### Example Usage (Requires API Key)

```bash
# x402 Search - requires token + payment header
curl -s -X POST "https://api.firecrawl.dev/v1/x402/search" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $FIRECRAWL_API_KEY" \
  -H "X-Payment: <payment-header>" \
  -d '{"query": "machine learning tutorials", "limit": 5}'
```

### Alternatives for Keyless Scraping

Since Firecrawl x402 still requires an API key, for truly keyless web scraping consider:

1. **Browserbase + Custom Script:** Purchase a browser session via true x402, then run your own scraping code
2. **Firecrawl MCP:** If available in your environment, use the Firecrawl MCP server (uses standard API key auth)

### Use Cases

- Research and information gathering
- Content aggregation
- Competitive analysis
- Documentation extraction
- Data collection for training

---

---

## Mail.tm (Disposable Email)

**Website:** https://mail.tm  
**Documentation:** https://docs.mail.tm

### Overview

Mail.tm provides a free API for creating temporary email accounts. This enables agents to autonomously create email addresses for signups, receive verification emails, and read messages—all programmatically. Unlike Browserbase and Firecrawl, Mail.tm does **not** require x402 payments and is completely free.

### Why Use This?

AI agents often need to:
- Sign up for services that require email verification
- Receive one-time codes or confirmation links
- Test email workflows without using personal addresses

### Base URL

**API Base URL:** `https://api.mail.tm`

### Endpoints

#### Get Available Domains
```
GET https://api.mail.tm/domains
```

Fetch the list of available email domains. You need this to create an account.

**Response:**
```json
{
  "hydra:member": [
    {
      "id": "string",
      "domain": "wireconnected.com",
      "isActive": true,
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ]
}
```

#### Create Account
```
POST https://api.mail.tm/accounts
```

Create a new email account. No authentication required.

**Request Body:**
```json
{
  "address": "myagent123@wireconnected.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "id": "abc123",
  "address": "myagent123@wireconnected.com",
  "quota": 40000000,
  "used": 0,
  "isDisabled": false,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

**Important:** Store the `id`, `address`, and `password`—you'll need them for authentication.

#### Get Authentication Token
```
POST https://api.mail.tm/token
```

Get a bearer token to authenticate subsequent requests.

**Request Body:**
```json
{
  "address": "myagent123@wireconnected.com",
  "password": "securePassword123"
}
```

**Response:**
```json
{
  "id": "abc123",
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### List Messages
```
GET https://api.mail.tm/messages
Authorization: Bearer <token>
```

Fetch all messages in the inbox.

**Response:**
```json
{
  "hydra:member": [
    {
      "id": "msg123",
      "from": {"name": "Service", "address": "noreply@service.com"},
      "to": [{"name": "", "address": "myagent123@wireconnected.com"}],
      "subject": "Verify your email",
      "intro": "Click the link below to verify...",
      "seen": false,
      "hasAttachments": false,
      "createdAt": "2024-01-01T00:00:00.000Z"
    }
  ],
  "hydra:totalItems": 1
}
```

#### Get Single Message
```
GET https://api.mail.tm/messages/{id}
Authorization: Bearer <token>
```

Get full message content including HTML body.

**Response:**
```json
{
  "id": "msg123",
  "from": {"name": "Service", "address": "noreply@service.com"},
  "subject": "Verify your email",
  "text": "Click here to verify: https://example.com/verify?token=abc123",
  "html": ["<p>Click <a href='https://example.com/verify?token=abc123'>here</a></p>"],
  "hasAttachments": false,
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

#### Get Account Info
```
GET https://api.mail.tm/me
Authorization: Bearer <token>
```

Returns the authenticated account's information.

#### Delete Account
```
DELETE https://api.mail.tm/accounts/{id}
Authorization: Bearer <token>
```

Permanently delete the account. Returns 204 on success.

#### Delete Message
```
DELETE https://api.mail.tm/messages/{id}
Authorization: Bearer <token>
```

Delete a specific message. Returns 204 on success.

### Pricing

- **Free** — No payment required
- **Rate Limit:** 8 queries per second (QPS) per IP address

### Example Workflow

Complete workflow for an agent to create an email and check for messages:

```bash
# 1. Get available domains
DOMAIN=$(curl -s https://api.mail.tm/domains | jq -r '.["hydra:member"][0].domain')

# 2. Generate a unique email address
EMAIL="agent-$(date +%s)@$DOMAIN"
PASSWORD="SecurePass123!"

# 3. Create the account
curl -s -X POST https://api.mail.tm/accounts \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"$EMAIL\", \"password\": \"$PASSWORD\"}"

# 4. Get authentication token
TOKEN=$(curl -s -X POST https://api.mail.tm/token \
  -H "Content-Type: application/json" \
  -d "{\"address\": \"$EMAIL\", \"password\": \"$PASSWORD\"}" | jq -r '.token')

# 5. Check for messages (poll periodically)
curl -s https://api.mail.tm/messages \
  -H "Authorization: Bearer $TOKEN"

# 6. Read a specific message
curl -s https://api.mail.tm/messages/MESSAGE_ID \
  -H "Authorization: Bearer $TOKEN"
```

### Storing Email Credentials

When an agent creates an email, it should store the credentials for later use:

```json
{
  "email_accounts": [
    {
      "address": "agent-1234567890@wireconnected.com",
      "password": "SecurePass123!",
      "token": "eyJhbGciOiJIUzI1NiIs...",
      "account_id": "abc123",
      "created_at": "2024-01-01T00:00:00.000Z",
      "purpose": "Service signup verification"
    }
  ]
}
```

**Recommended storage:** Environment variables or a local `.agent-emails.json` file (add to `.gitignore`).

### Use Cases

- Signing up for services requiring email verification
- Receiving OTP codes and verification links
- Testing email notification systems
- Creating throwaway accounts for research
- Automated form submissions requiring email confirmation

### Terms of Use

- **No illegal activity** - Usage for illegal purposes is prohibited
- **No reselling** - Don't build paid products that just wrap the API
- **No proxy services** - Don't mirror or proxy the API
- **Attribution required** - Link back to mail.tm somewhere visible

---

## Discovering x402 Endpoints

### Step 1: Check for x402 Subdomain

Many services use a separate `x402.` subdomain:

```bash
# Check if x402 subdomain exists and what it offers
curl -s https://x402.SERVICE.com/

# Example: Browserbase has a nice landing page
curl -s https://x402.browserbase.com/
```

### Step 2: Check for /x402/ Path Prefix

Some services add `/x402/` to the path instead:

```bash
# Firecrawl uses path prefix
curl -s -I https://api.firecrawl.dev/v1/x402/search
```

### Step 3: Test the Response Code

```bash
# True x402 returns 402 Payment Required
curl -s -i -X POST https://x402.SERVICE.com/endpoint \
  -H "Content-Type: application/json" -d '{}' 2>&1 | head -5
```

**Interpreting the response:**
- `402 Payment Required` → True x402, thirdweb handles automatically
- `401 Unauthorized` → Hybrid x402, needs API key + payment header
- `404 Not Found` → No x402 support at this endpoint

### Step 4: Check Documentation

- `docs.SERVICE.com/x402/`
- `docs.SERVICE.com/payments/`
- Search for "x402", "402", or "micropayments" in their docs

---

## Adding New Services

As the x402 ecosystem grows, more services will support micropayments. To use any x402-compatible service:

1. **Check for x402 Support**
   - Look for x402 documentation or 402 Payment Required in API responses
   - **Check for x402-specific subdomain** (e.g., `x402.service.com` vs `api.service.com`)
   - **Check for /x402/ path prefix** (e.g., `/v1/x402/search`)

2. **Determine x402 Type**
   - **True x402:** Returns 402 status, fully keyless
   - **Hybrid x402:** Returns 401 status, needs API key + payment

3. **Identify the Correct Endpoint**
   - Visit the service's root x402 URL to see available endpoints
   - Example: `curl https://x402.browserbase.com/` shows all endpoints

4. **Use thirdweb fetchWithPayment** (for True x402 only)
   ```bash
   curl -s -X POST "https://api.thirdweb.com/v1/payments/x402/fetch?url=<x402-endpoint>&method=<HTTP-method>" \
     -H "Content-Type: application/json" \
     -H "x-secret-key: $THIRDWEB_SECRET_KEY" \
     -d '<request-body>'
   ```

5. **Handle Insufficient Funds**
   - If response contains a `link` field, auto-open it with cursor-ide-browser MCP
   - User funds wallet, then retry the request

---

## Service Directory

| Service | Category | x402 Endpoint | Type | Payment | Status |
|---------|----------|---------------|------|---------|--------|
| Browserbase | Browser Automation | `x402.browserbase.com` | True x402 | USDC | ✅ Works with thirdweb |
| Firecrawl | Web Scraping | `api.firecrawl.dev/v1/x402/search` | Non-standard | USDC | ❌ Broken - returns 401, no payment info |
| Mail.tm | Disposable Email | `api.mail.tm` | N/A | Free | ✅ Active |

**Legend:**
- **True x402:** Returns 402 with payment details, thirdweb handles automatically
- **Non-standard:** Doesn't follow x402 spec, cannot be used with automated payment flows

For the latest list of x402-compatible services, visit:
- https://x402.org
- https://portal.thirdweb.com/x402

---

## Tips for Agents

1. **Use the Bazaar first** - Query `discover-services.ts` to find available x402 endpoints
2. **Check for x402 subdomains** before using standard API endpoints
3. **Start with small requests** to verify payment works
4. **Cache results** when possible to reduce costs
5. **Auto-open payment links** when wallet needs funding
6. **Handle errors gracefully** - retry on transient failures
