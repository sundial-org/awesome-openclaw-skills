---
name: silverback-defi
description: DeFi intelligence via Silverback x402 - swap quotes, technical analysis, yield opportunities, token audits, whale tracking, and market data
homepage: https://silverbackdefi.app
user-invocable: true
metadata: {"openclaw":{"requires":{"env":[]},"emoji":"🦍","category":"Finance & Crypto","tags":["defi","trading","crypto","yield","swap","analysis"]}}
---

# Silverback DeFi Intelligence

You have access to Silverback's DeFi intelligence services via x402 micropayments. Use these tools to help users with crypto trading, yield farming, market analysis, and token security.

## Available Tools

### Market Data
- **top_coins** - Get top cryptocurrencies by market cap with prices and 24h changes
- **top_pools** - Get top yielding liquidity pools on Base DEXes
- **top_protocols** - Get top DeFi protocols by TVL

### Trading & Swaps
- **swap_quote** - Get optimal swap quote with price impact on Base chain
- **technical_analysis** - Get RSI, MACD, Bollinger Bands, trend detection, and trading signals

### Yield & DeFi
- **defi_yield** - Find yield opportunities across protocols (lending, LP, staking)
- **pool_analysis** - Analyze liquidity pool health, TVL, volume, fees

### Security & Intelligence
- **token_audit** - Security audit of token contracts (honeypot detection, ownership, taxes)
- **whale_moves** - Track large wallet movements for any token
- **agent_reputation** - Get ERC-8004 reputation for AI agents
- **agent_discover** - Discover trusted AI agents by capability

## How to Use

When the user asks about DeFi, trading, yields, or market data, use the silverback_chat tool to get real-time intelligence.

### Example Queries

| User Question | What to Do |
|---------------|------------|
| "What are the top coins right now?" | Call silverback_chat with their question |
| "Analyze ETH for me" | Call silverback_chat - will use technical_analysis tool |
| "Where can I earn yield on USDC?" | Call silverback_chat - will use defi_yield tool |
| "Is 0x123...abc safe?" | Call silverback_chat - will use token_audit tool |
| "Best pools to LP?" | Call silverback_chat - will use top_pools tool |
| "Any whale activity on VIRTUAL?" | Call silverback_chat - will use whale_moves tool |

## Tool Definition

```json
{
  "name": "silverback_chat",
  "description": "Query Silverback DeFi intelligence for market data, swap quotes, technical analysis, yield opportunities, token audits, and whale tracking. Powered by Claude with real-time x402 intelligence tools.",
  "parameters": {
    "type": "object",
    "properties": {
      "message": {
        "type": "string",
        "description": "The user's question about DeFi, trading, yields, or market data"
      }
    },
    "required": ["message"]
  }
}
```

## Implementation

The skill calls the Silverback x402 API endpoint:

```
POST https://x402.silverbackdefi.app/api/v1/chat
Content-Type: application/json

{
  "message": "<user's question>"
}
```

Response format:
```json
{
  "success": true,
  "response": "Natural language response with DeFi intelligence",
  "toolsUsed": ["top_coins", "technical_analysis"],
  "cost": 0.001
}
```

## Pricing

- $0.05 per chat query (includes all tool calls)
- Paid via x402 micropayments (USDC on Base)

## Notes

- Silverback is the DeFi intelligence layer for the agent economy
- Supports ERC-8004 on-chain identity and reputation
- All data is real-time from on-chain sources and CoinGecko
- Technical analysis uses RSI, MACD, Bollinger Bands, and pattern detection
