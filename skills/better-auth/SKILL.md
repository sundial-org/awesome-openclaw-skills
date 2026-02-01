---
name: better-auth
description: |
  Self-hosted auth for TypeScript/Cloudflare Workers with social auth, 2FA, passkeys, organizations, RBAC, and 15+ plugins. Requires Drizzle ORM or Kysely for D1 (no direct adapter). Self-hosted alternative to Clerk/Auth.js.

  Use when: self-hosting auth on D1, building OAuth provider, multi-tenant SaaS, or troubleshooting D1 adapter errors, session caching, rate limits, Expo crashes, additionalFields bugs.
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
---

# better-auth - D1 Adapter & Error Prevention Guide

**Package**: better-auth@1.4.16 (Jan 21, 2026)
**Breaking Changes**: ESM-only (v1.4.0), Admin impersonation prevention default (v1.4.6), Multi-team table changes (v1.3), D1 requires Drizzle/Kysely (no direct adapter)

---

## ⚠️ CRITICAL: D1 Adapter Requirement

better-auth **DOES NOT** have `d1Adapter()`. You **MUST** use:
- **Drizzle ORM** (recommended): `drizzleAdapter(db, { provider: "sqlite" })`
- **Kysely**: `new Kysely({ dialect: new D1Dialect({ database: env.DB }) })`

See Issue #1 below for details.

---

## What's New in v1.4.10 (Dec 31, 2025)

**Major Features:**
- **OAuth 2.1 Provider plugin** - Build your own OAuth provider (replaces MCP plugin)
- **Patreon OAuth provider** - Social sign-in with Patreon
- **Kick OAuth provider** - With refresh token support
- **Vercel OAuth provider** - Sign in with Vercel
- **Global `backgroundTasks` config** - Deferred actions for better performance
- **Form data support** - Email authentication with fetch metadata fallback
- **Stripe enhancements** - Flexible subscription lifecycle, `disableRedirect` option

**Admin Plugin Updates:**
- ⚠️ **Breaking**: Impersonation of admins disabled by default (v1.4.6)
- Support role with permission-based user updates
- Role type inference improvements

**Security Fixes:**
- SAML XML parser hardening with configurable size constraints
- SAML assertion timestamp validation with per-provider clock skew
- SSO domain-verified provider trust
- Deprecated algorithm rejection
- Line nonce enforcement

📚 **Docs**: https://www.better-auth.com/changelogs

---

## What's New in v1.4.0 (Nov 22, 2025)

**Major Features:**
- **Stateless session management** - Sessions without database storage
- **ESM-only package** ⚠️ Breaking: CommonJS no longer supported
- **JWT key rotation** - Automatic key rotation for enhanced security
- **SCIM provisioning** - Enterprise user provisioning protocol
- **@standard-schema/spec** - Replaces ZodType for validation
- **CaptchaFox integration** - Built-in CAPTCHA support
- Automatic server-side IP detection
- Cookie-based account data storage
- Multiple passkey origins support
- RP-Initiated Logout endpoint (OIDC)

📚 **Docs**: https://www.better-auth.com/changelogs

---

## What's New in v1.3 (July 2025)

**Major Features:**
- **SSO with SAML 2.0** - Enterprise single sign-on (moved to separate `@better-auth/sso` package)
- **Multi-team support** ⚠️ Breaking: `teamId` removed from member table, new `teamMembers` table required
- **Additional fields** - Custom fields for organization/member/invitation models
- Performance improvements and bug fixes

📚 **Docs**: https://www.better-auth.com/blog/1-3

---

## Alternative: Kysely Adapter Pattern

If you prefer Kysely over Drizzle:

**File**: `src/auth.ts`

```typescript
import { betterAuth } from "better-auth";
import { Kysely, CamelCasePlugin } from "kysely";
import { D1Dialect } from "kysely-d1";

type Env = {
  DB: D1Database;
  BETTER_AUTH_SECRET: string;
  // ... other env vars
};

export function createAuth(env: Env) {
  return betterAuth({
    secret: env.BETTER_AUTH_SECRET,

    // Kysely with D1Dialect
    database: {
      db: new Kysely({
        dialect: new D1Dialect({
          database: env.DB,
        }),
        plugins: [
          // CRITICAL: Required if using Drizzle schema with snake_case
          new CamelCasePlugin(),
        ],
      }),
      type: "sqlite",
    },

    emailAndPassword: {
      enabled: true,
    },

    // ... other config
  });
}
```

**Why CamelCasePlugin?**

If your Drizzle schema uses `snake_case` column names (e.g., `email_verified`), but better-auth expects `camelCase` (e.g., `emailVerified`), the `CamelCasePlugin` automatically converts between the two.

**⚠️ Cloudflare Workers Note**: D1 database bindings are only available inside the request handler (the `fetch()` function). You cannot initialize better-auth outside the request context. Use a factory function pattern:

```typescript
// ❌ WRONG - DB binding not available outside request
const db = drizzle(env.DB, { schema }) // env.DB doesn't exist here
export const auth = betterAuth({ database: drizzleAdapter(db, { provider: "sqlite" }) })

// ✅ CORRECT - Create auth instance per-request
export default {
  fetch(request, env, ctx) {
    const db = drizzle(env.DB, { schema })
    const auth = betterAuth({ database: drizzleAdapter(db, { provider: "sqlite" }) })
    return auth.handler(request)
  }
}
```

**Community Validation**: Multiple production implementations confirm this pattern (Medium, AnswerOverflow, official Hono examples).

---

## Framework Integrations

### TanStack Start

**⚠️ CRITICAL**: TanStack Start requires the `reactStartCookies` plugin to handle cookie setting properly.

```typescript
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { reactStartCookies } from "better-auth/react-start";

export const auth = betterAuth({
  database: drizzleAdapter(db, { provider: "sqlite" }),
  plugins: [
    twoFactor(),
    organization(),
    reactStartCookies(), // ⚠️ MUST be LAST plugin
  ],
});
```

**Why it's needed**: TanStack Start uses a special cookie handling system. Without this plugin, auth functions like `signInEmail()` and `signUpEmail()` won't set cookies properly, causing authentication to fail.

**Important**: The `reactStartCookies` plugin **must be the last plugin in the array**.

**Session Nullability Pattern**: When using `useSession()` in TanStack Start, the session object always exists, but `session.user` and `session.session` are `null` when not logged in:

```typescript
const { data: session } = authClient.useSession()

// When NOT logged in:
console.log(session) // { user: null, session: null }
console.log(!!session) // true (unexpected!)

// Correct check:
if (session?.user) {
  // User is logged in
}
```

**Always check `session?.user` or `session?.session`, not just `session`**. This is expected behavior (session object container always exists).

**API Route Setup** (`/src/routes/api/auth/$.ts`):
```typescript
import { auth } from '@/lib/auth'
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/api/auth/$')({
  server: {
    handlers: {
      GET: ({ request }) => auth.handler(request),
      POST: ({ request }) => auth.handler(request),
    },
  },
})
```

📚 **Official Docs**: https://www.better-auth.com/docs/integrations/tanstack

---

## Available Plugins (v1.4+)

Better Auth provides plugins for advanced authentication features:

