# Mayar.id API Reference

## Overview

Mayar.id provides a headless e-commerce API for Indonesian payment processing. This reference covers the REST API endpoints (alternative to MCP).

**Official Documentation:** https://docs.mayar.id/api-reference/introduction

## Authentication

All API requests require Bearer token authentication.

```bash
Authorization: Bearer YOUR_JWT_TOKEN
```

Get your API key from:
- **Production:** https://web.mayar.id/api-keys
- **Sandbox:** https://web.mayar.club/api-keys

## Base URLs

**Production:**
```
https://api.mayar.id/hl/v1/
```

**Sandbox (Testing):**
```
https://api.mayar.club/hl/v1/
```

## Core Endpoints

### Invoice

#### Create Invoice (POST)

```
POST /hl/v1/invoice/create
```

**Request Body:**
```json
{
  "name": "Customer Name",
  "email": "customer@email.com",
  "mobile": "6281234567890",
  "description": "Order description",
  "redirectURL": "https://yoursite.com/success",
  "expiredAt": "2026-12-31T23:59:59+07:00",
  "items": [
    {
      "quantity": 1,
      "rate": 500000,
      "description": "Product A"
    }
  ]
}
```

**Response:**
```json
{
  "statusCode": 200,
  "messages": "success",
  "data": {
    "id": "uuid",
    "transactionId": "uuid",
    "link": "https://subdomain.myr.id/invoices/slug",
    "expiredAt": 1234567890123
  }
}
```

#### Get Invoice List (GET)

```
GET /hl/v1/invoice
```

**Query Parameters:**
- `page` - Page number
- `pageSize` - Items per page

#### Get Invoice Detail (GET)

```
GET /hl/v1/invoice/:invoiceId
```

#### Edit Invoice (POST)

```
POST /hl/v1/invoice/edit
```

#### Close Invoice (GET)

```
GET /hl/v1/invoice/:invoiceId/close
```

#### Reopen Invoice (GET)

```
GET /hl/v1/invoice/:invoiceId/reopen
```

### Request Payment

#### Create Single Payment Request (POST)

```
POST /hl/v1/request-payment/create
```

**Request Body:**
```json
{
  "name": "Customer Name",
  "email": "customer@email.com",
  "mobile": "6281234567890",
  "amount": 500000,
  "description": "Simple payment",
  "redirectURL": "https://yoursite.com/success",
  "expiredAt": "2026-12-31T23:59:59+07:00"
}
```

**Difference from Invoice:**
- `amount` instead of `items[]`
- Simpler for single-amount payments
- No itemization

### Product

#### Get Product Page (GET)

```
GET /hl/v1/product/page
```

#### Search Product (GET)

```
GET /hl/v1/product/search?q=keyword
```

#### Get Product Detail (GET)

```
GET /hl/v1/product/:productId
```

### Customer

#### Get Customer (GET)

```
GET /hl/v1/customer/:customerId
```

#### Create Customer (POST)

```
POST /hl/v1/customer/create
```

**Request Body:**
```json
{
  "name": "Customer Name",
  "email": "customer@email.com",
  "mobile": "6281234567890"
}
```

#### Update Customer Email (POST)

```
POST /hl/v1/customer/update-email
```

#### Create Magic Link (POST)

```
POST /hl/v1/customer/magic-link
```

Generates passwordless login link for customer portal.

### Webhook

#### Register URL Hook (POST)

```
POST /hl/v1/webhook/register
```

**Request Body:**
```json
{
  "urlHook": "https://yoursite.com/webhook"
}
```

**Response:**
```json
{
  "statusCode": 200,
  "messages": "success"
}
```

#### Test URL Hook (POST)

```
POST /hl/v1/webhook/test
```

Sends test webhook to registered URL.

#### Get Webhook History (GET)

```
GET /hl/v1/webhook/history
```

#### Retry Webhook (POST)

```
POST /hl/v1/webhook/retry
```

## Webhook Payload

When payment is successful, Mayar sends POST request to your registered webhook URL:

```json
{
  "eventType": "transaction.paid",
  "data": {
    "id": "transaction-uuid",
    "invoiceId": "invoice-uuid",
    "customerId": "customer-uuid",
    "amount": 500000,
    "status": "paid",
    "paymentMethod": "bank_transfer",
    "paidAt": "2026-01-31T12:34:56+07:00",
    "customer": {
      "name": "Customer Name",
      "email": "customer@email.com",
      "mobile": "6281234567890"
    }
  }
}
```

