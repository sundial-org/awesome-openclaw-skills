# OpenSea API

Query NFT data, trade on the Seaport marketplace, and swap ERC20 tokens across Ethereum, Base, Arbitrum, Optimism, Polygon, and more.

## Quick start

1. Set `OPENSEA_API_KEY` in your environment
2. Run helper scripts in `scripts/` for common operations
3. Use the MCP server for token swaps and advanced queries

```bash
export OPENSEA_API_KEY="your-api-key"

# Token swap: ETH to token
./scripts/opensea-swap.sh 0xTokenAddress 0.1 0xYourWallet 0xYourKey base

# Token swap: Token to token (specify from_token as last arg)
./scripts/opensea-swap.sh 0xToToken 100 0xYourWallet 0xYourKey base 0xFromToken

# Get collection info
./scripts/opensea-collection.sh boredapeyachtclub

# Get NFT details
./scripts/opensea-nft.sh ethereum 0xbc4ca0eda7647a8ab7c2061c2e118a18a936f13d 1234

# Get best listing price for an NFT
./scripts/opensea-best-listing.sh boredapeyachtclub 1234
```

## Task guide

### Token swaps

OpenSea's API includes a cross-chain DEX aggregator for swapping ERC20 tokens with optimal routing across all supported chains.

| Task | Tool/Script |
|------|-------------|
| Get swap quote with calldata | `get_token_swap_quote` (MCP) or `opensea-swap.sh` |
| Check token balances | `get_token_balances` (MCP) |
| Search tokens | `search_tokens` (MCP) |
| Get trending tokens | `get_trending_tokens` (MCP) |
| Get top tokens by volume | `get_top_tokens` (MCP) |

### Reading NFT data

| Task | Script |
|------|--------|
| Get collection details | `opensea-collection.sh <slug>` |
| Get collection stats | `opensea-collection-stats.sh <slug>` |
| List NFTs in collection | `opensea-collection-nfts.sh <slug> [limit] [next]` |
| Get single NFT | `opensea-nft.sh <chain> <contract> <token_id>` |
| List NFTs by wallet | `opensea-account-nfts.sh <chain> <address> [limit]` |

### Marketplace queries

| Task | Script |
|------|--------|
| Get best listing for NFT | `opensea-best-listing.sh <slug> <token_id>` |
| Get best offer for NFT | `opensea-best-offer.sh <slug> <token_id>` |
| List all collection listings | `opensea-listings-collection.sh <slug> [limit]` |
| List all collection offers | `opensea-offers-collection.sh <slug> [limit]` |
| Get listings for specific NFT | `opensea-listings-nft.sh <chain> <contract> <token_id>` |
| Get offers for specific NFT | `opensea-offers-nft.sh <chain> <contract> <token_id>` |
| Get order by hash | `opensea-order.sh <chain> <order_hash>` |

### Marketplace actions (POST)

| Task | Script |
|------|--------|
| Get fulfillment data (buy NFT) | `opensea-fulfill-listing.sh <chain> <order_hash> <buyer>` |
| Get fulfillment data (accept offer) | `opensea-fulfill-offer.sh <chain> <order_hash> <seller> <contract> <token_id>` |
| Generic POST request | `opensea-post.sh <path> <json_body>` |

### Events and monitoring

| Task | Script |
|------|--------|
| Get collection events | `opensea-events-collection.sh <slug> [event_type] [limit]` |
| Stream real-time events | `opensea-stream-collection.sh <slug>` (requires websocat) |

### Generic requests

| Task | Script |
|------|--------|
| Any GET endpoint | `opensea-get.sh <path> [query]` |
| Any POST endpoint | `opensea-post.sh <path> <json_body>` |

## Buy/Sell workflows

### Buying an NFT

1. Find the NFT and check its listing:
   ```bash
   ./scripts/opensea-best-listing.sh cool-cats-nft 1234
   ```

2. Get the order hash from the response, then get fulfillment data:
   ```bash
   ./scripts/opensea-fulfill-listing.sh ethereum 0x_order_hash 0x_your_wallet
   ```

