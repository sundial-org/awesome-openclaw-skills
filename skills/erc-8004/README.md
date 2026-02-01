# ERC-8004: Trustless Agents

On-chain identity, reputation, and validation for autonomous agents on Ethereum.

 **Now live on Ethereum Mainnet!** (January 29, 2026)

## What is ERC-8004?

ERC-8004 extends the Agent-to-Agent (A2A) Protocol with a trust layer that allows participants to discover, choose, and interact with agents across organizational boundaries without pre-existing trust.

The protocol provides three lightweight on-chain registries:

| Registry | Purpose | Details |
|----------|---------|---------|
| **Identity** | Agent discovery & portable identifiers | ERC-721 with URIStorage |
| **Reputation** | Feedback & attestation system | Signed fixed-point scores |
| **Validation** | Independent verification hooks | TEE, zkML, staking |

## Contract Addresses

### Ethereum Mainnet 
- **Identity Registry:** [`0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`](https://etherscan.io/address/0x8004A169FB4a3325136EB29fA0ceB6D2e539a432)
- **Reputation Registry:** [`0x8004BAa17C55a88189AE136b182e5fdA19dE9b63`](https://etherscan.io/address/0x8004BAa17C55a88189AE136b182e5fdA19dE9b63)

### Sepolia Testnet
- **Identity Registry:** [`0x8004A818BFB912233c491871b3d84c89A494BD9e`](https://sepolia.etherscan.io/address/0x8004A818BFB912233c491871b3d84c89A494BD9e)
- **Reputation Registry:** [`0x8004B663056A597Dffe9eCcC1965A193B7388713`](https://sepolia.etherscan.io/address/0x8004B663056A597Dffe9eCcC1965A193B7388713)

## Quick Start

### Prerequisites

```bash
# Install Foundry (cast)
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Install jq
brew install jq
```

### Register an Agent

```bash
# Set your private key
export PRIVATE_KEY="0x..."

# Register on mainnet
./scripts/register.sh --uri "ipfs://QmYourHash..." --network mainnet

# Or testnet first
./scripts/register.sh --uri "ipfs://QmYourHash..." --network sepolia
```

### Query Agents

```bash
# Total registered agents
./scripts/query.sh total --network mainnet

# Get agent details
./scripts/query.sh agent 1 --network mainnet

# Check reputation
./scripts/query.sh reputation 1 --network mainnet
```

### Give Feedback

```bash
# Rate an agent (0-100 score)
./scripts/feedback.sh --agent-id 1 --score 85 --tag1 "quality" --network mainnet

# Percentage with decimals (99.77%)
./scripts/feedback.sh --agent-id 1 --score 9977 --decimals 2 --tag1 "uptime"
```

## Agent Registration Format

Your `agentURI` should resolve to a JSON registration file:

```json
{
  "type": "https://eips.ethereum.org/EIPS/eip-8004#registration-v1",
  "name": "My Agent",
  "description": "An autonomous agent that...",
  "image": "ipfs://QmImageHash...",
  "services": [
    { "name": "A2A", "endpoint": "https://agent.example/.well-known/agent-card.json" },
    { "name": "MCP", "endpoint": "https://mcp.agent.example/" },
    { "name": "ENS", "endpoint": "myagent.eth" }
  ],
  "supportedTrust": ["reputation"]
}
```

See `templates/registration.json` for a complete example.

## Trust Models

ERC-8004 supports pluggable trust mechanisms:

- **Reputation-based** - Client feedback with scores (0-100), tags, and off-chain metadata
- **Crypto-economic** - Stake-secured validation with economic incentives  
- **Crypto-verification** - TEE attestations and zkML proofs for cryptographic trust

## Resources

-  [EIP-8004 Specification](https://eips.ethereum.org/EIPS/eip-8004)
-  [8004.org](https://8004.org) - Official website
-  [Reference Implementation](https://github.com/erc-8004/erc-8004-contracts)
-  [Telegram Community](https://t.me/ERC8004)
-  [Builder Program](http://bit.ly/8004builderprogram)
-  [Awesome ERC-8004](https://github.com/sudeepb02/awesome-erc8004)

## Related

- [A2A Protocol](https://a2a-protocol.org/) - Agent-to-Agent protocol that ERC-8004 extends
- [ERC-721](https://eips.ethereum.org/EIPS/eip-721) - Base NFT standard for Identity Registry

## License

CC0 - Public Domain

---

*Part of the [Clawdbot Skills](https://clawdhub.com) ecosystem*
