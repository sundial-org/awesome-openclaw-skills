/**
 * better-auth + Hono + Cloudflare Workers Integration
 *
 * This is the recommended pattern for using better-auth with Hono on Cloudflare Workers.
 * Based on: https://hono.dev/examples/better-auth-on-cloudflare
 *
 * @package better-auth@1.4.10
 * @package hono@4.x
 */

import { Hono } from "hono";
import { cors } from "hono/cors";
import { betterAuth } from "better-auth";
import { drizzleAdapter } from "better-auth/adapters/drizzle";
import { admin, organization, twoFactor, oauthProvider, jwt } from "better-auth/plugins";
import { drizzle } from "drizzle-orm/d1";
import * as schema from "./db/schema";

// ============================================================================
// Types
// ============================================================================

interface Env {
  DB: D1Database;
  BETTER_AUTH_SECRET: string;
  BETTER_AUTH_URL: string;
  GOOGLE_CLIENT_ID?: string;
  GOOGLE_CLIENT_SECRET?: string;
  GITHUB_CLIENT_ID?: string;
  GITHUB_CLIENT_SECRET?: string;
}

// ============================================================================
// Auth Factory (per-request instance)
// ============================================================================

/**
 * Create auth instance with environment bindings.
 *
 * IMPORTANT: better-auth must be instantiated per-request in Workers
 * because env bindings are only available in request context.
 */
export function createAuth(env: Env) {
  const db = drizzle(env.DB, { schema });

  return betterAuth({
    secret: env.BETTER_AUTH_SECRET,
    baseURL: env.BETTER_AUTH_URL,

    database: drizzleAdapter(db, { provider: "sqlite" }),

    // Email + Password Authentication
    emailAndPassword: {
      enabled: true,
      requireEmailVerification: false, // Enable in production
    },

    // Social Providers (optional)
    socialProviders: {
      ...(env.GOOGLE_CLIENT_ID && env.GOOGLE_CLIENT_SECRET && {
        google: {
          clientId: env.GOOGLE_CLIENT_ID,
          clientSecret: env.GOOGLE_CLIENT_SECRET,
          scope: ["openid", "email", "profile"],
        },
      }),
      ...(env.GITHUB_CLIENT_ID && env.GITHUB_CLIENT_SECRET && {
        github: {
          clientId: env.GITHUB_CLIENT_ID,
          clientSecret: env.GITHUB_CLIENT_SECRET,
          scope: ["user:email", "read:user"],
        },
      }),
    },

    // Session Configuration
    session: {
      expiresIn: 60 * 60 * 24 * 7, // 7 days
      updateAge: 60 * 60 * 24, // Update every 24 hours
    },

    // Plugins
    plugins: [
      twoFactor(),
      organization(),
      admin({
        allowImpersonatingAdmins: false, // v1.4.6+ default
      }),
      // Uncomment for OAuth provider capabilities:
      // jwt(),
      // oauthProvider({
      //   accessTokenExpiresIn: 3600,
      //   refreshTokenExpiresIn: 2592000,
      // }),
    ],
  });
}

// Type helper for the auth instance
export type Auth = ReturnType<typeof createAuth>;

// ============================================================================
// Hono App
// ============================================================================

const app = new Hono<{ Bindings: Env }>();

// CORS middleware for SPA clients
app.use(
  "/api/auth/*",
  cors({
    origin: (origin) => origin, // Or specify allowed origins
    credentials: true,
    allowMethods: ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowHeaders: ["Content-Type", "Authorization"],
  })
);

// Mount better-auth handler
// Handles all /api/auth/* routes automatically
app.on(["GET", "POST"], "/api/auth/*", async (c) => {
  const auth = createAuth(c.env);
  return auth.handler(c.req.raw);
});

// ============================================================================
// Auth Middleware for Protected Routes
// ============================================================================

/**
 * Middleware to protect routes with authentication.
 *
 * Usage:
 * app.use("/api/protected/*", authMiddleware);
 */
app.use("/api/protected/*", async (c, next) => {
  const auth = createAuth(c.env);

  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Attach user and session to context for downstream handlers
  c.set("user", session.user);
  c.set("session", session.session);

  await next();
});

// Example protected route
app.get("/api/protected/profile", async (c) => {
  const user = c.get("user");
  return c.json({ user });
});

// ============================================================================
// Admin Middleware
// ============================================================================

/**
 * Middleware to protect admin routes.
 * Requires user to have 'admin' role.
 */
app.use("/api/admin/*", async (c, next) => {
  const auth = createAuth(c.env);

  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  });

  if (!session) {
    return c.json({ error: "Unauthorized" }, 401);
  }

  // Check for admin role
  if (session.user.role !== "admin") {
    return c.json({ error: "Forbidden" }, 403);
  }

  c.set("user", session.user);
  c.set("session", session.session);

  await next();
});

// Example admin route
app.get("/api/admin/users", async (c) => {
  const auth = createAuth(c.env);

  const users = await auth.api.listUsers({
    query: { limit: 50 },
    headers: c.req.raw.headers,
  });

  return c.json(users);
});

// ============================================================================
// Health Check
// ============================================================================

app.get("/health", (c) => {
  return c.json({ status: "ok", timestamp: new Date().toISOString() });
});

export default app;

// ============================================================================
// Type Augmentation for Hono Context
// ============================================================================

declare module "hono" {
  interface ContextVariableMap {
    user: {
      id: string;
      email: string;
      name: string | null;
      image: string | null;
      role: string | null;
      emailVerified: boolean;
      createdAt: Date;
      updatedAt: Date;
    };
    session: {
      id: string;
      userId: string;
      expiresAt: Date;
      token: string;
      createdAt: Date;
      updatedAt: Date;
    };
  }
}
