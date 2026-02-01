# Wojak.ink Skill

Browse, search, and analyze Wojak Farmers Plot NFTs from the wojak.ink collection.

## What It Does

**Basic Features:**
- Search NFTs by ID, name, or traits
- View floor prices by character type
- Browse marketplace listings from Dexie
- Look up individual NFT details
- Track collection statistics

**Advanced Features:**
- 🎯 Rarity estimation & scoring
- 📊 Price history tracking & trends
- 🎨 Trait analysis & distribution
- 💎 Deal finder (underpriced NFTs)
- 📈 Market statistics & analytics
- 🔔 Historical data storage

## Collection Info

**Wojak Farmers Plot**
- Total: 4,200 NFTs on Chia blockchain
- 14 character types (Wojak, Soyjak, Waifu, Baddie, and variants)
- Collection ID: `col10hfq4hml2z0z0wutu3a9hvt60qy9fcq4k4dznsfncey4lu6kpt3su7u9ah`
- Website: https://wojak.ink

## Commands

All commands can be triggered via:
- `/wojak <command>` in Telegram
- `wojak <command>` in CLI

### Basic Commands

#### Floor Prices

```bash
/wojak floor                    # Collection floor price
/wojak floor wojak              # Wojak character floor
/wojak floor soyjak             # Soyjak character floor
/wojak floor papa-tang          # Papa Tang floor
```

### Search

```bash
/wojak search "king"            # Search NFTs by trait/name
/wojak search 42                # Find NFT #42 specifically
/wojak search "bepe"            # Find all Bepe variants
```

### Listings

```bash
/wojak listings                 # Show all current listings
/wojak listings wojak           # Show Wojak listings only
/wojak listings alien-waifu     # Show Alien Waifu listings
```

### NFT Lookup

```bash
/wojak nft 1                    # Info about NFT #0001
/wojak nft 4200                 # Info about NFT #4200
```

### Collection Stats

```bash
/wojak stats                    # Collection-wide statistics
/wojak characters               # List all character types
```

### Advanced Features

#### Rarity Analysis

```bash
/wojak rarity 1                 # Estimate rarity for NFT #0001
/wojak rarity 4200              # Check rarity for NFT #4200
```

Provides:
- Estimated rarity score
- Rarity tier (Common → Legendary)
- Approximate rank within collection
- Character type information

#### Price History & Trends

```bash
/wojak history recent           # Last 10 sales
/wojak history trend 24         # 24-hour price trend
/wojak history stats 168        # 7-day price statistics
/wojak track                    # Record current floor price
/wojak track wojak              # Track Wojak floor price
```

Features:
- Sales history tracking
- Price trend detection (rising/falling/stable)
- Statistical analysis (min/max/avg/change%)
- Automated data storage

#### Trait Analysis

```bash
/wojak traits                   # List trait categories
/wojak traits Head              # Head trait distribution
/wojak traits Background        # Background trait distribution
```

Analyze:
- Trait categories (Base, Face, Clothes, etc.)
- Trait rarity percentages
- Trait combinations
- Naked floor prices per trait

#### Deal Finder

```bash
/wojak deals                    # Find 10%+ discounts
/wojak deals 20                 # Find 20%+ discounts
/wojak deals 5                  # Find 5%+ discounts
```

Automatically:
- Calculates average listing price
- Finds NFTs below threshold
- Sorts by best deals first
- Shows savings percentage

## Character Types

The collection has 14 character types:

| Character | Count | ID Range |
|-----------|-------|----------|
| Wojak | 800 | #0001-#0800 |
| Soyjak | 700 | #0801-#1500 |
| Waifu | 500 | #1501-#2000 |
| Baddie | 500 | #2001-#2500 |
| Papa Tang | 100 | #2501-#2600 |
| Monkey Zoo | 300 | #2601-#2900 |
| Bepe Wojak | 200 | #2901-#3100 |
| Bepe Soyjak | 200 | #3101-#3300 |
| Bepe Waifu | 200 | #3301-#3500 |
| Bepe Baddie | 200 | #3501-#3700 |
| Alien Wojak | 150 | #3701-#3850 |
| Alien Soyjak | 150 | #3851-#4000 |
| Alien Waifu | 100 | #4001-#4100 |
| Alien Baddie | 100 | #4101-#4200 |

## Agent Usage

When users ask about Wojak NFTs, the collection, or marketplace data:

```javascript
const { handleCommand } = require('./skills/wojak-ink');

// Natural language → formatted response
const output = await handleCommand(['floor', 'wojak']);
```

The skill handles:
- Command parsing and normalization
- API calls to MintGarden and Dexie
- Data caching (5-minute TTL)
- Formatted text output (CLI/Telegram friendly)

## API Clients

The skill uses two main APIs:

### MintGarden API
- NFT metadata and collection stats
- Base: `https://api.mintgarden.io`
- No API key required

### Dexie API
- Marketplace offers and listings
- Base: `https://api.dexie.space/v1`
- No API key required

## Installation

```bash
cd ~/clawd/skills/wojak-ink
npm install
chmod +x cli.js
npm link  # Makes 'wojak' command global
```

## Output Format

All commands return plain text suitable for:
- Terminal output (CLI)
- Telegram messages
- Discord messages
- WhatsApp messages

No markdown tables (for WhatsApp compatibility).

## Caching

- Listings cache: 5 minutes
- Prevents excessive API calls
- Force refresh available via code

## Examples

**Find cheapest Wojak:**
```bash
wojak floor wojak
```

**Search for specific NFT:**
```bash
wojak nft 1337
```

**See all Papa Tang listings:**
```bash
wojak listings papa-tang
```

**Search by trait:**
```bash
wojak search "king crown"
```

## Implemented Features

✅ Rarity score estimation
✅ Price history tracking
✅ Trait analysis framework
✅ Deal finder
✅ Market trend detection
✅ Historical data storage

## Future Enhancements

Potential additions:
- Full trait data integration (requires collection scrape)
- Wallet portfolio lookup
- Real-time sales notifications
- Price alerts via Telegram
- Advanced rarity ranking with full metadata
- Trait combination rarity scoring
- Cross-collection comparisons

## Tips

- Character type names are case-insensitive
- NFT IDs can be searched with or without padding
- Search supports partial matches
- Listings update every 5 minutes automatically

## Support

- Collection: https://wojak.ink
- MintGarden: https://mintgarden.io
- Dexie: https://dexie.space
- Bug reports: File in skill repository
