<p align="center">
  <h1 align="center">💱 Dexie.space API Client</h1>
  <p align="center">
    <strong>Track Chia DEX trading - offers, prices, liquidity</strong>
  </p>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://nodejs.org/">
    <img src="https://img.shields.io/badge/Node.js-v18+-green.svg" alt="Node.js: v18+">
  </a>
  <a href="https://dexie.space">
    <img src="https://img.shields.io/badge/DEX-Dexie.space-blue.svg" alt="Dexie.space">
  </a>
  <a href="https://clawd.bot">
    <img src="https://img.shields.io/badge/Framework-Clawdbot-orange.svg" alt="Built with Clawdbot">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
</p>

---

## 🎯 Overview

Access the Dexie.space API to track decentralized exchange activity on Chia. Monitor offers, check token prices, view liquidity pools, and analyze trading pairs.

**No API key required** — Dexie's API is free and public.

## ✨ Features

- 💱 **Offers** — Browse active, completed, and cancelled trades
- 🪙 **Tokens** — View prices, volume, liquidity for CATs
- 📊 **Pairs** — List trading pairs and markets
- 🔍 **Search** — Find tokens by name or code
- 📈 **Stats** — Platform-wide statistics

## 🚀 Quick Start

### Installation

```bash
# Via ClawdHub (recommended)
clawdhub install dexie

# Or manually
cd ~/.clawd/skills
git clone https://github.com/Koba42Corp/dexie-skill.git dexie
cd dexie
npm install
chmod +x cli.js
npm link
```

### Usage

#### CLI

```bash
# Offers
dex offers
dex offers completed
dex offer <id>

# Tokens
dex assets
dex asset SBX
dex price DBX
dex search bucks

# Pairs & Stats
dex pairs
dex stats
```

#### Telegram

```
/dex offers
/dex price SBX
/dex assets
/dex stats
```

#### Clawdbot Agent

```javascript
const { handleCommand } = require('./skills/dexie');

const output = await handleCommand('show me top tokens');
console.log(output);
```

#### API Client

```javascript
const DexieAPI = require('./skills/dexie/lib/api');
const api = new DexieAPI();

// Get active offers
const offers = await api.getOffers({ status: 0, page_size: 20 });

// Get token info
const token = await api.getAsset('a628c1c2c6fcb74d53746157e438e108eab5c0bb3e5c80ff9b1910b3e4832913');

// List all tokens
const assets = await api.getAssets({ sort: 'volume' });

// Get pairs
const pairs = await api.getPairs();
```

## 📖 Command Reference

### Offers

| Command | Description | Example |
|---------|-------------|---------|
| `dex offers` | List active offers | `dex offers` |
| `dex offers completed` | List completed trades | `dex offers completed` |
| `dex offers cancelled` | List cancelled offers | `dex offers cancelled` |
| `dex offer <id>` | Offer details | `dex offer Bk6Lr12H6P4DuhPd...` |

### Tokens

| Command | Description | Example |
|---------|-------------|---------|
| `dex assets` | Top tokens by volume | `dex assets` |
| `dex asset <code>` | Token details | `dex asset SBX` |
| `dex price <code>` | Quick price check | `dex price DBX` |
| `dex search <query>` | Search tokens | `dex search bucks` |

### Shortcuts

| Input | Action |
|-------|--------|
| `dex SBX` | Get SBX price |
| `dex DBX` | Get DBX price |

## 🛠️ API Methods

Complete method reference:

### Offers
- `getOffers(options)` — List offers
- `getOffer(id)` — Get offer details

### Assets
- `getAssets(options)` — List tokens
- `getAsset(id)` — Get token details
- `searchCATs(query, options)` — Search tokens

### Pairs
- `getPairs()` — List trading pairs
- `getPair(id)` — Get pair details

### Stats
- `getStats()` — Platform statistics

## 📊 Output Examples

### Token List
```
🪙 Top Tokens by Volume (24h):

1. SBX - Spacebucks
   Price: $0.000067
   Volume: 1.37 XCH
   Liquidity: 669.63 XCH

2. wUSDC.b - Base warp.green USDC
   Price: $0.252859
   Volume: 322.02 XCH
   Liquidity: 2.46K XCH
```

### Offers
```
💱 Active Offers:

1. 163.48 wUSDC.b → 43.91 XCH
   Price: 0.268585
   ID: 6bWyrsjd2FSSmzTbYgmNWcZfGi2d3jcQihjQNFb1ALx1

2. 1000.00 SBX → 0.07 XCH
   Price: 0.000070
   ID: Bk6Lr12H6P4DuhPdzzAcXXApErMxo8712aEfKeNyDPL7
```

## 🔧 Configuration

No configuration required! The API is public and doesn't need authentication.

### Options

Methods accept an `options` object:

```javascript
{
  page: 1,          // Page number
  page_size: 20,    // Results per page
  status: 0,        // Offer status (0=active, 1=completed, 2=cancelled)
  sort: 'volume'    // Sort field
}
```

## 🧪 Examples

### Track a specific token

```javascript
const api = new DexieAPI();

const sbx = await api.getAsset('a628c1c2c6fcb74d53746157e438e108eab5c0bb3e5c80ff9b1910b3e4832913');
console.log(`SBX Price: $${sbx.current_avg_price}`);
console.log(`Volume: ${sbx.volume[0]} XCH`);
```

### Monitor active offers

```javascript
const api = new DexieAPI();

setInterval(async () => {
  const offers = await api.getOffers({ status: 0, page_size: 5 });
  console.log(`Active offers: ${offers.count}`);
  
  offers.offers.forEach(offer => {
    const from = offer.offered[0];
    const to = offer.requested[0];
    console.log(`${from.amount} ${from.code} → ${to.amount} ${to.code}`);
  });
}, 60000); // Every minute
```

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

## 🔗 Links

- **Dexie**: https://dexie.space
- **API**: https://api.dexie.space/v1
- **Clawdbot**: https://clawd.bot
- **ClawdHub**: https://clawdhub.com
- **Chia Network**: https://chia.net

## 💬 Support

- Issues: [GitHub Issues](https://github.com/Koba42Corp/dexie-skill/issues)
- Discord: [Clawdbot Community](https://discord.gg/clawd)
- Telegram: [@clawdbot](https://t.me/clawdbot)

---

<p align="center">Made with 🖖 by the Clawdbot community</p>
