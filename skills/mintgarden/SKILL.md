# MintGarden Skill

Browse, search, and analyze Chia NFTs via the MintGarden API.

## What It Does

- Search NFTs and collections
- View collection stats, floor prices, trading volume
- Track NFT ownership and trade history
- Monitor recent sales and activity
- Get trending collections and top traders
- Access profiles and portfolios

## Commands

All commands can be triggered via:
- `/mg <command>` in Telegram
- `/mintgarden <command>` in Telegram  
- `mg <command>` in CLI
- `mintgarden <command>` in CLI

### Search

```bash
/mg search <query>              # Search everything
/mg search nfts "rare zombie"   # Search NFTs only
/mg search collections "pixel"  # Search collections only
```

### Collections

```bash
/mg collections list            # Top collections by volume
/mg collection <id>             # Collection details
/mg collection nfts <id>        # NFTs in collection
/mg collection stats <id>       # Collection statistics
/mg collection activity <id>    # Recent sales/transfers
```

### NFTs

```bash
/mg nft <launcher_id>           # NFT details
/mg nft history <launcher_id>   # Trade history
/mg nft offers <launcher_id>    # Active offers
```

### Profiles

```bash
/mg profile <username>          # Profile details
/mg profile nfts <username>     # User's NFTs
/mg profile activity <username> # User's recent activity
```

### Events & Stats

```bash
/mg events                      # Recent global activity
/mg events <collection_id>      # Collection-specific events
/mg stats                       # Global marketplace stats
/mg trending                    # Trending collections (24h)
/mg top collectors              # Top collectors (7d)
/mg top traders                 # Top traders (7d)
```

### Shortcuts

```bash
/mg col1abc...                  # Quick collection lookup
/mg nft1abc...                  # Quick NFT lookup
/mg did:chia:...                # Quick profile lookup
```

## Agent Usage

When users ask about Chia NFTs, collections, or MintGarden:

```javascript
const { handleCommand } = require('./skills/mintgarden');

// Natural language → formatted response
const output = await handleCommand('show me trending collections');
```

The skill handles:
- Command parsing and normalization
- API calls with error handling
- Formatted text output (CLI/Telegram friendly)
- Pagination for large results

## API Client

For custom integrations, use the API client directly:

```javascript
const MintGardenAPI = require('./skills/mintgarden/lib/api');
const api = new MintGardenAPI();

// Search
const results = await api.search('zombie');
const nfts = await api.searchNFTs('rare', { limit: 50 });

// Collections
const collections = await api.getCollections({ sort: 'volume_7d' });
const collection = await api.getCollection('col1abc...');
const stats = await api.getCollectionStats('col1abc...');

// NFTs
const nft = await api.getNFT('nft1abc...');
const history = await api.getNFTHistory('nft1abc...');

// Profiles
const profile = await api.getProfile('username');
const profileNFTs = await api.getProfileNFTs('did:chia:...');

// Events
const events = await api.getEvents({ limit: 20 });
const trending = await api.getTrending({ period: '24h' });

// Stats
const globalStats = await api.getGlobalStats();
const topCollectors = await api.getTopCollectors({ period: '7d' });
```

## Installation

```bash
cd skills/mintgarden
npm install
chmod +x cli.js
npm link  # Makes 'mg' and 'mintgarden' global
```

## Configuration

No API key required — MintGarden API is public.

Optional: Set custom base URL via environment:

```bash
export MINTGARDEN_API_URL=https://api.mintgarden.io
```

## Output Format

All commands return plain text suitable for:
- Terminal output (CLI)
- Telegram messages
- Discord messages
- WhatsApp messages

No markdown tables (for WhatsApp compatibility).

## Error Handling

- Invalid IDs → Clear error message
- API failures → Retry-friendly error
- Network issues → Timeout after 30s
- Empty results → Helpful "not found" message

## Limits

- Default limit: 50 results per query
- Max limit: 100 results per query
- No rate limiting (MintGarden is generous)
- Pagination available via API client

## Examples

**Find rare NFTs in a collection:**
```bash
/mg collection nfts col1abc...
```

**Check floor price:**
```bash
/mg collection col1abc...
```

**See what's hot:**
```bash
/mg trending
```

**Track a specific NFT:**
```bash
/mg nft history nft1abc...
```

**Monitor marketplace:**
```bash
/mg events
```

## Tips

- Use shortcuts for quick lookups (paste IDs directly)
- Collection IDs start with `col1`
- NFT launcher IDs start with `nft1`
- Profile DIDs start with `did:chia:`
- Trending updates every hour
- Volume stats use 7-day window by default

## Support

- MintGarden API: https://api.mintgarden.io/docs
- Chia NFTs: https://mintgarden.io
- Bug reports: File in skill repository
