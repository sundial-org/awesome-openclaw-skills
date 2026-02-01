/**
 * Complete better-auth Database Schema for Drizzle ORM + D1
 *
 * This schema includes all tables required by better-auth core.
 * You can add your own application tables below.
 *
 * ═══════════════════════════════════════════════════════════════
 * CRITICAL NOTES
 * ═══════════════════════════════════════════════════════════════
 *
 * 1. Column names use camelCase (emailVerified, createdAt)
 *    - This matches better-auth expectations
 *    - If you use snake_case, you MUST use CamelCasePlugin with Kysely
 *
 * 2. Timestamps use INTEGER with mode: "timestamp"
 *    - D1 (SQLite) doesn't have native timestamp type
 *    - Unix epoch timestamps (seconds since 1970)
 *
 * 3. Booleans use INTEGER with mode: "boolean"
 *    - D1 (SQLite) doesn't have native boolean type
 *    - 0 = false, 1 = true
 *
 * 4. Foreign keys use onDelete: "cascade"
 *    - Automatically delete related records
 *    - session deleted when user deleted
 *    - account deleted when user deleted
 *
 * ═══════════════════════════════════════════════════════════════
 */

import { integer, sqliteTable, text, index } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

// ═══════════════════════════════════════════════════════════════
// better-auth CORE TABLES
// ═══════════════════════════════════════════════════════════════

/**
 * Users table - stores all user accounts
 */
export const user = sqliteTable(
  "user",
  {
    id: text().primaryKey(),
    name: text().notNull(),
    email: text().notNull().unique(),
    emailVerified: integer({ mode: "boolean" }).notNull().default(false),
    image: text(), // Profile picture URL
    createdAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
    updatedAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
  },
  (table) => ({
    emailIdx: index("user_email_idx").on(table.email),
  })
);

/**
 * Sessions table - stores active user sessions
 *
 * NOTE: Consider using KV storage for sessions instead of D1
 * to avoid eventual consistency issues
 */
export const session = sqliteTable(
  "session",
  {
    id: text().primaryKey(),
    userId: text()
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    token: text().notNull().unique(),
    expiresAt: integer({ mode: "timestamp" }).notNull(),
    ipAddress: text(),
    userAgent: text(),
    createdAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
    updatedAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
  },
  (table) => ({
    userIdIdx: index("session_user_id_idx").on(table.userId),
    tokenIdx: index("session_token_idx").on(table.token),
  })
);

/**
 * Accounts table - stores OAuth provider accounts and passwords
 */
export const account = sqliteTable(
  "account",
  {
    id: text().primaryKey(),
    userId: text()
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    accountId: text().notNull(), // Provider's user ID
    providerId: text().notNull(), // "google", "github", etc.
    accessToken: text(),
    refreshToken: text(),
    accessTokenExpiresAt: integer({ mode: "timestamp" }),
    refreshTokenExpiresAt: integer({ mode: "timestamp" }),
    scope: text(), // OAuth scopes granted
    idToken: text(), // OpenID Connect ID token
    password: text(), // Hashed password for email/password auth
    createdAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
    updatedAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
  },
  (table) => ({
    userIdIdx: index("account_user_id_idx").on(table.userId),
    providerIdx: index("account_provider_idx").on(
      table.providerId,
      table.accountId
    ),
  })
);

/**
 * Verification tokens - for email verification, password reset, etc.
 */
export const verification = sqliteTable(
  "verification",
  {
    id: text().primaryKey(),
    identifier: text().notNull(), // Email or user ID
    value: text().notNull(), // Token value
    expiresAt: integer({ mode: "timestamp" }).notNull(),
    createdAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
    updatedAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
  },
  (table) => ({
    identifierIdx: index("verification_identifier_idx").on(table.identifier),
    valueIdx: index("verification_value_idx").on(table.value),
  })
);

// ═══════════════════════════════════════════════════════════════
// OPTIONAL: Additional tables for better-auth plugins
// ═══════════════════════════════════════════════════════════════

