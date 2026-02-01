<p align="center">
  <h1 align="center">🔍 Spacescan.io API Client</h1>
  <p align="center">
    <strong>Explore the Chia blockchain - blocks, transactions, addresses, network stats</strong>
  </p>
</p>

<p align="center">
  <a href="https://opensource.org/licenses/MIT">
    <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT">
  </a>
  <a href="https://nodejs.org/">
    <img src="https://img.shields.io/badge/Node.js-v18+-green.svg" alt="Node.js: v18+">
  </a>
  <a href="https://spacescan.io">
    <img src="https://img.shields.io/badge/Explorer-Spacescan.io-blue.svg" alt="Spacescan.io">
  </a>
  <a href="https://clawd.bot">
    <img src="https://img.shields.io/badge/Framework-Clawdbot-orange.svg" alt="Built with Clawdbot">
  </a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg" alt="Status">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue.svg" alt="Version">
  <img src="https://img.shields.io/badge/API%20Key-Required-red.svg" alt="API Key Required">
</p>

---

## ⚠️ API Key Required

Spacescan.io requires an API key for access. Get yours at:

**🔑 https://www.spacescan.io/apis**

Free tier available with rate limits.

---

## 🎯 Overview

Access Spacescan.io's comprehensive Chia blockchain API. View blocks, track transactions, monitor addresses, check network stats, and explore CAT tokens and NFTs.

## ✨ Features

- 🧱 **Blocks** — Latest blocks, block ranges, block details
- 💸 **Transactions** — Transaction lookup and history
- 👤 **Addresses** — Balance, transactions, coin tracking
- 🪙 **Coins** — Coin details and lineage
- 📊 **Network** — Stats, space, mempool, blockchain state
- 🎨 **NFTs** — NFT details and collections
- 🪙 **CATs** — Token list and details
- 💰 **Price** — Real-time XCH price
- 🔍 **Search** — Universal blockchain search

## 🚀 Quick Start

### Setup

1. **Get API Key:** https://www.spacescan.io/apis
2. **Set Environment Variable:**

```bash
export SPACESCAN_API_KEY=your_key_here
```

Add to your shell profile for persistence:

```bash
echo 'export SPACESCAN_API_KEY=your_key_here' >> ~/.zshrc
source ~/.zshrc
```

### Installation

```bash
# Via ClawdHub (recommended)
clawdhub install spacescan

# Or manually
cd ~/.clawd/skills
git clone https://github.com/Koba42Corp/spacescan-skill.git spacescan
cd spacescan
npm install
chmod +x cli.js
npm link
```

### Usage

#### CLI

```bash
# Blocks
scan block latest
scan block 5000000
scan blocks 5000000 5000010

# Transactions
scan tx <tx_id>

# Addresses
scan address xch1...
scan address balance xch1...
scan address txs xch1...

# Network
scan stats
scan price
scan mempool
scan space

# Tokens
scan cats
scan cat <asset_id>

# NFTs
scan nft <nft_id>

# Search
scan search xch1...
```

#### Telegram

```
/scan block latest
/scan price
/scan stats
/scan address xch1...
```

#### Clawdbot Agent

```javascript
const { handleCommand } = require('./skills/spacescan');

// Requires SPACESCAN_API_KEY environment variable
const output = await handleCommand('block latest');
console.log(output);
```

#### API Client

```javascript
const SpacescanAPI = require('./skills/spacescan/lib/api');

// Pass API key directly or use SPACESCAN_API_KEY env var
const api = new SpacescanAPI('your-api-key');

// Get latest block
const block = await api.getLatestBlock();
console.log(`Height: ${block.height}`);

// Check address balance
const balance = await api.getAddressBalance('xch1...');
console.log(`Balance: ${balance.balance / 1e12} XCH`);

// Network stats
const stats = await api.getNetworkStats();
console.log(`Peak: ${stats.peak_height}`);

// Search
const result = await api.search('xch1...');
console.log(`Found: ${result.type}`);
```

## 📖 Command Reference

### Blocks

| Command | Description | Example |
|---------|-------------|---------|
| `scan block latest` | Get latest block | `scan block latest` |
| `scan block <height>` | Get block by height | `scan block 5000000` |
| `scan block <hash>` | Get block by hash | `scan block 0x...` |
| `scan blocks <s> <e>` | Get block range | `scan blocks 100 110` |

