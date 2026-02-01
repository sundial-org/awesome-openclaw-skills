# Debugging

## Handler Not Triggering

Most common issue. Check in order:

### 1. Webhook URL Correct?

```bash
# Your bot should log incoming requests
curl -X POST https://your-webhook-url/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

### 2. Tunnel Running? (local dev)

```bash
# Tailscale
tailscale funnel status

# ngrok
curl http://127.0.0.1:4040/api/tunnels
```

### 3. Bot Added to Channel?

Bot must be:
- Installed in the Space (Settings → Integrations)
- Added to the specific channel (Channel Settings → Integrations)

### 4. Message Forwarding Mode?

In Developer Portal:
- "Mentions Only" = only `@bot` messages
- "All Messages" = everything (required for `onTip`)

### 5. Slash Command Registered?

Must be in `commands` array passed to `makeTownsBot`:

```typescript
const commands = [
  { name: 'mycommand', description: 'Does something' }
] as const satisfies BotCommand[]

const bot = await makeTownsBot(creds, secret, { commands })
```

## Add Request Logging

```typescript
const bot = await makeTownsBot(
  process.env.APP_PRIVATE_DATA!,
  process.env.JWT_SECRET!,
  { commands }
)

// Log all incoming events
bot.onMessage(async (handler, event) => {
  console.log('[onMessage]', {
    userId: event.userId,
    channelId: event.channelId,
    message: event.message.slice(0, 100),
    isMentioned: event.isMentioned
  })
  // ... rest of handler
})

bot.onSlashCommand('*', async (handler, event) => {
  console.log('[onSlashCommand]', {
    command: event.command,
    args: event.args,
    userId: event.userId
  })
})
```

## Common Error Messages

| Error | Cause | Fix |
|-------|-------|-----|
| `JWT verification failed` | Wrong JWT_SECRET | Match secret in Developer Portal |
| `insufficient funds for gas` | Empty gas wallet | Fund `bot.viem.account.address` |
| `Invalid APP_PRIVATE_DATA` | Malformed credentials | Re-copy from Developer Portal |
| `ECONNREFUSED` on RPC | Bad RPC URL or rate limited | Use dedicated RPC (Alchemy/Infura) |
| `nonce too low` | Concurrent transactions | Add transaction queue or retry logic |

## Verify Webhook Connectivity

```typescript
import { Hono } from 'hono'

const app = new Hono()

app.get('/health', (c) => c.json({
  status: 'ok',
  timestamp: new Date().toISOString(),
  gasWallet: bot.viem.account.address
}))

// Test from outside:
// curl https://your-webhook-url/health
```

## Debug Transaction Failures

```typescript
import { waitForTransactionReceipt } from 'viem/actions'

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

## Check Gas Wallet Balance

```typescript
import { formatEther } from 'viem'

const balance = await bot.viem.getBalance({
  address: bot.viem.account.address
})

console.log('Gas wallet balance:', formatEther(balance), 'ETH')

if (balance === 0n) {
  console.error('WARNING: Gas wallet is empty!')
  console.error('Fund this address:', bot.viem.account.address)
}
```
