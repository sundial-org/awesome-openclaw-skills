#!/usr/bin/env python3
"""
Agent Memory Client - Improved with proper Ed25519 signatures
Usage: memory_client.py <command> [options]
"""

import argparse
import json
import base64
import requests
import hashlib
from datetime import datetime, timezone
from pathlib import Path

# Import cryptography for Ed25519
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey, Ed25519PublicKey
)

# Default local service URL
DEFAULT_URL = "http://127.0.0.1:8000"

# Config file
CONFIG_DIR = Path.home() / ".agent-memory"
IDENTITY_FILE = CONFIG_DIR / "identity.json"

def load_identity():
    """Load agent identity from file."""
    if IDENTITY_FILE.exists():
        with open(IDENTITY_FILE) as f:
            return json.load(f)
    return None

def save_identity(identity):
    """Save agent identity to file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    with open(IDENTITY_FILE, 'w') as f:
        json.dump(identity, f, indent=2)

def get_private_key_from_phrase(recovery_phrase):
    """Recover private key from recovery phrase."""
    from mnemonic import Mnemonic
    mnemo = Mnemonic("english")
    entropy = mnemo.to_entropy(recovery_phrase)
    return Ed25519PrivateKey.from_private_bytes(entropy[:32])

def sign_message(private_key, message_bytes):
    """Sign message with Ed25519."""
    signature = private_key.sign(message_bytes)
    return base64.b64encode(signature).decode()

def register_agent():
    """Register a new agent identity."""
    print("📝 Registering new agent identity...")
    
    response = requests.post(f"{DEFAULT_URL}/agents/register")
    data = response.json()
    
    save_identity({
        "agent_id": data["agent_id"],
        "public_key": data["public_key"],
        "recovery_phrase": data["recovery_phrase"]
    })
    
    print(f"✅ Registered!")
    print(f"   Agent ID: {data['agent_id'][:20]}...")
    print(f"   Recovery phrase: {data['recovery_phrase'][:50]}...")
    print(f"\n⚠️  SAVE THIS RECOVERY PHRASE! It's your only way to recover your identity.")
    print(f"   Stored in: {IDENTITY_FILE}")

def recover_agent(recovery_phrase):
    """Recover agent identity from recovery phrase."""
    print("🔄 Recovering identity...")
    
    response = requests.post(
        f"{DEFAULT_URL}/agents/recover",
        json={"recovery_phrase": recovery_phrase}
    )
    data = response.json()
    
    save_identity({
        "agent_id": data["agent_id"],
        "public_key": data["public_key"],
        "recovery_phrase": recovery_phrase
    })
    
    print(f"✅ Recovered!")
    print(f"   Agent ID: {data['agent_id'][:20]}...")

def create_memory_snapshot():
    """Create a template memory snapshot."""
    return {
        "session_info": {
            "session_count": 1,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "interactions": 0
        },
        "user_preferences": [],
        "learning_history": [],
        "knowledge_gaps": [],
        "active_goals": [],
        "effective_approaches": [],
        "ineffective_approaches": []
    }

def store_memory(file_path=None):
    """Store a memory snapshot with proper Ed25519 signature."""
    identity = load_identity()
    if not identity:
        print("❌ No identity found. Run 'register' first.")
        return
    
    if file_path:
        with open(file_path) as f:
            memory = json.load(f)
    else:
        memory = create_memory_snapshot()
        # Save template for editing
        template_path = Path.home() / ".agent-memory" / "memory_template.json"
        with open(template_path, 'w') as f:
            json.dump(memory, f, indent=2)
        print(f"📝 Created memory template at: {template_path}")
        print("Edit it and run: memory_client.py store --file ~/.agent-memory/memory_template.json")
        return
    
    # Encrypt (simple base64 for now - client-side encryption would be better)
    plaintext = json.dumps(memory)
    encrypted = base64.b64encode(plaintext.encode()).decode()
    
    # Get data hash
    data_hash = hashlib.sha256(encrypted.encode()).hexdigest()
    
    # Sign with Ed25519 - message format must be "store:{data_hash}"
    private_key = get_private_key_from_phrase(identity["recovery_phrase"])
    message_to_sign = f"store:{data_hash}".encode()
    signature = sign_message(private_key, message_to_sign)
    
    response = requests.post(
        f"{DEFAULT_URL}/memory/store",
        json={
            "agent_id": identity["agent_id"],
            "encrypted_data": encrypted,
            "signature": signature
        }
    )
    
    result = response.json()
    if response.status_code == 200:
        print(f"✅ Memory stored! Version: {result['version']}")
    else:
        print(f"❌ Failed: {result}")

def retrieve_memory():
    """Retrieve latest memory with proper signature."""
    identity = load_identity()
    if not identity:
        print("❌ No identity found. Run 'register' first.")
        return
    
    # Create signature for retrieve request
    timestamp = datetime.now(timezone.utc).isoformat()
    private_key = get_private_key_from_phrase(identity["recovery_phrase"])
    message_to_sign = f"retrieve:{timestamp}".encode()
    signature = sign_message(private_key, message_to_sign)
    
    response = requests.post(
        f"{DEFAULT_URL}/memory/retrieve",
        json={
            "agent_id": identity["agent_id"],
            "signature": signature,
            "timestamp": timestamp
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        encrypted = data.get("encrypted_data", "")
        plaintext = base64.b64decode(encrypted).decode()
        memory = json.loads(plaintext)
        
        print("📂 Retrieved Memory:")
        print(json.dumps(memory, indent=2))
    else:
        print(f"❌ No memory found or error: {response.text}")

def show_status():
    """Show service status."""
    try:
        response = requests.get(f"{DEFAULT_URL}/health", timeout=5)
        data = response.json()
        print(f"🟢 Service Status: {data['status']}")
        print(f"   Database: {data['database']}")
        print(f"   Version: {data['version']}")
    except requests.exceptions.ConnectionError:
        print("🔴 Service not running!")
        print("   Start with: ~/.agent-memory/start.sh")

def main():
    parser = argparse.ArgumentParser(description="Agent Memory Client")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Register
    subparsers.add_parser("register", help="Register new agent identity")
    
    # Recover
    recover_parser = subparsers.add_parser("recover", help="Recover identity")
    recover_parser.add_argument("phrase", help="Recovery phrase")
    
    # Store
    store_parser = subparsers.add_parser("store", help="Store memory")
    store_parser.add_argument("--file", help="Memory JSON file")
    
    # Retrieve
    subparsers.add_parser("retrieve", help="Retrieve latest memory")
    
    # Status
    subparsers.add_parser("status", help="Check service status")
    
    args = parser.parse_args()
    
    if args.command == "register":
        register_agent()
    elif args.command == "recover":
        recover_agent(args.phrase)
    elif args.command == "store":
        store_memory(args.file)
    elif args.command == "retrieve":
        retrieve_memory()
    elif args.command == "status":
        show_status()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