/**
 * Two-Factor Authentication table (if using 2FA plugin)
 */
export const twoFactor = sqliteTable(
  "two_factor",
  {
    id: text().primaryKey(),
    userId: text()
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    secret: text().notNull(), // TOTP secret
    backupCodes: text(), // JSON array of backup codes
    enabled: integer({ mode: "boolean" }).notNull().default(false),
    createdAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
  },
  (table) => ({
    userIdIdx: index("two_factor_user_id_idx").on(table.userId),
  })
);

/**
 * Organizations table (if using organization plugin)
 */
export const organization = sqliteTable("organization", {
  id: text().primaryKey(),
  name: text().notNull(),
  slug: text().notNull().unique(),
  logo: text(),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});

/**
 * Organization members table (if using organization plugin)
 */
export const organizationMember = sqliteTable(
  "organization_member",
  {
    id: text().primaryKey(),
    organizationId: text()
      .notNull()
      .references(() => organization.id, { onDelete: "cascade" }),
    userId: text()
      .notNull()
      .references(() => user.id, { onDelete: "cascade" }),
    role: text().notNull(), // "owner", "admin", "member"
    createdAt: integer({ mode: "timestamp" })
      .notNull()
      .default(sql`(unixepoch())`),
  },
  (table) => ({
    orgIdIdx: index("org_member_org_id_idx").on(table.organizationId),
    userIdIdx: index("org_member_user_id_idx").on(table.userId),
  })
);

// ═══════════════════════════════════════════════════════════════
// YOUR APPLICATION TABLES
// ═══════════════════════════════════════════════════════════════

/**
 * Example: User profile extension
 */
export const profile = sqliteTable("profile", {
  id: text().primaryKey(),
  userId: text()
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  bio: text(),
  website: text(),
  location: text(),
  phone: text(),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});

/**
 * Example: User preferences
 */
export const userPreferences = sqliteTable("user_preferences", {
  id: text().primaryKey(),
  userId: text()
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  theme: text().notNull().default("system"), // "light", "dark", "system"
  language: text().notNull().default("en"),
  emailNotifications: integer({ mode: "boolean" }).notNull().default(true),
  pushNotifications: integer({ mode: "boolean" }).notNull().default(false),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});

// ═══════════════════════════════════════════════════════════════
// Export all schemas for Drizzle
// ═══════════════════════════════════════════════════════════════
export const schema = {
  user,
  session,
  account,
  verification,
  twoFactor,
  organization,
  organizationMember,
  profile,
  userPreferences,
} as const;

/**
 * ═══════════════════════════════════════════════════════════════
 * USAGE INSTRUCTIONS
 * ═══════════════════════════════════════════════════════════════
 *
 * 1. Save this file as: src/db/schema.ts
 *
 * 2. Create drizzle.config.ts:
 *    import type { Config } from "drizzle-kit";
 *
 *    export default {
 *      out: "./drizzle",
 *      schema: "./src/db/schema.ts",
 *      dialect: "sqlite",
 *      driver: "d1-http",
 *      dbCredentials: {
 *        databaseId: process.env.CLOUDFLARE_DATABASE_ID!,
 *        accountId: process.env.CLOUDFLARE_ACCOUNT_ID!,
 *        token: process.env.CLOUDFLARE_TOKEN!,
 *      },
 *    } satisfies Config;
 *
 * 3. Generate migrations:
 *    npx drizzle-kit generate
 *
 * 4. Apply migrations to D1:
 *    wrangler d1 migrations apply my-app-db --local
 *    wrangler d1 migrations apply my-app-db --remote
 *
 * 5. Use in your Worker:
 *    import { drizzle } from "drizzle-orm/d1";
 *    import * as schema from "./db/schema";
 *
 *    const db = drizzle(env.DB, { schema });
 *
 * 6. Query example:
 *    const users = await db.query.user.findMany({
 *      where: (user, { eq }) => eq(user.emailVerified, true)
 *    });
 *
 * ═══════════════════════════════════════════════════════════════
 */
