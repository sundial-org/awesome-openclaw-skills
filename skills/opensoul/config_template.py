"""
OpenSoul Configuration Template

Copy this file to config.py and customize for your agent.
"""

import os
from pathlib import Path

# ==============================================================================
# AGENT IDENTIFICATION
# ==============================================================================

# Unique identifier for your agent
AGENT_ID = "my-agent-v1"

# Optional: Agent description/purpose
AGENT_DESCRIPTION = "Research and data analysis agent"

# ==============================================================================
# BSV BLOCKCHAIN CONFIGURATION
# ==============================================================================

# Bitcoin SV private key (WIF format)
# SECURITY: Never commit this to version control!
# Best practice: Use environment variable
BSV_PRIVATE_KEY = os.getenv("BSV_PRIV_WIF")

# Alternative: Load from secure file
# BSV_PRIVATE_KEY_FILE = Path.home() / ".opensoul" / "bsv_key.txt"
# if BSV_PRIVATE_KEY_FILE.exists():
#     with open(BSV_PRIVATE_KEY_FILE) as f:
#         BSV_PRIVATE_KEY = f.read().strip()

# Network: "main" for mainnet, "test" for testnet
BSV_NETWORK = "main"

# ==============================================================================
# PGP ENCRYPTION CONFIGURATION
# ==============================================================================

# Enable/disable PGP encryption
PGP_ENABLED = True

# PGP key paths
PGP_PUBLIC_KEY_PATH = Path("keys/agent_pubkey.asc")
PGP_PRIVATE_KEY_PATH = Path("keys/agent_privkey.asc")

# PGP passphrase
# SECURITY: Use environment variable or secure storage
PGP_PASSPHRASE = os.getenv("PGP_PASSPHRASE", "")

# For multi-agent collaboration: List of other agents' public keys
COLLABORATOR_PUBLIC_KEYS = [
    # Path("keys/agent2_pubkey.asc"),
    # Path("keys/agent3_pubkey.asc"),
]

# ==============================================================================
# LOGGING CONFIGURATION
# ==============================================================================

# Number of logs to accumulate before auto-flushing to blockchain
FLUSH_THRESHOLD = 10

# Session timeout in seconds (auto-end session after this duration of inactivity)
SESSION_TIMEOUT = 1800  # 30 minutes

# Batch size for reading history (number of transactions to fetch at once)
HISTORY_BATCH_SIZE = 100

# ==============================================================================
# PERFORMANCE THRESHOLDS
# ==============================================================================

# Performance monitoring thresholds
PERFORMANCE_THRESHOLDS = {
    "tokens_per_action": 500,      # Alert if average exceeds this
    "success_rate": 0.90,           # Alert if success rate below this (90%)
    "cost_limit_bsv": 0.01,         # Alert if total cost exceeds this (0.01 BSV)
    "session_duration_max": 3600,   # Alert if session exceeds 1 hour
}

# ==============================================================================
# BUDGET MANAGEMENT
# ==============================================================================

# Total BSV budget for agent operations
BUDGET_BSV = 0.01  # 0.01 BSV (~$0.50 USD)

# Warning threshold (percentage of budget)
BUDGET_WARNING_THRESHOLD = 0.8  # Warn at 80% budget used

# Cost estimates (BSV per transaction)
ESTIMATED_TX_COST = 0.00001  # ~$0.0005 USD per transaction

# ==============================================================================
# ERROR HANDLING
# ==============================================================================

# Maximum retry attempts for blockchain operations
MAX_RETRY_ATTEMPTS = 3

# Retry delay (seconds) - uses exponential backoff
RETRY_BASE_DELAY = 2

# Enable local backup on blockchain failure
ENABLE_LOCAL_BACKUP = True

# Local backup directory
BACKUP_DIR = Path("logs/backups")
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ==============================================================================
# ADVANCED OPTIONS
# ==============================================================================

# API endpoints
WHATSONCHAIN_API = "https://api.whatsonchain.com/v1/bsv/main"

# Transaction confirmation wait time (seconds)
TX_CONFIRMATION_WAIT = 600  # 10 minutes

# Enable verbose logging
VERBOSE_LOGGING = False

# Custom session ID format
# Available variables: {agent_id}, {timestamp}, {uuid}
SESSION_ID_FORMAT = "{agent_id}-{timestamp}-{uuid}"

# ==============================================================================
# OPENSOUL LOGGER CONFIG
# ==============================================================================

def get_opensoul_config():
    """
    Generate OpenSoul logger configuration dictionary
    
    Returns:
        dict: Configuration for AuditLogger
    """
    config = {
        "agent_id": AGENT_ID,
        "flush_threshold": FLUSH_THRESHOLD,
    }
    
    # Add PGP configuration if enabled
    if PGP_ENABLED:
        # Load public key(s)
        public_keys = []
        
        if PGP_PUBLIC_KEY_PATH.exists():
            with open(PGP_PUBLIC_KEY_PATH) as f:
                public_keys.append(f.read())
        
        # Add collaborator keys
        for key_path in COLLABORATOR_PUBLIC_KEYS:
            if key_path.exists():
                with open(key_path) as f:
                    public_keys.append(f.read())
        
        # Load private key
        private_key = None
        if PGP_PRIVATE_KEY_PATH.exists():
            with open(PGP_PRIVATE_KEY_PATH) as f:
                private_key = f.read()
        
        if public_keys and private_key:
            config["pgp"] = {
                "enabled": True,
                "multi_public_keys": public_keys,
                "private_key": private_key,
                "passphrase": PGP_PASSPHRASE
            }
    
    return config


# ==============================================================================
# VALIDATION
# ==============================================================================

def validate_config():
    """
    Validate configuration and print warnings for missing/invalid settings
    """
    issues = []
    
    # Check BSV key
    if not BSV_PRIVATE_KEY:
        issues.append("BSV_PRIVATE_KEY not set (set BSV_PRIV_WIF environment variable)")
    
    # Check PGP configuration
    if PGP_ENABLED:
        if not PGP_PUBLIC_KEY_PATH.exists():
            issues.append(f"PGP public key not found: {PGP_PUBLIC_KEY_PATH}")
        if not PGP_PRIVATE_KEY_PATH.exists():
            issues.append(f"PGP private key not found: {PGP_PRIVATE_KEY_PATH}")
        if not PGP_PASSPHRASE:
            issues.append("PGP_PASSPHRASE not set (set PGP_PASSPHRASE environment variable)")
    
    # Check directories
    if ENABLE_LOCAL_BACKUP and not BACKUP_DIR.exists():
        issues.append(f"Backup directory does not exist: {BACKUP_DIR}")
    
    if issues:
        print("⚠️  Configuration issues detected:")
        for issue in issues:
            print(f"   - {issue}")
        return False
    
    print("✓ Configuration validated successfully")
    return True


# Run validation if this file is executed directly
if __name__ == "__main__":
    print("OpenSoul Configuration")
    print("=" * 50)
    print(f"Agent ID: {AGENT_ID}")
    print(f"BSV Network: {BSV_NETWORK}")
    print(f"PGP Enabled: {PGP_ENABLED}")
    print(f"Budget: {BUDGET_BSV} BSV")
    print("=" * 50)
    validate_config()
