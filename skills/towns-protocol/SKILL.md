---
name: bots
description: >-
  Use when building Towns Protocol bots - covers SDK initialization, slash commands,
  message handlers, reactions, interactive forms, blockchain operations, and deployment.
  Triggers: "towns bot", "makeTownsBot", "onSlashCommand", "onMessage", "sendInteractionRequest",
  "webhook", "bot deployment", "@towns-protocol/bot"
license: MIT
compatibility: Requires Bun runtime, Base network RPC access, @towns-protocol/bot SDK
metadata:
  author: towns-protocol
  version: "2.0.0"
---

# Towns Protocol Bot SDK Reference

## Critical Rules

**MUST follow these rules - violations cause silent failures:**

1. **User IDs are Ethereum addresses** - Always `0x...` format, never usernames
2. **Mentions require BOTH** - `<@{userId}>` format in text AND `mentions` array in options
3. **Two-wallet architecture**:
   - `bot.viem.account.address` = Gas wallet (signs & pays fees) - **MUST fund with Base ETH**
   - `bot.appAddress` = Treasury (optional, for transfers)
4. **Slash commands DON'T trigger onMessage** - They're exclusive handlers
5. **Interactive forms use `type` property** - Not `case` (e.g., `type: 'form'`)
6. **Never trust txHash alone** - Verify `receipt.status === 'success'` before granting access

## Quick Reference

### Key Imports

```typescript
import { makeTownsBot, getSmartAccountFromUserId } from '@towns-protocol/bot'
import type { BotCommand, BotHandler } from '@towns-protocol/bot'
import { Permission } from '@towns-protocol/web3'
import { parseEther, formatEther, erc20Abi, zeroAddress } from 'viem'
import { readContract, waitForTransactionReceipt } from 'viem/actions'
import { execute } from 'viem/experimental/erc7821'
```

### Handler Methods

| Method | Signature | Notes |
|--------|-----------|-------|
| `sendMessage` | `(channelId, text, opts?) → { eventId }` | opts: `{ threadId?, replyId?, mentions?, attachments? }` |
| `editMessage` | `(channelId, eventId, text)` | Bot's own messages only |
| `removeEvent` | `(channelId, eventId)` | Bot's own messages only |
| `sendReaction` | `(channelId, messageId, emoji)` | |
| `sendInteractionRequest` | `(channelId, payload)` | Forms, transactions, signatures |
| `hasAdminPermission` | `(userId, spaceId) → boolean` | |
| `ban` / `unban` | `(userId, spaceId)` | Needs ModifyBanning permission |

### Bot Properties

| Property | Description |
|----------|-------------|
| `bot.viem` | Viem client for blockchain |
| `bot.viem.account.address` | Gas wallet - **MUST fund with Base ETH** |
| `bot.appAddress` | Treasury wallet (optional) |
| `bot.botId` | Bot identifier |

**For detailed guides, see [references/](references/):**
- [Messaging API](references/MESSAGING.md) - Mentions, threads, attachments, formatting
- [Blockchain Operations](references/BLOCKCHAIN.md) - Read/write contracts, verify transactions
- [Interactive Components](references/INTERACTIVE.md) - Forms, transaction requests
- [Deployment](references/DEPLOYMENT.md) - Local dev, Render, tunnels
- [Debugging](references/DEBUGGING.md) - Troubleshooting guide

---

## Bot Setup

### Project Initialization

```bash
bunx towns-bot init my-bot
cd my-bot
bun install
```

### Environment Variables

```bash
APP_PRIVATE_DATA=<base64_credentials>   # From app.towns.com/developer
JWT_SECRET=<webhook_secret>              # Min 32 chars
PORT=3000
BASE_RPC_URL=https://base-mainnet.g.alchemy.com/v2/KEY  # Recommended
```

### Basic Bot Template

