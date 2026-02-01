# OpenSoul Troubleshooting Guide

This document provides solutions to common issues when implementing OpenSoul in AI agents.

## Table of Contents

1. [Installation Issues](#installation-issues)
2. [BSV Blockchain Issues](#bsv-blockchain-issues)
3. [PGP Encryption Issues](#pgp-encryption-issues)
4. [Transaction Failures](#transaction-failures)
5. [Performance Issues](#performance-issues)
6. [Data Recovery](#data-recovery)

---

## Installation Issues

### Error: "Module not found: bitsv"

**Symptoms**:
```
ModuleNotFoundError: No module named 'bitsv'
```

**Solutions**:

1. **Install with --break-system-packages** (if using system Python):
```bash
pip install bitsv --break-system-packages
```

2. **Use virtual environment** (recommended):
```bash
python -m venv opensoul-env
source opensoul-env/bin/activate  # Windows: opensoul-env\Scripts\activate
pip install bitsv requests cryptography pgpy
```

3. **Verify Python version**:
```bash
python --version  # Should be 3.8+
```

---

### Error: "externally-managed-environment"

**Symptoms**:
```
error: externally-managed-environment

This environment is externally managed
```

**Solutions**:

1. **Add --break-system-packages flag**:
```bash
pip install bitsv --break-system-packages
```

2. **Use pipx** (for isolated installations):
```bash
pipx install bitsv
```

3. **Use virtual environment** (best practice):
```bash
python -m venv venv
source venv/bin/activate
pip install bitsv requests cryptography pgpy
```

---

### Error: Dependencies conflict

**Symptoms**:
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Solution**:

Create a clean virtual environment:
```bash
# Remove old environment
rm -rf opensoul-env

# Create fresh environment
python -m venv opensoul-env
source opensoul-env/bin/activate

# Install dependencies in order
pip install --upgrade pip
pip install bitsv==0.11.9
pip install requests==2.31.0
pip install cryptography==41.0.7
pip install pgpy==0.6.0
```

---

## BSV Blockchain Issues

### Error: "Insufficient funds"

**Symptoms**:
```
bitsv.exceptions.InsufficientFunds: Balance of 0 satoshis is less than 1000 satoshis.
```

**Solutions**:

1. **Check your balance**:
```python
from bitsv import Key
import os

key = Key(os.getenv("BSV_PRIV_WIF"))
balance_satoshis = key.get_balance()
balance_bsv = balance_satoshis / 100000000

print(f"Balance: {balance_satoshis} satoshis ({balance_bsv} BSV)")
```

2. **Fund your wallet**:
   - Buy BSV from an exchange (Coinbase, Kraken, etc.)
   - Send at least 0.001 BSV to your agent's address
   - Minimum recommended: 0.001 BSV (~100 transactions)

3. **Check address**:
```python
print(f"Send BSV to: {key.address}")
```

4. **Verify on block explorer**:
   - Visit: `https://whatsonchain.com/address/YOUR_ADDRESS`
   - Confirm transaction has confirmed (usually ~10 minutes)

---

### Error: "Cannot resolve host: api.whatsonchain.com"

**Symptoms**:
```
requests.exceptions.ConnectionError: Cannot resolve host: api.whatsonchain.com
```

**Solutions**:

1. **Check internet connection**:
```bash
ping api.whatsonchain.com
```

2. **Check DNS**:
```bash
nslookup api.whatsonchain.com
```

3. **Use alternative DNS** (e.g., Google DNS):
```bash
# Linux
sudo echo "nameserver 8.8.8.8" >> /etc/resolv.conf

# macOS
networksetup -setdnsservers Wi-Fi 8.8.8.8 8.8.4.4
```

4. **Check firewall**:
   - Ensure outbound HTTPS (port 443) is allowed
   - Whitelist: `api.whatsonchain.com`

5. **Test API directly**:
```python
import requests

try:
    response = requests.get("https://api.whatsonchain.com/v1/bsv/main/chain/info", timeout=10)
    print(f"✓ API accessible: {response.status_code}")
except Exception as e:
    print(f"✗ API error: {e}")
```

---

### Error: "Transaction not confirming"

**Symptoms**:
- Transaction sent successfully
- Not appearing in block explorer after 30+ minutes

**Solutions**:

1. **Check transaction status**:
```python
import requests

tx_id = "your_transaction_id"
url = f"https://api.whatsonchain.com/v1/bsv/main/tx/{tx_id}"

response = requests.get(url)
if response.status_code == 200:
    print("✓ Transaction found on blockchain")
    print(response.json())
else:
    print(f"✗ Transaction not found: {response.status_code}")
```

2. **Verify transaction was broadcast**:
   - Check logger output for transaction ID
   - Search on: `https://whatsonchain.com/tx/TX_ID`

3. **Check fee rate**:
```python
# Ensure adequate fee (default is usually fine)
from bitsv import Key

key = Key(os.getenv("BSV_PRIV_WIF"))
# Fee is automatically calculated, but can be set:
tx_hash = key.send(outputs, fee=1)  # 1 satoshi/byte
```

4. **Wait for confirmation**:
   - BSV blocks: ~10 minutes average
   - Wait at least 15-20 minutes before concerned

---

### Error: "Invalid private key"

**Symptoms**:
```
ValueError: Invalid WIF private key
```

**Solutions**:

1. **Verify WIF format**:
   - Should start with 'K', 'L', or '5'
   - Should be 51-52 characters long
   - Example: `L1aW4aubDFB7yfras2S1mN3bqg9nwySY8nkoLmJebSLD5BWv3ENZ`

2. **Test key loading**:
```python
from bitsv import Key

try:
    key = Key("YOUR_PRIVATE_KEY_HERE")
    print(f"✓ Valid key. Address: {key.address}")
except ValueError as e:
    print(f"✗ Invalid key: {e}")
```

3. **Re-export from wallet**:
   - If key is from a wallet, re-export in WIF format
   - Ensure no extra whitespace or characters

4. **Generate new key** (if testing):
```python
from bitsv import Key

new_key = Key()
print(f"Address: {new_key.address}")
print(f"Private Key: {new_key.to_wif()}")
```

---

## PGP Encryption Issues

### Error: "PGP decryption failed"

**Symptoms**:
```
pgpy.errors.PGPDecryptionError: Decryption failed
```

**Solutions**:

1. **Verify passphrase**:
```python
from Scripts.pgp_utils import decrypt_data

# Test with known encrypted data
try:
    decrypted = decrypt_data(encrypted, private_key, passphrase)
    print("✓ Passphrase correct")
except Exception as e:
    print(f"✗ Wrong passphrase or corrupted key: {e}")
```

2. **Check key format**:
   - Should be ASCII-armored
   - Should start with `-----BEGIN PGP PRIVATE KEY BLOCK-----`
   - Should end with `-----END PGP PRIVATE KEY BLOCK-----`

3. **Verify key matches encrypted data**:
```python
# Encrypt with public key, decrypt with matching private key
from Scripts.pgp_utils import encrypt_data, decrypt_data

test_data = {"test": "message"}
encrypted = encrypt_data(test_data, [public_key])
decrypted = decrypt_data(encrypted, private_key, passphrase)

assert test_data == decrypted
```

4. **Re-export keys**:
```bash
# Export fresh copies
gpg --armor --export your@email.com > new_pubkey.asc
gpg --armor --export-secret-keys your@email.com > new_privkey.asc
```

---

### Error: "Cannot import PGP key"

**Symptoms**:
```
ValueError: Could not parse PGP key
```

**Solutions**:

1. **Check file encoding**:
```bash
file agent_pubkey.asc
# Should say: ASCII text
```

2. **Remove extra content**:
   - Ensure file contains ONLY the PGP block
   - No extra headers, footers, or whitespace outside the block

3. **Validate key structure**:
```bash
gpg --show-keys agent_pubkey.asc
# Should display key information
```

4. **Re-generate with proper format**:
```bash
gpg --armor --export your@email.com | tee agent_pubkey.asc
```

---

### Error: Multi-agent decryption fails

**Symptoms**:
- Encrypted with multiple public keys
- Only some agents can decrypt

**Solutions**:

1. **Verify all public keys were used in encryption**:
```python
# Ensure all agent keys are in the list
public_keys = [agent1_pub, agent2_pub, agent3_pub]
encrypted = encrypt_data(data, public_keys)
```

2. **Test each key individually**:
```python
for i, (pub, priv, passphrase) in enumerate(keys):
    try:
        encrypted = encrypt_data(data, [pub])
        decrypted = decrypt_data(encrypted, priv, passphrase)
        print(f"✓ Agent {i} key working")
    except Exception as e:
        print(f"✗ Agent {i} key failed: {e}")
```

3. **Ensure key compatibility**:
   - All keys should be RSA 4096-bit (recommended)
   - Generated with compatible tools (GnuPG, GPG4Win, etc.)

---

## Transaction Failures

### Error: "Transaction broadcast failed"

**Symptoms**:
```
Exception: Failed to broadcast transaction
```

**Solutions**:

1. **Retry with exponential backoff**:
```python
import asyncio

async def safe_flush(logger, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await logger.flush()
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt
                print(f"Retry {attempt + 1} after {wait_time}s...")
                await asyncio.sleep(wait_time)
            else:
                raise
```

2. **Check network status**:
```bash
# Test blockchain API
curl https://api.whatsonchain.com/v1/bsv/main/chain/info
```

3. **Verify UTXO availability**:
```python
key = Key(os.getenv("BSV_PRIV_WIF"))
unspents = key.get_unspents()
print(f"Available UTXOs: {len(unspents)}")
```

4. **Save logs locally as fallback**:
```python
try:
    await logger.flush()
except Exception as e:
    print(f"Flush failed: {e}. Saving locally...")
    logger.save_to_file("backup_logs.json")
```

---

### Error: "Double-spend detected"

**Symptoms**:
```
Error: Transaction references spent output
```

**Solutions**:

1. **Wait for previous transaction confirmation**:
```python
import time
import requests

def wait_for_confirmation(tx_id, max_wait=300):
    """Wait up to 5 minutes for confirmation"""
    start = time.time()
    while time.time() - start < max_wait:
        response = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/tx/{tx_id}")
        if response.status_code == 200:
            confirmations = response.json().get('confirmations', 0)
            if confirmations > 0:
                return True
        time.sleep(10)
    return False
```

2. **Avoid rapid successive transactions**:
```python
# Add delay between flushes
await logger.flush()
await asyncio.sleep(15)  # Wait 15 seconds
await logger.flush()
```

3. **Use batching**:
```python
# Accumulate logs before flushing
logger = AuditLogger(
    priv_wif=os.getenv("BSV_PRIV_WIF"),
    config={"flush_threshold": 10}  # Batch 10 logs
)
```

---

## Performance Issues

### Issue: Slow blockchain writes

**Symptoms**:
- `flush()` takes >30 seconds
- Transaction broadcast timeouts

**Solutions**:

1. **Increase timeout**:
```python
import requests

# In Scripts/AuditLogger.py, modify requests timeout
response = requests.post(url, json=payload, timeout=30)  # Increase from default
```

2. **Use batching**:
```python
# Reduce blockchain writes
logger = AuditLogger(
    config={"flush_threshold": 20}  # Flush every 20 logs
)
```

3. **Check network latency**:
```bash
ping api.whatsonchain.com
# Should be <100ms ideally
```

---

### Issue: High token usage

**Symptoms**:
- Average >500 tokens per action
- Exceeding budget quickly

**Solutions**:

1. **Reduce log detail**:
```python
# Instead of logging full details
logger.log({
    "action": "search",
    "tokens_in": 100,
    "tokens_out": 200,
    "details": {"query": "short query"},  # Keep minimal
    "status": "success"
})
```

2. **Log summaries instead of individual actions**:
```python
# Batch actions, log summary
actions = []
for i in range(10):
    actions.append(perform_action(i))

logger.log({
    "action": "batch_summary",
    "tokens_in": sum(a.tokens_in for a in actions),
    "tokens_out": sum(a.tokens_out for a in actions),
    "details": {"count": len(actions)},
    "status": "success"
})
```

3. **Implement reflection-based optimization**:
```python
async def optimize_if_needed(logger):
    history = await logger.get_history()
    total_tokens = sum(
        log.get("total_tokens_in", 0) + log.get("total_tokens_out", 0)
        for log in history
    )
    
    if total_tokens > 100000:  # Threshold
        print("⚠️  High token usage detected. Reducing logging detail...")
        # Adjust logging strategy
```

---

## Data Recovery

### Issue: Lost transaction ID

**Symptoms**:
- Flushed logs but didn't save transaction ID
- Need to retrieve past logs

**Solutions**:

1. **Get all transactions for address**:
```python
import requests
from bitsv import Key

key = Key(os.getenv("BSV_PRIV_WIF"))
address = key.address

response = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/address/{address}/history")
transactions = response.json()

print(f"Found {len(transactions)} transactions")
for tx in transactions:
    print(f"  TX: {tx['tx_hash']}")
```

2. **Parse OP_RETURN data**:
```python
def get_log_from_tx(tx_id):
    response = requests.get(f"https://api.whatsonchain.com/v1/bsv/main/tx/{tx_id}/out/1/hex")
    hex_data = response.text
    
    # Decode OP_RETURN
    # (Implementation depends on your encoding)
    import binascii
    data = binascii.unhexlify(hex_data)
    # Parse JSON...
```

---

### Issue: Corrupted local backup

**Symptoms**:
```
json.decoder.JSONDecodeError: Expecting value
```

**Solutions**:

1. **Validate JSON**:
```bash
python -m json.tool backup_logs.json
# Shows parsing errors
```

2. **Recover from blockchain**:
```python
# Re-download all history
history = await logger.get_history()

# Save as backup
import json
with open("recovered_logs.json", "w") as f:
    json.dump(history, f, indent=2)
```

3. **Implement backup validation**:
```python
import json

def safe_load_backup(filepath):
    try:
        with open(filepath) as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"⚠️  Corrupted backup: {filepath}")
        # Try to recover partial data
        with open(filepath) as f:
            content = f.read()
            # Manual parsing or recovery logic
        return []
```

---

## Advanced Troubleshooting

### Enable Debug Logging

Add verbose logging to diagnose issues:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('OpenSoul')

# In your code
logger.debug(f"Attempting to flush {len(pending_logs)} logs...")
logger.debug(f"Transaction payload: {payload}")
```

### Test in Isolation

Create minimal test scripts:

```python
# test_minimal.py
from Scripts.AuditLogger import AuditLogger
import os
import asyncio

async def test():
    logger = AuditLogger(
        priv_wif=os.getenv("BSV_PRIV_WIF"),
        config={"agent_id": "test"}
    )
    
    logger.log({"action": "test", "tokens_in": 1, "tokens_out": 1, "status": "success"})
    
    tx_id = await logger.flush()
    print(f"Success: {tx_id}")

asyncio.run(test())
```

### Use Testnet for Development

Avoid mainnet costs during testing:

```python
from bitsv import PrivateKeyTestnet

# Use testnet key
key = PrivateKeyTestnet(os.getenv("BSV_TESTNET_WIF"))

# Get free testnet BSV from faucet:
# https://testnet.satoshisvision.network/
```

---

## Getting Help

If issues persist:

1. **Check repository issues**: https://github.com/MasterGoogler/OpenSoul/issues
2. **Review documentation**: [SKILL.md](SKILL.md), [PREREQUISITES.md](PREREQUISITES.md)
3. **Test with examples**: [EXAMPLES.md](EXAMPLES.md)
4. **BSV documentation**: https://wiki.bitcoinsv.io/
5. **WhatsOnChain API docs**: https://developers.whatsonchain.com/

When reporting issues, include:
- Error message (full stack trace)
- Python version
- Operating system
- Steps to reproduce
- Relevant code snippet
