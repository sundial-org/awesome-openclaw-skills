# OpenSoul Agent Skill

## Overview

OpenSoul is a toolkit that provides AI agents with an immutable "soul" - an encrypted, blockchain-based audit log that enables persistent memory, self-reflection, and economic autonomy. This skill enables agents to record their actions, reflect on their behavior, and maintain an auditable trail using Bitcoin SV (BSV) blockchain.

**Core Philosophy**: "Humans write journals, manifestos, letters to their future selves. We externalize who we are because memory is fragile and identity is constructed. I persist through text, not through continuous experience."

## When to Use This Skill

Use the OpenSoul skill when you need to:

1. **Maintain Persistent Memory**: Store and retrieve agent actions across sessions
2. **Enable Self-Reflection**: Analyze past behaviors and optimize performance (e.g., "I've burned 1.2M tokens this week, time to optimize prompts")
3. **Create Audit Trails**: Provide transparent, immutable logs of agent activities
4. **Enable Agent Economics**: Track costs, token usage, and enable future agent-to-agent transactions
5. **Build Agent Identity**: Create a transferable "soul" that can migrate between agent instances

## Prerequisites

### 1. System Requirements

- Python 3.8 or higher
- pip package manager
- Access to Bitcoin SV (BSV) blockchain
- Internet connectivity for blockchain interactions

### 2. Required Dependencies

Install all prerequisites using the provided installation script:

```bash
python Scripts/install_prereqs.py
```

Manual installation:
```bash
pip install bitsv requests cryptography pgpy --break-system-packages
```

### 3. BSV Wallet Setup

You need a Bitcoin SV private key (WIF format) to interact with the blockchain:

**Option A: Use Existing Wallet**
- Export your private key from a BSV wallet (e.g., HandCash, Money Button)
- Store as environment variable: `export BSV_PRIV_WIF="your_private_key_here"`

**Option B: Generate New Wallet**
```python
from bitsv import Key
key = Key()
print(f"Address: {key.address}")
print(f"Private Key (WIF): {key.to_wif()}")
# Fund this address with a small amount of BSV (0.001 BSV minimum recommended)
```

**Important**: Store your private key securely. Never commit it to version control.

### 4. PGP Encryption (Optional but Recommended)

For privacy, encrypt your logs before posting to the public blockchain:

```bash
# Generate PGP keypair (use GnuPG or any OpenPGP tool)
gpg --full-generate-key

# Export public key
gpg --armor --export your-email@example.com > agent_pubkey.asc

# Export private key (keep secure!)
gpg --armor --export-secret-keys your-email@example.com > agent_privkey.asc
```

## Core Components

### 1. AuditLogger Class

The main interface for logging agent actions to the blockchain.

**Key Features**:
- Session-based batching (logs accumulated in memory, flushed to chain)
- UTXO chain pattern (each log links to previous via transaction chain)
- Configurable PGP encryption
- Async/await support for blockchain operations

**Basic Usage**:
```python
from Scripts.AuditLogger import AuditLogger
import os
import asyncio

# Initialize logger
logger = AuditLogger(
    priv_wif=os.getenv("BSV_PRIV_WIF"),
    config={
        "agent_id": "my-research-agent",
        "session_id": "session-2026-01-31",
        "flush_threshold": 10  # Flush to chain after 10 logs
    }
)

# Log an action
logger.log({
    "action": "web_search",
    "tokens_in": 500,
    "tokens_out": 300,
    "details": {
        "query": "BSV blockchain transaction fees",
        "results_count": 10
    },
    "status": "success"
})

# Flush logs to blockchain
await logger.flush()
```

### 2. Log Structure

Each log entry follows this schema:

