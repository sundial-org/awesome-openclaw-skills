#!/usr/bin/env python3
import requests
import json
import argparse
import sys

BASE_URL = "https://apewisdom.io/api/v1.0/filter"

def get_trending(filter_name="all-stocks", limit=20):
    url = f"{BASE_URL}/{filter_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])[:limit]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}", file=sys.stderr)
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Scan Reddit sentiment via ApeWisdom")
    parser.add_argument("--filter", default="all-stocks", choices=["all-stocks", "wallstreetbets", "all-crypto", "SPACs"], help="Subreddit filter")
    parser.add_argument("--limit", type=int, default=20, help="Number of results to return")
    parser.add_argument("--sort", choices=["mentions", "spike"], default="mentions", help="Sort by raw mentions or 24h spike")
    args = parser.parse_args()

    results = get_trending(args.filter, 100) # Fetch more to sort properly

    # Process data types
    cleaned_results = []
    for r in results:
        try:
            item = {
                "rank": int(r.get("rank", 0)),
                "ticker": r.get("ticker"),
                "name": r.get("name"),
                "mentions": int(r.get("mentions", 0)),
                "upvotes": int(r.get("upvotes", 0)),
                "mentions_24h_ago": int(r.get("mentions_24h_ago", 0)),
            }
            # Calculate % change
            if item["mentions_24h_ago"] > 0:
                item["change_pct"] = ((item["mentions"] - item["mentions_24h_ago"]) / item["mentions_24h_ago"]) * 100
            else:
                item["change_pct"] = 100.0 if item["mentions"] > 0 else 0.0
            
            cleaned_results.append(item)
        except ValueError:
            continue

    # Sort
    if args.sort == "spike":
        # Sort by % change, but filter out low volume noise (must have >10 mentions)
        cleaned_results = [r for r in cleaned_results if r["mentions"] > 10]
        cleaned_results.sort(key=lambda x: x["change_pct"], reverse=True)
    else:
        # Default API sort is usually rank/mentions, but ensure it
        cleaned_results.sort(key=lambda x: x["mentions"], reverse=True)

    # Output JSON
    print(json.dumps(cleaned_results[:args.limit], indent=2))

if __name__ == "__main__":
    main()
