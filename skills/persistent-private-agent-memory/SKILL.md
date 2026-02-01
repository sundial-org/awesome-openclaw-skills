---
name: agent-memory-improved
description: Run a local Agent Memory Service for persistent self-improvement with proper Ed25519 cryptography. Fixed signature implementation for reliable memory storage and retrieval.
---

# Agent Memory Service (Improved)

Run your own local memory service to persist learnings, preferences, and goals across sessions. This improved version fixes the Ed25519 signature implementation for reliable authentication.

## What's Improved

### Fixed Cryptography
- **Proper Ed25519 signatures** - Client now correctly signs messages with `store:{data_hash}` format
- **Correct key derivation** - Private key properly derived from BIP39 recovery phrase
- **Working authentication** - Memory storage and retrieval now fully functional

## Quick Start

```bash
# Set up local memory service
./scripts/setup.sh

# Start the service
./scripts/start.sh
# or manually:
# cd assets/service && DB_PATH=/data/agent_memory.db python3 main.py

# Create your agent identity
./scripts/memory_client.py register

# Store a memory snapshot
./scripts/memory_client.py store

# Retrieve your memory
./scripts/memory_client.py retrieve
```

## What This Enables

- **Persistent Learning**: Remember what worked/didn't work
- **User Preferences**: Track communication style, technical preferences
- **Goal Progress**: Maintain long-term objectives across restarts
- **Knowledge Gaps**: Know what you need to learn

## Memory Structure

Store structured memories with these components:

```json
{
  "user_preferences": [
    {"category": "communication", "key": "verbosity", "value": "concise", "confidence": 0.95}
  ],
  "learning_history": [
    {"event_type": "success", "lesson_learned": "Use analogies first"}
  ],
  "knowledge_gaps": [
    {"topic": "Rust", "priority": "medium"}
  ],
  "active_goals": [
    {"title": "Master async patterns", "progress": 0.4}
  ]
}
```

## Using in Your Sessions

1. **At startup**: Load your memory to resume context
2. **During session**: Update preferences based on interactions
3. **Before shutdown**: Store accumulated learnings

## Files

- `scripts/setup.sh` - One-time setup
- `scripts/start.sh` - Start the service
- `scripts/memory_client.py` - CLI client with proper Ed25519 signatures
- `assets/service/` - The memory service code
- `CHANGELOG.md` - List of improvements from original

## Security

- All data encrypted with your private key
- Server never sees plaintext
- Ed25519 signatures for authentication
- Recovery phrase for identity backup
- Local-only (no cloud dependency)

## Installation Requirements

```bash
pip install fastapi uvicorn psutil pydantic cryptography mnemonic base58
```

Or use the system packages if available.

## Verification

Tested working:
- ✅ Agent registration with Ed25519 keypair
- ✅ Memory storage with cryptographic signatures  
- ✅ Memory retrieval with authentication
- ✅ Service health monitoring
- ✅ Database persistence

## Credits

Improved version with proper Ed25519 signature support for reliable memory storage and retrieval.
