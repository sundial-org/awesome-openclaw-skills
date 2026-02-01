/**
 * Complete Cloudflare Worker with better-auth + Drizzle ORM
 *
 * This example demonstrates:
 * - D1 database with Drizzle ORM adapter
 * - Email/password authentication
 * - Google and GitHub OAuth
 * - Protected routes with session verification
 * - CORS configuration for SPA
 * - KV storage for sessions (strong consistency)
 * - Rate limiting with KV
 *
 * ⚠️ CRITICAL: better-auth requires Drizzle ORM or Kysely for D1
 * There is NO direct d1Adapter()!
 */

import { Hono } from "hono";
import { cors } from "hono/cors";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { drizzle, type DrizzleD1Database } from "drizzle-orm/d1";
import { rateLimit } from "better-auth/plugins";
import * as schema from "../db/schema"; // Your Drizzle schema

// ═══════════════════════════════════════════════════════════════
// Environment bindings
// ═══════════════════════════════════════════════════════════════
type Env = {
  DB: D1Database;
  SESSIONS_KV: KVNamespace;
  RATE_LIMIT_KV: KVNamespace;
  BETTER_AUTH_SECRET: string;
  BETTER_AUTH_URL: string;
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  GITHUB_CLIENT_ID: string;
  GITHUB_CLIENT_SECRET: string;
  FRONTEND_URL: string;
};

// Database type
export type Database = DrizzleD1Database<typeof schema>;

const app = new Hono<{ Bindings: Env }>();

// ═══════════════════════════════════════════════════════════════
// CORS configuration for SPA
// ═══════════════════════════════════════════════════════════════
app.use("/api/*", async (c, next) => {
  const corsMiddleware = cors({
    origin: [c.env.FRONTEND_URL, "http://localhost:3000"],
    credentials: true,
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
  });
  return corsMiddleware(c, next);
});

// ═══════════════════════════════════════════════════════════════
// Helper: Initialize Drizzle database
// ═══════════════════════════════════════════════════════════════
function createDatabase(d1: D1Database): Database {
  return drizzle(d1, { schema });
}

// ═══════════════════════════════════════════════════════════════
// Helper: Initialize auth (per-request to access env)
// ═══════════════════════════════════════════════════════════════
function createAuth(db: Database, env: Env) {
  return betterAuth({
    // Base URL for OAuth callbacks
    baseURL: env.BETTER_AUTH_URL,

    // Secret for signing tokens
    secret: env.BETTER_AUTH_SECRET,

    // ⚠️ CRITICAL: Use Drizzle adapter with SQLite provider
    // There is NO direct d1Adapter()!
    database: drizzleAdapter(db, {
      provider: "sqlite",
    }),

    // Email/password authentication
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      sendVerificationEmail: async ({ user, url, token }) => {
        // TODO: Implement email sending
        // Use Resend, SendGrid, or Cloudflare Email Routing
        console.log(`Verification email for ${user.email}: ${url}`);
        console.log(`Verification code: ${token}`);
      },
    },

    // Social providers
    socialProviders: {
      google: {
        clientId: env.GOOGLE_CLIENT_ID,
        clientSecret: env.GOOGLE_CLIENT_SECRET,
        scope: ["openid", "email", "profile"],
      },
      github: {
        clientId: env.GITHUB_CLIENT_ID,
        clientSecret: env.GITHUB_CLIENT_SECRET,
        scope: ["user:email", "read:user"],
      },
    },

    // Session configuration
    session: {
      expiresIn: 60 * 60 * 24 * 7, // 7 days
      updateAge: 60 * 60 * 24, // Update every 24 hours

      // Use KV for sessions (strong consistency vs D1 eventual consistency)
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

    // Plugins
    plugins: [
      rateLimit({
        window: 60, // 60 seconds
        max: 10, // 10 requests per window
        storage: {
          get: async (key) => {
            return await env.RATE_LIMIT_KV.get(key);
          },
          set: async (key, value, ttl) => {
            await env.RATE_LIMIT_KV.put(key, value, {
              expirationTtl: ttl,
            });
          },
        },
      }),
    ],
  });
}

// ═══════════════════════════════════════════════════════════════
// Auth routes - handle all better-auth endpoints
// ═══════════════════════════════════════════════════════════════
app.all("/api/auth/*", async (c) => {
  const db = createDatabase(c.env.DB);
  const auth = createAuth(db, c.env);
  return auth.handler(c.req.raw);
});

