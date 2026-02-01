---
name: moneydevkit
description: Accept payments on any website using moneydevkit. Use when building a site that sells something, adding a checkout/paywall, or integrating payments into a Next.js or Replit app. Supports fixed pricing, pay-what-you-want, products, customers, and orders. Bitcoin Lightning under the hood — works globally, no bank account needed.
---

# moneydevkit

Add payments to any web app in under 5 minutes. Two supported frameworks: Next.js and Replit (Express + Vite).

## Workflow

### 1. Get credentials

**Option A — MCP:**

There are two MCP servers:
- **Unauthenticated** (`/mcp/`) — for creating a new account and minting credentials
- **Authenticated** (`/mcp/account/`) — for managing your account after setup (requires OAuth)

To create a new account:
```
claude mcp add moneydevkit --transport http https://mcp.moneydevkit.com/mcp/
```

After you have credentials, switch to the authenticated MCP for full account control:
```
claude mcp add moneydevkit --transport http https://mcp.moneydevkit.com/mcp/account/
```

**Option B — CLI:**
```bash
npx @moneydevkit/create
```

**Option C — Dashboard:**
Sign up at [moneydevkit.com](https://moneydevkit.com) and create an app.

All options produce two values:
- `MDK_ACCESS_TOKEN` — API key
- `MDK_MNEMONIC` — wallet seed phrase

Add both to `.env` (or Replit Secrets, Vercel env vars, etc.). Both are required.

### 2. Pick a framework and follow its guide

- **Next.js** → read [references/nextjs.md](references/nextjs.md)
- **Replit (Express + Vite)** → read [references/replit.md](references/replit.md)

### 3. Create products (optional)

For fixed catalog items, create products via the dashboard or MCP:
```
mcporter call moneydevkit.create-product name="T-Shirt" priceAmount=2500 currency=USD
```
Then use `type: 'PRODUCTS'` checkouts with the product ID.

For dynamic amounts (tips, donations, invoices), skip products and use `type: 'AMOUNT'` directly.

### 4. Deploy

Deploy to Vercel (Next.js) or Replit. Ensure `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` are set in the production environment.

⚠️ Use `printf` not `echo` when piping env vars — trailing newlines cause silent auth failures.

## Checkout types

| Type | Use case | Required fields |
|------|----------|----------------|
| `AMOUNT` | Dynamic amounts, tips, invoices | `amount`, `currency` |
| `PRODUCTS` | Sell dashboard products | `product` (product ID) |

## Pricing options

- **Fixed price** — set specific amount (USD cents or whole sats)
- **Pay what you want** — customer chooses amount (set `amountType: 'CUSTOM'` on product)

## Currency

- `USD` — amounts in cents (e.g. 500 = $5.00)
- `SAT` — amounts in whole satoshis

## Customers

Collect customer info to track purchases and enable refunds:
```ts
await createCheckout({
  // ...checkout fields
  customer: { email: 'jane@example.com', name: 'Jane', externalId: 'user-123' },
  requireCustomerData: ['email', 'name'] // show form for missing fields
})
```

## MCP tools

If the [moneydevkit MCP server](https://mcp.moneydevkit.com/mcp/account/) is connected (authenticated), these tools are available:

- `create-app` / `list-apps` / `update-app` / `rotate-api-key` — manage apps
- `create-product` / `list-products` / `get-product` / `update-product` / `delete-product`
- `create-customer` / `list-customers` / `get-customer` / `update-customer` / `delete-customer`
- `list-checkouts` / `get-checkout` — view checkout sessions
- `list-orders` / `get-order` — view completed payments
- `search-docs` — search moneydevkit documentation

## Docs

Full documentation: [docs.moneydevkit.com](https://docs.moneydevkit.com)
