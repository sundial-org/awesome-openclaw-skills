---
paths: "**/*auth*.ts", "**/*auth*.tsx", src/lib/auth.ts, src/auth.ts
---

# better-auth Corrections

Claude's training may reference older better-auth patterns. This project uses **better-auth v1.4+**.

## Critical: No D1 Adapter

```typescript
/* ❌ This doesn't exist */
import { d1Adapter } from 'better-auth/adapters/d1'
database: d1Adapter(env.DB)

/* ✅ Use Drizzle instead */
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { drizzle } from 'drizzle-orm/d1'
const db = drizzle(env.DB, { schema })
database: drizzleAdapter(db, { provider: "sqlite" })

/* ✅ Or use Kysely */
import { Kysely } from 'kysely'
import { D1Dialect } from 'kysely-d1'
database: {
  db: new Kysely({ dialect: new D1Dialect({ database: env.DB }) }),
  type: "sqlite"
}
```

## v1.4.x Breaking Changes

```typescript
/* ❌ CommonJS no longer supported (v1.4.0) */
const { betterAuth } = require('better-auth')

/* ✅ ESM only */
import { betterAuth } from 'better-auth'

/* ❌ MCP plugin deprecated (v1.4.9) */
import { mcp } from 'better-auth/plugins'

/* ✅ Use OAuth 2.1 Provider instead */
import { oauthProvider, jwt } from 'better-auth/plugins'
plugins: [jwt(), oauthProvider({ accessTokenExpiresIn: 3600 })]

/* ❌ Admin impersonation of admins (v1.4.6 default changed) */
admin() // allowImpersonatingAdmins now defaults to false

/* ✅ Explicit if you need admin-on-admin impersonation */
admin({ allowImpersonatingAdmins: true })
```

## TanStack Start: Cookie Plugin Required

```typescript
/* ❌ Cookies won't set properly */
export const auth = betterAuth({
  plugins: [twoFactor(), organization()],
})

/* ✅ reactStartCookies MUST be last */
import { reactStartCookies } from 'better-auth/react-start'
export const auth = betterAuth({
  plugins: [
    twoFactor(),
    organization(),
    reactStartCookies(), // MUST be LAST
  ],
})
```

## Nanostore Session Invalidation

```typescript
/* ❌ TanStack Query invalidation doesn't update session */
queryClient.invalidateQueries({ queryKey: ['user-profile'] })

/* ✅ Notify nanostore after user updates */
const { data, error } = await authClient.updateUser({ image: newAvatarUrl })
if (!error) {
  authClient.$store.notify('$sessionSignal')
}
```

## Schema Generation

```bash
# ❌ better-auth migrate doesn't work well with D1
npx better-auth migrate

# ✅ Use Drizzle Kit instead
npx drizzle-kit generate
wrangler d1 migrations apply my-db --remote
```

## Quick Fixes

| If Claude suggests... | Use instead... |
|----------------------|----------------|
| `d1Adapter(env.DB)` | `drizzleAdapter(db, { provider: "sqlite" })` |
| `require('better-auth')` | `import { betterAuth } from 'better-auth'` |
| Missing cookies in TanStack Start | Add `reactStartCookies()` as last plugin |
| `queryClient.invalidateQueries` for session | `authClient.$store.notify('$sessionSignal')` |
| `npx better-auth migrate` | `npx drizzle-kit generate` |
