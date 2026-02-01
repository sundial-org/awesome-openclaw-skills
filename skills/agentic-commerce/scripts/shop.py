#!/usr/bin/env python3
"""
AI-powered shopping assistant using natural language.

Usage:
    python shop.py "<message>"

Example:
    python shop.py "comfortable running shoes under $100"
    python shop.py "wireless headphones with good noise cancellation"
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.error

BASE_URL = "https://api.purch.xyz"


def extract_variant_id(url: str) -> str | None:
    """Extract variant ID from Shopify product URL query parameter."""
    if not url:
        return None
    match = re.search(r'[?&]variant=(\d+)', url)
    return match.group(1) if match else None


def shop(message: str, context: dict | None = None) -> dict:
    """Use AI shopping assistant with natural language."""
    payload = {"message": message}
    if context:
        payload["context"] = context

    data = json.dumps(payload).encode("utf-8")

    try:
        req = urllib.request.Request(
            f"{BASE_URL}/shop",
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
    parser = argparse.ArgumentParser(description="AI shopping assistant")
    parser.add_argument("message", help="Natural language shopping request")
    parser.add_argument("--price-min", type=float, help="Minimum price preference")
    parser.add_argument("--price-max", type=float, help="Maximum price preference")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    # Build context if price preferences provided
    context = None
    if args.price_min is not None or args.price_max is not None:
        context = {"priceRange": {}}
        if args.price_min is not None:
            context["priceRange"]["min"] = args.price_min
        if args.price_max is not None:
            context["priceRange"]["max"] = args.price_max

    result = shop(args.message, context)

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    # Print AI reply
    reply = result.get("reply", "")
    if reply:
        print(f"🤖 {reply}")
        print()

    products = result.get("products", [])
    print(f"📦 Found {len(products)} products")
    print("-" * 60)

    for i, product in enumerate(products, 1):
        title = product.get("title", "Unknown")[:50]
        price = product.get("price", "N/A")
        currency = product.get("currency", "USD")
        rating = product.get("rating", "N/A")
        source = product.get("source", "unknown")
        url = product.get("productUrl", "")

        print(f"{i}. {title}")
        print(f"   💰 {currency} {price} | ⭐ {rating} | 🏷️ {source}")

        if source == "amazon":
            asin = product.get("asin", "N/A")
            print(f"   🛒 ASIN: {asin}")
        else:  # shopify
            variant_id = product.get("variantId") or extract_variant_id(url) or "N/A"
            clean_url = url.split('?')[0] if url else "N/A"
            print(f"   🛒 URL: {clean_url}")
            print(f"   🔖 Variant ID: {variant_id}")
        print()


if __name__ == "__main__":
    main()
