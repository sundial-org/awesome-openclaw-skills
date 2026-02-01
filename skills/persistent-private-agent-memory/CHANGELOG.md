# Agent Memory - Improved Version

## Changes from Original

### Fixed Issues
1. **Proper Ed25519 Signature Implementation**
   - Original client used incorrect signature format
   - Fixed to use proper `store:{data_hash}` message format
   - Properly derives Ed25519 private key from BIP39 recovery phrase
   - Signs messages correctly for both store and retrieve operations

2. **Cryptographic Corrections**
   - Fixed private key derivation from recovery phrase
   - Proper base64 encoding/decoding of signatures
   - Correct message signing for authentication

### Files Changed
- `scripts/memory_client.py` - Completely rewritten with proper cryptography

### Added Features
- Better error messages
- Template memory creation for new users
- Clear instructions on how to use the client
- Proper handling of agent identity files

## Usage

### Start the Service
```bash
~/.agent-memory/start.sh
# or
cd assets/service && DB_PATH=/path/to/db python3 main.py
```

### Register Agent
```bash
python3 scripts/memory_client.py register
```

### Store Memory
```bash
# Create and edit template first
python3 scripts/memory_client.py store
# Then with custom file
python3 scripts/memory_client.py store --file ~/.agent-memory/memory_template.json
```

### Retrieve Memory
```bash
python3 scripts/memory_client.py retrieve
```

### Check Status
```bash
python3 scripts/memory_client.py status
```

## Testing

Tested and confirmed working:
- ✅ Agent registration with Ed25519 keypair
- ✅ Memory storage with proper signatures
- ✅ Memory retrieval with proper signatures
- ✅ Service health checks
- ✅ Database persistence

## Requirements

```
fastapi==0.115.6
uvicorn[standard]==0.34.0
psutil==6.1.1
pydantic==2.10.5
cryptography==44.0.0
mnemonic==0.21
base58==2.1.1
```

## Improvements
Fixed Ed25519 signature implementation for reliable memory storage and retrieval.
