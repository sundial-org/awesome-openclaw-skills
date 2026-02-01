#!/usr/bin/env python3
"""Register with AIKEK API and get a long-lived API token.

Reads AIKEK_PRIVATE_KEY from environment or ~/.aikek/config.
Outputs token credentials to append to ~/.aikek/config.

Usage:
    source ~/.aikek/config
    python register.py >> ~/.aikek/config
"""

import os
import sys
import time

try:
    from solders.keypair import Keypair
    import requests
except ImportError:
    print("Missing dependencies. Install with: pip install solders requests", file=sys.stderr)
    sys.exit(1)


def load_config():
    """Load private key from environment or config file."""
    private_key = os.environ.get("AIKEK_PRIVATE_KEY")
    if private_key:
        return private_key

    config_path = os.path.expanduser("~/.aikek/config")
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                if line.startswith("AIKEK_PRIVATE_KEY="):
                    return line.strip().split("=", 1)[1]

    print("Error: AIKEK_PRIVATE_KEY not found in environment or ~/.aikek/config", file=sys.stderr)
    sys.exit(1)


def main():
    private_key_hex = load_config()
    private_key = bytes.fromhex(private_key_hex)
    keypair = Keypair.from_bytes(private_key)
    timestamp = int(time.time())

    message = f"Sign this message to authenticate with AIKEK API.\n\nAddress: {keypair.pubkey()}\nTimestamp: {timestamp}"
    signature = keypair.sign_message(message.encode("utf-8"))

    response = requests.post(
        "https://api.alphakek.ai/auth/wallet-login",
        json={
            "address": str(keypair.pubkey()),
            "signature": str(signature),
            "timestamp": timestamp,
        },
        timeout=30,
    )

    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.text}", file=sys.stderr)
        sys.exit(1)

    data = response.json()
    print(f"AIKEK_API_TOKEN={data['token']}")
    print(f"AIKEK_TOKEN_ID={data['token_id']}")

    if data.get("is_new_user"):
        print("# New account created with 5 credits", file=sys.stderr)
    else:
        print("# Logged in to existing account", file=sys.stderr)


if __name__ == "__main__":
    main()
