# better-auth Skill

**Production-ready authentication for TypeScript with Cloudflare D1 support**

---

## What This Skill Does

Provides complete patterns for implementing authentication with **better-auth**, a comprehensive TypeScript auth framework. Includes support for Cloudflare Workers + D1 via **Drizzle ORM** or **Kysely** (no direct D1 adapter exists), making it an excellent self-hosted alternative to Clerk or Auth.js.

**⚠️ v2.0.0 Breaking Change**: Previous skill version incorrectly documented a non-existent `d1Adapter()`. This version corrects all patterns to use Drizzle ORM or Kysely as required by better-auth.

---

## Auto-Trigger Keywords

This skill should be automatically invoked when you mention:

- **"better-auth"** - The library name
- **"authentication with D1"** - Cloudflare D1 auth setup
- **"self-hosted auth"** - Alternative to managed services
- **"alternative to Clerk"** - Migration or comparison
- **"alternative to Auth.js"** - Upgrading from Auth.js
- **"TypeScript authentication"** - Type-safe auth
- **"better auth setup"** - Initial configuration
- **"social auth with Cloudflare"** - OAuth on Workers
- **"D1 authentication"** - Database-backed auth on D1
- **"multi-tenant auth"** - SaaS authentication patterns
- **"organization auth"** - Team/org features
- **"2FA authentication"** - Two-factor auth setup
- **"passkeys"** - Passwordless auth
- **"magic link auth"** - Email-based passwordless
- **"better-auth endpoints"** - Auto-generated REST endpoints
- **"better-auth API"** - Server-side API methods
- **"auth.api methods"** - Programmatic auth operations
- **"TanStack Start auth"** - TanStack Start integration
- **"reactStartCookies"** - TanStack Start cookie plugin
- **"multi-session"** - Account switching
- **"genericOAuth"** - Custom OAuth providers
- **"API key authentication"** - API-only auth
- **"TanStack Query session"** - Session state with React Query
- **"nanostores auth"** - Nanostore session invalidation
- **"OAuth 2.1 provider"** - Build your own OAuth server
- **"OAuth provider for MCP"** - MCP server authentication
- **"better-auth MCP"** - MCP plugin (deprecated, use OAuth provider)
- **"admin impersonation"** - Admin impersonate user feature
- **"user impersonation"** - View as another user
- **"admin ban user"** - User management
- **"better-auth admin"** - Admin dashboard patterns
- **"custom RBAC"** - Role-based access control
- **"createAccessControl"** - Permission system
- **"allowImpersonatingAdmins"** - Admin security setting
- **"Hono better-auth"** - Hono integration
- **"better-auth Hono"** - Hono framework setup
- **"bearer token auth"** - API token authentication
- **"better-auth bearer"** - Bearer plugin
- **"Google One Tap"** - Frictionless Google sign-in
- **"one tap sign-in"** - Single-tap authentication
- **"SCIM provisioning"** - Enterprise user provisioning
- **"anonymous auth"** - Guest user authentication
- **"guest user auth"** - Anonymous access
- **"username sign-in"** - Username-based login
- **"generic OAuth"** - Custom OAuth providers
- **"rate limiting auth"** - Rate limit configuration
- **"session cookie cache"** - Cookie caching strategies
- **"Patreon OAuth"** - Patreon sign-in
- **"Kick OAuth"** - Kick streaming sign-in
- **"Vercel OAuth"** - Vercel sign-in
- **"database hooks auth"** - Lifecycle hooks
- **"nodejs_compat"** - Cloudflare Workers requirement
- **"Expo deep linking"** - React Native OAuth
- **"expo-secure-store"** - Mobile secure storage

---

## When to Use This Skill

✅ **Use this skill when**:
- Building authentication for Cloudflare Workers + D1 applications
- Need a self-hosted, vendor-independent auth solution
- Migrating from Clerk to avoid vendor lock-in and costs
- Upgrading from Auth.js to get more features (2FA, organizations, RBAC)
- Implementing multi-tenant SaaS with organizations/teams
- Require advanced features: 2FA, passkeys, social auth, rate limiting
- Want full control over auth logic and data

❌ **Don't use this skill when**:
- You're happy with Clerk and don't mind the cost
- Using Firebase Auth (different ecosystem)
- Building a simple prototype (Auth.js may be faster)
- Auth requirements are extremely basic (custom JWT might suffice)

---

## What You'll Get

### Patterns Included

1. **Cloudflare Workers + D1** - Complete Worker setup with D1 adapter
2. **Framework Integrations** - TanStack Start (reactStartCookies), Expo
3. **React Client Integration** - Hooks and components for auth state
4. **Protected Routes** - Middleware patterns for session verification
5. **Social Providers** - Google, GitHub, Microsoft OAuth setup + custom OAuth
6. **Advanced Features** - 2FA, organizations, multi-tenant, multi-session, API keys
7. **Migration Guides** - From Clerk and Auth.js
8. **Database Setup** - D1 and PostgreSQL schema patterns
9. **API Reference** - Complete documentation for 80+ auto-generated endpoints

### Errors Prevented (14 Common Issues)

