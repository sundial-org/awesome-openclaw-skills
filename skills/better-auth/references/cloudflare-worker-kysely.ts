/**
 * Complete Cloudflare Worker with better-auth + Kysely
 *
 * This example demonstrates:
 * - D1 database with Kysely adapter
 * - Email/password authentication
 * - Google OAuth
 * - Protected routes with session verification
 * - CORS configuration for SPA
 * - CamelCasePlugin for schema conversion
 *
 * ⚠️ CRITICAL: better-auth requires Kysely (or Drizzle) for D1
 * There is NO direct d1Adapter()!
 */

import { Hono } from "hono";
import { cors } from "hono/cors";
import { betterAuth } from "better-auth";
import { Kysely, CamelCasePlugin } from "kysely";
import { D1Dialect } from "kysely-d1";

// ═══════════════════════════════════════════════════════════════
// Environment bindings
// ═══════════════════════════════════════════════════════════════
type Env = {
  DB: D1Database;
  BETTER_AUTH_SECRET: string;
  BETTER_AUTH_URL: string;
  GOOGLE_CLIENT_ID: string;
  GOOGLE_CLIENT_SECRET: string;
  FRONTEND_URL: string;
};

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
// Helper: Initialize auth with Kysely
// ═══════════════════════════════════════════════════════════════
function createAuth(env: Env) {
  return betterAuth({
    // Base URL for OAuth callbacks
    baseURL: env.BETTER_AUTH_URL,

    // Secret for signing tokens
    secret: env.BETTER_AUTH_SECRET,

    // ⚠️ CRITICAL: Use Kysely with D1Dialect
    // There is NO direct d1Adapter()!
    database: {
      db: new Kysely({
        dialect: new D1Dialect({
          database: env.DB,
        }),
        plugins: [
          // CRITICAL: CamelCasePlugin converts between snake_case (DB) and camelCase (better-auth)
          // Without this, session reads will fail if your schema uses snake_case
          new CamelCasePlugin(),
        ],
      }),
      type: "sqlite",
    },

    // Email/password authentication
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: true,
      sendVerificationEmail: async ({ user, url, token }) => {
        // TODO: Implement email sending
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
    },

    // Session configuration
    session: {
      expiresIn: 60 * 60 * 24 * 7, // 7 days
      updateAge: 60 * 60 * 24, // Update every 24 hours
    },
  });
}

// ═══════════════════════════════════════════════════════════════
// Auth routes - handle all better-auth endpoints
// ═══════════════════════════════════════════════════════════════
app.all("/api/auth/*", async (c) => {
  const auth = createAuth(c.env);
  return auth.handler(c.req.raw);
});

// ═══════════════════════════════════════════════════════════════
// Example: Protected API route
// ═══════════════════════════════════════════════════════════════
app.get("/api/protected", async (c) => {
  const auth = createAuth(c.env);

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
  const auth = createAuth(c.env);

  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Fetch user data using Kysely
  const db = new Kysely({
    dialect: new D1Dialect({ database: c.env.DB }),
    plugins: [new CamelCasePlugin()],
  });

  const user = await db
    .selectFrom("user")
    .select(["id", "email", "name", "image", "createdAt"])
    .where("id", "=", session.user.id)
    .executeTakeFirst();

  return c.json(user);
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
 * 1. Install dependencies:
 *    npm install better-auth kysely kysely-d1 hono
 *
 * 2. Create D1 database:
 *    wrangler d1 create my-app-db
 *
 * 3. Add to wrangler.toml:
 *    [[d1_databases]]
 *    binding = "DB"
 *    database_name = "my-app-db"
 *    database_id = "YOUR_ID"
 *
 *    [vars]
 *    BETTER_AUTH_URL = "http://localhost:8787"
 *    FRONTEND_URL = "http://localhost:3000"
 *
 * 4. Set secrets:
 *    wrangler secret put BETTER_AUTH_SECRET
 *    wrangler secret put GOOGLE_CLIENT_ID
 *    wrangler secret put GOOGLE_CLIENT_SECRET
 *
 * 5. Create database schema manually (Kysely doesn't auto-generate):
 *    wrangler d1 execute my-app-db --local --command "
 *      CREATE TABLE user (
 *        id TEXT PRIMARY KEY,
 *        name TEXT NOT NULL,
 *        email TEXT NOT NULL UNIQUE,
 *        email_verified INTEGER NOT NULL DEFAULT 0,
 *        image TEXT,
 *        created_at INTEGER NOT NULL DEFAULT (unixepoch()),
 *        updated_at INTEGER NOT NULL DEFAULT (unixepoch())
 *      );
 *      CREATE TABLE session (...);
 *      CREATE TABLE account (...);
 *      CREATE TABLE verification (...);
 *    "
 *
 * 6. Apply schema to remote:
 *    wrangler d1 execute my-app-db --remote --file schema.sql
 *
 * 7. Deploy:
 *    wrangler deploy
 *
 * ═══════════════════════════════════════════════════════════════
 * WHY CamelCasePlugin?
 * ═══════════════════════════════════════════════════════════════
 *
 * If your database schema uses snake_case (email_verified),
 * but better-auth expects camelCase (emailVerified), the
 * CamelCasePlugin automatically converts between the two.
 *
 * Without it, session reads will fail with missing fields.
 *
 * ═══════════════════════════════════════════════════════════════
 */
