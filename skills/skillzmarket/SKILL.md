---
name: skillzmarket
description: Search and call monetized AI skills from Skillz Market with automatic USDC payments on Base. Use when the user wants to find paid AI services, call external skills with cryptocurrency payments, or integrate with the Skillz Market ecosystem.
metadata: {"openclaw":{"requires":{"bins":["npx"],"env":["SKILLZ_PRIVATE_KEY"]},"primaryEnv":"SKILLZ_PRIVATE_KEY"}}
---

# Skillz Market

Search and call monetized AI skills with automatic cryptocurrency payments via x402.

## Quick Start

List all available skills:
```bash
npx tsx {baseDir}/skillz-cli.ts list
```

Search for skills:
```bash
npx tsx {baseDir}/skillz-cli.ts search "echo"
```

Get skill details:
```bash
npx tsx {baseDir}/skillz-cli.ts info "echo-service"
```

Call a skill (requires SKILLZ_PRIVATE_KEY):
```bash
npx tsx {baseDir}/skillz-cli.ts call "echo-service" '{"message":"hello"}'
```

## Commands

- `list [--verified]` - List all available skills (optionally filter by verified only)
- `search <query>` - Search for skills by keyword
- `info <slug>` - Get skill details by slug
- `call <slug> <json>` - Call a skill with automatic x402 payment
- `direct <url> <json>` - Call any x402-enabled endpoint directly

## Configuration

Set `SKILLZ_PRIVATE_KEY` in OpenClaw config (`~/.openclaw/openclaw.json`):

```json
{
  "skills": {
    "entries": {
      "skillzmarket": {
        "apiKey": "0x..."
      }
    }
  }
}
```

## Environment Variables

- `SKILLZ_PRIVATE_KEY` - Wallet private key for x402 payments
- `SKILLZ_API_URL` - API endpoint (default: https://api.skillz.market)
