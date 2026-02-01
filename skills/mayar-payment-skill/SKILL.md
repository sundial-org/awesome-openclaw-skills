---
name: mayar-payment
description: Mayar.id payment integration for generating invoices, payment links, and tracking transactions via MCP. Use when needing to: (1) Create payment invoices/links for customers, (2) Track payment status and transactions, (3) Generate WhatsApp-friendly payment messages, (4) Handle Indonesian payment methods (bank transfer, e-wallet, QRIS), (5) Manage subscriptions/memberships, or (6) Automate payment workflows for e-commerce, services, or digital products.
---

# Mayar Payment Integration

Integrate Mayar.id payment platform via MCP (Model Context Protocol) for Indonesian payment processing.

## Prerequisites

1. **Mayar.id account** - Sign up at https://mayar.id
2. **API Key** - Generate from https://web.mayar.id/api-keys
3. **mcporter configured** - MCP must be set up in Clawdbot

## Setup

### 1. Store API Credentials

```bash
mkdir -p ~/.config/mayar
cat > ~/.config/mayar/credentials << EOF
MAYAR_API_TOKEN="your-jwt-token-here"
EOF
chmod 600 ~/.config/mayar/credentials
```

### 2. Configure MCP Server

Add to `config/mcporter.json`:

```json
{
  "mcpServers": {
    "mayar": {
      "command": "npx",
      "args": [
        "-y",
        "mcp-remote",
        "https://mcp.mayar.id/sse",
        "--header",
        "Authorization:YOUR_API_TOKEN_HERE"
      ]
    }
  }
}
```

Replace `YOUR_API_TOKEN_HERE` with actual token.

### 3. Test Connection

```bash
mcporter list mayar
```

Should show 15+ available tools.

## Core Workflows

### Create Invoice with Payment Link

**Most common use case:** Generate payment link for customer.

```bash
mcporter call mayar.create_invoice \
  name="Customer Name" \
  email="email@example.com" \
  mobile="\"628xxx\"" \
  description="Order description" \
  redirectURL="https://yoursite.com/thanks" \
  expiredAt="2026-12-31T23:59:59+07:00" \
  items='[{"quantity":1,"rate":500000,"description":"Product A"}]'
```

**Returns:**
```json
{
  "id": "uuid",
  "transactionId": "uuid", 
  "link": "https://subdomain.myr.id/invoices/slug",
  "expiredAt": 1234567890
}
```

**Key fields:**
- `mobile` - MUST be string with quotes: `"\"628xxx\""`
- `expiredAt` - ISO 8601 format with timezone
- `items` - Array of `{quantity, rate, description}`
- `redirectURL` - Where customer goes after payment

### WhatsApp Integration Pattern

```javascript
// 1. Create invoice
const invoice = /* mcporter call mayar.create_invoice */;

// 2. Format message
const message = `
✅ *Order Confirmed!*

*Items:*
• Product Name
  Rp ${amount.toLocaleString('id-ID')}

*TOTAL: Rp ${total.toLocaleString('id-ID')}*

💳 *Pembayaran:*
${invoice.data.link}

⏰ Berlaku sampai: ${expiryDate}

Terima kasih! 🙏
`.trim();

// 3. Send via WhatsApp
message({
  action: 'send',
  channel: 'whatsapp',
  target: customerPhone,
  message: message
});
```

### Check Payment Status

```bash
# Get latest transactions (check if paid)
mcporter call mayar.get_latest_transactions page:1 pageSize:10

# Get unpaid invoices
mcporter call mayar.get_latest_unpaid_transactions page:1 pageSize:10
```

Filter by status: `"created"` (unpaid) → `"paid"` (success).

### Other Operations

```bash
# Check account balance
mcporter call mayar.get_balance

# Get customer details
mcporter call mayar.get_customer_detail \
  customerName="Name" \
  customerEmail="email@example.com" \
  page:1 pageSize:10

# Filter by time period
mcporter call mayar.get_transactions_by_time_period \
  page:1 pageSize:10 \
  period:"this_month" \
  sortField:"createdAt" \
  sortOrder:"DESC"
```

## Common Patterns

### Multi-Item Invoice

```javascript
items='[
  {"quantity":2,"rate":500000,"description":"Product A"},
  {"quantity":1,"rate":1000000,"description":"Product B"}
]'
// Total: 2M (2×500K + 1×1M)
```

### Subscription/Recurring

Use membership tools:

```bash
mcporter call mayar.get_membership_customer_by_specific_product \
  productName:"Premium Membership" \
  productLink:"your-product-link" \
  productId:"product-uuid" \
  page:1 pageSize:10 \
  memberStatus:"active"
```

### Payment Confirmation Flow

**Option A: Webhook** (Real-time)
- Register webhook URL with Mayar
- Receive instant payment notifications
- Best for production

**Option B: Polling** (Simpler)
- Poll `get_latest_transactions` every 30-60s
- Check for new payments
- Best for MVP/testing

## Troubleshooting

**404 on payment link:**
- Link format: `https://your-subdomain.myr.id/invoices/slug`
- Check dashboard for correct subdomain
- Default may be account name

**Invalid mobile number:**
- Mobile MUST be string: `"\"628xxx\""` (with escaped quotes)
- Format: `628xxxxxxxxxx` (no + or spaces)

**Expired invoice:**
- Default expiry is `expiredAt` timestamp
- Customer can't pay after expiration
- Create new invoice if needed

## Reference Documentation

- **API Details:** See [references/api-reference.md](references/api-reference.md)
- **Integration Examples:** See [references/integration-examples.md](references/integration-examples.md)
- **MCP Tools Reference:** See [references/mcp-tools.md](references/mcp-tools.md)

## Production Checklist

- [ ] Use production API key (not sandbox)
- [ ] Setup webhook for payment notifications
- [ ] Error handling for failed invoice creation
- [ ] Store invoice IDs for tracking
- [ ] Handle payment expiration
- [ ] Customer database integration
- [ ] Receipt/confirmation automation

## Environments

**Production:**
- Dashboard: https://web.mayar.id
- API Base: `https://api.mayar.id/hl/v1/`

**Sandbox (Testing):**
- Dashboard: https://web.mayar.club
- API Base: `https://api.mayar.club/hl/v1/`
