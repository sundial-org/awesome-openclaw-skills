#!/usr/bin/env python3
"""
Create a purchase order AND sign/submit the Solana transaction.

Usage:
    # Amazon product (by ASIN)
    python buy_and_sign.py --asin B0CXYZ1234 --email buyer@example.com --wallet 7xKXtg... --private-key 5abc... --address "John Doe,123 Main St,New York,NY,10001,US"

    # Shopify product (requires URL + variant)
    python buy_and_sign.py --url "https://store.com/products/item" --variant 41913945718867 --email buyer@example.com --wallet 7xKXtg... --private-key 5abc... --address "..."

Address format: "Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"

Required packages:
    pip install solana solders base58
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.purch.xyz"


def parse_address(address_str: str) -> dict:
    """Parse address string into dict."""
    parts = address_str.split(",")
    if len(parts) < 6:
        raise ValueError("Address must have at least: Name,Line1,City,State,PostalCode,Country")

    address = {
        "name": parts[0].strip(),
        "line1": parts[1].strip(),
        "city": parts[2].strip(),
        "state": parts[3].strip(),
        "postalCode": parts[4].strip(),
        "country": parts[5].strip(),
    }

    if len(parts) > 6:
        address["line2"] = parts[6].strip()
    if len(parts) > 7:
        address["phone"] = parts[7].strip()

    return address


def create_order(
    email: str,
    wallet_address: str,
    shipping_address: dict,
    asin: str | None = None,
    product_url: str | None = None,
    variant_id: str | None = None,
) -> dict:
    """Create a purchase order."""
    payload = {
        "email": email,
        "walletAddress": wallet_address,
        "shippingAddress": shipping_address,
    }

    if asin:
        payload["asin"] = asin
    if product_url:
        payload["productUrl"] = product_url
    if variant_id:
        payload["variantId"] = variant_id

    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/buy",
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=60) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}


def sign_and_send_transaction(
    serialized_tx: str,
    private_key: str,
    rpc_url: str = "https://api.mainnet-beta.solana.com"
) -> dict:
    """Sign and submit a Solana transaction."""
    try:
        import base58
        from solders.keypair import Keypair
        from solders.transaction import VersionedTransaction
        from solana.rpc.api import Client
        from solana.rpc.commitment import Confirmed
    except ImportError:
        return {"error": "Missing packages. Run: pip install solana solders base58"}

    # Decode private key
    try:
        key_bytes = base58.b58decode(private_key)
        keypair = Keypair.from_bytes(key_bytes)
    except Exception as e:
        return {"error": f"Invalid private key: {e}"}

    # Decode transaction
    try:
        tx_bytes = base58.b58decode(serialized_tx)
        transaction = VersionedTransaction.from_bytes(tx_bytes)
    except Exception as e:
        return {"error": f"Invalid transaction: {e}"}

    # Sign
    try:
        transaction.sign([keypair])
    except Exception as e:
        return {"error": f"Failed to sign: {e}"}

    # Send
    client = Client(rpc_url)

    try:
        result = client.send_transaction(transaction)
        signature = str(result.value)
        client.confirm_transaction(signature, commitment=Confirmed)

        return {
            "success": True,
            "signature": signature,
            "explorer_url": f"https://solscan.io/tx/{signature}"
        }
    except Exception as e:
        return {"error": f"Transaction failed: {e}"}


def main():
    parser = argparse.ArgumentParser(description="Create order and sign transaction")
    parser.add_argument("--asin", help="Amazon ASIN")
    parser.add_argument("--url", help="Product URL (Amazon or Shopify)")
    parser.add_argument("--variant", help="Variant ID (required for Shopify)")
    parser.add_argument("--email", required=True, help="Buyer email")
    parser.add_argument("--wallet", required=True, help="Solana wallet address")
    parser.add_argument("--private-key", required=True, help="Base58 private key for signing")
    parser.add_argument("--address", required=True, help="Shipping address")
    parser.add_argument("--rpc-url", default="https://api.mainnet-beta.solana.com", help="Solana RPC URL")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    if not args.asin and not args.url:
        print("❌ Error: Either --asin or --url is required")
        sys.exit(1)

    try:
        shipping_address = parse_address(args.address)
    except ValueError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

    # Step 1: Create order
    print("📦 Creating order...")
    order_result = create_order(
        email=args.email,
        wallet_address=args.wallet,
        shipping_address=shipping_address,
        asin=args.asin,
        product_url=args.url,
        variant_id=args.variant,
    )

    if "error" in order_result:
        if args.json:
            print(json.dumps(order_result, indent=2))
        else:
            print(f"❌ Order creation failed: {order_result['error']}")
        sys.exit(1)

    order_id = order_result.get("orderId")
    serialized_tx = order_result.get("serializedTransaction")
    product = order_result.get("product", {})
    total_price = order_result.get("totalPrice", {})

    print(f"✅ Order created: {order_id}")
    print(f"   Product: {product.get('title', 'N/A')}")
    print(f"   Total: {total_price.get('amount', 'N/A')} {total_price.get('currency', 'USDC').upper()}")
    print()

    # Step 2: Sign and submit transaction
    print("🔐 Signing and submitting transaction...")
    tx_result = sign_and_send_transaction(serialized_tx, args.private_key, args.rpc_url)

    if args.json:
        print(json.dumps({"order": order_result, "transaction": tx_result}, indent=2))
        return

    if "error" in tx_result:
        print(f"❌ Transaction failed: {tx_result['error']}")
        print()
        print(f"🌐 You can complete payment via browser: {order_result.get('checkoutUrl')}")
        sys.exit(1)

    print("✅ Payment complete!")
    print(f"   Signature: {tx_result['signature']}")
    print(f"   Explorer:  {tx_result['explorer_url']}")


if __name__ == "__main__":
    main()
