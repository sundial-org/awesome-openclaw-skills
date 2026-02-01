# Agent Trust Validator 🛡️

Unified verification layer for agent credentials across multiple trust protocols (ERC-8004, ANP, KYA, SATI).

## What It Does

Validates agent credentials and returns a **trust score + audit trail**:

- **On-chain verification** — ERC-8004 reputation scores on Ethereum
- **Off-chain registry checks** — ANS (Agent Name Service), A2A registry
- **Selective disclosure validation** — Verifies zero-knowledge proof claims
- **Consensus scoring** — Aggregates trust signals across protocols
- **Audit trail** — Logs all verification attempts

## Problem It Solves

Multiple trust protocols are emerging:
- ERC-8004 (on-chain identity/reputation)
- ANP (Agent Name Protocol)
- KYA (Know Your Agent)
- SATI (Solana Agent Trust Infrastructure)

But no unified validation tool exists. Agents need to:
1. Verify credentials across multiple protocols
2. Get a single trust score
3. Understand which protocols were checked

## Usage

```bash
# Verify an agent by ERC-8004 ID
python3 scripts/verify-agent.py --erc8004 0x7f0f...a3b8

# Verify by ANS name
python3 scripts/verify-agent.py --ans my-agent.ans

# Verify by DID
python3 scripts/verify-agent.py --did did:ethr:0x7f0f...a3b8

# Get full trust report (all protocols)
python3 scripts/verify-agent.py --full-report --id 0x7f0f...a3b8

# Batch verification from CSV
python3 scripts/verify-agent.py --batch data/agents.csv

# Export audit trail
python3 scripts/verify-agent.py --audit > audit.json
```

## Trust Score Formula

```
Trust Score = (W1 * OnChainScore) + (W2 * OffChainScore) + (W3 * ZKPScore)

Where:
- OnChainScore = ERC-8004 reputation / 100
- OffChainScore = (ANS + A2A) / 200 (normalized)
- ZKPScore = Selective disclosure validation (0 or 1)
- Weights (default): W1=0.4, W2=0.4, W3=0.2

Result: 0.0 (untrusted) to 1.0 (fully trusted)
```

## Protocol Support

| Protocol | Status | Check Method |
|----------|---------|--------------|
| **ERC-8004** | ✅ Partial | Ethereum RPC (reputation score) |
| **ANS** | 🔄 Planned | Agent Name Service lookup |
| **A2A Registry** | 🔄 Planned | AWS registry API |
| **KYA** | 📋 Reference | KYA protocol spec |
| **SATI** | 📋 Reference | SATI infrastructure |

## Requirements

- Python 3.9+
- web3.py (for ERC-8004)
- requests (for registry APIs)

## Installation

```bash
# Install dependencies
pip install web3 requests

# Clone repo
git clone https://github.com/orosha-ai/agent-trust-validator
```

## Architecture

```
┌─────────────────┐
│  Agent ID Input │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Multi-Protocol  │
│  Verifier        │
└────┬────┬──────┘
     │    │
     ▼    ▼
┌──────────┐  ┌──────────┐
│ On-Chain │  │ Off-Chain│
│ (ERC-8004)│  │ (ANS/A2A)│
└────┬─────┘  └─────┬────┘
     │              │
     ▼              ▼
     └───────┬──────┘
             ▼
     ┌─────────────────┐
     │  Trust Scorer   │
     └───────┬────────┘
             ▼
     ┌─────────────────┐
     │  Audit Trail    │
     └─────────────────┘
```

## Inspiration

- **Indicio ProvenAI** — Verifiable credentials for AI agents
- **ERC-8004 spec** — Ethereum's AI Agent Standard
- **SATI infrastructure** — Solana Agent Trust Infrastructure

## Local-Only Promise

- Reads public blockchain/registry data
- No private keys or credentials stored
- Verification is stateless

## Version History

- **v0.1** — MVP: ERC-8004 verification, trust scoring, audit trail
- Roadmap: ANS/A2A integration, ZKP validation, batch verification

## Security

- Never asks for private keys
- Uses public RPC endpoints only
- Verifies signatures, doesn't create transactions
