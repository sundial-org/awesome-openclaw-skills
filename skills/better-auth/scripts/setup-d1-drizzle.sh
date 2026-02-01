#!/bin/bash

# ═══════════════════════════════════════════════════════════════
# better-auth + D1 + Drizzle ORM Setup Script
# ═══════════════════════════════════════════════════════════════
#
# This script automates the setup of better-auth with Cloudflare D1
# and Drizzle ORM.
#
# CRITICAL: better-auth requires Drizzle ORM or Kysely for D1.
# There is NO direct d1Adapter()!
#
# Usage:
#   chmod +x setup-d1-drizzle.sh
#   ./setup-d1-drizzle.sh my-app-name
#
# ═══════════════════════════════════════════════════════════════

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if app name provided
if [ -z "$1" ]; then
  echo -e "${RED}Error: Please provide an app name${NC}"
  echo "Usage: ./setup-d1-drizzle.sh my-app-name"
  exit 1
fi

APP_NAME=$1
DB_NAME="${APP_NAME}-db"

echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}better-auth + D1 + Drizzle Setup${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "App Name: ${GREEN}$APP_NAME${NC}"
echo -e "Database: ${GREEN}$DB_NAME${NC}"
echo ""

# ═══════════════════════════════════════════════════════════════
# Step 1: Install dependencies
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[1/8]${NC} Installing dependencies..."
npm install better-auth drizzle-orm drizzle-kit @cloudflare/workers-types hono

# ═══════════════════════════════════════════════════════════════
# Step 2: Create D1 database
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[2/8]${NC} Creating D1 database..."
wrangler d1 create $DB_NAME

echo -e "${GREEN}✓${NC} Database created!"
echo -e "${YELLOW}⚠${NC}  Copy the database_id from the output above and update wrangler.toml"
echo ""
read -p "Press Enter after updating wrangler.toml..."

# ═══════════════════════════════════════════════════════════════
# Step 3: Create directory structure
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[3/8]${NC} Creating directory structure..."
mkdir -p src/db
mkdir -p drizzle

# ═══════════════════════════════════════════════════════════════
# Step 4: Create database schema
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[4/8]${NC} Creating database schema..."
cat > src/db/schema.ts << 'EOF'
import { integer, sqliteTable, text } from "drizzle-orm/sqlite-core";
import { sql } from "drizzle-orm";

export const user = sqliteTable("user", {
  id: text().primaryKey(),
  name: text().notNull(),
  email: text().notNull().unique(),
  emailVerified: integer({ mode: "boolean" }).notNull().default(false),
  image: text(),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});

export const session = sqliteTable("session", {
  id: text().primaryKey(),
  userId: text()
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  token: text().notNull(),
  expiresAt: integer({ mode: "timestamp" }).notNull(),
  ipAddress: text(),
  userAgent: text(),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});

export const account = sqliteTable("account", {
  id: text().primaryKey(),
  userId: text()
    .notNull()
    .references(() => user.id, { onDelete: "cascade" }),
  accountId: text().notNull(),
  providerId: text().notNull(),
  accessToken: text(),
  refreshToken: text(),
  accessTokenExpiresAt: integer({ mode: "timestamp" }),
  refreshTokenExpiresAt: integer({ mode: "timestamp" }),
  scope: text(),
  idToken: text(),
  password: text(),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});

export const verification = sqliteTable("verification", {
  id: text().primaryKey(),
  identifier: text().notNull(),
  value: text().notNull(),
  expiresAt: integer({ mode: "timestamp" }).notNull(),
  createdAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
  updatedAt: integer({ mode: "timestamp" })
    .notNull()
    .default(sql`(unixepoch())`),
});
EOF

# ═══════════════════════════════════════════════════════════════
# Step 5: Create Drizzle config
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[5/8]${NC} Creating Drizzle config..."
cat > drizzle.config.ts << 'EOF'
import type { Config } from "drizzle-kit";

export default {
  out: "./drizzle",
  schema: "./src/db/schema.ts",
  dialect: "sqlite",
  driver: "d1-http",
  dbCredentials: {
    databaseId: process.env.CLOUDFLARE_DATABASE_ID!,
    accountId: process.env.CLOUDFLARE_ACCOUNT_ID!,
    token: process.env.CLOUDFLARE_TOKEN!,
  },
} satisfies Config;
EOF

echo -e "${GREEN}✓${NC} Config created"
echo ""
echo -e "${YELLOW}⚠${NC}  Create a .env file with:"
echo "  CLOUDFLARE_ACCOUNT_ID=your-account-id"
echo "  CLOUDFLARE_DATABASE_ID=your-database-id"
echo "  CLOUDFLARE_TOKEN=your-api-token"
echo ""
read -p "Press Enter after creating .env..."

# ═══════════════════════════════════════════════════════════════
# Step 6: Generate migrations
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[6/8]${NC} Generating migrations..."
npx drizzle-kit generate

# ═══════════════════════════════════════════════════════════════
# Step 7: Apply migrations
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[7/8]${NC} Applying migrations..."
echo -e "Applying to ${GREEN}local${NC} D1..."
wrangler d1 migrations apply $DB_NAME --local

read -p "Apply to remote D1 too? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  echo -e "Applying to ${GREEN}remote${NC} D1..."
  wrangler d1 migrations apply $DB_NAME --remote
fi

# ═══════════════════════════════════════════════════════════════
# Step 8: Set secrets
# ═══════════════════════════════════════════════════════════════
echo -e "${YELLOW}[8/8]${NC} Setting secrets..."
echo ""
echo -e "${BLUE}Generating BETTER_AUTH_SECRET...${NC}"
SECRET=$(openssl rand -base64 32)
echo "$SECRET" | wrangler secret put BETTER_AUTH_SECRET

echo ""
echo -e "${GREEN}✓ Setup complete!${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Next Steps${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo "1. Add OAuth client IDs and secrets (if needed):"
echo "   wrangler secret put GOOGLE_CLIENT_ID"
echo "   wrangler secret put GOOGLE_CLIENT_SECRET"
echo ""
echo "2. Test locally:"
echo "   npm run dev"
echo ""
echo "3. Deploy:"
echo "   wrangler deploy"
echo ""
echo -e "${YELLOW}⚠ IMPORTANT:${NC} Update your wrangler.toml with the database_id from Step 2"
echo ""