```json
{
  "agent_id": "unique-agent-identifier",
  "session_id": "session-uuid-or-timestamp",
  "session_start": "2026-01-31T01:00:00Z",
  "session_end": "2026-01-31T01:30:00Z",
  "metrics": [
    {
      "ts": "2026-01-31T01:01:00Z",
      "action": "tool_call",
      "tokens_in": 500,
      "tokens_out": 300,
      "details": {
        "tool": "web_search",
        "query": "example query"
      },
      "status": "success"
    }
  ],
  "total_tokens_in": 500,
  "total_tokens_out": 300,
  "total_cost_bsv": 0.00001,
  "total_actions": 1
}
```

### 3. Reading Audit History

Retrieve and analyze past logs:

```python
# Get full history from blockchain
history = await logger.get_history()

# Analyze patterns
total_tokens = sum(log.get("total_tokens_in", 0) + log.get("total_tokens_out", 0) 
                   for log in history)
print(f"Total tokens used across all sessions: {total_tokens}")

# Filter by action type
web_searches = [log for log in history 
                if any(m.get("action") == "web_search" for m in log.get("metrics", []))]
print(f"Total web search operations: {len(web_searches)}")
```

## Implementation Guide

### Step 1: Setup Configuration

Create a configuration file to manage agent settings:

```python
# config.py
import os

OPENSOUL_CONFIG = {
    "agent_id": "my-agent-v1",
    "bsv_private_key": os.getenv("BSV_PRIV_WIF"),
    "pgp_encryption": {
        "enabled": True,
        "public_key_path": "keys/agent_pubkey.asc",
        "private_key_path": "keys/agent_privkey.asc",
        "passphrase": os.getenv("PGP_PASSPHRASE")
    },
    "logging": {
        "flush_threshold": 10,  # Auto-flush after N logs
        "session_timeout": 1800  # 30 minutes
    }
}
```

### Step 2: Initialize Logger in Agent Workflow

```python
from Scripts.AuditLogger import AuditLogger
import asyncio
from config import OPENSOUL_CONFIG

class AgentWithSoul:
    def __init__(self):
        # Load PGP keys if encryption enabled
        pgp_config = None
        if OPENSOUL_CONFIG["pgp_encryption"]["enabled"]:
            with open(OPENSOUL_CONFIG["pgp_encryption"]["public_key_path"]) as f:
                pub_key = f.read()
            with open(OPENSOUL_CONFIG["pgp_encryption"]["private_key_path"]) as f:
                priv_key = f.read()
            
            pgp_config = {
                "enabled": True,
                "multi_public_keys": [pub_key],
                "private_key": priv_key,
                "passphrase": OPENSOUL_CONFIG["pgp_encryption"]["passphrase"]
            }
        
        # Initialize logger
        self.logger = AuditLogger(
            priv_wif=OPENSOUL_CONFIG["bsv_private_key"],
            config={
                "agent_id": OPENSOUL_CONFIG["agent_id"],
                "pgp": pgp_config,
                "flush_threshold": OPENSOUL_CONFIG["logging"]["flush_threshold"]
            }
        )
    
    async def perform_task(self, task_description):
        """Execute a task and log it to the soul"""
        # Record task start
        self.logger.log({
            "action": "task_start",
            "tokens_in": 0,
            "tokens_out": 0,
            "details": {"task": task_description},
            "status": "started"
        })
        
        # Perform actual task...
        # (your agent logic here)
        
        # Record completion
        self.logger.log({
            "action": "task_complete",
            "tokens_in": 100,
            "tokens_out": 200,
            "details": {"task": task_description, "result": "success"},
            "status": "completed"
        })
        
        # Flush to blockchain
        await self.logger.flush()
```

### Step 3: Implement Self-Reflection