**Event Types:**
- `transaction.paid` - Payment successful
- `transaction.failed` - Payment failed
- `transaction.expired` - Invoice expired
- `transaction.refunded` - Payment refunded

## Payment Methods

Mayar supports various Indonesian payment methods:

**Bank Transfer:**
- BCA
- Mandiri
- BNI
- BRI
- Permata
- CIMB Niaga

**E-Wallet:**
- GoPay
- OVO
- DANA
- LinkAja
- ShopeePay

**Others:**
- QRIS (QR Code)
- Virtual Account
- Credit/Debit Card (via partner)

## Data Formats

### Phone Numbers
- Format: `"628xxxxxxxxxx"`
- No + symbol
- No spaces or dashes
- Country code 62 (Indonesia)

### Dates (ISO 8601)
```
2026-12-31T23:59:59+07:00
```
- Include timezone (+07:00 for Jakarta)
- YYYY-MM-DDTHH:mm:ss+TZ

### Currency
- Integer (no decimals)
- In Rupiah
- Example: `500000` = Rp 500,000

### Status Values

**Invoice:**
- `created` - Unpaid
- `paid` - Payment successful
- `expired` - Past expiration date
- `cancelled` - Manually cancelled

**Transaction:**
- `pending` - Awaiting payment
- `processing` - Payment being verified
- `paid` - Payment confirmed
- `failed` - Payment failed
- `refunded` - Payment refunded

**Membership:**
- `active` - Currently active
- `inactive` - Not active
- `finished` - Completed
- `stopped` - Manually stopped

## Rate Limits

Mayar does not publicly document rate limits, but recommended practice:
- Max 10 requests/second per endpoint
- Use exponential backoff for retries
- Cache responses when possible

## Error Codes

```json
{
  "statusCode": 400,
  "messages": "Invalid request",
  "errors": [
    {
      "field": "email",
      "message": "Invalid email format"
    }
  ]
}
```

**Common Status Codes:**
- `200` - Success
- `400` - Bad Request (validation error)
- `401` - Unauthorized (invalid API key)
- `404` - Not Found
- `422` - Unprocessable Entity (business logic error)
- `500` - Internal Server Error

## Pagination

Most list endpoints support pagination:

**Query Parameters:**
- `page` - Page number (starts from 1)
- `pageSize` - Items per page (default: 10, max: 100)

**Response:**
```json
{
  "currentPage": 1,
  "totalPage": 5,
  "pageSize": 10,
  "totalData": 47,
  "nextPage": 2,
  "previousPage": null,
  "data": [...]
}
```

## Filtering & Sorting

**Time-based filtering:**
- `period` - `today`, `this_week`, `this_month`, `this_year`
- `startAt` / `endAt` - Custom date range (ISO 8601)

**Sorting:**
- `sortField` - Field to sort by (`createdAt`, `amount`)
- `sortOrder` - `ASC` or `DESC`

## Best Practices

### 1. Use Idempotency
Store invoice IDs to avoid duplicate invoice creation:

```javascript
const existingInvoice = cache.get(orderId);
if (existingInvoice) {
  return existingInvoice;
}

const newInvoice = await createInvoice(...);
cache.set(orderId, newInvoice);
```

### 2. Handle Webhooks Properly
```javascript
app.post('/webhook', (req, res) => {
  // Respond immediately
  res.status(200).json({ received: true });
  
  // Process async
  processPayment(req.body).catch(console.error);
});
```

### 3. Validate Webhook Signature
(If Mayar provides signature verification - check docs)

### 4. Set Appropriate Expiry
```javascript
// Short for immediate purchase (24h)
const expiry = new Date(Date.now() + 24 * 60 * 60 * 1000);

// Longer for invoices (7-30 days)
const expiry = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
```

### 5. Store Transaction Data
```javascript
{
  orderId: "ORD-123",
  invoiceId: "mayar-invoice-uuid",
  transactionId: "mayar-transaction-uuid",
  customerId: "customer-uuid",
  amount: 500000,
  status: "pending",
  createdAt: "2026-01-31T12:00:00Z",
  paidAt: null
}
```

## Sandbox vs Production

**Sandbox:**
- Use for testing
- No real payments
- Separate dashboard (web.mayar.club)
- Separate API keys

**Production:**
- Real payments
- Live dashboard (web.mayar.id)
- Production API keys
- Use after thorough testing

**Migration:**
- Generate new API key from production
- Update base URL
- Test with small amount first

## Support

- **Community:** https://t.me/mcngroup
- **Blog:** https://blog.mayar.id
- **Dashboard:** https://web.mayar.id

For technical issues, contact via dashboard support.
