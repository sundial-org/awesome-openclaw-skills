# Interactive Components

## Send Button Form

```typescript
await handler.sendInteractionRequest(channelId, {
  type: 'form',           // NOT 'case'
  id: 'my-form',
  components: [
    { id: 'yes', type: 'button', label: 'Yes' },
    { id: 'no', type: 'button', label: 'No' }
  ],
  recipient: event.userId  // Optional: private to this user
})
```

## Handle Form Response

```typescript
bot.onInteractionResponse(async (handler, event) => {
  if (event.response.payload.content?.case !== 'form') return

  const form = event.response.payload.content.value
  for (const c of form.components) {
    if (c.component.case === 'button') {
      console.log('Button clicked:', c.id)

      if (c.id === 'yes') {
        await handler.sendMessage(event.channelId, 'You clicked Yes!')
      }
    }
  }
})
```

## Request Transaction

```typescript
import { encodeFunctionData, erc20Abi, parseUnits } from 'viem'

await handler.sendInteractionRequest(channelId, {
  type: 'transaction',
  id: 'payment',
  title: 'Send Tokens',
  subtitle: 'Transfer 50 USDC',
  tx: {
    chainId: '8453',
    to: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',  // USDC
    value: '0',
    data: encodeFunctionData({
      abi: erc20Abi,
      functionName: 'transfer',
      args: [recipient, parseUnits('50', 6)]
    })
  },
  recipient: event.userId
})
```

## Handle Transaction Response

```typescript
bot.onInteractionResponse(async (handler, event) => {
  if (event.response.payload.content?.case !== 'transaction') return

  const tx = event.response.payload.content.value

  if (tx.txHash) {
    // IMPORTANT: Always verify on-chain before granting access
    // See BLOCKCHAIN.md for full verification pattern
    const receipt = await waitForTransactionReceipt(bot.viem, {
      hash: tx.txHash
    })

    if (receipt.status === 'success') {
      await handler.sendMessage(event.channelId,
        'Payment confirmed: https://basescan.org/tx/' + tx.txHash)
    } else {
      await handler.sendMessage(event.channelId, 'Transaction failed on-chain')
    }
  } else if (tx.error) {
    await handler.sendMessage(event.channelId, 'Transaction rejected: ' + tx.error)
  }
})
```

## Request Signature

```typescript
await handler.sendInteractionRequest(channelId, {
  type: 'signature',
  id: 'sign-message',
  title: 'Sign Message',
  message: 'I agree to the terms of service',
  recipient: event.userId
})
```

## Important Notes

- **Use `type` property** - NOT `case` (common mistake)
- **`recipient` is optional** - If set, only that user sees the interaction
- **Always verify transactions** - Never trust txHash alone, check receipt.status