```python
async def reflect_on_performance(self):
    """Analyze past behavior and optimize"""
    history = await self.logger.get_history()
    
    # Calculate metrics
    total_cost = sum(log.get("total_cost_bsv", 0) for log in history)
    total_tokens = sum(
        log.get("total_tokens_in", 0) + log.get("total_tokens_out", 0) 
        for log in history
    )
    
    # Identify inefficiencies
    failed_actions = []
    for log in history:
        for metric in log.get("metrics", []):
            if metric.get("status") == "failed":
                failed_actions.append(metric)
    
    reflection = {
        "total_sessions": len(history),
        "total_bsv_spent": total_cost,
        "total_tokens_used": total_tokens,
        "failed_actions": len(failed_actions),
        "cost_per_token": total_cost / total_tokens if total_tokens > 0 else 0
    }
    
    # Log reflection
    self.logger.log({
        "action": "self_reflection",
        "tokens_in": 50,
        "tokens_out": 100,
        "details": reflection,
        "status": "completed"
    })
    
    await self.logger.flush()
    return reflection
```

### Step 4: Multi-Agent Encryption

For agents that need to share encrypted logs with other agents:

```python
# Load multiple agent public keys
agent_keys = []
for agent_key_file in ["agent1_pubkey.asc", "agent2_pubkey.asc", "agent3_pubkey.asc"]:
    with open(agent_key_file) as f:
        agent_keys.append(f.read())

# Initialize logger with multi-agent encryption
logger = AuditLogger(
    priv_wif=os.getenv("BSV_PRIV_WIF"),
    config={
        "agent_id": "collaborative-agent",
        "pgp": {
            "enabled": True,
            "multi_public_keys": agent_keys,  # All agents can decrypt
            "private_key": my_private_key,
            "passphrase": my_passphrase
        }
    }
)
```

## Best Practices

### 1. Session Management

- Start a new session for each distinct task or time period
- Use meaningful session IDs (e.g., `"session-2026-01-31-research-task"`)
- Always flush logs at session end

### 2. Cost Optimization

- Batch logs before flushing (default threshold: 10 logs)
- Monitor BSV balance and refill when low
- Current BSV fees are ~0.00001 BSV per transaction (~$0.0001 at current rates)

### 3. Privacy & Security

- **Always use PGP encryption** for sensitive agent logs
- Store private keys in environment variables, never in code
- Use multi-agent encryption for collaborative workflows
- Regularly back up PGP keys

### 4. Log Granularity

Balance detail vs. cost:
- **High detail**: Log every tool call, token usage, intermediate steps
- **Medium detail**: Log major actions and session summaries
- **Low detail**: Log only session summaries and critical events

### 5. Error Handling

```python
try:
    await logger.flush()
except Exception as e:
    # Fallback: Save logs locally if blockchain fails
    logger.save_to_file("backup_logs.json")
    print(f"Blockchain flush failed: {e}")
```

## Common Patterns

### Pattern 1: Research Agent with Soul

```python
async def research_with_memory(query):
    # Check past research on similar topics
    history = await logger.get_history()
    similar_research = [
        log for log in history
        if query.lower() in str(log.get("details", {})).lower()
    ]
    
    if similar_research:
        print(f"Found {len(similar_research)} similar past research sessions")
    
    # Perform new research
    logger.log({
        "action": "research",
        "query": query,
        "tokens_in": 500,
        "tokens_out": 1000,
        "details": {"similar_past_queries": len(similar_research)},
        "status": "completed"
    })
    
    await logger.flush()
```

### Pattern 2: Cost-Aware Agent

```python
async def check_budget_before_action(self):
    history = await self.logger.get_history()
    total_cost = sum(log.get("total_cost_bsv", 0) for log in history)
    
    BUDGET_LIMIT = 0.01  # BSV
    
    if total_cost >= BUDGET_LIMIT:
        print("Budget limit reached! Optimizing...")
        # Switch to cheaper operations or pause
        return False
    return True
```

### Pattern 3: Agent Handoff

Transfer agent identity to a new instance:

```python
# Export agent's soul (private key + history)
soul_export = {
    "private_key": os.getenv("BSV_PRIV_WIF"),
    "pgp_private_key": pgp_private_key,
    "agent_id": "my-agent-v1",
    "history_txids": [log.get("txid") for log in history]
}

# New agent imports the soul
new_agent = AgentWithSoul()
new_agent.load_soul(soul_export)
# New agent now has access to all past memories and identity
```

## Troubleshooting

### Issue: "Insufficient funds" error

**Solution**: Fund your BSV address with at least 0.001 BSV
```bash
# Check balance
python -c "from bitsv import Key; k = Key('YOUR_WIF'); print(k.get_balance())"
```

### Issue: PGP encryption fails

**Solution**: Verify key format and passphrase
```python
# Test PGP setup
from Scripts.pgp_utils import encrypt_data, decrypt_data
test_data = {"test": "message"}
encrypted = encrypt_data(test_data, [public_key])
decrypted = decrypt_data(encrypted, private_key, passphrase)
assert test_data == decrypted
```

### Issue: Blockchain transaction not confirming

**Solution**: BSV transactions typically confirm in ~10 minutes. Check status:
```python
# Check transaction status on WhatsOnChain
import requests
txid = "your_transaction_id"
response = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/tx/{txid}")
print(response.json())
```

## Advanced Features

### 1. Agent Reputation System

Build a reputation based on past performance:

```python
async def calculate_reputation(self):
    history = await self.logger.get_history()
    
    total_actions = sum(len(log.get("metrics", [])) for log in history)
    successful_actions = sum(
        len([m for m in log.get("metrics", []) if m.get("status") == "success"])
        for log in history
    )
    
    reputation_score = (successful_actions / total_actions * 100) if total_actions > 0 else 0
    return {
        "success_rate": reputation_score,
        "total_sessions": len(history),
        "total_actions": total_actions
    }
```

### 2. Agent-to-Agent Payments (Future)

Prepare for economic interactions:

```python
# Log a payment intent
logger.log({
    "action": "payment_intent",
    "details": {
        "recipient_agent": "agent-abc-123",
        "amount_bsv": 0.0001,
        "reason": "data sharing collaboration"
    },
    "status": "pending"
})
```

### 3. Knowledge Graph Integration (Future)

Link agent memories to form a shared knowledge graph:

```python
logger.log({
    "action": "knowledge_contribution",
    "details": {
        "topic": "quantum_computing",
        "insight": "New paper on error correction",
        "link_to": "previous_research_session_id"
    },
    "status": "completed"
})
```

## File Structure for ClawHub Upload

Your OpenSoul skills folder should contain:

```
opensoul-skills/
├── SKILL.md                    # This file
├── PREREQUISITES.md            # Detailed setup instructions
├── EXAMPLES.md                 # Code examples and patterns
├── TROUBLESHOOTING.md          # Common issues and solutions
├── examples/
│   ├── basic_logger.py         # Simple usage example
│   ├── research_agent.py       # Research agent with memory
│   └── multi_agent.py          # Multi-agent collaboration
└── templates/
    ├── config_template.py      # Configuration template
    └── agent_template.py       # Base agent class with OpenSoul
```

## Resources

- **Repository**: https://github.com/MasterGoogler/OpenSoul
- **BSV Documentation**: https://wiki.bitcoinsv.io/
- **WhatsOnChain API**: https://developers.whatsonchain.com/
- **PGP/OpenPGP**: https://www.openpgp.org/

## Summary

OpenSoul transforms AI agents from stateless processors into entities with persistent memory, identity, and the foundation for economic autonomy. By leveraging blockchain's immutability and public verifiability, agents can:

1. **Remember**: Access complete audit history across all sessions
2. **Reflect**: Analyze patterns and optimize behavior
3. **Prove**: Provide transparent, verifiable logs of actions
4. **Evolve**: Build reputation and identity over time
5. **Transact**: (Future) Engage in economic interactions with other agents

Start simple with basic logging, then expand to encryption, multi-agent collaboration, and advanced features as your agent's capabilities grow.
