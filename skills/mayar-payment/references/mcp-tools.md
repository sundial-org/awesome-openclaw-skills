# Mayar MCP Tools Reference

Complete list of available tools via Mayar MCP server.

## Payment Generation

### create_invoice

Create itemized invoice with payment link.

**Input:**
- `name` (string, required) - Customer name
- `email` (string, required) - Customer email
- `mobile` (string, required) - Customer phone (format: "628xxx")
- `description` (string, required) - Order description
- `redirectURL` (string, required) - Post-payment redirect URL
- `expiredAt` (string, required) - Expiry date (ISO 8601 with timezone)
- `items` (array, required) - Items array:
  - `quantity` (number) - Item quantity
  - `rate` (number) - Price per unit (in Rupiah)
  - `description` (string) - Item name

**Output:**
- `id` - Invoice UUID
- `transactionId` - Transaction UUID
- `link` - Payment link URL
- `expiredAt` - Expiry timestamp (epoch ms)

**Example:**
```bash
mcporter call mayar.create_invoice \
  name="John Doe" \
  email="john@example.com" \
  mobile="\"6281234567890\"" \
  description="Product purchase" \
  redirectURL="https://example.com/thanks" \
  expiredAt="2026-12-31T23:59:59+07:00" \
  items='[{"quantity":1,"rate":100000,"description":"Product A"}]'
```

### send_portal_link

Send customer portal access link via email.

**Input:**
- `email` (string, required) - Customer email

**Output:**
- Success status

## Balance & Account

### get_balance

Get current account balance.

**Input:** None

**Output:**
- `balanceActive` - Available balance
- `balancePending` - Pending balance
- `balance` - Total balance

**Example:**
```bash
mcporter call mayar.get_balance
```

## Transaction Queries

### get_latest_transactions

Get recent paid transactions.

**Input:**
- `page` (number, required) - Page number (start from 1)
- `pageSize` (number, required) - Items per page

**Output:**
- `currentPage`, `totalPage`, `totalData`
- `data` - Array of transactions

### get_latest_unpaid_transactions

Get unpaid invoices.

**Input:**
- `page` (number, required)
- `pageSize` (number, required)

**Output:**
- Array of unpaid transactions

### get_transactions_by_time_period

Filter transactions by predefined periods.

**Input:**
- `page` (number, required)
- `pageSize` (number, required)
- `period` (string, required) - One of: `"today"`, `"this_week"`, `"this_month"`, `"this_year"`
- `sortField` (string, required) - `"createdAt"` or `"amount"`
- `sortOrder` (string, required) - `"ASC"` or `"DESC"`

**Example:**
```bash
mcporter call mayar.get_transactions_by_time_period \
  page:1 pageSize:10 \
  period:"this_month" \
  sortField:"createdAt" \
  sortOrder:"DESC"
```

### get_transactions_by_time_range

Filter transactions by custom date range.

**Input:**
- `page`, `pageSize` (numbers, required)
- `startAt` (string, required) - Start date (ISO 8601)
- `endAt` (string, required) - End date (ISO 8601)
- `sortField`, `sortOrder` (strings, required)

**Example:**
```bash
mcporter call mayar.get_transactions_by_time_range \
  page:1 pageSize:10 \
  startAt:"2026-01-01T00:00:00+07:00" \
  endAt:"2026-01-31T23:59:59+07:00" \
  sortField:"amount" \
  sortOrder:"DESC"
```

### get_transactions_by_customer_and_time_period

Filter by customer AND time period.

**Input:**
- `page`, `pageSize`, `period`, `sortField`, `sortOrder` (as above)
- `customerEmail` (string, required)
- `customerName` (string, required)

### get_transactions_by_customer_and_time_range

Filter by customer AND custom date range.

**Input:**
- `page`, `pageSize`, `startAt`, `endAt`, `sortField`, `sortOrder` (as above)
- `customerName`, `customerEmail` (strings, required)

### get_unpaid_transactions_by_time_range

Get unpaid transactions in date range.

**Input:**
- All fields from `get_transactions_by_time_range`
- Plus: `customerName`, `customerEmail` (strings, required)

## Customer Management

### get_customer_detail

Get customer transaction history.

**Input:**
- `customerName` (string, required)
- `customerEmail` (string, required)
- `page` (number, required)
- `pageSize` (number, required)

**Output:**
- Customer details + transaction list

## Product-Specific Queries

### get_transactions_by_specific_product

Get transactions for a specific product.

**Input:**
- `productName` (string, required)
- `productLink` (string, required)
- `productId` (string, required)
- `page`, `pageSize` (numbers, required)

### get_latest_transactions_by_customer

Filter by customer + product.

**Input:**
- `customerName`, `customerEmail` (strings, required)
- `productName`, `productLink` (strings, required)
- `page`, `pageSize` (numbers, required)

## Membership/Subscription Tools

### get_membership_customer_by_specific_product

Get membership customers for a product.

**Input:**
- `productName`, `productLink`, `productId` (strings, required)
- `page`, `pageSize` (numbers, required)
- `memberStatus` (string, required) - One of: `"active"`, `"inactive"`, `"finished"`, `"stopped"`

**Example:**
```bash
mcporter call mayar.get_membership_customer_by_specific_product \
  productName:"Premium Membership" \
  productLink:"premium-membership" \
  productId:"uuid-here" \
  page:1 pageSize:10 \
  memberStatus:"active"
```

### get_membership_customer_by_specific_product_and_tier

Filter membership by tier.

**Input:**
- All fields from above
- Plus: `membershipTierName`, `membershipTierId` (strings, required)

## Common Patterns

### Check if Invoice is Paid

```bash
# Get unpaid transactions
result=$(mcporter call mayar.get_latest_unpaid_transactions page:1 pageSize:50 --output json)

# Check if your invoice ID exists
# If NOT in unpaid list → it's paid!
```

### Get Today's Revenue

```bash
mcporter call mayar.get_transactions_by_time_period \
  page:1 pageSize:100 \
  period:"today" \
  sortField:"amount" \
  sortOrder:"DESC"
```

### Find Customer's Last Purchase

```bash
mcporter call mayar.get_customer_detail \
  customerName:"Customer Name" \
  customerEmail:"email@example.com" \
  page:1 pageSize:1
```

## Field Formats

**Phone Numbers:**
- Format: `"628xxxxxxxxxx"` (no + or spaces)
- Must be string with escaped quotes in CLI: `"\"628xxx\""`

**Dates (ISO 8601):**
- With timezone: `"2026-12-31T23:59:59+07:00"`
- UTC: `"2026-12-31T23:59:59Z"`

**Currency:**
- Always in Rupiah (integer)
- No decimal points
- Example: `100000` = Rp 100,000

**Status Values:**
- Invoice: `"created"` (unpaid), `"paid"`, `"expired"`, `"cancelled"`
- Member: `"active"`, `"inactive"`, `"finished"`, `"stopped"`

**Time Periods:**
- `"today"`, `"this_week"`, `"this_month"`, `"this_year"`

**Sort Fields:**
- `"createdAt"`, `"amount"`

**Sort Order:**
- `"ASC"` (ascending), `"DESC"` (descending)