```typescript
import { makeTownsBot } from '@towns-protocol/bot'
import type { BotCommand } from '@towns-protocol/bot'

const commands = [
  { name: 'help', description: 'Show help' },
  { name: 'ping', description: 'Check if alive' }
] as const satisfies BotCommand[]

const bot = await makeTownsBot(
  process.env.APP_PRIVATE_DATA!,
  process.env.JWT_SECRET!,
  { commands }
)

bot.onSlashCommand('ping', async (handler, event) => {
  const latency = Date.now() - event.createdAt.getTime()
  await handler.sendMessage(event.channelId, 'Pong! ' + latency + 'ms')
})

export default bot.start()
```

### Config Validation

```typescript
import { z } from 'zod'

const EnvSchema = z.object({
  APP_PRIVATE_DATA: z.string().min(1),
  JWT_SECRET: z.string().min(32),
  DATABASE_URL: z.string().url().optional()
})

const env = EnvSchema.safeParse(process.env)
if (!env.success) {
  console.error('Invalid config:', env.error.issues)
  process.exit(1)
}
```

---

## Event Handlers

### onMessage

Triggers on regular messages (NOT slash commands).

```typescript
bot.onMessage(async (handler, event) => {
  // event: { userId, spaceId, channelId, eventId, message, isMentioned, threadId?, replyId? }

  if (event.isMentioned) {
    await handler.sendMessage(event.channelId, 'You mentioned me!')
  }
})
```

### onSlashCommand

Triggers on `/command`. Does NOT trigger onMessage.

```typescript
bot.onSlashCommand('weather', async (handler, { args, channelId }) => {
  // /weather San Francisco → args: ['San', 'Francisco']
  const location = args.join(' ')
  if (!location) {
    await handler.sendMessage(channelId, 'Usage: /weather <location>')
    return
  }
  // ... fetch weather
})
```

### onReaction

```typescript
bot.onReaction(async (handler, event) => {
  // event: { reaction, messageId, channelId }
  if (event.reaction === '👋') {
    await handler.sendMessage(event.channelId, 'I saw your wave!')
  }
})
```

### onTip

Requires "All Messages" mode in Developer Portal.

```typescript
bot.onTip(async (handler, event) => {
  // event: { senderAddress, receiverAddress, amount (bigint), currency }
  if (event.receiverAddress === bot.appAddress) {
    await handler.sendMessage(event.channelId,
      'Thanks for ' + formatEther(event.amount) + ' ETH!')
  }
})
```

### onInteractionResponse

```typescript
bot.onInteractionResponse(async (handler, event) => {
  switch (event.response.payload.content?.case) {
    case 'form':
      const form = event.response.payload.content.value
      for (const c of form.components) {
        if (c.component.case === 'button' && c.id === 'yes') {
          await handler.sendMessage(event.channelId, 'You clicked Yes!')
        }
      }
      break
    case 'transaction':
      const tx = event.response.payload.content.value
      if (tx.txHash) {
        // IMPORTANT: Verify on-chain before granting access
        // See references/BLOCKCHAIN.md for full verification pattern
        await handler.sendMessage(event.channelId,
          'TX: https://basescan.org/tx/' + tx.txHash)
      }
      break
  }
})
```

### Event Context Validation

Always validate context before using:

```typescript
bot.onSlashCommand('cmd', async (handler, event) => {
  if (!event.spaceId || !event.channelId) {
    console.error('Missing context:', { userId: event.userId })
    return
  }
  // Safe to proceed
})
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| `insufficient funds for gas` | Fund `bot.viem.account.address` with Base ETH |
| Mention not highlighting | Include BOTH `<@userId>` in text AND `mentions` array |
| Slash command not working | Add to `commands` array in makeTownsBot |
| Handler not triggering | Check message forwarding mode in Developer Portal |
| `writeContract` failing | Use `execute()` for external contracts |
| Granting access on txHash | Verify `receipt.status === 'success'` first |
| Message lines overlapping | Use `\n\n` (double newlines), not `\n` |
| Missing event context | Validate `spaceId`/`channelId` before using |

---

## Resources

- **Developer Portal**: https://app.towns.com/developer
- **Documentation**: https://docs.towns.com/build/bots
- **SDK**: https://www.npmjs.com/package/@towns-protocol/bot
- **Chain ID**: 8453 (Base Mainnet)