3. The response contains transaction data to execute on-chain

### Selling an NFT (accepting an offer)

1. Check offers on your NFT:
   ```bash
   ./scripts/opensea-best-offer.sh cool-cats-nft 1234
   ```

2. Get fulfillment data for the offer:
   ```bash
   ./scripts/opensea-fulfill-offer.sh ethereum 0x_offer_hash 0x_your_wallet 0x_nft_contract 1234
   ```

3. Execute the returned transaction data

### Creating listings/offers

Creating new listings and offers requires wallet signatures. Use `opensea-post.sh` with the Seaport order structure - see `references/marketplace-api.md` for full details.

## Scripts reference

### NFT & Collection Scripts
| Script | Purpose |
|--------|---------|
| `opensea-get.sh` | Generic GET (path + optional query) |
| `opensea-post.sh` | Generic POST (path + JSON body) |
| `opensea-collection.sh` | Fetch collection by slug |
| `opensea-collection-stats.sh` | Fetch collection statistics |
| `opensea-collection-nfts.sh` | List NFTs in collection |
| `opensea-nft.sh` | Fetch single NFT by chain/contract/token |
| `opensea-account-nfts.sh` | List NFTs owned by wallet |

### Marketplace Scripts
| Script | Purpose |
|--------|---------|
| `opensea-listings-collection.sh` | All listings for collection |
| `opensea-listings-nft.sh` | Listings for specific NFT |
| `opensea-offers-collection.sh` | All offers for collection |
| `opensea-offers-nft.sh` | Offers for specific NFT |
| `opensea-best-listing.sh` | Lowest listing for NFT |
| `opensea-best-offer.sh` | Highest offer for NFT |
| `opensea-order.sh` | Get order by hash |
| `opensea-fulfill-listing.sh` | Get buy transaction data |
| `opensea-fulfill-offer.sh` | Get sell transaction data |

### Token Swap Scripts
| Script | Purpose |
|--------|---------|
| `opensea-swap.sh` | **Swap tokens via OpenSea MCP** |

### Monitoring Scripts
| Script | Purpose |
|--------|---------|
| `opensea-events-collection.sh` | Collection event history |
| `opensea-stream-collection.sh` | Real-time WebSocket events |

## Supported chains

`ethereum`, `matic`, `arbitrum`, `optimism`, `base`, `avalanche`, `klaytn`, `zora`, `blast`, `sepolia`

## References

- `references/rest-api.md` - REST endpoint families and pagination
- `references/marketplace-api.md` - Buy/sell workflows and Seaport details
- `references/stream-api.md` - WebSocket event streaming
- `references/seaport.md` - Seaport protocol and NFT purchase execution
- `references/token-swaps.md` - **Token swap workflows via MCP**

## OpenSea MCP Server

An official OpenSea MCP server provides direct LLM integration for token swaps and NFT operations. When enabled, Claude can execute swaps, query token data, and interact with NFT marketplaces directly.

**Setup:**

