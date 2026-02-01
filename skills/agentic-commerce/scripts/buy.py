#!/usr/bin/env python3
"""
Create a purchase order (without signing the transaction).

Usage:
    # Amazon product (by ASIN)
    python buy.py --asin B0CXYZ1234 --email buyer@example.com --wallet 7xKXtg... --address "John Doe,123 Main St,New York,NY,10001,US"

    # Amazon product (by URL)
    python buy.py --url "https://amazon.com/dp/B0CXYZ1234" --email buyer@example.com --wallet 7xKXtg... --address "..."

    # Shopify product (requires URL + variant)
    python buy.py --url "https://store.com/products/item" --variant 41913945718867 --email buyer@example.com --wallet 7xKXtg... --address "..."

Address format: "Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"
"""

import argparse
import json
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.purch.xyz"


def parse_address(address_str: str) -> dict:
    """Parse address string into dict. Format: Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]"""
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


def main():
    parser = argparse.ArgumentParser(description="Create a purchase order on Purch API")
    parser.add_argument("--asin", help="Amazon ASIN (for Amazon products)")
    parser.add_argument("--url", help="Product URL (Amazon or Shopify)")
    parser.add_argument("--variant", help="Variant ID (required for Shopify)")
    parser.add_argument("--email", required=True, help="Buyer email address")
    parser.add_argument("--wallet", required=True, help="Solana wallet address")
    parser.add_argument("--address", required=True, help="Shipping address: Name,Line1,City,State,PostalCode,Country[,Line2][,Phone]")
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

    result = create_order(
        email=args.email,
        wallet_address=args.wallet,
        shipping_address=shipping_address,
        asin=args.asin,
        product_url=args.url,
        variant_id=args.variant,
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    print("✅ Order created successfully!")
    print(f"   Order ID: {result.get('orderId', 'N/A')}")
    print(f"   Status: {result.get('status', 'N/A')}")

    product = result.get("product", {})
    if product:
        print(f"   Product: {product.get('title', 'N/A')}")

    total_price = result.get("totalPrice", {})
    if total_price:
        print(f"   Total: {total_price.get('amount', 'N/A')} {total_price.get('currency', 'USDC').upper()}")

    print()
    print("📝 Next step: Sign the serialized transaction to complete payment")
    print(f"   Transaction: {result.get('serializedTransaction', 'N/A')[:50]}...")

    checkout_url = result.get("checkoutUrl")
    if checkout_url:
        print()
        print(f"🌐 Or pay via browser: {checkout_url}")


if __name__ == "__main__":
    main()
