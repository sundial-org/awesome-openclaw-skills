# Dexie Skill

Track Chia DEX trading via the Dexie.space API.

## What It Does

- List active/completed offers
- View token prices and liquidity
- Search tokens (CATs)
- Monitor trading pairs
- Get platform statistics

## Commands

All commands can be triggered via:
- `/dex <command>` in Telegram
- `/dexie <command>` in Telegram
- `dex <command>` in CLI
- `dexie <command>` in CLI

### Offers

```bash
/dex offers                List active offers
/dex offers completed      List completed offers
/dex offers cancelled      List cancelled offers
/dex offer <id>            Get offer details
```

### Tokens

```bash
/dex assets                List top tokens by volume
/dex asset <id|code>       Get token details (e.g., SBX, DBX)
/dex search <query>        Search tokens
/dex price <code>          Get token price
```

### Pairs

```bash
/dex pairs                 List trading pairs
/dex pair <id>             Get pair details
```

### Stats

```bash
/dex stats                 Get platform statistics
```

### Shortcuts

```bash
/dex SBX                   Quick price lookup
/dex DBX                   Quick price lookup
```

## Agent Usage

When users ask about Chia DEX, trading, or token prices:

```javascript
const { handleCommand } = require('./skills/dexie');

// Natural language → formatted response
const output = await handleCommand('show me top tokens');
```

## API Client

For custom integrations:

```javascript
const DexieAPI = require('./skills/dexie/lib/api');
const api = new DexieAPI();

// Get active offers
const offers = await api.getOffers({ page_size: 20, status: 0 });

// Get token details
const token = await api.getAsset('a628c1c2c6fcb74d53746157e438e108eab5c0bb3e5c80ff9b1910b3e4832913');

// List all assets
const assets = await api.getAssets({ page_size: 50, sort: 'volume' });

// Get trading pairs
const pairs = await api.getPairs();
```

## Installation

```bash
cd skills/dexie
npm install
chmod +x cli.js
npm link  # Makes 'dex' and 'dexie' global
```

## Configuration

No API key required — Dexie API is public.

## Output Format

All commands return plain text suitable for:
- Terminal output (CLI)
- Telegram messages
- Discord messages
- WhatsApp messages

## Examples

**Check token price:**
```bash
/dex price SBX
```

**List active offers:**
```bash
/dex offers
```

**Search for a token:**
```bash
/dex search bucks
```

**Get platform stats:**
```bash
/dex stats
```

## Tips

- Asset IDs are long hex strings
- Token codes are short (e.g., SBX, DBX, XCH)
- Use search to find tokens by name
- Prices are in USD
- Volumes and liquidity in XCH

## Support

- Dexie.space: https://dexie.space
- API Docs: https://api.dexie.space/v1
- Bug reports: File in skill repository
