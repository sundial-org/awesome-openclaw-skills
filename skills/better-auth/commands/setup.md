# Setup better-auth

Add self-hosted authentication to a Cloudflare Workers + D1 project using better-auth.

---

## Your Task

Follow these steps to configure better-auth with Drizzle ORM and D1.

### 1. Check Prerequisites

Verify the project has:
- Cloudflare Workers with D1 binding
- Drizzle ORM configured (run `/drizzle-orm-d1/init` first if not)
- TypeScript

### 2. Install Dependencies

```bash
npm install better-auth
npm install -D @better-auth/cli
```

### 3. Create Auth Configuration

Create `src/lib/auth/index.ts`:

```typescript
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import type { DrizzleD1Database } from 'drizzle-orm/d1';
import * as schema from '@/db/schema';

export function createAuth(db: DrizzleD1Database<typeof schema>, env: Env) {
  return betterAuth({
    database: drizzleAdapter(db, {
      provider: 'sqlite',
      schema: {
        user: schema.users,
        session: schema.sessions,
        account: schema.accounts,
        verification: schema.verifications,
      },
    }),
    secret: env.BETTER_AUTH_SECRET,
    baseURL: env.BETTER_AUTH_URL,
    emailAndPassword: {
      enabled: true,
    },
    socialProviders: {
      // Add providers as needed
      // google: {
      //   clientId: env.GOOGLE_CLIENT_ID,
      //   clientSecret: env.GOOGLE_CLIENT_SECRET,
      // },
    },
  });
}
```

### 4. Generate Auth Schema

Create `src/lib/auth/cli.ts` for schema generation:

```typescript
import { betterAuth } from 'better-auth';
import { drizzleAdapter } from 'better-auth/adapters/drizzle';
import { drizzle } from 'drizzle-orm/better-sqlite3';
import Database from 'better-sqlite3';

const sqlite = new Database(':memory:');
const db = drizzle(sqlite);

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: 'sqlite' }),
  emailAndPassword: { enabled: true },
});
```

Run schema generation:
```bash
npx @better-auth/cli generate --config ./src/lib/auth/cli.ts
```

### 5. Add Auth Tables to Schema

Update `src/db/schema.ts` with generated tables:

```typescript
import { sqliteTable, text, integer } from 'drizzle-orm/sqlite-core';

// Your existing tables...

// Auth tables (from better-auth generate)
export const users = sqliteTable('users', {
  id: text('id').primaryKey(),
  email: text('email').notNull().unique(),
  emailVerified: integer('email_verified', { mode: 'boolean' }).default(false),
  name: text('name'),
  image: text('image'),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
  updatedAt: integer('updated_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
});

export const sessions = sqliteTable('sessions', {
  id: text('id').primaryKey(),
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  token: text('token').notNull().unique(),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull(),
  ipAddress: text('ip_address'),
  userAgent: text('user_agent'),
  createdAt: integer('created_at', { mode: 'timestamp' }).$defaultFn(() => new Date()),
});

export const accounts = sqliteTable('accounts', {
  id: text('id').primaryKey(),
  userId: text('user_id').notNull().references(() => users.id, { onDelete: 'cascade' }),
  providerId: text('provider_id').notNull(),
  providerAccountId: text('provider_account_id').notNull(),
  accessToken: text('access_token'),
  refreshToken: text('refresh_token'),
  expiresAt: integer('expires_at', { mode: 'timestamp' }),
});

export const verifications = sqliteTable('verifications', {
  id: text('id').primaryKey(),
  identifier: text('identifier').notNull(),
  value: text('value').notNull(),
  expiresAt: integer('expires_at', { mode: 'timestamp' }).notNull(),
});
```

### 6. Create Auth Routes

Add to your Hono app (`src/index.ts`):

```typescript
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { createAuth } from './lib/auth';
import { createDb } from './db';

const app = new Hono<{ Bindings: Env }>();

// CORS for credentials
app.use('/api/auth/*', cors({
  origin: (origin) => origin,
  credentials: true,
}));

// Auth routes
app.all('/api/auth/*', async (c) => {
  const db = createDb(c.env.DB);
  const auth = createAuth(db, c.env);
  return auth.handler(c.req.raw);
});
```

### 7. Configure Environment

Add to `wrangler.jsonc`:
```jsonc
{
  "vars": {
    "BETTER_AUTH_URL": "http://localhost:8787"
  }
}
```

Create `.dev.vars`:
```bash
BETTER_AUTH_SECRET=your-secret-at-least-32-characters-here
```

Set production secret:
```bash
echo "your-production-secret" | npx wrangler secret put BETTER_AUTH_SECRET
```

### 8. Generate and Apply Migrations

```bash
npm run db:generate
npm run db:migrate:local
npm run db:migrate:remote
```

### 9. Create Auth Client

Create `src/client/lib/auth.ts`:

```typescript
import { createAuthClient } from 'better-auth/react';

export const authClient = createAuthClient({
  baseURL: import.meta.env.VITE_API_URL || window.location.origin,
});

export const { useSession, signIn, signUp, signOut } = authClient;
```

### 10. Provide Next Steps

```
✅ better-auth configured with D1!

📁 Added:
   - src/lib/auth/index.ts    (Auth configuration)
   - Auth tables in schema    (users, sessions, accounts, verifications)
   - /api/auth/* routes       (Auth endpoints)

🔐 Client Usage:
   import { useSession, signIn, signUp, signOut } from '@/lib/auth';

   const { data: session } = useSession();
   await signIn.email({ email, password });
   await signUp.email({ email, password, name });
   await signOut();

⚡ Plugins Available:
   - 2FA (twoFactor)
   - Passkeys (passkey)
   - Organizations (organization)
   - RBAC (admin)

📚 Skill loaded: better-auth
   - D1 via Drizzle adapter
   - Session caching patterns
   - Rate limiting included
```

---

## Critical Notes

1. **D1 requires Drizzle**: better-auth has no direct D1 adapter
2. **ESM only**: better-auth v1.4+ is 100% ESM
3. **nodejs_compat**: Required in wrangler.jsonc compatibility_flags
