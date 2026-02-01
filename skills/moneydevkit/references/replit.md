# Replit Integration (Express + Vite)

## Install

```bash
npm install @moneydevkit/replit express
```

Add to `.env` or Replit Secrets:
```
MDK_ACCESS_TOKEN=your_api_key_here
MDK_MNEMONIC=your_mnemonic_here
```

## Bundler config

Allowlist moneydevkit packages in `script/build.ts` so Replit's bundler can import them:
```ts
// script/build.ts
const allowlist = [
  '@moneydevkit/core',
  '@moneydevkit/replit',
  // ... other packages
]
```

## Backend: Express route

Mount the moneydevkit endpoint:
```ts
// server/index.ts
import express from 'express'
import { createMdkExpressRouter } from '@moneydevkit/replit/server/express'

const app = express()
app.use('/api/mdk', createMdkExpressRouter())

app.listen(3000, () => {
  console.log('Server listening on http://localhost:3000')
})
```

## Frontend: Vite + React

### Buy button

```tsx
// src/App.tsx
import { useCheckout } from '@moneydevkit/replit'
import { useState } from 'react'

export default function App() {
  const { createCheckout, isLoading } = useCheckout()
  const [error, setError] = useState<string | null>(null)

  const handlePurchase = async () => {
    setError(null)

    const result = await createCheckout({
      type: 'AMOUNT',
      title: 'My Product',
      description: 'A great product',
      amount: 500,        // $5.00 (cents)
      currency: 'USD',
      successUrl: '/checkout/success',
      metadata: { name: 'John Doe' },
    })

    if (result.error) {
      setError(result.error.message)
      return
    }

    window.location.href = result.data.checkoutUrl
  }

  return (
    <div>
      {error && <p style={{ color: 'red' }}>{error}</p>}
      <button onClick={handlePurchase} disabled={isLoading}>
        {isLoading ? 'Creating checkout…' : 'Buy Now'}
      </button>
    </div>
  )
}
```

### Checkout page

```tsx
// src/routes/checkout/[id].tsx
import { Checkout } from '@moneydevkit/replit'

export default function CheckoutPage({ params }: { params: { id: string } }) {
  return <Checkout id={params.id} />
}
```

### Success page

```tsx
import { useCheckoutSuccess } from '@moneydevkit/replit'

export function SuccessPage() {
  const { isCheckoutPaidLoading, isCheckoutPaid, metadata } = useCheckoutSuccess()

  if (isCheckoutPaidLoading || isCheckoutPaid === null) return <p>Verifying payment…</p>
  if (!isCheckoutPaid) return <p>Payment has not been confirmed.</p>

  return <p>Payment confirmed for {metadata?.name ?? 'customer'}.</p>
}
```

## Product checkouts

```tsx
import { useCheckout, useProducts } from '@moneydevkit/replit'

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
