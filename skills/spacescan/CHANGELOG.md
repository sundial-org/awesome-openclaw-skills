# Changelog

All notable changes to the Spacescan skill will be documented in this file.

## [1.0.0] - 2026-01-29

### Added
- Initial release
- Complete Spacescan.io API wrapper
- API key authentication support
- CLI commands via `scan` and `spacescan`
- Telegram integration with `/scan` command
- Natural language command parsing
- Block browsing (latest, by height, by hash, ranges)
- Transaction lookup
- Address info, balance, and transaction history
- Coin details and tracking
- Network statistics and info
- Network space monitoring
- Mempool status
- XCH price lookup
- CAT token listing and details
- NFT details
- Universal blockchain search
- Formatted output for CLI and messaging platforms
- API client for programmatic access
- ClawdHub package structure
- Comprehensive documentation (SKILL.md, README.md)
- Installation script with API key instructions
- MIT License

### Features
- 🧱 Blocks: Latest, by height/hash, ranges
- 💸 Transactions: Lookup and history
- 👤 Addresses: Balance, transactions, coins
- 🪙 Coins: Details and lineage
- 📊 Network: Stats, space, mempool
- 🎨 NFTs: Details and collections
- 🪙 CATs: Token list and info
- 💰 Price: Real-time XCH price
- 🔍 Search: Universal blockchain search

### Technical
- Node.js 18+ compatibility
- Axios for HTTP requests
- 30-second timeout for API calls
- Graceful error handling with API key validation
- Rate limit error messaging
- API key via environment variable or constructor
- Production-ready code

### Requirements
- **API Key Required:** Get from https://www.spacescan.io/apis
- Set `SPACESCAN_API_KEY` environment variable

---

[1.0.0]: https://github.com/Koba42Corp/spacescan-skill/releases/tag/v1.0.0
