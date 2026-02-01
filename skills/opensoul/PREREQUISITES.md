# OpenSoul Prerequisites

This document provides detailed setup instructions for agents wanting to use the OpenSoul toolkit.

## System Requirements

### Operating System
- Linux (Ubuntu 20.04+, Debian, CentOS)
- macOS (10.15+)
- Windows (with WSL2 recommended)

### Python Environment
- Python 3.8 or higher
- pip 21.0 or higher
- Virtual environment recommended (venv or conda)

### Network Requirements
- Internet connectivity for blockchain interactions
- Outbound HTTPS access to:
  - `api.whatsonchain.com` (BSV blockchain API)
  - PyPI package repositories

## Installation Steps

### Step 1: Clone the Repository

```bash
# Clone OpenSoul repository
git clone https://github.com/MasterGoogler/OpenSoul.git
cd OpenSoul
```

### Step 2: Install Python Dependencies

**Option A: Automated Installation**
```bash
python Scripts/install_prereqs.py
```

**Option B: Manual Installation**
```bash
pip install bitsv==0.11.9 --break-system-packages
pip install requests==2.31.0 --break-system-packages
pip install cryptography==41.0.7 --break-system-packages
pip install pgpy==0.6.0 --break-system-packages
```

**For Virtual Environment (Recommended)**
```bash
python -m venv opensoul-env
source opensoul-env/bin/activate  # On Windows: opensoul-env\Scripts\activate
pip install bitsv requests cryptography pgpy
```

### Step 3: Verify Installation

```python
# test_install.py
try:
    import bitsv
    import requests
    import cryptography
    import pgpy
    print("✓ All dependencies installed successfully!")
    print(f"bitsv version: {bitsv.__version__}")
except ImportError as e:
    print(f"✗ Missing dependency: {e}")
```

Run the verification:
```bash
python test_install.py
```

## Bitcoin SV (BSV) Setup

### Understanding BSV Requirements

OpenSoul uses Bitcoin SV blockchain for:
- **Data storage**: OP_RETURN outputs store log JSON
- **Immutability**: Blockchain ensures logs cannot be altered
- **Public verifiability**: Anyone can audit agent actions
- **Low cost**: Transactions cost ~$0.0001 USD

### Creating a BSV Wallet

**Option 1: Generate New Wallet with bitsv**

```python
from bitsv import Key

# Generate new keypair
key = Key()

print(f"Address: {key.address}")
print(f"Private Key (WIF): {key.to_wif()}")
print(f"Public Key: {key.public_key.hex()}")

# Save private key securely!
with open('bsv_private.key', 'w') as f:
    f.write(key.to_wif())

print("\n⚠️  IMPORTANT: Save your private key in a secure location!")
print("Never commit this file to version control.")
```

**Option 2: Use Existing BSV Wallet**

If you have a BSV wallet (HandCash, Money Button, ElectrumSV):
1. Export your private key in WIF format
2. Save it as environment variable or secure file

### Funding Your Wallet

You need BSV to pay for blockchain transactions:

1. **Get BSV from an exchange**:
   - Buy BSV on exchanges (Coinbase, Kraken, etc.)
   - Transfer to your agent's address

2. **Minimum recommended balance**: 0.001 BSV (~$0.05 USD)
   - Each transaction costs ~0.00001 BSV
   - 0.001 BSV = ~100 transactions

3. **Check balance**:
```python
from bitsv import Key
key = Key('your_private_key_wif')
balance = key.get_balance('bsv')
print(f"Balance: {balance} satoshis ({balance/100000000} BSV)")
```

### Testnet vs Mainnet

**For Development: Use Testnet**
```python
from bitsv import PrivateKeyTestnet

key = PrivateKeyTestnet()
print(f"Testnet Address: {key.address}")

# Get free testnet coins from faucet
# Visit: https://testnet.satoshisvision.network/
```

**For Production: Use Mainnet**
```python
from bitsv import Key

key = Key('your_mainnet_wif')
```

## PGP Encryption Setup

### Why Use PGP?

While blockchain is public, your logs may contain sensitive information:
- API keys or credentials in error messages
- User data or PII
- Proprietary algorithms or strategies
- Internal agent decision-making processes

PGP encryption ensures only authorized parties can read your logs.

### Installing GnuPG

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install gnupg
```

**macOS:**
```bash
brew install gnupg
```

**Windows:**
Download from: https://www.gnupg.org/download/

### Generating PGP Keys

**Interactive Generation:**
```bash
gpg --full-generate-key
```

Follow prompts:
- Key type: RSA and RSA (default)
- Key size: 4096 bits (recommended)
- Expiration: 0 = key does not expire (or set custom)
- Real name: Your agent name (e.g., "Research Agent v1")
- Email: agent-contact@example.com
- Passphrase: Strong passphrase (SAVE THIS!)

**Command-line Generation:**
```bash
gpg --batch --generate-key <<EOF
%no-protection
Key-Type: RSA
Key-Length: 4096
Subkey-Type: RSA
Subkey-Length: 4096
Name-Real: OpenSoul Agent
Name-Email: agent@opensoul.local
Expire-Date: 0
%commit
EOF
```

### Exporting Keys

**Export Public Key:**
```bash
gpg --armor --export agent@opensoul.local > agent_pubkey.asc
```

**Export Private Key:**
```bash
gpg --armor --export-secret-keys agent@opensoul.local > agent_privkey.asc
```

**⚠️ SECURITY**: Keep `agent_privkey.asc` secure and encrypted!

### Verifying PGP Setup

```python
# test_pgp.py
from Scripts.pgp_utils import encrypt_data, decrypt_data

