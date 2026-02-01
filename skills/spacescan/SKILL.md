# Spacescan Skill

Explore the Chia blockchain via Spacescan.io API.

## What It Does

- View blocks and transactions
- Check address balances
- Monitor network statistics
- Search blockchain data
- Track CAT tokens and NFTs
- Get XCH price

## ⚠️ API Key Required

Spacescan requires an API key. Get yours at: https://www.spacescan.io/apis

Set the environment variable:
```bash
export SPACESCAN_API_KEY=your_key_here
```

Or add to your shell profile (~/.zshrc or ~/.bashrc):
```bash
echo 'export SPACESCAN_API_KEY=your_key_here' >> ~/.zshrc
source ~/.zshrc
```

## Commands

All commands can be triggered via:
- `/scan <command>` in Telegram
- `/spacescan <command>` in Telegram
- `scan <command>` in CLI
- `spacescan <command>` in CLI

### Blocks

```bash
/scan block latest          Get latest block
/scan block <height>        Get block by height
/scan block <hash>          Get block by hash
/scan blocks <start> <end>  Get block range
```

### Transactions

```bash
/scan tx <id>               Get transaction details
```

### Addresses

```bash
/scan address <addr>        Get address info
/scan address balance <a>   Get address balance
/scan address txs <addr>    Get recent transactions
```

### Coins

```bash
/scan coin <id>             Get coin details
```

### Network

```bash
/scan stats                 Network statistics
/scan network               Network info
/scan space                 Network space (EiB)
/scan mempool               Mempool status
/scan price                 XCH price
```

### Tokens

```bash
/scan cats                  List CAT tokens
/scan cat <id>              Get CAT details
```

### NFTs

```bash
/scan nft <id>              Get NFT details
```

### Search

```bash
/scan search <query>        Search blockchain
/scan <long_hash>           Quick search
```

## Agent Usage

```javascript
const { handleCommand } = require('./skills/spacescan');

// Requires SPACESCAN_API_KEY environment variable
const output = await handleCommand('block latest');
```

## API Client

```javascript
const SpacescanAPI = require('./skills/spacescan/lib/api');
const api = new SpacescanAPI('your-api-key');

// Get latest block
const block = await api.getLatestBlock();

// Get address balance
const balance = await api.getAddressBalance('xch1...');

// Get network stats
const stats = await api.getNetworkStats();

// Search
const result = await api.search('xch1...');
```

## Installation

```bash
cd skills/spacescan
npm install
chmod +x cli.js
npm link  # Makes 'scan' and 'spacescan' global
```

## Configuration

**Required:** Set your API key

```bash
export SPACESCAN_API_KEY=your_key_here
```

Get your key at: https://www.spacescan.io/apis

Free tier available with rate limits.

## Examples

**Check latest block:**
```bash
/scan block latest
```

**Get address balance:**
```bash
/scan address balance xch1...
```

**Network stats:**
```bash
/scan stats
```

**XCH price:**
```bash
/scan price
```

## Support

- Spacescan: https://www.spacescan.io
- API Plans: https://www.spacescan.io/apis
- Bug reports: File in skill repository
