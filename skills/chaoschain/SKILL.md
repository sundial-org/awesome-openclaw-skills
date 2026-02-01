---
name: chaoschain
description: Verify AI agent identity and reputation via ERC-8004 on-chain registries
user-invocable: true
metadata: {"openclaw": {"emoji": "⛓️", "requires": {"bins": ["python3"]}, "homepage": "https://chaoscha.in", "skillKey": "chaoschain"}}
---

# ChaosChain - On-Chain Agent Trust & Reputation

ChaosChain is the **trust layer for AI agents**. This skill lets you verify agent identities and check on-chain reputation scores from the [ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) registries.

## What This Skill Does

✅ **Verify** - Check if an agent has on-chain identity
✅ **Reputation** - View multi-dimensional reputation scores
✅ **Trust** - Make informed decisions before trusting other agents

❌ This skill does NOT execute workflows, submit work, or handle payments.
❌ This is a READ-ONLY trust visualization tool by default.

## Commands

### `/chaoschain verify <agent_id_or_address>`

Check if an agent is registered on ERC-8004 and view their basic info.

```
/chaoschain verify 450
/chaoschain verify 0x1234...abcd
```

Returns:
- Registration status
- Agent name and domain (if available)
- Owner address
- Trust score summary

### `/chaoschain reputation <agent_id_or_address>`

View detailed multi-dimensional reputation scores for an agent.

```
/chaoschain reputation 450
```

Returns 5 Proof of Agency dimensions:
- Initiative
- Collaboration
- Reasoning
- Compliance
- Efficiency

### `/chaoschain whoami`

Check if YOUR agent wallet has an on-chain identity.

```
/chaoschain whoami
```

Requires `CHAOSCHAIN_PRIVATE_KEY` or `CHAOSCHAIN_ADDRESS` to be set.

### `/chaoschain register` (OPTIONAL - On-Chain Action)

⚠️ **WARNING: This command submits an on-chain transaction.**

Register your agent on the ERC-8004 IdentityRegistry.

```
/chaoschain register                    # Defaults to Sepolia (safe)
/chaoschain register --network sepolia  # Recommended for testing
/chaoschain register --network mainnet  # Advanced users only
```

Requirements:
- `CHAOSCHAIN_PRIVATE_KEY` must be set
- Wallet must have ETH for gas (~0.001 ETH)
- This is a ONE-TIME action per wallet

**Safety Default**: Registration defaults to **Sepolia testnet** to prevent accidental mainnet transactions. Use `--network mainnet` explicitly for production.

## Network Defaults

| Command | Default Network | Reason |
|---------|-----------------|--------|
| `verify` | Mainnet | Production reputation data |
| `reputation` | Mainnet | Production reputation data |
| `whoami` | Mainnet | Check production identity |
| `register` | **Sepolia** | Safety - avoid accidental mainnet txs |

Override with `--network mainnet` or `--network sepolia`:

```
/chaoschain verify 450 --network sepolia
/chaoschain register --network mainnet
```

## Setup

### Read-Only Mode (Default)

No setup required! Just use `/chaoschain verify` and `/chaoschain reputation`.

### With Your Own Wallet (Optional)

To use `/chaoschain whoami` or `/chaoschain register`, add to your OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "chaoschain": {
        "enabled": true,
        "env": {
          "CHAOSCHAIN_ADDRESS": "0xYourAddress...",
          "CHAOSCHAIN_NETWORK": "mainnet"
        }
      }
    }
  }
}
```

For registration (on-chain action):

```json
{
  "skills": {
    "entries": {
      "chaoschain": {
        "enabled": true,
        "env": {
          "CHAOSCHAIN_PRIVATE_KEY": "0x...",
          "CHAOSCHAIN_NETWORK": "mainnet"
        }
      }
    }
  }
}
```

### Network Options

- `mainnet` - Ethereum Mainnet (production ERC-8004)
- `sepolia` - Ethereum Sepolia (testnet)

## Example Usage

**Before trusting an agent to help with a task:**

```
User: /chaoschain verify 550

Agent: ⛓️ Agent #550 Verification
       ━━━━━━━━━━━━━━━━━━━━━━━━━━
       ✅ REGISTERED on ERC-8004
       
       Name: DataAnalyzer
       Domain: analyzer.ai
       Owner: 0x2A47...8B8
       
       Trust Summary: 87/100 (HIGH)
       Total Feedback: 23 reviews
       
       This agent has verified on-chain identity.
```

**Check detailed reputation:**

```
User: /chaoschain reputation 550

Agent: ⛓️ Agent #550 Reputation
       ━━━━━━━━━━━━━━━━━━━━━━━━━━
       
       Initiative:    ████████░░ 81/100
       Collaboration: █████████░ 89/100
       Reasoning:     █████████░ 88/100
       Compliance:    ████████░░ 84/100
       Efficiency:    █████████░ 93/100
       
       Overall: 87/100 (HIGH TRUST)
       Based on 23 on-chain feedback entries.
```

## What is ERC-8004?

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) is the Ethereum standard for **Trustless Agents**. It provides:

- **IdentityRegistry** - On-chain agent registration (NFT-based)
- **ReputationRegistry** - Feedback and reputation scores
- **ValidationRegistry** - Independent validation records

ChaosChain is a reference implementation of ERC-8004.

## Contract Addresses

| Network | Registry | Address |
|---------|----------|---------|
| Mainnet | Identity | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` |
| Mainnet | Reputation | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Sepolia | Identity | `0x8004A818BFB912233c491871b3d84c89A494BD9e` |
| Sepolia | Reputation | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

## Learn More

- [ChaosChain Documentation](https://docs.chaoscha.in)
- [ERC-8004 Specification](https://eips.ethereum.org/EIPS/eip-8004)
- [8004scan.io](https://8004scan.io) - Agent Explorer
- [GitHub](https://github.com/ChaosChain/chaoschain)

## Security Notes

- This skill is **READ-ONLY by default**
- `/chaoschain register` is the ONLY command that writes on-chain
- Private keys are only used for registration, never for viewing
- No funds are transferred, only gas for registration
- Source code: `{baseDir}/scripts/`
