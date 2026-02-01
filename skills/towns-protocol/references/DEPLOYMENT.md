# Deployment

## Local Development

```bash
# Start bot (default port 5123)
bun run dev

# Expose webhook via Tailscale Funnel
tailscale funnel 5123
# Creates URL like: https://your-machine.taild8e1b0.ts.net/

# Alternative: ngrok
ngrok http 5123
```

## Setup Webhook in Developer Portal

1. Go to https://app.towns.com/developer
2. Select your bot
3. Set Webhook URL to your tunnel URL + `/webhook`
   - Example: `https://your-machine.taild8e1b0.ts.net/webhook`
4. Save changes

## Testing Checklist

- [ ] Bot server running (`bun run dev`)
- [ ] Tunnel active (Tailscale/ngrok)
- [ ] Webhook URL updated in Developer Portal
- [ ] Bot installed in a Space (Settings → Integrations)
- [ ] Bot added to the specific channel (Channel Settings → Integrations)
- [ ] Check logs for incoming webhook events

## Render.com Deployment

1. Create Web Service from Git repo
2. Set build command: `bun install`
3. Set start command: `bun run start`
4. Set environment variables:
   - `APP_PRIVATE_DATA`
   - `JWT_SECRET`
   - `DATABASE_URL` (if using database)
   - `BASE_RPC_URL` (recommended: Alchemy/Infura)
5. Set webhook URL in app.towns.com/developer to Render URL + `/webhook`

## Health Check Endpoint

Add for deployment platforms that require health checks:

```typescript
import { Hono } from 'hono'

const app = new Hono()

app.get('/health', (c) => c.json({
  status: 'ok',
  timestamp: new Date().toISOString(),
  gasWallet: bot.viem.account.address
}))
```

## Graceful Shutdown

Handle SIGTERM for clean shutdown (required for Render/Kubernetes):

```typescript
process.on('SIGTERM', async () => {
  console.log('SIGTERM received, closing...')
  await pool.end()  // Close DB connections
  process.exit(0)
})
```

## Database Connection Pool

```typescript
import { Pool } from 'pg'

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000
})

// Health check on startup
await pool.query('SELECT 1')
```

## Thread Ownership Pattern (Race-Safe)

```typescript
// First writer wins
await pool.query(
  `INSERT INTO threads (thread_id, user_id)
   VALUES ($1, $2)
   ON CONFLICT (thread_id) DO NOTHING`,
  [threadId, userId]
)

// Check ownership
const result = await pool.query(
  'SELECT user_id FROM threads WHERE thread_id = $1',
  [threadId]
)
return result.rows[0]?.user_id === userId
```
