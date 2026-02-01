# Blockchain Operations

## Read Contract

```typescript
import { readContract } from 'viem/actions'
import { erc20Abi } from 'viem'

const balance = await readContract(bot.viem, {
  address: tokenAddress,
  abi: erc20Abi,
  functionName: 'balanceOf',
  args: [userAddress]
})
```

## Execute Transaction

```typescript
import { execute } from 'viem/experimental/erc7821'
import { waitForTransactionReceipt } from 'viem/actions'

const hash = await execute(bot.viem, {
  address: bot.appAddress,
  account: bot.viem.account,
  calls: [{
    to: targetAddress,
    abi: contractAbi,
    functionName: 'transfer',
    args: [recipient, amount]
  }]
})

await waitForTransactionReceipt(bot.viem, { hash })
```

## Verify Transaction (Critical for Payments)

**Never grant access based on txHash alone.** Always verify on-chain:

```typescript
bot.onInteractionResponse(async (handler, event) => {
  if (event.response.payload.content?.case !== 'transaction') return
  const tx = event.response.payload.content.value

  if (tx.txHash) {
    const receipt = await waitForTransactionReceipt(bot.viem, {
      hash: tx.txHash
    })

    if (receipt.status !== 'success') {
      await handler.sendMessage(event.channelId, 'Transaction failed on-chain')
      return
    }

    // NOW safe to grant access
    await grantUserAccess(event.userId)
    await handler.sendMessage(event.channelId, 'Payment confirmed!')
  }
})
```

## Debug Transaction Failures

```typescript
try {
  const hash = await execute(bot.viem, { /* ... */ })
  console.log('TX submitted:', hash)

  const receipt = await waitForTransactionReceipt(bot.viem, { hash })
  console.log('TX result:', {
    status: receipt.status,
    gasUsed: receipt.gasUsed.toString(),
    blockNumber: receipt.blockNumber
  })

  if (receipt.status !== 'success') {
    console.error('TX reverted. Check on basescan:',
      'https://basescan.org/tx/' + hash)
  }
} catch (err) {
  console.error('TX failed:', err.message)
  // Common: insufficient funds, nonce issues, contract revert
}
```

## Token Addresses (Base Mainnet)

```typescript
import { zeroAddress } from 'viem'

const TOKENS = {
  ETH: zeroAddress,
  USDC: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  TOWNS: '0x00000000A22C618fd6b4D7E9A335C4B96B189a38'
}
```

## Check Balances

```typescript
import { formatEther } from 'viem'

const gasBalance = await bot.viem.getBalance({ address: bot.viem.account.address })
const treasuryBalance = await bot.viem.getBalance({ address: bot.appAddress })
console.log('Gas: ' + formatEther(gasBalance) + ' ETH')
console.log('Treasury: ' + formatEther(treasuryBalance) + ' ETH')
```

## Get User's Smart Account

```typescript
import { getSmartAccountFromUserId } from '@towns-protocol/bot'

const userSmartAccount = getSmartAccountFromUserId(event.userId)
```
