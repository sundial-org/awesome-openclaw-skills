# 🍊 Wojak.ink Skill

A Clawdbot skill for browsing, searching, and analyzing Wojak Farmers Plot NFTs.

## Quick Start

```bash
# Install
cd ~/clawd/skills/wojak-ink
npm install
chmod +x cli.js

# Test
node cli.js help
node cli.js characters
node cli.js nft 1
```

## Features

✅ **Floor Price Tracking** - Get floor prices for the entire collection or specific characters  
✅ **NFT Search** - Search by ID, name, or traits  
✅ **Marketplace Listings** - Browse active offers from Dexie  
✅ **Character Types** - 14 different character variants  
✅ **Collection Stats** - Total volume, floor, listed count  
✅ **Caching** - 5-minute cache to reduce API load

## Usage

### CLI

```bash
wojak floor                    # Collection floor
wojak floor wojak              # Wojak floor
wojak search "king"            # Search
wojak nft 42                   # NFT details
wojak listings papa-tang       # Listings
wojak characters               # Character types
```

### Telegram

```
/wojak floor
/wojak search bepe
/wojak nft 1337
/wojak listings wojak
```

### As a Module

```javascript
const { handleCommand } = require('./skills/wojak-ink');

const output = await handleCommand(['floor', 'wojak']);
console.log(output);
```

## Collection

**Wojak Farmers Plot**
- 4,200 total NFTs
- 14 character types
- Chia blockchain
- Collection: `col10hfq...u7u9ah`

## Data Sources

- **MintGarden API** - NFT metadata, collection stats
- **Dexie API** - Marketplace offers and pricing
- **IPFS** - NFT images via Web3.Storage

## Character Types

| Type | Count | Range |
|------|-------|-------|
| Wojak | 800 | 1-800 |
| Soyjak | 700 | 801-1500 |
| Waifu | 500 | 1501-2000 |
| Baddie | 500 | 2001-2500 |
| Papa Tang | 100 | 2501-2600 |
| Monkey Zoo | 300 | 2601-2900 |
| Bepe (4 types) | 200 each | 2901-3700 |
| Alien (4 types) | 100-150 each | 3701-4200 |

## Architecture

```
wojak-ink/
├── SKILL.md          # Documentation
├── cli.js            # CLI interface
├── package.json      # Dependencies
└── lib/
    ├── api.js        # API client (MintGarden/Dexie)
    └── format.js     # Output formatting
```

## Future Ideas

- [ ] Rarity score integration
- [ ] Price history charts
- [ ] Trait rarity analysis
- [ ] Wallet portfolio lookup
- [ ] Sale notifications
- [ ] Price alerts
- [ ] Integration with mint-garden, dexie, spacescan skills

## Contributing

This skill is part of the Clawdbot ecosystem. Improvements welcome!

## License

MIT

---

Built with 🍊 by the Tang Gang
