---
name: opensea-mcp
description: Query OpenSea NFT marketplace data via official MCP server. Get floor prices, trending collections, token prices, wallet balances, swap quotes, and NFT holdings. Supports Ethereum, Base, Polygon, Solana, and other major chains. Requires OpenSea developer account for MCP token.
homepage: https://docs.opensea.io/docs/mcp
metadata: {"openclaw":{"emoji":"🌊","requires":{"bins":["mcporter"],"env":["OPENSEA_MCP_TOKEN"]}}}
---

# OpenSea MCP

Access OpenSea's NFT marketplace data via the official hosted MCP server.

## Setup

### 1. Get MCP Token

1. Sign in to [opensea.io](https://opensea.io)
2. Go to [Settings → Developer](https://opensea.io/account/settings/developer)
3. Copy your MCP token

### 2. Add to Environment

```bash
# Add to ~/.openclaw/.env or export
OPENSEA_MCP_TOKEN=your_token_here
```

### 3. Configure mcporter

Add to `config/mcporter.json`:

```json
{
  "mcpServers": {
    "opensea": {
      "baseUrl": "https://mcp.opensea.io/mcp",
      "description": "OpenSea NFT Data API",
      "headers": {
        "Authorization": "Bearer ${OPENSEA_MCP_TOKEN}"
      }
    }
  }
}
```

### 4. Test

```bash
mcporter list opensea
mcporter call 'opensea.search(query: "trending NFT collections")'
```

## Available Tools

| Tool | Description | Example |
|------|-------------|---------|
| `search` | AI-powered search across OpenSea | `search(query: "Pudgy Penguins")` |
| `get_collections` | Collection details, floor, stats | `get_collections(slugs: ["pudgypenguins"])` |
| `search_collections` | Find collections by name | `search_collections(query: "azuki")` |
| `get_items` | NFT item details | `get_items(ids: ["..."])` |
| `search_items` | Find individual NFTs | `search_items(query: "Bored Ape #1234")` |
| `get_tokens` | Token/coin prices | `get_tokens(symbols: ["WETH"])` |
| `search_tokens` | Find tokens | `search_tokens(query: "PEPE")` |
| `get_token_swap_quote` | Swap quotes with gas | `get_token_swap_quote(...)` |
| `get_token_balances` | Wallet token holdings | `get_token_balances(address: "0x...")` |
| `get_nft_balances` | Wallet NFT holdings | `get_nft_balances(address: "vitalik.eth")` |

## Usage Examples

### Get Floor Prices

```bash
mcporter call 'opensea.get_collections(slugs: ["pudgypenguins", "azuki", "boredapeyachtclub"])'
```

### Search Trending

```bash
mcporter call 'opensea.search(query: "trending NFT collections this week")'
```

### Check Wallet NFTs

```bash
mcporter call 'opensea.get_nft_balances(address: "vitalik.eth")'
```

### Token Prices

```bash
mcporter call 'opensea.get_tokens(symbols: ["ETH", "WETH", "USDC"])'
```

### Swap Quote

```bash
mcporter call 'opensea.get_token_swap_quote(from: "ETH", to: "USDC", amount: "1")'
```

## Supported Chains

Ethereum, Base, Polygon, Solana, Arbitrum, Optimism, Avalanche, BNB Chain, Klaytn

## Resources

- [OpenSea MCP Docs](https://docs.opensea.io/docs/mcp)
- [Developer Portal](https://opensea.io/account/settings/developer)
- [Sample App](https://github.com/ProjectOpenSea/opensea-mcp-next-sample)
