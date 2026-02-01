#!/usr/bin/env python3
"""
Sign and submit a Solana transaction for Purch API checkout.

Usage:
    python sign_transaction.py <serialized_transaction> <private_key> [--rpc-url <url>]

Arguments:
    serialized_transaction  Base58-encoded transaction from /buy endpoint
    private_key             Base58-encoded Solana private key (64 bytes)

Options:
    --rpc-url               Solana RPC URL (default: mainnet-beta)

Example:
    python sign_transaction.py "NwbtPCP62oXk..." "5abc123..." --rpc-url https://api.mainnet-beta.solana.com
"""

import argparse
import sys
import json

try:
    import base58
    from solders.keypair import Keypair
    from solders.transaction import VersionedTransaction
    from solana.rpc.api import Client
    from solana.rpc.commitment import Confirmed
except ImportError:
    print("Error: Required packages not installed. Run:")
    print("  pip install solana solders base58")
    sys.exit(1)


def sign_and_send_transaction(
    serialized_tx: str,
    private_key: str,
    rpc_url: str = "https://api.mainnet-beta.solana.com"
) -> dict:
    """
    Sign and submit a Solana transaction.

    Args:
        serialized_tx: Base58-encoded transaction from Purch API
        private_key: Base58-encoded private key (64 bytes)
        rpc_url: Solana RPC endpoint URL

    Returns:
        dict with signature and status
    """
    # Decode private key and create keypair
    try:
        key_bytes = base58.b58decode(private_key)
        keypair = Keypair.from_bytes(key_bytes)
    except Exception as e:
        return {"success": False, "error": f"Invalid private key: {e}"}

    # Decode the serialized transaction
    try:
        tx_bytes = base58.b58decode(serialized_tx)
        transaction = VersionedTransaction.from_bytes(tx_bytes)
    except Exception as e:
        return {"success": False, "error": f"Invalid transaction: {e}"}

    # Sign the transaction
    try:
        transaction.sign([keypair])
    except Exception as e:
        return {"success": False, "error": f"Failed to sign: {e}"}

    # Connect and send
    client = Client(rpc_url)

    try:
        # Send transaction
        result = client.send_transaction(transaction)
        signature = str(result.value)

        # Wait for confirmation
        client.confirm_transaction(signature, commitment=Confirmed)

        return {
            "success": True,
            "signature": signature,
            "explorer_url": f"https://solscan.io/tx/{signature}"
        }
    except Exception as e:
        return {"success": False, "error": f"Transaction failed: {e}"}


def main():
    parser = argparse.ArgumentParser(
        description="Sign and submit a Solana transaction for Purch checkout"
    )
    parser.add_argument(
        "serialized_transaction",
        help="Base58-encoded transaction from /buy endpoint"
    )
    parser.add_argument(
        "private_key",
        help="Base58-encoded Solana private key"
    )
    parser.add_argument(
        "--rpc-url",
        default="https://api.mainnet-beta.solana.com",
        help="Solana RPC URL (default: mainnet-beta)"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )

    args = parser.parse_args()

    result = sign_and_send_transaction(
        args.serialized_transaction,
        args.private_key,
        args.rpc_url
    )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        if result["success"]:
            print(f"✅ Transaction successful!")
            print(f"   Signature: {result['signature']}")
            print(f"   Explorer:  {result['explorer_url']}")
        else:
            print(f"❌ Transaction failed: {result['error']}")
            sys.exit(1)


if __name__ == "__main__":
    main()