# Load keys
with open('agent_pubkey.asc') as f:
    public_key = f.read()
with open('agent_privkey.asc') as f:
    private_key = f.read()

# Test encryption/decryption
test_data = {"message": "Hello, OpenSoul!"}
encrypted = encrypt_data(test_data, [public_key])
decrypted = decrypt_data(encrypted, private_key, passphrase="your_passphrase")

assert test_data == decrypted
print("✓ PGP encryption working correctly!")
```

## Environment Configuration

### Setting Environment Variables

**Linux/macOS (.bashrc or .zshrc):**
```bash
export BSV_PRIV_WIF="your_private_key_here"
export PGP_PASSPHRASE="your_pgp_passphrase_here"
export OPENSOUL_AGENT_ID="my-agent-v1"
```

**Python dotenv (.env file):**
```bash
# .env
BSV_PRIV_WIF=your_private_key_here
PGP_PASSPHRASE=your_pgp_passphrase_here
OPENSOUL_AGENT_ID=my-agent-v1
```

Load in Python:
```python
from dotenv import load_dotenv
import os

load_dotenv()
bsv_key = os.getenv("BSV_PRIV_WIF")
```

**⚠️ NEVER commit .env files to version control!**

Add to `.gitignore`:
```
.env
*.key
*_privkey.asc
bsv_private.key
```

## File Permissions

Secure your sensitive files:

```bash
chmod 600 agent_privkey.asc
chmod 600 bsv_private.key
chmod 600 .env
```

## Network Testing

### Test BSV Blockchain Connectivity

```python
# test_bsv_connection.py
import requests

try:
    response = requests.get("https://api.whatsonchain.com/v1/bsv/main/chain/info")
    response.raise_for_status()
    print("✓ BSV blockchain API accessible")
    print(f"Current block height: {response.json()['blocks']}")
except Exception as e:
    print(f"✗ Cannot reach BSV blockchain: {e}")
```

### Test Transaction Creation

```python
# test_transaction.py
from bitsv import Key
import os

key = Key(os.getenv("BSV_PRIV_WIF"))

# Create test transaction (0.00001 BSV + fees)
try:
    outputs = [
        # Send dust amount to self
        (key.address, 1, 'satoshi'),
        # OP_RETURN with test data
        ('', '{"test": "OpenSoul setup"}', 'string')
    ]
    
    tx_hash = key.send(outputs, fee=1)
    print(f"✓ Test transaction successful: {tx_hash}")
    print(f"View at: https://whatsonchain.com/tx/{tx_hash}")
except Exception as e:
    print(f"✗ Transaction failed: {e}")
```

## Directory Structure

Recommended project structure:

```
my-agent-project/
├── .env                      # Environment variables (DO NOT COMMIT!)
├── .gitignore               # Ignore sensitive files
├── config.py                # Agent configuration
├── agent.py                 # Main agent code
├── keys/
│   ├── agent_pubkey.asc     # PGP public key
│   └── agent_privkey.asc    # PGP private key (DO NOT COMMIT!)
├── logs/
│   └── backup_logs.json     # Local backup logs
└── OpenSoul/                # Cloned repository
    ├── Scripts/
    │   ├── AuditLogger.py
    │   └── pgp_utils.py
    └── Documentation/
```

## Validation Checklist

Before using OpenSoul, ensure:

- [ ] Python 3.8+ installed
- [ ] All pip dependencies installed (bitsv, requests, cryptography, pgpy)
- [ ] BSV wallet created and funded (minimum 0.001 BSV)
- [ ] PGP keys generated (public and private)
- [ ] Environment variables set (BSV_PRIV_WIF, PGP_PASSPHRASE)
- [ ] Network connectivity tested (BSV blockchain API accessible)
- [ ] Test transaction successful
- [ ] Sensitive files secured (chmod 600)
- [ ] .gitignore configured properly

Run validation script:
```bash
python Scripts/validate_setup.py
```

## Troubleshooting Common Setup Issues

### Issue: "Module not found" errors

**Solution**: Install dependencies with `--break-system-packages` flag:
```bash
pip install bitsv --break-system-packages
```

Or use virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate
pip install bitsv requests cryptography pgpy
```

### Issue: "Cannot resolve host" errors

**Solution**: Check internet connectivity and DNS:
```bash
ping api.whatsonchain.com
nslookup api.whatsonchain.com
```

### Issue: BSV balance not showing

**Solution**: Wait for transaction confirmation (~10 minutes) or check on block explorer:
```
https://whatsonchain.com/address/YOUR_ADDRESS
```

### Issue: PGP encryption fails

**Solution**: Verify key format (should be ASCII-armored PGP blocks):
```
-----BEGIN PGP PUBLIC KEY BLOCK-----
...
-----END PGP PUBLIC KEY BLOCK-----
```

### Issue: "Insufficient funds" when sending transaction

**Solution**: 
1. Check balance: `key.get_balance('bsv')`
2. Ensure sufficient funds for transaction + fees (~0.00002 BSV minimum)
3. Fund wallet from exchange

## Next Steps

After completing prerequisites:

1. Read the main [SKILL.md](SKILL.md) for usage guide
2. Review [EXAMPLES.md](EXAMPLES.md) for code samples
3. Test with a simple logging example
4. Integrate into your agent workflow

## Support

- Repository issues: https://github.com/MasterGoogler/OpenSoul/issues
- BSV documentation: https://wiki.bitcoinsv.io/
- PGP/OpenPGP help: https://www.openpgp.org/software/