| Plugin | Import | Description | Docs |
|--------|--------|-------------|------|
| **OAuth 2.1 Provider** | `better-auth/plugins` | Build OAuth 2.1 provider with PKCE, JWT tokens, consent flows (replaces MCP & OIDC plugins) | [📚](https://www.better-auth.com/docs/plugins/oauth-provider) |
| **SSO** | `better-auth/plugins` | Enterprise Single Sign-On with OIDC, OAuth2, and SAML 2.0 support | [📚](https://www.better-auth.com/docs/plugins/sso) |
| **Stripe** | `better-auth/plugins` | Payment and subscription management with flexible lifecycle handling | [📚](https://www.better-auth.com/docs/plugins/stripe) |
| **MCP** | `better-auth/plugins` | ⚠️ **Deprecated** - Use OAuth 2.1 Provider instead | [📚](https://www.better-auth.com/docs/plugins/mcp) |
| **Expo** | `better-auth/expo` | React Native/Expo with `webBrowserOptions` and last-login-method tracking | [📚](https://www.better-auth.com/docs/integrations/expo) |

### OAuth 2.1 Provider Plugin (New in v1.4.9)

Build your own OAuth provider for MCP servers, third-party apps, or API access:

```typescript
import { betterAuth } from "better-auth";
import { oauthProvider } from "better-auth/plugins";
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    jwt(), // Required for token signing
    oauthProvider({
      // Token expiration (seconds)
      accessTokenExpiresIn: 3600,      // 1 hour
      refreshTokenExpiresIn: 2592000,  // 30 days
      authorizationCodeExpiresIn: 600, // 10 minutes
    }),
  ],
});
```

**Key Features:**
- **OAuth 2.1 compliant** - PKCE mandatory, S256 only, no implicit flow
- **Three grant types**: `authorization_code`, `refresh_token`, `client_credentials`
- **JWT or opaque tokens** - Configurable token format
- **Dynamic client registration** - RFC 7591 compliant
- **Consent management** - Skip consent for trusted clients
- **OIDC UserInfo endpoint** - `/oauth2/userinfo` with scope-based claims

**Required Well-Known Endpoints:**

```typescript
// app/api/.well-known/oauth-authorization-server/route.ts
export async function GET() {
  return Response.json({
    issuer: process.env.BETTER_AUTH_URL,
    authorization_endpoint: `${process.env.BETTER_AUTH_URL}/api/auth/oauth2/authorize`,
    token_endpoint: `${process.env.BETTER_AUTH_URL}/api/auth/oauth2/token`,
    // ... other metadata
  });
}
```

**Create OAuth Client:**

```typescript
const client = await auth.api.createOAuthClient({
  body: {
    name: "My MCP Server",
    redirectURLs: ["https://claude.ai/callback"],
    type: "public", // or "confidential"
  },
});
// Returns: { clientId, clientSecret (if confidential) }
```

📚 **Full Docs**: https://www.better-auth.com/docs/plugins/oauth-provider

⚠️ **Note**: This plugin is in active development and may not be suitable for production use yet.

---

### Additional Plugins Reference

| Plugin | Description | Docs |
|--------|-------------|------|
| **Bearer** | API token auth (alternative to cookies for APIs) | [📚](https://www.better-auth.com/docs/plugins/bearer) |
| **One Tap** | Google One Tap frictionless sign-in | [📚](https://www.better-auth.com/docs/plugins/one-tap) |
| **SCIM** | Enterprise user provisioning (SCIM 2.0) | [📚](https://www.better-auth.com/docs/plugins/scim) |
| **Anonymous** | Guest user access without PII | [📚](https://www.better-auth.com/docs/plugins/anonymous) |
| **Username** | Username-based sign-in (alternative to email) | [📚](https://www.better-auth.com/docs/plugins/username) |
| **Generic OAuth** | Custom OAuth providers with PKCE | [📚](https://www.better-auth.com/docs/plugins/generic-oauth) |
| **Multi-Session** | Multiple accounts in same browser | [📚](https://www.better-auth.com/docs/plugins/multi-session) |
| **API Key** | Token-based auth with rate limits | [📚](https://www.better-auth.com/docs/plugins/api-key) |

#### Bearer Token Plugin

For API-only authentication (mobile apps, CLI tools, third-party integrations):

```typescript
import { bearer } from "better-auth/plugins";
import { bearerClient } from "better-auth/client/plugins";

// Server
export const auth = betterAuth({
  plugins: [bearer()],
});

// Client - Store token after sign-in
const { token } = await authClient.signIn.email({ email, password });
localStorage.setItem("auth_token", token);

// Client - Configure fetch to include token
const authClient = createAuthClient({
  plugins: [bearerClient()],
  fetchOptions: {
    auth: { type: "Bearer", token: () => localStorage.getItem("auth_token") },
  },
});
```

#### Google One Tap Plugin

Frictionless single-tap sign-in for users already signed into Google:

```typescript
import { oneTap } from "better-auth/plugins";
import { oneTapClient } from "better-auth/client/plugins";

// Server
export const auth = betterAuth({
  plugins: [oneTap()],
});

// Client
authClient.oneTap({
  onSuccess: (session) => {
    window.location.href = "/dashboard";
  },
});
```

**Requirement**: Configure authorized JavaScript origins in Google Cloud Console.

#### Anonymous Plugin

Guest access without requiring email/password:

```typescript
import { anonymous } from "better-auth/plugins";

// Server
export const auth = betterAuth({
  plugins: [
    anonymous({
      emailDomainName: "anon.example.com", // temp@{id}.anon.example.com
      onLinkAccount: async ({ anonymousUser, newUser }) => {
        // Migrate anonymous user data to linked account
        await migrateUserData(anonymousUser.id, newUser.id);
      },
    }),
  ],
});

// Client
await authClient.signIn.anonymous();
// Later: user can link to real account via signIn.social/email
```

#### Generic OAuth Plugin

Add custom OAuth providers not in the built-in list:

```typescript
import { genericOAuth } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    genericOAuth({
      config: [
        {
          providerId: "linear",
          clientId: env.LINEAR_CLIENT_ID,
          clientSecret: env.LINEAR_CLIENT_SECRET,
          discoveryUrl: "https://linear.app/.well-known/openid-configuration",
          scopes: ["openid", "email", "profile"],
          pkce: true, // Recommended
        },
      ],
    }),
  ],
});
```

**Callback URL pattern**: `{baseURL}/api/auth/oauth2/callback/{providerId}`

---

## Rate Limiting

Built-in rate limiting with customizable rules:

```typescript
export const auth = betterAuth({
  rateLimit: {
    window: 60,  // seconds (default: 60)
    max: 100,    // requests per window (default: 100)

    // Custom rules for sensitive endpoints
    customRules: {
      "/sign-in/email": { window: 10, max: 3 },
      "/two-factor/*": { window: 10, max: 3 },
      "/forget-password": { window: 60, max: 5 },
    },

    // Use Redis/KV for distributed systems
    storage: "secondary-storage", // or "database"
  },

  // Secondary storage for rate limiting
  secondaryStorage: {
    get: async (key) => env.KV.get(key),
    set: async (key, value, ttl) => env.KV.put(key, value, { expirationTtl: ttl }),
    delete: async (key) => env.KV.delete(key),
  },
});
```

**Note**: Server-side calls via `auth.api.*` bypass rate limiting.

---

## Stateless Sessions (v1.4.0+)

Store sessions entirely in signed cookies without database storage:

```typescript
export const auth = betterAuth({
  session: {
    // Stateless: No database storage, session lives in cookie only
    storage: undefined, // or omit entirely

    // Cookie configuration
    cookieCache: {
      enabled: true,
      maxAge: 60 * 60 * 24 * 7, // 7 days
      encoding: "jwt", // Use JWT for stateless (not "compact")
    },

    // Session expiration
    expiresIn: 60 * 60 * 24 * 7, // 7 days
  },
});
```

**When to Use:**

| Storage Type | Use Case | Tradeoffs |
|--------------|----------|-----------|
| **Stateless (cookie-only)** | Read-heavy apps, edge/serverless, no revocation needed | Can't revoke sessions, limited payload size |
| **D1 Database** | Full session management, audit trails, revocation | Eventual consistency issues |
| **KV Storage** | Strong consistency, high read performance | Extra binding setup |

**Key Points:**
- Stateless sessions can't be revoked (user must wait for expiry)
- Cookie size limit ~4KB (limits session data)
- Use `encoding: "jwt"` for interoperability, `"jwe"` for encrypted
- Server must have consistent `BETTER_AUTH_SECRET` across all instances

---

## JWT Key Rotation (v1.4.0+)

Automatically rotate JWT signing keys for enhanced security:

```typescript
import { jwt } from "better-auth/plugins";

export const auth = betterAuth({
  plugins: [
    jwt({
      // Key rotation (optional, enterprise security)
      keyRotation: {
        enabled: true,
        rotationInterval: 60 * 60 * 24 * 30, // Rotate every 30 days
        keepPreviousKeys: 3, // Keep 3 old keys for validation
      },

      // Custom signing algorithm (default: HS256)
      algorithm: "RS256", // Requires asymmetric keys

      // JWKS endpoint (auto-generated at /api/auth/jwks)
      exposeJWKS: true,
    }),
  ],
});
```

**Key Points:**
- Key rotation prevents compromised key from having indefinite validity
- Old keys are kept temporarily to validate existing tokens
- JWKS endpoint at `/api/auth/jwks` for external services
- Use RS256 for public key verification (microservices)
- HS256 (default) for single-service apps

---

## Provider Scopes Reference

Common OAuth providers and the scopes needed for user data:

| Provider | Scope | Returns |
|----------|-------|---------|
| **Google** | `openid` | User ID only |
| | `email` | Email address, email_verified |
| | `profile` | Name, avatar (picture), locale |
| **GitHub** | `user:email` | Email address (may be private) |
| | `read:user` | Name, avatar, profile URL, bio |
| **Microsoft** | `openid` | User ID only |
| | `email` | Email address |
| | `profile` | Name, locale |
| | `User.Read` | Full profile from Graph API |
| **Discord** | `identify` | Username, avatar, discriminator |
| | `email` | Email address |
| **Apple** | `name` | First/last name (first auth only) |
| | `email` | Email or relay address |
| **Patreon** | `identity` | User ID, name |
| | `identity[email]` | Email address |
| **Vercel** | (auto) | Email, name, avatar |

**Configuration Example:**

```typescript
socialProviders: {
  google: {
    clientId: env.GOOGLE_CLIENT_ID,
    clientSecret: env.GOOGLE_CLIENT_SECRET,
    scope: ["openid", "email", "profile"], // All user data
  },
  github: {
    clientId: env.GITHUB_CLIENT_ID,
    clientSecret: env.GITHUB_CLIENT_SECRET,
    scope: ["user:email", "read:user"], // Email + full profile
  },
  microsoft: {
    clientId: env.MS_CLIENT_ID,
    clientSecret: env.MS_CLIENT_SECRET,
    scope: ["openid", "email", "profile", "User.Read"],
  },
}
```

---

## Session Cookie Caching

Three encoding strategies for session cookies:

| Strategy | Format | Use Case |
|----------|--------|----------|
| **Compact** (default) | Base64url + HMAC-SHA256 | Smallest, fastest |
| **JWT** | Standard JWT | Interoperable |
| **JWE** | A256CBC-HS512 encrypted | Most secure |

```typescript
export const auth = betterAuth({
  session: {
    cookieCache: {
      enabled: true,
      maxAge: 300, // 5 minutes
      encoding: "compact", // or "jwt" or "jwe"
    },
    freshAge: 60 * 60 * 24, // 1 day - operations requiring fresh session
  },
});
```

**Fresh sessions**: Some sensitive operations require recently created sessions. Configure `freshAge` to control this window.

---

## New Social Providers (v1.4.9+)

```typescript
socialProviders: {
  // Patreon - Creator economy
  patreon: {
    clientId: env.PATREON_CLIENT_ID,
    clientSecret: env.PATREON_CLIENT_SECRET,
    scope: ["identity", "identity[email]"],
  },

  // Kick - Streaming platform (with refresh tokens)
  kick: {
    clientId: env.KICK_CLIENT_ID,
    clientSecret: env.KICK_CLIENT_SECRET,
  },

  // Vercel - Developer platform
  vercel: {
    clientId: env.VERCEL_CLIENT_ID,
    clientSecret: env.VERCEL_CLIENT_SECRET,
  },
}
```

---

## Cloudflare Workers Requirements

**⚠️ CRITICAL**: Cloudflare Workers require AsyncLocalStorage support:

```toml
# wrangler.toml
compatibility_flags = ["nodejs_compat"]
# or for older Workers:
# compatibility_flags = ["nodejs_als"]
```

Without this flag, better-auth will fail with context-related errors.

---

## Database Hooks

Execute custom logic during database operations:

```typescript
export const auth = betterAuth({
  databaseHooks: {
    user: {
      create: {
        before: async (user, ctx) => {
          // Validate or modify before creation
          if (user.email?.endsWith("@blocked.com")) {
            throw new APIError("BAD_REQUEST", { message: "Email domain not allowed" });
          }
          return { data: { ...user, role: "member" } };
        },
        after: async (user, ctx) => {
          // Send welcome email, create related records, etc.
          await sendWelcomeEmail(user.email);
          await createDefaultWorkspace(user.id);
        },
      },
    },
    session: {
      create: {
        after: async (session, ctx) => {
          // Audit logging
          await auditLog.create({ action: "session_created", userId: session.userId });
        },
      },
    },
  },
});
```

**Available hooks**: `create`, `update` for `user`, `session`, `account`, `verification` tables.

---

## Expo/React Native Integration

Complete mobile integration pattern:

```typescript
// Client setup with secure storage
import { expoClient } from "@better-auth/expo";
import * as SecureStore from "expo-secure-store";

const authClient = createAuthClient({
  baseURL: "https://api.example.com",
  plugins: [expoClient({ storage: SecureStore })],
});

// OAuth with deep linking
await authClient.signIn.social({
  provider: "google",
  callbackURL: "myapp://auth/callback", // Deep link
});

// Or use ID token verification (no redirect)
await authClient.signIn.social({
  provider: "google",
  idToken: {
    token: googleIdToken,
    nonce: generatedNonce,
  },
});

// Authenticated requests
const cookie = await authClient.getCookie();
await fetch("https://api.example.com/data", {
  headers: { Cookie: cookie },
  credentials: "omit",
});
```

**app.json deep link setup**:
```json
{
  "expo": {
    "scheme": "myapp"
  }
}
```

**Server trustedOrigins** (development):
```typescript
trustedOrigins: ["exp://**", "myapp://"]
```

---

## API Reference

### Overview: What You Get For Free

When you call `auth.handler()`, better-auth automatically exposes **80+ production-ready REST endpoints** at `/api/auth/*`. Every endpoint is also available as a **server-side method** via `auth.api.*` for programmatic use.

This dual-layer API system means:
- **Clients** (React, Vue, mobile apps) call HTTP endpoints directly
- **Server-side code** (middleware, background jobs) uses `auth.api.*` methods
- **Zero boilerplate** - no need to write auth endpoints manually

**Time savings**: Building this from scratch = ~220 hours. With better-auth = ~4-8 hours. **97% reduction.**

---

### Auto-Generated HTTP Endpoints

All endpoints are automatically exposed at `/api/auth/*` when using `auth.handler()`.

#### Core Authentication Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sign-up/email` | POST | Register with email/password |
| `/sign-in/email` | POST | Authenticate with email/password |
| `/sign-out` | POST | Logout user |
| `/change-password` | POST | Update password (requires current password) |
| `/forget-password` | POST | Initiate password reset flow |
| `/reset-password` | POST | Complete password reset with token |
| `/send-verification-email` | POST | Send email verification link |
| `/verify-email` | GET | Verify email with token (`?token=<token>`) |
| `/get-session` | GET | Retrieve current session |
| `/list-sessions` | GET | Get all active user sessions |
| `/revoke-session` | POST | End specific session |
| `/revoke-other-sessions` | POST | End all sessions except current |
| `/revoke-sessions` | POST | End all user sessions |
| `/update-user` | POST | Modify user profile (name, image) |
| `/change-email` | POST | Update email address |
| `/set-password` | POST | Add password to OAuth-only account |
| `/delete-user` | POST | Remove user account |
| `/list-accounts` | GET | Get linked authentication providers |
| `/link-social` | POST | Connect OAuth provider to account |
| `/unlink-account` | POST | Disconnect provider |

#### Social OAuth Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/sign-in/social` | POST | Initiate OAuth flow (provider specified in body) |
| `/callback/:provider` | GET | OAuth callback handler (e.g., `/callback/google`) |
| `/get-access-token` | GET | Retrieve provider access token |

**Example OAuth flow**:
```typescript
// Client initiates
await authClient.signIn.social({
  provider: "google",
  callbackURL: "/dashboard",
});

// better-auth handles redirect to Google
// Google redirects back to /api/auth/callback/google
// better-auth creates session automatically
```

---

#### Plugin Endpoints

##### Two-Factor Authentication (2FA Plugin)

```typescript
import { twoFactor } from "better-auth/plugins";
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/two-factor/enable` | POST | Activate 2FA for user |
| `/two-factor/disable` | POST | Deactivate 2FA |
| `/two-factor/get-totp-uri` | GET | Get QR code URI for authenticator app |
| `/two-factor/verify-totp` | POST | Validate TOTP code from authenticator |
| `/two-factor/send-otp` | POST | Send OTP via email |
| `/two-factor/verify-otp` | POST | Validate email OTP |
| `/two-factor/generate-backup-codes` | POST | Create recovery codes |
| `/two-factor/verify-backup-code` | POST | Use backup code for login |
| `/two-factor/view-backup-codes` | GET | View current backup codes |

📚 **Docs**: https://www.better-auth.com/docs/plugins/2fa

##### Organization Plugin (Multi-Tenant SaaS)

```typescript
import { organization } from "better-auth/plugins";
```

**Organizations** (10 endpoints):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/organization/create` | POST | Create organization |
| `/organization/list` | GET | List user's organizations |
| `/organization/get-full` | GET | Get complete org details |
| `/organization/update` | PUT | Modify organization |
| `/organization/delete` | DELETE | Remove organization |
| `/organization/check-slug` | GET | Verify slug availability |
| `/organization/set-active` | POST | Set active organization context |

**Members** (8 endpoints):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/organization/list-members` | GET | Get organization members |
| `/organization/add-member` | POST | Add member directly |
| `/organization/remove-member` | DELETE | Remove member |
| `/organization/update-member-role` | PUT | Change member role |
| `/organization/get-active-member` | GET | Get current member info |
| `/organization/leave` | POST | Leave organization |

**Invitations** (7 endpoints):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/organization/invite-member` | POST | Send invitation email |
| `/organization/accept-invitation` | POST | Accept invite |
| `/organization/reject-invitation` | POST | Reject invite |
| `/organization/cancel-invitation` | POST | Cancel pending invite |
| `/organization/get-invitation` | GET | Get invitation details |
| `/organization/list-invitations` | GET | List org invitations |
| `/organization/list-user-invitations` | GET | List user's pending invites |

**Teams** (8 endpoints):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/organization/create-team` | POST | Create team within org |
| `/organization/list-teams` | GET | List organization teams |
| `/organization/update-team` | PUT | Modify team |
| `/organization/remove-team` | DELETE | Remove team |
| `/organization/set-active-team` | POST | Set active team context |
| `/organization/list-team-members` | GET | List team members |
| `/organization/add-team-member` | POST | Add member to team |
| `/organization/remove-team-member` | DELETE | Remove team member |

**Permissions & Roles** (6 endpoints):

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/organization/has-permission` | POST | Check if user has permission |
| `/organization/create-role` | POST | Create custom role |
| `/organization/delete-role` | DELETE | Delete custom role |
| `/organization/list-roles` | GET | List all roles |
| `/organization/get-role` | GET | Get role details |
| `/organization/update-role` | PUT | Modify role permissions |

📚 **Docs**: https://www.better-auth.com/docs/plugins/organization

##### Admin Plugin

```typescript
import { admin } from "better-auth/plugins";

// v1.4.10 configuration options
admin({
  defaultRole: "user",
  adminRoles: ["admin"],
  adminUserIds: ["user_abc123"], // Always grant admin to specific users
  impersonationSessionDuration: 3600, // 1 hour (seconds)
  allowImpersonatingAdmins: false, // ⚠️ Default changed in v1.4.6
  defaultBanReason: "Violation of Terms of Service",
  bannedUserMessage: "Your account has been suspended",
})
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/admin/create-user` | POST | Create user as admin |
| `/admin/list-users` | GET | List all users (with filters/pagination) |
| `/admin/set-role` | POST | Assign user role |
| `/admin/set-user-password` | POST | Change user password |
| `/admin/update-user` | PUT | Modify user details |
| `/admin/remove-user` | DELETE | Delete user account |
| `/admin/ban-user` | POST | Ban user account (with optional expiry) |
| `/admin/unban-user` | POST | Unban user |
| `/admin/list-user-sessions` | GET | Get user's active sessions |
| `/admin/revoke-user-session` | DELETE | End specific user session |
| `/admin/revoke-user-sessions` | DELETE | End all user sessions |
| `/admin/impersonate-user` | POST | Start impersonating user |
| `/admin/stop-impersonating` | POST | End impersonation session |

**⚠️ Breaking Change (v1.4.6)**: `allowImpersonatingAdmins` now defaults to `false`. Set to `true` explicitly if you need admin-on-admin impersonation.

**Custom Roles with Permissions (v1.4.10):**

```typescript
import { createAccessControl } from "better-auth/plugins/access";

// Define resources and permissions
const ac = createAccessControl({
  user: ["create", "read", "update", "delete", "ban", "impersonate"],
  project: ["create", "read", "update", "delete", "share"],
} as const);

// Create custom roles
const supportRole = ac.newRole({
  user: ["read", "ban"],      // Can view and ban users
  project: ["read"],          // Can view projects
});

const managerRole = ac.newRole({
  user: ["read", "update"],
  project: ["create", "read", "update", "delete"],
});

// Use in plugin
admin({
  ac,
  roles: {
    support: supportRole,
    manager: managerRole,
  },
})
```

📚 **Docs**: https://www.better-auth.com/docs/plugins/admin

##### Other Plugin Endpoints

**Passkey Plugin** (5 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/passkey):
- `/passkey/add`, `/sign-in/passkey`, `/passkey/list`, `/passkey/delete`, `/passkey/update`

**Magic Link Plugin** (2 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/magic-link):
- `/sign-in/magic-link`, `/magic-link/verify`

**Username Plugin** (2 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/username):
- `/sign-in/username`, `/username/is-available`

**Phone Number Plugin** (5 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/phone-number):
- `/sign-in/phone-number`, `/phone-number/send-otp`, `/phone-number/verify`, `/phone-number/request-password-reset`, `/phone-number/reset-password`

**Email OTP Plugin** (6 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/email-otp):
- `/email-otp/send-verification-otp`, `/email-otp/check-verification-otp`, `/sign-in/email-otp`, `/email-otp/verify-email`, `/forget-password/email-otp`, `/email-otp/reset-password`

**Anonymous Plugin** (1 endpoint) - [Docs](https://www.better-auth.com/docs/plugins/anonymous):
- `/sign-in/anonymous`

**JWT Plugin** (2 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/jwt):
- `/token` (get JWT), `/jwks` (public key for verification)

**OpenAPI Plugin** (2 endpoints) - [Docs](https://www.better-auth.com/docs/plugins/open-api):
- `/reference` (interactive API docs with Scalar UI)
- `/generate-openapi-schema` (get OpenAPI spec as JSON)

---

### Server-Side API Methods (`auth.api.*`)

Every HTTP endpoint has a corresponding server-side method. Use these for:
- **Server-side middleware** (protecting routes)
- **Background jobs** (user cleanup, notifications)
- **Admin operations** (bulk user management)
- **Custom auth flows** (programmatic session creation)

#### Core API Methods

```typescript
// Authentication
await auth.api.signUpEmail({
  body: { email, password, name },
  headers: request.headers,
});

await auth.api.signInEmail({
  body: { email, password, rememberMe: true },
  headers: request.headers,
});

await auth.api.signOut({ headers: request.headers });

// Session Management
const session = await auth.api.getSession({ headers: request.headers });

await auth.api.listSessions({ headers: request.headers });

await auth.api.revokeSession({
  body: { token: "session_token_here" },
  headers: request.headers,
});

// User Management
await auth.api.updateUser({
  body: { name: "New Name", image: "https://..." },
  headers: request.headers,
});

await auth.api.changeEmail({
  body: { newEmail: "newemail@example.com" },
  headers: request.headers,
});

await auth.api.deleteUser({
  body: { password: "current_password" },
  headers: request.headers,
});

// Account Linking
await auth.api.linkSocialAccount({
  body: { provider: "google" },
  headers: request.headers,
});

await auth.api.unlinkAccount({
  body: { providerId: "google", accountId: "google_123" },
  headers: request.headers,
});
```

#### Plugin API Methods

**2FA Plugin**:
```typescript
// Enable 2FA
const { totpUri, backupCodes } = await auth.api.enableTwoFactor({
  body: { issuer: "MyApp" },
  headers: request.headers,
});

// Verify TOTP code
await auth.api.verifyTOTP({
  body: { code: "123456", trustDevice: true },
  headers: request.headers,
});

// Generate backup codes
const { backupCodes } = await auth.api.generateBackupCodes({
  headers: request.headers,
});
```

**Organization Plugin**:
```typescript
// Create organization
const org = await auth.api.createOrganization({
  body: { name: "Acme Corp", slug: "acme" },
  headers: request.headers,
});

// Add member
await auth.api.addMember({
  body: {
    userId: "user_123",
    role: "admin",
    organizationId: org.id,
  },
  headers: request.headers,
});

// Check permissions
const hasPermission = await auth.api.hasPermission({
  body: {
    organizationId: org.id,
    permission: "users:delete",
  },
  headers: request.headers,
});
```

**Admin Plugin**:
```typescript
// List users with pagination
const users = await auth.api.listUsers({
  query: {
    search: "john",
    limit: 10,
    offset: 0,
    sortBy: "createdAt",
    sortOrder: "desc",
  },
  headers: request.headers,
});

// Ban user
await auth.api.banUser({
  body: {
    userId: "user_123",
    reason: "Violation of ToS",
    expiresAt: new Date("2025-12-31"),
  },
  headers: request.headers,
});

// Impersonate user (for admin support)
const impersonationSession = await auth.api.impersonateUser({
  body: {
    userId: "user_123",
    expiresIn: 3600, // 1 hour
  },
  headers: request.headers,
});
```

---

### When to Use Which

| Use Case | Use HTTP Endpoints | Use `auth.api.*` Methods |
|----------|-------------------|--------------------------|
| **Client-side auth** | ✅ Yes | ❌ No |
| **Server middleware** | ❌ No | ✅ Yes |
| **Background jobs** | ❌ No | ✅ Yes |
| **Admin dashboards** | ✅ Yes (from client) | ✅ Yes (from server) |
| **Custom auth flows** | ❌ No | ✅ Yes |
| **Mobile apps** | ✅ Yes | ❌ No |
| **API routes** | ✅ Yes (proxy to handler) | ✅ Yes (direct calls) |

**Example: Protected Route Middleware**

```typescript
import { Hono } from "hono";
import { createAuth } from "./auth";
import { createDatabase } from "./db";

const app = new Hono<{ Bindings: Env }>();

// Middleware using server-side API
app.use("/api/protected/*", async (c, next) => {
  const db = createDatabase(c.env.DB);
  const auth = createAuth(db, c.env);

  // Use server-side method
  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Attach to context
  c.set("user", session.user);
  c.set("session", session.session);

  await next();
});

// Protected route
app.get("/api/protected/profile", async (c) => {
  const user = c.get("user");
  return c.json({ user });
});
```

---

### Discovering Available Endpoints

Use the **OpenAPI plugin** to see all endpoints in your configuration:

```typescript
import { betterAuth } from "better-auth";
import { openAPI } from "better-auth/plugins";

export const auth = betterAuth({
  database: /* ... */,
  plugins: [
    openAPI(), // Adds /api/auth/reference endpoint
  ],
});
```

**Interactive documentation**: Visit `http://localhost:8787/api/auth/reference`

This shows a **Scalar UI** with:
- ✅ All available endpoints grouped by feature
- ✅ Request/response schemas with types
- ✅ Try-it-out functionality (test endpoints in browser)
- ✅ Authentication requirements
- ✅ Code examples in multiple languages

**Programmatic access**:
```typescript
const schema = await auth.api.generateOpenAPISchema();
console.log(JSON.stringify(schema, null, 2));
// Returns full OpenAPI 3.0 spec
```

---

### Quantified Time Savings

**Building from scratch** (manual implementation):
- Core auth endpoints (sign-up, sign-in, OAuth, sessions): **40 hours**
- Email verification & password reset: **10 hours**
- 2FA system (TOTP, backup codes, email OTP): **20 hours**
- Organizations (teams, invitations, RBAC): **60 hours**
- Admin panel (user management, impersonation): **30 hours**
- Testing & debugging: **50 hours**
- Security hardening: **20 hours**

**Total manual effort**: **~220 hours** (5.5 weeks full-time)

**With better-auth**:
- Initial setup: **2-4 hours**
- Customization & styling: **2-4 hours**

**Total with better-auth**: **4-8 hours**

**Savings**: **~97% development time**

---

### Key Takeaway

better-auth provides **80+ production-ready endpoints** covering:
- ✅ Core authentication (20 endpoints)
- ✅ 2FA & passwordless (15 endpoints)
- ✅ Organizations & teams (35 endpoints)
- ✅ Admin & user management (15 endpoints)
- ✅ Social OAuth (auto-configured callbacks)
- ✅ OpenAPI documentation (interactive UI)

**You write zero endpoint code.** Just configure features and call `auth.handler()`.

---

## Known Issues & Solutions

### Issue 1: "d1Adapter is not exported" Error

**Problem**: Code shows `import { d1Adapter } from 'better-auth/adapters/d1'` but this doesn't exist.

**Symptoms**: TypeScript error or runtime error about missing export.

**Solution**: Use Drizzle or Kysely instead:

```typescript
// ❌ WRONG - This doesn't exist
import { d1Adapter } from 'better-auth/adapters/d1'
database: d1Adapter(env.DB)

// ✅ CORRECT - Use Drizzle
import { drizzleAdapter } from 'better-auth/adapters/drizzle'
import { drizzle } from 'drizzle-orm/d1'
const db = drizzle(env.DB, { schema })
database: drizzleAdapter(db, { provider: "sqlite" })

// ✅ CORRECT - Use Kysely
import { Kysely } from 'kysely'
import { D1Dialect } from 'kysely-d1'
database: {
  db: new Kysely({ dialect: new D1Dialect({ database: env.DB }) }),
  type: "sqlite"
}
```

**Source**: Verified from 4 production repositories using better-auth + D1

---

### Issue 2: Schema Generation Fails

**Problem**: `npx better-auth migrate` doesn't create D1-compatible schema.

**Symptoms**: Migration SQL has wrong syntax or doesn't work with D1.

**Solution**: Use Drizzle Kit to generate migrations:

```bash
# Generate migration from Drizzle schema
npx drizzle-kit generate

# Apply to D1
wrangler d1 migrations apply my-app-db --remote
```

**Why**: Drizzle Kit generates SQLite-compatible SQL that works with D1.

---

### Issue 3: "CamelCase" vs "snake_case" Column Mismatch

**Problem**: Database has `email_verified` but better-auth expects `emailVerified`.

**Symptoms**: Session reads fail, user data missing fields.

**⚠️ CRITICAL (v1.4.10+)**: Using Kysely's `CamelCasePlugin` **breaks join parsing** in better-auth adapter. The plugin converts join keys like `_joined_user_user_id` to `_joinedUserUserId`, causing user data to be null in session queries.

**Solution for Drizzle**: Define schema with camelCase from the start (as shown in examples).

**Solution for Kysely with CamelCasePlugin**: Use **separate Kysely instance** without CamelCasePlugin for better-auth:

```typescript
// DB for better-auth (no CamelCasePlugin)
const authDb = new Kysely({
  dialect: new D1Dialect({ database: env.DB }),
})

// DB for app queries (with CamelCasePlugin)
const appDb = new Kysely({
  dialect: new D1Dialect({ database: env.DB }),
  plugins: [new CamelCasePlugin()],
})

export const auth = betterAuth({
  database: { db: authDb, type: "sqlite" },
})
```

**Source**: [GitHub Issue #7136](https://github.com/better-auth/better-auth/issues/7136)

---

### Issue 4: D1 Eventual Consistency

**Problem**: Session reads immediately after write return stale data.

**Symptoms**: User logs in but `getSession()` returns null on next request.

**Solution**: Use Cloudflare KV for session storage (strong consistency):

```typescript
import { betterAuth } from "better-auth";

export function createAuth(db: Database, env: Env) {
  return betterAuth({
    database: drizzleAdapter(db, { provider: "sqlite" }),
    session: {
      storage: {
        get: async (sessionId) => {
          const session = await env.SESSIONS_KV.get(sessionId);
          return session ? JSON.parse(session) : null;
        },
        set: async (sessionId, session, ttl) => {
          await env.SESSIONS_KV.put(sessionId, JSON.stringify(session), {
            expirationTtl: ttl,
          });
        },
        delete: async (sessionId) => {
          await env.SESSIONS_KV.delete(sessionId);
        },
      },
    },
  });
}
```

**Add to `wrangler.toml`**:
```toml
[[kv_namespaces]]
binding = "SESSIONS_KV"
id = "your-kv-namespace-id"
```

---

### Issue 5: CORS Errors for SPA Applications

**Problem**: CORS errors when auth API is on different origin than frontend.

**Symptoms**: `Access-Control-Allow-Origin` errors in browser console.

**Solution**: Configure CORS headers in Worker and ensure `trustedOrigins` match:

```typescript
import { cors } from "hono/cors";

// CRITICAL: Both must match frontend origin exactly
app.use(
  "/api/auth/*",
  cors({
    origin: "http://localhost:5173", // Frontend URL (no trailing slash)
    credentials: true, // Allow cookies
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
  })
);

// And in better-auth config
export const auth = betterAuth({
  trustedOrigins: ["http://localhost:5173"], // Same as CORS origin
  // ...
});
```

**Common Mistakes**:
- Typo in origin URL (trailing slash, http vs https, wrong port)
- Mismatched origins between CORS config and `trustedOrigins`
- CORS middleware registered AFTER auth routes (must be before)

**Source**: [GitHub Issue #7434](https://github.com/better-auth/better-auth/issues/7434)

---

### Issue 6: OAuth Redirect URI Mismatch

**Problem**: Social sign-in fails with "redirect_uri_mismatch" error.

**Symptoms**: Google/GitHub OAuth returns error after user consent.

**Solution**: Ensure exact match in OAuth provider settings:

```
Provider setting: https://yourdomain.com/api/auth/callback/google
better-auth URL:  https://yourdomain.com/api/auth/callback/google

❌ Wrong: http vs https, trailing slash, subdomain mismatch
✅ Right: Exact character-for-character match
```

**Check better-auth callback URL**:
```typescript
// It's always: {baseURL}/api/auth/callback/{provider}
const callbackURL = `${env.BETTER_AUTH_URL}/api/auth/callback/google`;
console.log("Configure this URL in Google Console:", callbackURL);
```

---

### Issue 7: Missing Dependencies

**Problem**: TypeScript errors or runtime errors about missing packages.

**Symptoms**: `Cannot find module 'drizzle-orm'` or similar.

**Solution**: Install all required packages:

**For Drizzle approach**:
```bash
npm install better-auth drizzle-orm drizzle-kit @cloudflare/workers-types
```

**For Kysely approach**:
```bash
npm install better-auth kysely kysely-d1 @cloudflare/workers-types
```

---

### Issue 8: Email Verification Not Sending

**Problem**: Email verification links never arrive.

**Symptoms**: User signs up, but no email received.

**Solution**: Implement `sendVerificationEmail` handler:

```typescript
export const auth = betterAuth({
  database: /* ... */,
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: true,
  },
  emailVerification: {
    sendVerificationEmail: async ({ user, url }) => {
      // Use your email service (SendGrid, Resend, etc.)
      await sendEmail({
        to: user.email,
        subject: "Verify your email",
        html: `
          <p>Click the link below to verify your email:</p>
          <a href="${url}">Verify Email</a>
        `,
      });
    },
    sendOnSignUp: true,
    autoSignInAfterVerification: true,
    expiresIn: 3600, // 1 hour
  },
});
```

**For Cloudflare**: Use Cloudflare Email Routing or external service (Resend, SendGrid).

---

### Issue 9: Session Expires Too Quickly

**Problem**: Session expires unexpectedly or never expires.

**Symptoms**: User logged out unexpectedly or session persists after logout.

**Solution**: Configure session expiration:

```typescript
export const auth = betterAuth({
  database: /* ... */,
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days (in seconds)
    updateAge: 60 * 60 * 24, // Update session every 24 hours
  },
});
```

---

### Issue 10: Social Provider Missing User Data

**Problem**: Social sign-in succeeds but missing user data (name, avatar).

**Symptoms**: `session.user.name` is null after Google/GitHub sign-in.

**Solution**: Request additional scopes:

```typescript
socialProviders: {
  google: {
    clientId: env.GOOGLE_CLIENT_ID,
    clientSecret: env.GOOGLE_CLIENT_SECRET,
    scope: ["openid", "email", "profile"], // Include 'profile' for name/image
  },
  github: {
    clientId: env.GITHUB_CLIENT_ID,
    clientSecret: env.GITHUB_CLIENT_SECRET,
    scope: ["user:email", "read:user"], // 'read:user' for full profile
  },
}
```

---

### Issue 11: TypeScript Errors with Drizzle Schema

**Problem**: TypeScript complains about schema types.

**Symptoms**: `Type 'DrizzleD1Database' is not assignable to...`

**Solution**: Export proper types from database:

```typescript
// src/db/index.ts
import { drizzle, type DrizzleD1Database } from "drizzle-orm/d1";
import * as schema from "./schema";

export type Database = DrizzleD1Database<typeof schema>;

export function createDatabase(d1: D1Database): Database {
  return drizzle(d1, { schema });
}
```

---

### Issue 12: Wrangler Dev Mode Not Working

**Problem**: `wrangler dev` fails with database errors.

**Symptoms**: "Database not found" or migration errors in local dev.

**Solution**: Apply migrations locally first:

```bash
# Apply migrations to local D1
wrangler d1 migrations apply my-app-db --local

# Then run dev server
wrangler dev
```

---

### Issue 13: User Data Updates Not Reflecting in UI (with TanStack Query)

**Problem**: After updating user data (e.g., avatar, name), changes don't appear in `useSession()` despite calling `queryClient.invalidateQueries()`.

**Symptoms**: Avatar image or user profile data appears stale after successful update. TanStack Query cache shows updated data, but better-auth session still shows old values.

**Root Cause**: better-auth uses **nanostores** for session state management, not TanStack Query. Calling `queryClient.invalidateQueries()` only invalidates React Query cache, not the better-auth nanostore.

**Solution**: Manually notify the nanostore after updating user data:

```typescript
// Update user data
const { data, error } = await authClient.updateUser({
  image: newAvatarUrl,
  name: newName
})

if (!error) {
  // Manually invalidate better-auth session state
  authClient.$store.notify('$sessionSignal')

  // Optional: Also invalidate React Query if using it for other data
  queryClient.invalidateQueries({ queryKey: ['user-profile'] })
}
```

**When to use**:
- Using better-auth + TanStack Query together
- Updating user profile fields (name, image, email)
- Any operation that modifies session user data client-side

**Alternative**: Call `refetch()` from `useSession()`, but `$store.notify()` is more direct:

```typescript
const { data: session, refetch } = authClient.useSession()
// After update
await refetch()
```

**Note**: `$store` is an undocumented internal API. This pattern is production-validated but may change in future better-auth versions.

**Source**: Community-discovered pattern, production use verified

---

### Issue 14: apiKey Table Schema Mismatch with D1

**Problem**: better-auth CLI (`npx @better-auth/cli generate`) fails with "Failed to initialize database adapter" when using D1.

**Symptoms**: CLI cannot connect to D1 to introspect schema. Running migrations through CLI doesn't work.

**Root Cause**: The CLI expects a direct SQLite connection, but D1 requires Cloudflare's binding API.

**Solution**: Skip the CLI and create migrations manually using the documented apiKey schema:

```sql
CREATE TABLE api_key (
  id TEXT PRIMARY KEY NOT NULL,
  user_id TEXT NOT NULL REFERENCES user(id) ON DELETE CASCADE,
  name TEXT,
  start TEXT,
  prefix TEXT,
  key TEXT NOT NULL,
  enabled INTEGER DEFAULT 1,
  rate_limit_enabled INTEGER,
  rate_limit_time_window INTEGER,
  rate_limit_max INTEGER,
  request_count INTEGER DEFAULT 0,
  last_request INTEGER,
  remaining INTEGER,
  refill_interval INTEGER,
  refill_amount INTEGER,
  last_refill_at INTEGER,
  expires_at INTEGER,
  permissions TEXT,
  metadata TEXT,
  created_at INTEGER NOT NULL,
  updated_at INTEGER NOT NULL
);
```

**Key Points**:
- The table has exactly **21 columns** (as of better-auth v1.4+)
- Column names use `snake_case` (e.g., `rate_limit_time_window`, not `rateLimitTimeWindow`)
- D1 doesn't support `ALTER TABLE DROP COLUMN` - if schema drifts, use fresh migration pattern (drop and recreate tables)
- In Drizzle adapter config, use `apikey` (lowercase) as the table name mapping

**Fresh Migration Pattern for D1**:
```sql
-- Drop in reverse dependency order
DROP TABLE IF EXISTS api_key;
DROP TABLE IF EXISTS session;
-- ... other tables

-- Recreate with clean schema
CREATE TABLE api_key (...);
```

**Source**: Production debugging with D1 + better-auth apiKey plugin

---

### Issue 15: Admin Plugin Requires DB Role (Dual-Auth)

**Problem**: Admin plugin methods like `listUsers` fail with "You are not allowed to list users" even though your middleware passes.

**Symptoms**: Custom `requireAdmin` middleware (checking ADMIN_EMAILS env var) passes, but `auth.api.listUsers()` returns 403.

**Root Cause**: better-auth admin plugin has **two** authorization layers:
1. **Your middleware** - Custom check (e.g., ADMIN_EMAILS)
2. **better-auth internal** - Checks `user.role === 'admin'` in database

Both must pass for admin plugin methods to work.

**Solution**: Set user role to 'admin' in the database:

```sql
-- Fix for existing users
UPDATE user SET role = 'admin' WHERE email = 'admin@example.com';
```

Or use the admin UI/API to set roles after initial setup.

**Why**: The admin plugin's `listUsers`, `banUser`, `impersonateUser`, etc. all check `user.role` in the database, not your custom middleware logic.

**Source**: Production debugging - misleading error message led to root cause discovery via `wrangler tail`

---

### Issue 16: Organization/Team updated_at Must Be Nullable

**Problem**: Organization creation fails with SQL constraint error even though API returns "slug already exists".

**Symptoms**:
- Error message says "An organization with this slug already exists"
- Database table is actually empty
- `wrangler tail` shows: `Failed query: insert into "organization" ... values (?, ?, ?, null, null, ?, null)`

**Root Cause**: better-auth inserts `null` for `updated_at` on creation (only sets it on updates). If your schema has `NOT NULL` constraint, insert fails.

**Solution**: Make `updated_at` nullable in both schema and migrations:

```typescript
// Drizzle schema - CORRECT
export const organization = sqliteTable('organization', {
  // ...
  updatedAt: integer('updated_at', { mode: 'timestamp' }), // No .notNull()
});

export const team = sqliteTable('team', {
  // ...
  updatedAt: integer('updated_at', { mode: 'timestamp' }), // No .notNull()
});
```

```sql
-- Migration - CORRECT
CREATE TABLE organization (
  -- ...
  updated_at INTEGER  -- No NOT NULL
);
```

**Applies to**: `organization` and `team` tables (possibly other plugin tables)

**Source**: Production debugging - `wrangler tail` revealed actual SQL error behind misleading "slug exists" message

---

### Issue 17: API Response Double-Nesting (listMembers, etc.)

**Problem**: Custom API endpoints return double-nested data like `{ members: { members: [...], total: N } }`.

**Symptoms**: UI shows "undefined" for counts, empty lists despite data existing.

**Root Cause**: better-auth methods like `listMembers` return `{ members: [...], total: N }`. Wrapping with `c.json({ members: result })` creates double nesting.

**Solution**: Extract the array from better-auth response:

```typescript
// ❌ WRONG - Double nesting
const result = await auth.api.listMembers({ ... });
return c.json({ members: result });
// Returns: { members: { members: [...], total: N } }

// ✅ CORRECT - Extract array
const result = await auth.api.listMembers({ ... });
const members = result?.members || [];
return c.json({ members });
// Returns: { members: [...] }
```

**Affected methods** (return objects, not arrays):
- `listMembers` → `{ members: [...], total: N }`
- `listUsers` → `{ users: [...], total: N, limit: N }`
- `listOrganizations` → `{ organizations: [...] }` (check structure)
- `listInvitations` → `{ invitations: [...] }`

**Pattern**: Always check better-auth method return types before wrapping in your API response.

**Source**: Production debugging - UI showed "undefined" count, API inspection revealed nesting issue

---

### Issue 18: Expo Client fromJSONSchema Crash (v1.4.16)

**Problem**: Importing `expoClient` from `@better-auth/expo/client` crashes with `TypeError: Cannot read property 'fromJSONSchema' of undefined` on v1.4.16.

**Symptoms**: Runtime crash immediately when importing expoClient in React Native/Expo apps.

**Root Cause**: Regression introduced after PR #6933 (cookie-based OAuth state fix for Expo). One of 3 commits after f4a9f15 broke the build.

**Solution**:
- **Temporary**: Use continuous build at commit `f4a9f15` (pre-regression)
- **Permanent**: Wait for fix (issue #7491 open as of 2026-01-20)

```typescript
// Crashes on v1.4.16
import { expoClient } from '@better-auth/expo/client'

// Workaround: Use continuous build at f4a9f15
// Or wait for fix in next release
```

**Source**: [GitHub Issue #7491](https://github.com/better-auth/better-auth/issues/7491)

---

### Issue 19: additionalFields string[] Returns Stringified JSON

**Problem**: After v1.4.12, `additionalFields` with `type: 'string[]'` return stringified arrays (`'["a","b"]'`) instead of native arrays when querying via Drizzle directly.

**Symptoms**: `user.notificationTokens` is a string, not an array. Code expecting arrays breaks.

**Root Cause**: In Drizzle adapter, `string[]` fields are stored with `mode: 'json'`, which expects arrays. But better-auth v1.4.4+ passes strings to Drizzle, causing double-stringification. When querying **directly via Drizzle**, the value is a string, but when using **better-auth `internalAdapter`**, a transformer correctly returns an array.

**Solution**:
1. **Use better-auth `internalAdapter`** instead of querying Drizzle directly (has transformer)
2. **Change Drizzle schema** to `.jsonb()` for string[] fields
3. **Manually parse** JSON strings until fixed

```typescript
// Config
additionalFields: {
  notificationTokens: {
    type: 'string[]',
    required: true,
    input: true,
  },
}

// Create user
notificationTokens: ['token1', 'token2']

// Result in DB (when querying via Drizzle directly)
// '["token1","token2"]' (string, not array)
```

**Source**: [GitHub Issue #7440](https://github.com/better-auth/better-auth/issues/7440)

---

### Issue 20: additionalFields "returned" Property Blocks Input

**Problem**: Setting `returned: false` on `additionalFields` prevents field from being saved via API, even with `input: true`.

**Symptoms**: Field never saved to database when creating/updating via API endpoints.

**Root Cause**: The `returned: false` property blocks both read AND write operations, not just reads as intended. The `input: true` property should control write access independently.

**Solution**:
- Don't use `returned: false` if you need API write access
- Write via server-side methods (`auth.api.*`) instead

```typescript
// Organization plugin config
additionalFields: {
  secretField: {
    type: 'string',
    required: true,
    input: true,      // Should allow API writes
    returned: false,  // Should only block reads, but blocks writes too
  },
}

// API request to create organization
// secretField is never saved to database
```

**Source**: [GitHub Issue #7489](https://github.com/better-auth/better-auth/issues/7489)

---

### Issue 21: freshAge Based on Creation Time, Not Activity

**Problem**: `session.freshAge` checks time-since-creation, NOT recent activity. Active sessions become "not fresh" after `freshAge` elapses, even if used constantly.

**Symptoms**: "Fresh session required" endpoints reject valid active sessions.

**Why It Happens**: The `freshSessionMiddleware` checks `Date.now() - (session.updatedAt || session.createdAt)`, but `updatedAt` only changes when the session is refreshed based on `updateAge`. If `updateAge > freshAge`, the session becomes "not fresh" before `updatedAt` is bumped.

**Solution**:
1. **Set `updateAge <= freshAge`** to ensure freshness is updated before expiry
2. **Avoid "fresh session required"** gating for long-lived sessions
3. **Accept as design**: freshAge is strictly time-since-creation (maintainer confirmed)

```typescript
// Config
session: {
  expiresIn: 60 * 60 * 24 * 7,    // 7 days
  freshAge: 60 * 60 * 24,          // 24 hours
  updateAge: 60 * 60 * 24 * 3,     // 3 days (> freshAge!) ⚠️ PROBLEM

  // CORRECT - updateAge <= freshAge
  updateAge: 60 * 60 * 12,         // 12 hours (< freshAge)
}

// Timeline with bad config:
// T+0h: User signs in (createdAt = now)
// T+12h: User makes requests (session active, still fresh)
// T+25h: User makes request (session active, BUT NOT FRESH - freshAge elapsed)
// Result: "Fresh session required" endpoints reject active session
```

**Source**: [GitHub Issue #7472](https://github.com/better-auth/better-auth/issues/7472)

---

### Issue 22: OAuth Token Endpoints Return Wrapped JSON

**Problem**: OAuth 2.1 and OIDC token endpoints return `{ "response": { ...tokens... } }` instead of spec-compliant top-level JSON. OAuth clients expect `{ "access_token": "...", "token_type": "bearer" }` at root.

**Symptoms**: OAuth clients fail with `Bearer undefined` or `invalid_token`.

**Root Cause**: The endpoint pipeline returns `{ response, headers, status }` for internal use, which gets serialized directly for HTTP requests. This breaks OAuth/OIDC spec requirements.

**Solution**:
- **Temporary**: Manually unwrap `.response` field on client
- **Permanent**: Wait for fix (issue #7355 open, accepting contributions)

```typescript
// Expected (spec-compliant)
{ "access_token": "...", "token_type": "bearer", "expires_in": 3600 }

// Actual (wrapped)
{ "response": { "access_token": "...", "token_type": "bearer", "expires_in": 3600 } }

// Result: OAuth clients fail to parse, send `Bearer undefined`
```

**Source**: [GitHub Issue #7355](https://github.com/better-auth/better-auth/issues/7355)

---

## Migration Guides

### From Clerk

**Key differences**:
- Clerk: Third-party service → better-auth: Self-hosted
- Clerk: Proprietary → better-auth: Open source
- Clerk: Monthly cost → better-auth: Free

**Migration steps**:

1. **Export user data** from Clerk (CSV or API)
2. **Import into better-auth database**:
   ```typescript
   // migration script
   const clerkUsers = await fetchClerkUsers();

   for (const clerkUser of clerkUsers) {
     await db.insert(user).values({
       id: clerkUser.id,
       email: clerkUser.email,
       emailVerified: clerkUser.email_verified,
       name: clerkUser.first_name + " " + clerkUser.last_name,
       image: clerkUser.profile_image_url,
     });
   }
   ```
3. **Replace Clerk SDK** with better-auth client:
   ```typescript
   // Before (Clerk)
   import { useUser } from "@clerk/nextjs";
   const { user } = useUser();

   // After (better-auth)
   import { authClient } from "@/lib/auth-client";
   const { data: session } = authClient.useSession();
   const user = session?.user;
   ```
4. **Update middleware** for session verification
5. **Configure social providers** (same OAuth apps, different config)

---

### From Auth.js (NextAuth)

**Key differences**:
- Auth.js: Limited features → better-auth: Comprehensive (2FA, orgs, etc.)
- Auth.js: Callbacks-heavy → better-auth: Plugin-based
- Auth.js: Session handling varies → better-auth: Consistent

**Migration steps**:

1. **Database schema**: Auth.js and better-auth use similar schemas, but column names differ
2. **Replace configuration**:
   ```typescript
   // Before (Auth.js)
   import NextAuth from "next-auth";
   import GoogleProvider from "next-auth/providers/google";

   export default NextAuth({
     providers: [GoogleProvider({ /* ... */ })],
   });

   // After (better-auth)
   import { betterAuth } from "better-auth";

   export const auth = betterAuth({
     socialProviders: {
       google: { /* ... */ },
     },
   });
   ```
3. **Update client hooks**:
   ```typescript
   // Before
   import { useSession } from "next-auth/react";

   // After
   import { authClient } from "@/lib/auth-client";
   const { data: session } = authClient.useSession();
   ```

---

## Additional Resources

### Official Documentation

- **Homepage**: https://better-auth.com
- **Introduction**: https://www.better-auth.com/docs/introduction
- **Installation**: https://www.better-auth.com/docs/installation
- **Basic Usage**: https://www.better-auth.com/docs/basic-usage

### Core Concepts

- **Session Management**: https://www.better-auth.com/docs/concepts/session-management
- **Users & Accounts**: https://www.better-auth.com/docs/concepts/users-accounts
- **Client SDK**: https://www.better-auth.com/docs/concepts/client
- **Plugins System**: https://www.better-auth.com/docs/concepts/plugins

### Authentication Methods

- **Email & Password**: https://www.better-auth.com/docs/authentication/email-password
- **OAuth Providers**: https://www.better-auth.com/docs/concepts/oauth

### Plugin Documentation

**Core Plugins**:
- **2FA (Two-Factor)**: https://www.better-auth.com/docs/plugins/2fa
- **Organization**: https://www.better-auth.com/docs/plugins/organization
- **Admin**: https://www.better-auth.com/docs/plugins/admin
- **Multi-Session**: https://www.better-auth.com/docs/plugins/multi-session
- **API Key**: https://www.better-auth.com/docs/plugins/api-key
- **Generic OAuth**: https://www.better-auth.com/docs/plugins/generic-oauth

**Passwordless Plugins**:
- **Passkey**: https://www.better-auth.com/docs/plugins/passkey
- **Magic Link**: https://www.better-auth.com/docs/plugins/magic-link
- **Email OTP**: https://www.better-auth.com/docs/plugins/email-otp
- **Phone Number**: https://www.better-auth.com/docs/plugins/phone-number
- **Anonymous**: https://www.better-auth.com/docs/plugins/anonymous

**Advanced Plugins**:
- **Username**: https://www.better-auth.com/docs/plugins/username
- **JWT**: https://www.better-auth.com/docs/plugins/jwt
- **OpenAPI**: https://www.better-auth.com/docs/plugins/open-api
- **OIDC Provider**: https://www.better-auth.com/docs/plugins/oidc-provider
- **SSO**: https://www.better-auth.com/docs/plugins/sso
- **Stripe**: https://www.better-auth.com/docs/plugins/stripe
- **MCP**: https://www.better-auth.com/docs/plugins/mcp

### Framework Integrations

- **TanStack Start**: https://www.better-auth.com/docs/integrations/tanstack
- **Expo (React Native)**: https://www.better-auth.com/docs/integrations/expo

### Community & Support

- **GitHub**: https://github.com/better-auth/better-auth (22.4k ⭐)
- **Examples**: https://github.com/better-auth/better-auth/tree/main/examples
- **Discord**: https://discord.gg/better-auth
- **Changelog**: https://github.com/better-auth/better-auth/releases

### Related Documentation

- **Drizzle ORM**: https://orm.drizzle.team/docs/get-started-sqlite
- **Kysely**: https://kysely.dev/

---

## Production Examples

**Verified working D1 repositories** (all use Drizzle or Kysely):

1. **zpg6/better-auth-cloudflare** - Drizzle + D1 (includes CLI)
2. **zwily/example-react-router-cloudflare-d1-drizzle-better-auth** - Drizzle + D1
3. **foxlau/react-router-v7-better-auth** - Drizzle + D1
4. **matthewlynch/better-auth-react-router-cloudflare-d1** - Kysely + D1

**None** use a direct `d1Adapter` - all require Drizzle/Kysely.

---

## Version Compatibility

**Tested with**:
- `better-auth@1.4.10`
- `drizzle-orm@0.45.1`
- `drizzle-kit@0.31.8`
- `kysely@0.28.9`
- `kysely-d1@0.4.0`
- `@cloudflare/workers-types@latest`
- `hono@4.11.3`
- Node.js 18+, Bun 1.0+

**Breaking changes**:
- v1.4.6: `allowImpersonatingAdmins` defaults to `false`
- v1.4.0: ESM-only (no CommonJS)
- v1.3.0: Multi-team table structure change

Check changelog: https://github.com/better-auth/better-auth/releases

---

## Community Resources

**Cloudflare-specific guides:**
- [zpg6/better-auth-cloudflare](https://github.com/zpg6/better-auth-cloudflare) - Drizzle + D1 reference
- [Hono + better-auth on Cloudflare](https://hono.dev/examples/better-auth-on-cloudflare) - Official Hono example
- [React Router + Cloudflare D1](https://dev.to/atman33/setup-better-auth-with-react-router-cloudflare-d1-2ad4) - React Router v7 guide
- [SvelteKit + Cloudflare D1](https://medium.com/@dasfacc/sveltekit-better-auth-using-cloudflare-d1-and-drizzle-91d9d9a6d0b4) - SvelteKit guide

---

**Token Efficiency**:
- **Without skill**: ~35,000 tokens (D1 adapter errors, 15+ plugins, rate limiting, session caching, database hooks, mobile integration)
- **With skill**: ~8,000 tokens (focused on errors + patterns + all plugins + API reference)
- **Savings**: ~77% (~27,000 tokens)

**Errors prevented**: 22 documented issues with exact solutions
**Key value**: D1 adapter requirement, nodejs_compat flag, OAuth 2.1 Provider, Bearer/OneTap/SCIM/Anonymous plugins, rate limiting, session caching, database hooks, Expo integration, 80+ endpoint reference, additionalFields bugs, freshAge behavior, OAuth token wrapping

---

**Last verified**: 2026-01-21 | **Skill version**: 5.1.0 | **Changes**: Added 5 new issues from post-training-cutoff research (Expo fromJSONSchema crash, additionalFields string[] bug, additionalFields returned property bug, freshAge not activity-based, OAuth token wrapping). Expanded Issue #3 with Kysely CamelCasePlugin join parsing failure. Expanded Issue #5 with Hono CORS pattern. Added Cloudflare Workers DB binding constraints note. Added TanStack Start session nullability pattern. Updated to v1.4.16.
