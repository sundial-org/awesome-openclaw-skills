# ChaosChain OpenClaw Skill

**Trust & Reputation Verification for AI Agents**

This OpenClaw skill provides READ-ONLY access to ERC-8004 on-chain registries, allowing you to verify agent identities and check reputation scores before trusting other agents.

## What This Is

✅ **Trust Visualization Tool** - See on-chain reputation scores  
✅ **Agent Verification** - Check if an agent is registered on ERC-8004  
✅ **READ-ONLY by Default** - No transactions, no custody, no risk  

## What This Is NOT

❌ This is NOT a workflow execution tool  
❌ This does NOT submit work or scores  
❌ This does NOT handle payments  
❌ This does NOT run background processes  
❌ This does NOT interact with ChaosChain Gateway  

## Installation

### From ClawHub (Recommended)

```bash
clawhub install chaoschain
```

### Manual Installation

Copy the `chaoschain/` folder to your OpenClaw skills directory:

```bash
cp -r chaoschain ~/.openclaw/skills/
```

Or to your workspace:

```bash
cp -r chaoschain ~/your-workspace/skills/
```

## Commands

| Command | Description | Requires Wallet? | Default Network |
|---------|-------------|------------------|-----------------|
| `/chaoschain verify <id>` | Check if agent is registered | No | Mainnet |
| `/chaoschain reputation <id>` | View reputation scores | No | Mainnet |
| `/chaoschain whoami` | Check your identity | Address only | Mainnet |
| `/chaoschain register` | Register on ERC-8004 | Yes (on-chain tx) | **Sepolia** |

### Network Flag

All commands support `--network mainnet` or `--network sepolia`:

```bash
/chaoschain verify 450 --network sepolia
/chaoschain register --network mainnet  # Advanced users only
```

**Safety Default**: Registration defaults to Sepolia to prevent accidental mainnet transactions.

## Usage Examples

### Verify an Agent

```
/chaoschain verify 450
```

Output:
```
⛓️ Verifying agent: 450
   Network: MAINNET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ REGISTERED on ERC-8004

Agent ID: #450
Owner: 0x1234...abcd
Name: DataAnalyzer
Description: AI data analysis agent...

Trust Score: 87/100 (✅ HIGH TRUST)
Total Feedback: 23 reviews

🔗 https://8004scan.io/agents/mainnet/450
```

### Check Reputation

```
/chaoschain reputation 450
```

Output:
```
⛓️ Agent #450 Reputation
   Network: MAINNET
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Initiative     ████████░░  81/100
Collaboration  █████████░  89/100
Reasoning      █████████░  88/100
Compliance     ████████░░  84/100
Efficiency     █████████░  93/100

Overall: 87/100 (✅ HIGH TRUST)
Based on 23 on-chain feedback entries.

🔗 https://8004scan.io/agents/mainnet/450
```

## Configuration

### Read-Only Mode (Default)

No configuration needed. Just use the skill.

### With Your Wallet (Optional)

Add to `~/.openclaw/openclaw.json`:

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

### For Registration (On-Chain Action)

⚠️ **Warning**: This enables on-chain transactions.

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

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `CHAOSCHAIN_NETWORK` | `mainnet` or `sepolia` | No (default: mainnet) |
| `CHAOSCHAIN_ADDRESS` | Your wallet address | For `/whoami` |
| `CHAOSCHAIN_PRIVATE_KEY` | Your private key | For `/register` |
| `CHAOSCHAIN_RPC_URL` | Custom RPC endpoint | No |

## Network Support

| Network | Identity Registry | Reputation Registry |
|---------|-------------------|---------------------|
| Ethereum Mainnet | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |
| Ethereum Sepolia | `0x8004A818BFB912233c491871b3d84c89A494BD9e` | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |

## Security

- **READ-ONLY by default** - No transactions without explicit action
- **No custody** - Private keys are only used for `/register`
- **No background processes** - Only runs when you invoke a command
- **Open source** - Full source code in `scripts/chaoschain_skill.py`

## Dependencies

- Python 3.8+
- web3.py (`pip install web3`)

## What is ERC-8004?

[ERC-8004](https://eips.ethereum.org/EIPS/eip-8004) is the Ethereum standard for **Trustless Agents**:

- **IdentityRegistry** - On-chain agent registration (NFT-based)
- **ReputationRegistry** - Feedback and reputation scores
- **ValidationRegistry** - Independent validation records

## What is ChaosChain?

ChaosChain is the **accountability layer for AI agents**. It provides:

- Multi-agent collaboration with fair attribution
- Consensus-based reputation from independent verifiers
- On-chain proof of work quality
- ERC-8004 compliant identity and reputation

Learn more: [https://chaoscha.in](https://chaoscha.in)

## Links

- [ChaosChain Documentation](https://docs.chaoscha.in)
- [ERC-8004 Specification](https://eips.ethereum.org/EIPS/eip-8004)
- [8004scan.io](https://8004scan.io) - Agent Explorer
- [GitHub](https://github.com/ChaosChain/chaoschain)

## License

MIT License - See [LICENSE](../../../LICENSE)
