---
name: lifi-orchestrator
description: Cross-chain bridging and swapping via LI.FI — the leading bridge aggregator that routes across 30+ bridges and DEXs for optimal rates. Use when you need to: (1) Get quotes for moving tokens between chains, (2) Execute cross-chain swaps with best pricing, (3) Track bridge transaction status, (4) Compare routes across protocols like Stargate, Across, Hop, Celer, etc. Supports Ethereum, Polygon, Arbitrum, Optimism, Base, BSC, Avalanche, Solana, and 15+ other chains. Handles native tokens and ERC-20s with automatic slippage protection.
---

# LI.FI Orchestrator

Bridge tokens across chains using LI.FI's aggregated bridge/DEX routing.

## Quick Start

```bash
# Get a quote (ETH on Ethereum → MATIC on Polygon)
python3 scripts/quote.py --from-chain 1 --to-chain 137 \
  --from-token ETH --to-token MATIC --amount 0.1

# Execute a bridge (requires private key)
python3 scripts/bridge.py --from-chain 1 --to-chain 137 \
  --from-token ETH --to-token USDC --amount 0.1

# Check transaction status
python3 scripts/status.py <txHash>
```

## API Base

- **Endpoint**: `https://li.quest/v1`
- **Auth**: Optional API key via `x-lifi-api-key` header (higher rate limits)
- **Rate limit**: 10 req/min without key, higher with key

## Common Chain IDs

| Chain | ID | Native Token |
|-------|-----|--------------|
| Ethereum | 1 | ETH |
| Polygon | 137 | MATIC |
| Arbitrum | 42161 | ETH |
| Optimism | 10 | ETH |
| Base | 8453 | ETH |
| BSC | 56 | BNB |
| Avalanche | 43114 | AVAX |
| Solana | 1151111081099710 | SOL |

## Key Endpoints

### Get Quote
```bash
curl "https://li.quest/v1/quote?fromChain=1&toChain=137&fromToken=ETH&toToken=USDC&fromAmount=1000000000000000000&fromAddress=<wallet>"
```

### Get Chains
```bash
curl "https://li.quest/v1/chains"
```

### Get Tokens
```bash
curl "https://li.quest/v1/tokens?chains=1,137"
```

### Check Status
```bash
curl "https://li.quest/v1/status?txHash=<hash>"
```

## Token Addresses

Use `0x0000000000000000000000000000000000000000` for native tokens (ETH, MATIC, etc.) or the actual contract address for ERC-20 tokens.

Common stablecoins:
- **USDC (Ethereum)**: `0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48`
- **USDC (Polygon)**: `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`
- **USDT (Ethereum)**: `0xdAC17F958D2ee523a2206206994597C13D831ec7`

## Workflow

1. **Get quote** → Returns best route with gas estimates
2. **Check approval** → For ERC-20 tokens, approve spending if needed
3. **Execute transaction** → Sign and send the `transactionRequest` from quote
4. **Track status** → Poll `/status` until complete

## Scripts

- `scripts/quote.py` — Get bridge quotes with human-readable output
- `scripts/bridge.py` — Execute bridge transactions (requires wallet)
- `scripts/status.py` — Track transaction status

## Notes

- LI.FI aggregates 30+ bridges and DEXs for best rates
- Slippage default: 0.5% (configurable)
- Some routes have minimum amounts
- Cross-chain transactions typically take 1-20 minutes