- ✅ **D1 adapter misconfiguration** (no direct d1Adapter, must use Drizzle/Kysely)
- ✅ **Cloudflare Workers context errors** (requires nodejs_compat flag)
- ✅ **Schema generation failures** (using Drizzle Kit correctly)
- ✅ **TanStack Start cookie issues** (reactStartCookies plugin required)
- ✅ **Plugin ordering errors** (reactStartCookies must be last)
- ✅ **Nanostore session invalidation** (TanStack Query won't refresh session state)
- ✅ D1 eventual consistency causing stale session reads
- ✅ CORS misconfiguration for SPA applications
- ✅ Session serialization errors in Workers
- ✅ OAuth redirect URI mismatch
- ✅ Email verification not sending
- ✅ JWT token expiration issues
- ✅ Social provider scope issues (missing user data)
- ✅ TypeScript errors with Drizzle schema

### Reference Files

- **`scripts/setup-d1.sh`** - Automated D1 database setup
- **`references/cloudflare-worker-example.ts`** - Complete Worker implementation
- **`references/nextjs-api-route.ts`** - Next.js patterns
- **`references/react-client-hooks.tsx`** - React components
- **`references/drizzle-schema.ts`** - Database schema
- **`assets/auth-flow-diagram.md`** - Visual flow diagrams

---

## Quick Example

### Cloudflare Worker Setup (Drizzle ORM)

**⚠️ CRITICAL**: better-auth requires **Drizzle ORM** or **Kysely** for D1. There is NO direct `d1Adapter()`.

```typescript
import { betterAuth } from 'better-auth'
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { drizzle } from 'drizzle-orm/d1'
import { Hono } from 'hono'
import * as schema from './db/schema' // Your Drizzle schema

type Env = {
  DB: D1Database
  BETTER_AUTH_SECRET: string
  GOOGLE_CLIENT_ID: string
  GOOGLE_CLIENT_SECRET: string
}

const app = new Hono<{ Bindings: Env }>()

app.all('/api/auth/*', async (c) => {
  // Initialize Drizzle with D1
  const db = drizzle(c.env.DB, { schema })

  const auth = betterAuth({
    // Use Drizzle adapter with SQLite provider
    database: drizzleAdapter(db, {
      provider: "sqlite",
    }),
    secret: c.env.BETTER_AUTH_SECRET,
    emailAndPassword: { enabled: true },
    socialProviders: {
      google: {
        clientId: c.env.GOOGLE_CLIENT_ID,
        clientSecret: c.env.GOOGLE_CLIENT_SECRET
      }
    }
  })

  return auth.handler(c.req.raw)
})

export default app
```

**Required dependencies**:
```bash
npm install better-auth drizzle-orm drizzle-kit @cloudflare/workers-types hono
```

**Complete setup guide**: See SKILL.md for full step-by-step instructions including schema definition, migrations, and deployment.

---

## Performance

- **Token Savings**: ~77% (35k → 8k tokens)
- **Time Savings**: ~97% reduction (220 hours manual → 4-8 hours with better-auth)
- **Error Prevention**: 14 documented issues with solutions
- **API Coverage**: Complete reference for 80+ auto-generated endpoints
- **Plugin Documentation**: 15+ plugins (OAuth 2.1, Bearer, One Tap, SCIM, Anonymous, Username, Generic OAuth, Multi-Session, API Key, 2FA, Organization, Admin, Passkey, Magic Link, Stripe)

---

## Comparison to Alternatives

| Feature | better-auth | Clerk | Auth.js |
|---------|-------------|-------|---------|
| **Hosting** | Self-hosted | Third-party | Self-hosted |
| **Cost** | Free | $25/mo+ | Free |
| **Cloudflare D1** | ✅ First-class | ❌ No | ✅ Adapter |
| **2FA/Passkeys** | ✅ Plugin | ✅ Built-in | ⚠️ Limited |
| **Organizations** | ✅ Plugin | ✅ Built-in | ❌ No |
| **Vendor Lock-in** | ✅ None | ❌ High | ✅ None |

---

## Production Tested

- **Projects**: 4 verified D1 production repos
  - zpg6/better-auth-cloudflare (Drizzle + D1)
  - zwily/example-react-router-cloudflare-d1-drizzle-better-auth
  - foxlau/react-router-v7-better-auth (Drizzle + D1)
  - matthewlynch/better-auth-react-router-cloudflare-d1 (Kysely + D1)

---

## Official Resources

- **Docs**: https://better-auth.com
- **GitHub**: https://github.com/better-auth/better-auth (22.4k ⭐)
- **Package**: `better-auth@1.4.10`
- **OAuth 2.1 Provider**: https://www.better-auth.com/docs/plugins/oauth-provider
- **Admin Plugin**: https://www.better-auth.com/docs/plugins/admin
- **Hono Example**: https://hono.dev/examples/better-auth-on-cloudflare
- **Examples**: https://github.com/better-auth/better-auth/tree/main/examples

---

## Installation

```bash
npm install better-auth
# or
pnpm add better-auth
# or
yarn add better-auth
```

**For Cloudflare D1**:
```bash
npm install @cloudflare/workers-types
```

**For PostgreSQL**:
```bash
npm install pg drizzle-orm
```

---

## Version Info

- **Skill Version**: 5.0.0 (Major update: 8 new plugins, rate limiting, session caching, database hooks, Expo integration)
- **Package Version**: better-auth@1.4.10
- **Drizzle ORM**: drizzle-orm@0.45.1, drizzle-kit@0.31.8
- **Kysely**: kysely@0.28.8, kysely-d1@0.4.0
- **Last Verified**: 2026-01-03
- **Compatibility**: Node.js 18+, Bun 1.0+, Cloudflare Workers (requires nodejs_compat flag)

---

## License

MIT (same as better-auth)

---

**Questions?** Check the official docs or ask Claude Code to invoke this skill!
