#!/usr/bin/env python3
"""
Search products using the Purch API.

Usage:
    python search.py <query> [--price-min <min>] [--price-max <max>] [--brand <brand>] [--page <page>]

Example:
    python search.py "wireless headphones" --price-max 100
    python search.py "running shoes" --brand Nike --price-min 50 --price-max 150
"""

import argparse
import json
import re
import sys
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://api.purch.xyz"


def extract_variant_id(url: str) -> str | None:
    """Extract variant ID from Shopify product URL query parameter."""
    if not url:
        return None
    match = re.search(r'[?&]variant=(\d+)', url)
    return match.group(1) if match else None


def search_products(
    query: str,
    price_min: float | None = None,
    price_max: float | None = None,
    brand: str | None = None,
    page: int = 1
) -> dict:
    """Search for products with optional filters."""
    params = {"q": query, "page": str(page)}

    if price_min is not None:
        params["priceMin"] = str(price_min)
    if price_max is not None:
        params["priceMax"] = str(price_max)
    if brand:
        params["brand"] = brand

    url = f"{BASE_URL}/search?{urllib.parse.urlencode(params)}"

    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        return {"error": f"HTTP {e.code}: {error_body}"}
    except Exception as e:
        return {"error": str(e)}


def main():
    parser = argparse.ArgumentParser(description="Search products on Purch API")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--price-min", type=float, help="Minimum price filter")
    parser.add_argument("--price-max", type=float, help="Maximum price filter")
    parser.add_argument("--brand", help="Brand filter")
    parser.add_argument("--page", type=int, default=1, help="Page number (default: 1)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")

    args = parser.parse_args()

    result = search_products(
        query=args.query,
        price_min=args.price_min,
        price_max=args.price_max,
        brand=args.brand,
        page=args.page
    )

    if args.json:
        print(json.dumps(result, indent=2))
        return

    if "error" in result:
        print(f"❌ Error: {result['error']}")
        sys.exit(1)

    products = result.get("products", [])
    total = result.get("totalResults", 0)
    has_more = result.get("hasMore", False)

    print(f"📦 Found {total} products (showing {len(products)}, page {args.page})")
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
            asin = product.get("asin") or product.get("id", "N/A")
            print(f"   🛒 ASIN: {asin}")
        else:  # shopify
            variant_id = product.get("variantId") or extract_variant_id(url) or "N/A"
            # Clean URL for display (remove query params)
            clean_url = url.split('?')[0] if url else "N/A"
            print(f"   🛒 URL: {clean_url}")
            print(f"   🔖 Variant ID: {variant_id}")
        print()

    if has_more:
        print(f"📄 More results available. Use --page {args.page + 1} to see next page.")


if __name__ == "__main__":
    main()