### Transactions

| Command | Description | Example |
|---------|-------------|---------|
| `scan tx <id>` | Transaction details | `scan tx 0x...` |

### Addresses

| Command | Description | Example |
|---------|-------------|---------|
| `scan address <addr>` | Address info | `scan address xch1...` |
| `scan address balance <a>` | Get balance | `scan address balance xch1...` |
| `scan address txs <addr>` | Recent transactions | `scan address txs xch1...` |

### Network

| Command | Description | Example |
|---------|-------------|---------|
| `scan stats` | Network statistics | `scan stats` |
| `scan network` | Network info | `scan network` |
| `scan space` | Network space | `scan space` |
| `scan mempool` | Mempool status | `scan mempool` |
| `scan price` | XCH price | `scan price` |

### Tokens & NFTs

| Command | Description | Example |
|---------|-------------|---------|
| `scan cats` | List CAT tokens | `scan cats` |
| `scan cat <id>` | CAT details | `scan cat 0x...` |
| `scan nft <id>` | NFT details | `scan nft nft1...` |

## 🛠️ API Methods

Complete method reference:

### Blockchain
- `getLatestBlock()` — Latest block
- `getBlock(heightOrHash)` — Block details
- `getBlockRange(start, end)` — Block range

### Transactions
- `getTransaction(txId)` — Transaction details
- `getTransactionsByBlock(height)` — Block transactions

### Addresses
- `getAddress(address)` — Address info
- `getAddressBalance(address)` — Balance
- `getAddressTransactions(address, options)` — Transaction history
- `getAddressCoins(address, options)` — Coin list

### Coins
- `getCoin(coinId)` — Coin details
- `getCoinChildren(coinId)` — Child coins

### Network
- `getNetworkStats()` — Statistics
- `getNetworkInfo()` — Network info
- `getNetworkSpace()` — Network space
- `getBlockchainState()` — Blockchain state

### Mempool
- `getMempool()` — Mempool status
- `getMempoolTransaction(txId)` — Mempool transaction

### Tokens & NFTs
- `getCAT(assetId)` — CAT details
- `getCATList(options)` — List CATs
- `getNFT(nftId)` — NFT details
- `getNFTCollection(collectionId)` — NFT collection

### Utilities
- `search(query)` — Universal search
- `getXCHPrice()` — Current XCH price

## 📊 Output Examples

### Latest Block
```
🧱 Latest Block

Height: 5,234,567
Hash: 0x123abc...
Timestamp: 1/29/2026, 3:45:00 PM
Transactions: 42
Farmer: 0x456def...
```

### Network Stats
```
📊 Network Statistics

Peak Height: 5,234,567
Network Space: 32.45 EiB
Total Supply: 8,234,567.1234 XCH
Block Time: 18.75s
Total Transactions: 12,345,678
```

### Price
```
💰 XCH Price

$3.87
₿0.00005432
```

## 🔧 Configuration

### Required

```bash
export SPACESCAN_API_KEY=your_key_here
```

### Optional

Pass API key directly to constructor:

```javascript
const api = new SpacescanAPI('your-api-key');
```

## 🧪 Examples

### Monitor latest blocks

```javascript
const api = new SpacescanAPI();

setInterval(async () => {
  const block = await api.getLatestBlock();
  console.log(`Block ${block.height}: ${block.tx_count} transactions`);
}, 30000); // Every 30 seconds
```

### Track address

```javascript
const api = new SpacescanAPI();
const address = 'xch1...';

const info = await api.getAddress(address);
console.log(`Balance: ${info.balance / 1e12} XCH`);

const txs = await api.getAddressTransactions(address);
console.log(`Recent transactions: ${txs.transactions.length}`);
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

- **Spacescan**: https://www.spacescan.io
- **API Plans**: https://www.spacescan.io/apis
- **Clawdbot**: https://clawd.bot
- **ClawdHub**: https://clawdhub.com
- **Chia Network**: https://chia.net

## 💬 Support

- Issues: [GitHub Issues](https://github.com/Koba42Corp/spacescan-skill/issues)
- Discord: [Clawdbot Community](https://discord.gg/clawd)
- Telegram: [@clawdbot](https://t.me/clawdbot)

---

<p align="center">Made with 🖖 by the Clawdbot community</p>
