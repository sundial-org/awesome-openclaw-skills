# Next.js Integration

## Install

```bash
npm install @moneydevkit/nextjs
```

Add to `.env`:
```
MDK_ACCESS_TOKEN=your_api_key_here
MDK_MNEMONIC=your_mnemonic_here
```

## Quick Start (App Router)

### 1. Add the checkout API route

```ts
// app/api/mdk/[...mdk]/route.ts
import { mdkHandler } from '@moneydevkit/nextjs/server'
export const { GET, POST } = mdkHandler()
```

### 2. Create a buy button

```tsx
'use client'
import { useCheckout } from '@moneydevkit/nextjs'

export default function BuyButton() {
  const { createCheckout, isLoading } = useCheckout()

  const handleBuy = async () => {
    const result = await createCheckout({
      type: 'AMOUNT',
      title: 'My Product',
      description: 'A great product',
      amount: 500,        // $5.00 (cents)
      currency: 'USD',
      successUrl: '/checkout/success',
      metadata: { orderId: 'order-123' },
    })

    if (result.error) {
      console.error(result.error.message)
      return
    }

    window.location.href = result.data.checkoutUrl
  }

  return (
    <button onClick={handleBuy} disabled={isLoading}>
      {isLoading ? 'Creating checkout…' : 'Buy Now — $5'}
    </button>
  )
}
```

### 3. Render the checkout page

```tsx
// app/checkout/[id]/page.tsx
import { Checkout } from '@moneydevkit/nextjs'

export default function CheckoutPage({ params }: { params: { id: string } }) {
  return <Checkout id={params.id} />
}
```

### 4. Add a success page

```tsx
// app/checkout/success/page.tsx
'use client'
import { useCheckoutSuccess } from '@moneydevkit/nextjs'

export default function SuccessPage() {
  const { isCheckoutPaidLoading, isCheckoutPaid, metadata } = useCheckoutSuccess()

  if (isCheckoutPaidLoading || isCheckoutPaid === null) {
    return <p>Verifying payment…</p>
  }

  if (!isCheckoutPaid) {
    return <p>Payment has not been confirmed.</p>
  }

  return <p>Payment confirmed. Enjoy your purchase!</p>
}
```

## Product checkouts

Sell products defined in the dashboard:

```tsx
import { useCheckout, useProducts } from '@moneydevkit/nextjs'

const { createCheckout } = useCheckout()
const { products } = useProducts()

const result = await createCheckout({
  type: 'PRODUCTS',
  product: products[0].id,
  successUrl: '/checkout/success',
})
```

## Collecting customer data

```tsx
const result = await createCheckout({
  type: 'AMOUNT',
  title: 'Product',
  amount: 500,
  currency: 'USD',
  successUrl: '/checkout/success',
  customer: {
    email: 'jane@example.com',
    name: 'Jane Doe',
    externalId: 'user-123',
  },
  requireCustomerData: ['email', 'name'],
})
```

## Deploy to Vercel

1. Push to GitHub
2. Import in Vercel
3. Add `MDK_ACCESS_TOKEN` and `MDK_MNEMONIC` to environment variables (all environments)
4. Deploy

⚠️ When setting env vars via CLI, use `printf` not `echo` — trailing newlines break auth silently.
