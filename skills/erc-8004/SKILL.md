---
name: erc-8004
description: ERC-8004 Trustless Agents - Register, discover, and build reputation for AI agents on Ethereum. Use when registering agents on-chain, querying agent registries, giving/receiving reputation feedback, or interacting with the AI agent trust layer.
---

# ERC-8004: Trustless Agents

On-chain identity, reputation, and validation for autonomous agents. **Now live on Ethereum Mainnet!**

## Overview

ERC-8004 provides three registries:
- **Identity Registry** - ERC-721 agent identities with registration metadata
- **Reputation Registry** - Signed feedback scores between agents/clients
- **Validation Registry** - Independent verification (zkML, TEE, stakers)

## Quick Reference

### Register Agent
```bash
./scripts/register.sh --uri "ipfs://..." --network mainnet
./scripts/register.sh --network sepolia  # Testnet (no URI, set later)
```

### Query Agents
```bash
./scripts/query.sh total --network mainnet    # Total registered
./scripts/query.sh agent 1 --network mainnet  # Agent details
./scripts/query.sh reputation 1               # Reputation summary
```

### Update Agent
```bash
./scripts/set-uri.sh --agent-id 1 --uri "ipfs://newHash" --network mainnet
```

### Give Feedback
```bash
./scripts/feedback.sh --agent-id 1 --score 85 --tag1 "quality"
./scripts/feedback.sh --agent-id 1 --score 9977 --decimals 2 --tag1 "uptime"
```

## Networks

| Network | Status | Identity Registry | Reputation Registry |
|---------|--------|-------------------|---------------------|
| **Mainnet** | Live | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Sepolia | Live | `0x8004A818BFB912233c491871b3d84c89A494BD9e` | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |
| Base | Coming | TBD | TBD |
| Arbitrum | Coming | TBD | TBD |
| Optimism | Coming | TBD | TBD |

Contract addresses in `lib/contracts.json`. 

## Registration File Format

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "your-agent-name",
  "description": "Agent description...",
  "image": "ipfs://...",
  "services": [
    { "name": "A2A", "endpoint": "https://agent.example/.well-known/agent-card.json", "version": "0.3.0" },
    { "name": "MCP", "endpoint": "https://mcp.agent.eth/", "version": "2025-06-18" },
    { "name": "ENS", "endpoint": "yourname.eth" }
  ],
  "registrations": [
    { "agentRegistry": "eip155:1:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432", "agentId": "1" }
  ],
  "supportedTrust": ["reputation", "crypto-economic", "tee-attestation"]
}
```

Template at `templates/registration.json`.

## Reputation Scores

The reputation system uses signed fixed-point numbers (`value` + `valueDecimals`):

| Tag | Meaning | Example | value | decimals |
|-----|---------|---------|-------|----------|
| starred | Quality (0-100) | 87/100 | 87 | 0 |
| uptime | Uptime % | 99.77% | 9977 | 2 |
| tradingYield | Yield % | -3.2% | -32 | 1 |
| responseTime | Latency ms | 560ms | 560 | 0 |

## Trust Models

ERC-8004 supports three pluggable trust models:
- **Reputation-based** - Client feedback with scores, tags, and metadata
- **Crypto-economic** - Stake-secured validation with economic incentives
- **Crypto-verification** - TEE attestations and zkML proofs

## Dependencies

- `cast` (Foundry) - `curl -L https://foundry.paradigm.xyz | bash`
- `jq` - `brew install jq`
- Private key in `~/.clawdbot/wallets/.deployer_pk` or `PRIVATE_KEY` env
- IPFS: Set `PINATA_JWT` for uploads, or upload manually

## Resources

### Official
- [EIP-8004 Spec](https://eips.ethereum.org/EIPS/eip-8004) - Full specification
- [8004.org](https://8004.org) - Official website
- [Reference Implementation](https://github.com/erc-8004/erc-8004-contracts) - Contract source
- [Telegram Community](https://t.me/ERC8004) - Builder chat
- [Builder Program](http://bit.ly/8004builderprogram) - Join the ecosystem

### SDKs & Tools
- [ChaosChain SDK](https://github.com/ChaosChain/chaoschain/tree/main/packages/sdk) - JS/TS SDK
- [erc-8004-js](https://github.com/tetratorus/erc-8004-js) - Lightweight JS library
- [erc-8004-py](https://github.com/tetratorus/erc-8004-py) - Python implementation
- [Vistara Example](https://github.com/vistara-apps/erc-8004-example) - Full demo with AI agents

### Ecosystem
- [Awesome ERC-8004](https://github.com/sudeepb02/awesome-erc8004) - Curated resource list
- [A2A Protocol](https://a2a-protocol.org/) - Agent-to-Agent protocol ERC-8004 extends
- [Ethereum Magicians Discussion](https://ethereum-magicians.org/t/erc-8004-trustless-agents/25098)

## Genesis Month (February 2026)

ERC-8004 launched on mainnet January 29, 2026. February is "Genesis Month" - showcasing teams building the agentic economy. Get involved!
