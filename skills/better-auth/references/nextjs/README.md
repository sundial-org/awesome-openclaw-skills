# Next.js Examples

This directory contains better-auth examples for **Next.js with PostgreSQL**.

**Important**: These examples are NOT for Cloudflare D1. They use PostgreSQL via Hyperdrive or direct connection.

## Files

### `postgres-example.ts`
Complete Next.js API route with better-auth using:
- **PostgreSQL** (not D1)
- Drizzle ORM with `postgres` driver
- Organizations plugin
- 2FA plugin
- Email verification
- Custom error handling

**Use this example when**:
- Building Next.js application (not Cloudflare Workers)
- Using PostgreSQL database
- Need organizations and 2FA features

**Installation**:
```bash
npm install better-auth drizzle-orm postgres
```

**Environment variables**:
```env
DATABASE_URL=postgresql://user:password@host:5432/database
BETTER_AUTH_SECRET=your-secret
NEXT_PUBLIC_APP_URL=http://localhost:3000
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
```

---

**For Cloudflare D1 examples**, see the parent `references/` directory:
- `cloudflare-worker-drizzle.ts` - Complete Worker with Drizzle + D1
- `cloudflare-worker-kysely.ts` - Complete Worker with Kysely + D1