// ═══════════════════════════════════════════════════════════════
// Example: Protected API route
// ═══════════════════════════════════════════════════════════════
app.get("/api/protected", async (c) => {
  const db = createDatabase(c.env.DB);
  const auth = createAuth(db, c.env);

  // Verify session
  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  return c.json({
    message: "Protected data",
    user: {
      id: session.user.id,
      email: session.user.email,
      name: session.user.name,
    },
  });
});

// ═══════════════════════════════════════════════════════════════
// Example: User profile endpoint
// ═══════════════════════════════════════════════════════════════
app.get("/api/user/profile", async (c) => {
  const db = createDatabase(c.env.DB);
  const auth = createAuth(db, c.env);

  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Fetch additional user data from D1
  const userProfile = await db.query.user.findFirst({
    where: (user, { eq }) => eq(user.id, session.user.id),
  });

  return c.json(userProfile);
});

// ═══════════════════════════════════════════════════════════════
// Example: Update user profile
// ═══════════════════════════════════════════════════════════════
app.patch("/api/user/profile", async (c) => {
  const db = createDatabase(c.env.DB);
  const auth = createAuth(db, c.env);

  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  const { name } = await c.req.json();

  // Update user in D1 using Drizzle
  await db
    .update(schema.user)
    .set({ name, updatedAt: new Date() })
    .where(eq(schema.user.id, session.user.id));

  return c.json({ success: true });
});

// ═══════════════════════════════════════════════════════════════
// Example: Admin-only endpoint
// ═══════════════════════════════════════════════════════════════
app.get("/api/admin/users", async (c) => {
  const db = createDatabase(c.env.DB);
  const auth = createAuth(db, c.env);

  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Check admin role (you'd store this in users table)
  const user = await db.query.user.findFirst({
    where: (user, { eq }) => eq(user.id, session.user.id),
    // Add role field to your schema if needed
  });

  // if (user.role !== 'admin') {
  //   return c.json({ error: 'Forbidden' }, 403)
  // }

  // Fetch all users
  const users = await db.query.user.findMany({
    columns: {
      id: true,
      email: true,
      name: true,
      createdAt: true,
    },
  });

  return c.json(users);
});

// ═══════════════════════════════════════════════════════════════
// Health check
// ═══════════════════════════════════════════════════════════════
app.get("/health", (c) => {
  return c.json({
    status: "ok",
    timestamp: new Date().toISOString(),
  });
});

// ═══════════════════════════════════════════════════════════════
// Export Worker
// ═══════════════════════════════════════════════════════════════
export default app;

/**
 * ═══════════════════════════════════════════════════════════════
 * SETUP CHECKLIST
 * ═══════════════════════════════════════════════════════════════
 *
 * 1. Create D1 database:
 *    wrangler d1 create my-app-db
 *
 * 2. Create KV namespaces:
 *    wrangler kv:namespace create SESSIONS_KV
 *    wrangler kv:namespace create RATE_LIMIT_KV
 *
 * 3. Add to wrangler.toml:
 *    [[d1_databases]]
 *    binding = "DB"
 *    database_name = "my-app-db"
 *    database_id = "YOUR_ID"
 *
 *    [[kv_namespaces]]
 *    binding = "SESSIONS_KV"
 *    id = "YOUR_ID"
 *
 *    [[kv_namespaces]]
 *    binding = "RATE_LIMIT_KV"
 *    id = "YOUR_ID"
 *
 *    [vars]
 *    BETTER_AUTH_URL = "http://localhost:8787"
 *    FRONTEND_URL = "http://localhost:3000"
 *
 * 4. Set secrets:
 *    wrangler secret put BETTER_AUTH_SECRET
 *    wrangler secret put GOOGLE_CLIENT_ID
 *    wrangler secret put GOOGLE_CLIENT_SECRET
 *    wrangler secret put GITHUB_CLIENT_ID
 *    wrangler secret put GITHUB_CLIENT_SECRET
 *
 * 5. Generate and apply migrations:
 *    npx drizzle-kit generate
 *    wrangler d1 migrations apply my-app-db --local
 *    wrangler d1 migrations apply my-app-db --remote
 *
 * 6. Deploy:
 *    wrangler deploy
 *
 * ═══════════════════════════════════════════════════════════════
 */