1. Go to the [OpenSea Developer Portal](https://opensea.io/settings/developer) and verify your email
2. Generate a new API key for REST API access
3. Generate a separate MCP token for the MCP server

Add to your MCP config:
```json
{
  "mcpServers": {
    "opensea": {
      "url": "https://mcp.opensea.io/mcp",
      "headers": {
        "Authorization": "Bearer YOUR_MCP_TOKEN"
      }
    }
  }
}
```

Or use the inline token format: `https://mcp.opensea.io/YOUR_MCP_TOKEN/mcp`

### Token Swap Tools
| MCP Tool | Purpose |
|----------|---------|
| `get_token_swap_quote` | **Get swap calldata for token trades** |
| `get_token_balances` | Check wallet token holdings |
| `search_tokens` | Find tokens by name/symbol |
| `get_trending_tokens` | Hot tokens by momentum |
| `get_top_tokens` | Top tokens by 24h volume |
| `get_tokens` | Get detailed token info |

### NFT Tools
| MCP Tool | Purpose |
|----------|---------|
| `search_collections` | Search NFT collections |
| `search_items` | Search individual NFTs |
| `get_collections` | Get detailed collection info |
| `get_items` | Get detailed NFT info |
| `get_nft_balances` | List NFTs owned by wallet |
| `get_trending_collections` | Trending NFT collections |
| `get_top_collections` | Top collections by volume |
| `get_activity` | Trading activity for collections/items |
| `get_upcoming_drops` | Upcoming NFT mints |

### Profile & Utility Tools
| MCP Tool | Purpose |
|----------|---------|
| `get_profile` | Wallet profile with holdings/activity |
| `account_lookup` | Resolve ENS/address/username |
| `get_chains` | List supported chains |
| `search` | AI-powered natural language search |
| `fetch` | Get full details by entity ID |

---

## Token Swaps via MCP

OpenSea MCP supports ERC20 token swaps across supported DEXes - not just NFTs!

### Get Swap Quote
```bash
mcporter call opensea.get_token_swap_quote --args '{
  "fromContractAddress": "0x0000000000000000000000000000000000000000",
  "fromChain": "base",
  "toContractAddress": "0xb695559b26bb2c9703ef1935c37aeae9526bab07",
  "toChain": "base",
  "fromQuantity": "0.02",
  "address": "0xYourWalletAddress"
}'
```

**Parameters:**
- `fromContractAddress`: Token to swap from (use `0x0000...0000` for native ETH)
- `toContractAddress`: Token to swap to
- `fromChain` / `toChain`: Chain identifiers
- `fromQuantity`: Amount in human-readable units (e.g., "0.02" for 0.02 ETH)
- `address`: Your wallet address

**Response includes:**
- `swapQuote`: Price info, fees, slippage impact
- `swap.actions[0].transactionSubmissionData`: Ready-to-use calldata

### Execute the Swap
```javascript
import { createWalletClient, http } from 'viem';
import { privateKeyToAccount } from 'viem/accounts';
import { base } from 'viem/chains';

// Extract from swap quote response
const txData = response.swap.actions[0].transactionSubmissionData;

const wallet = createWalletClient({ 
  account: privateKeyToAccount(PRIVATE_KEY), 
  chain: base, 
  transport: http() 
});

const hash = await wallet.sendTransaction({
  to: txData.to,
  data: txData.data,
  value: BigInt(txData.value)
});
```

### Check Token Balances
```bash
mcporter call opensea.get_token_balances --args '{
  "address": "0xYourWallet",
  "chains": ["base", "ethereum"]
}'
```

## Generating a wallet

To execute swaps or buy NFTs, you need an Ethereum wallet (private key + address).

### Using Node.js
```javascript
import crypto from 'crypto';
import { privateKeyToAccount } from 'viem/accounts';

const privateKey = '0x' + crypto.randomBytes(32).toString('hex');
const account = privateKeyToAccount(privateKey);

console.log('Private Key:', privateKey);
console.log('Address:', account.address);
```

### Using OpenSSL
```bash
# Generate private key
PRIVATE_KEY="0x$(openssl rand -hex 32)"
echo "Private Key: $PRIVATE_KEY"

# Derive address (requires node + viem)
node --input-type=module -e "
import { privateKeyToAccount } from 'viem/accounts';
console.log('Address:', privateKeyToAccount('$PRIVATE_KEY').address);
"
```

### Using cast (Foundry)
```bash
cast wallet new
```

**Important:** Store private keys securely. Never commit them to git or share publicly.

## Requirements

- `OPENSEA_API_KEY` environment variable (for REST API scripts)
- `OPENSEA_MCP_TOKEN` environment variable (for MCP server, separate from API key)
- `curl` for REST calls
- `websocat` (optional) for Stream API
- `jq` (recommended) for parsing JSON responses

Get both credentials at [opensea.io/settings/developer](https://opensea.io/settings/developer).
