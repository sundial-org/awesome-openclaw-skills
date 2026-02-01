#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "requests>=2.28.0",
# ]
# ///
"""
Polymarket prediction market data.
"""

import argparse
import json
import sys
from datetime import datetime

import requests

BASE_URL = "https://gamma-api.polymarket.com"


def fetch(endpoint: str, params: dict = None) -> dict:
    """Fetch from Gamma API."""
    url = f"{BASE_URL}{endpoint}"
    resp = requests.get(url, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def format_price(price) -> str:
    """Format price as percentage."""
    if price is None:
        return "N/A"
    try:
        pct = float(price) * 100
        return f"{pct:.1f}%"
    except:
        return str(price)


def format_volume(volume) -> str:
    """Format volume in human readable form."""
    if volume is None:
        return "N/A"
    try:
        v = float(volume)
        if v >= 1_000_000:
            return f"${v/1_000_000:.1f}M"
        elif v >= 1_000:
            return f"${v/1_000:.1f}K"
        else:
            return f"${v:.0f}"
    except:
        return str(volume)


def format_market(market: dict) -> str:
    """Format a single market for display."""
    lines = []
    
    question = market.get('question') or market.get('title', 'Unknown')
    lines.append(f"📊 **{question}**")
    
    # Prices
    outcomes = market.get('outcomes', [])
    if outcomes and len(outcomes) >= 2:
        prices = market.get('outcomePrices', [])
        if prices and len(prices) >= 2:
            lines.append(f"   Yes: {format_price(prices[0])} | No: {format_price(prices[1])}")
    elif market.get('bestBid') or market.get('bestAsk'):
        lines.append(f"   Bid: {format_price(market.get('bestBid'))} | Ask: {format_price(market.get('bestAsk'))}")
    
    # Volume
    volume = market.get('volume') or market.get('volumeNum')
    if volume:
        lines.append(f"   Volume: {format_volume(volume)}")
    
    # End date
    end_date = market.get('endDate') or market.get('end_date_iso')
    if end_date:
        try:
            dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
            lines.append(f"   Ends: {dt.strftime('%b %d, %Y')}")
        except:
            pass
    
    # Slug for reference
    slug = market.get('slug') or market.get('market_slug')
    if slug:
        lines.append(f"   🔗 polymarket.com/event/{slug}")
    
    return '\n'.join(lines)


def format_event(event: dict) -> str:
    """Format an event with its markets."""
    lines = []
    
    title = event.get('title', 'Unknown Event')
    lines.append(f"🎯 **{title}**")
    
    # Event-level info
    volume = event.get('volume')
    if volume:
        lines.append(f"   Total Volume: {format_volume(volume)}")
    
    # Markets in this event
    markets = event.get('markets', [])
    if markets:
        lines.append(f"   Markets: {len(markets)}")
        for m in markets[:5]:  # Show first 5
            q = m.get('question', m.get('groupItemTitle', ''))
            prices = m.get('outcomePrices')
            if prices:
                # Could be string or list
                if isinstance(prices, str):
                    try:
                        prices = json.loads(prices)
                    except:
                        pass
                if isinstance(prices, list) and len(prices) >= 1:
                    lines.append(f"   • {q}: {format_price(prices[0])}")
                else:
                    lines.append(f"   • {q}")
            else:
                lines.append(f"   • {q}")
        if len(markets) > 5:
            lines.append(f"   ... and {len(markets) - 5} more")
    
    slug = event.get('slug')
    if slug:
        lines.append(f"   🔗 polymarket.com/event/{slug}")
    
    return '\n'.join(lines)


def cmd_trending(args):
    """Get trending/active markets."""
    params = {
        'order': 'volume24hr',
        'ascending': 'false',
        'closed': 'false',
        'limit': args.limit
    }
    
    data = fetch('/events', params)
    
    print(f"🔥 **Trending on Polymarket**\n")
    
    for event in data:
        print(format_event(event))
        print()


def cmd_search(args):
    """Search markets."""
    # Use the markets endpoint with text search
    params = {
        'closed': 'false',
        'limit': args.limit
    }
    
    # Try search endpoint first
    try:
        resp = requests.get(f"{BASE_URL}/search", params={'query': args.query, 'limit': args.limit}, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            events = data if isinstance(data, list) else data.get('events', data.get('markets', []))
            
            print(f"🔍 **Search: '{args.query}'**\n")
            
            if not events:
                print("No markets found.")
                return
            
            for item in events[:args.limit]:
                if 'markets' in item:
                    print(format_event(item))
                else:
                    print(format_market(item))
                print()
            return
    except:
        pass
    
    # Fallback: get all events and filter
    data = fetch('/events', {'closed': 'false', 'limit': 100})
    
    query_lower = args.query.lower()
    matches = []
    
    for event in data:
        title = event.get('title', '').lower()
        desc = event.get('description', '').lower()
        if query_lower in title or query_lower in desc:
            matches.append(event)
            continue
        # Check markets
        for m in event.get('markets', []):
            q = m.get('question', '').lower()
            if query_lower in q:
                matches.append(event)
                break
    
    print(f"🔍 **Search: '{args.query}'**\n")
    
    if not matches:
        print("No markets found.")
        return
    
    for event in matches[:args.limit]:
        print(format_event(event))
        print()


def cmd_event(args):
    """Get specific event by slug."""
    try:
        data = fetch(f'/events/slug/{args.slug}')
        
        if isinstance(data, list) and data:
            data = data[0]
        
        print(format_event(data))
        
        # Show more detail on markets
        markets = data.get('markets', [])
        if markets:
            print(f"\n📊 **All Markets:**\n")
            for m in markets:
                print(format_market(m))
                print()
                
    except requests.HTTPError as e:
        if e.response.status_code == 404:
            print(f"❌ Event not found: {args.slug}")
        else:
            raise


def cmd_category(args):
    """Get markets by category."""
    # Map friendly names to tag IDs
    categories = {
        'politics': 'politics',
        'crypto': 'crypto',
        'sports': 'sports',
        'tech': 'tech',
        'entertainment': 'entertainment',
        'science': 'science',
        'business': 'business'
    }
    
    tag = categories.get(args.category.lower(), args.category)
    
    # Try to get events with this tag
    params = {
        'closed': 'false',
        'limit': args.limit,
        'order': 'volume24hr',
        'ascending': 'false'
    }
    
    data = fetch('/events', params)
    
    # Filter by category in title/tags
    matches = []
    tag_lower = tag.lower()
    for event in data:
        title = event.get('title', '').lower()
        tags = [t.get('label', '').lower() for t in event.get('tags', [])]
        if tag_lower in title or tag_lower in ' '.join(tags):
            matches.append(event)
    
    print(f"📁 **Category: {args.category.title()}**\n")
    
    if not matches:
        # Show all instead
        print(f"(No exact matches for '{tag}', showing trending)\n")
        matches = data[:args.limit]
    
    for event in matches[:args.limit]:
        print(format_event(event))
        print()


def main():
    parser = argparse.ArgumentParser(description="Polymarket prediction markets")
    parser.add_argument("--limit", "-l", type=int, default=5, help="Number of results")
    parser.add_argument("--json", "-j", action="store_true", help="Output raw JSON")
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Trending
    subparsers.add_parser("trending", help="Get trending markets")
    
    # Search
    search_parser = subparsers.add_parser("search", help="Search markets")
    search_parser.add_argument("query", help="Search query")
    
    # Event
    event_parser = subparsers.add_parser("event", help="Get specific event")
    event_parser.add_argument("slug", help="Event slug from URL")
    
    # Category
    cat_parser = subparsers.add_parser("category", help="Markets by category")
    cat_parser.add_argument("category", help="Category: politics, crypto, sports, tech, etc.")
    
    args = parser.parse_args()
    
    commands = {
        "trending": cmd_trending,
        "search": cmd_search,
        "event": cmd_event,
        "category": cmd_category,
    }
    
    try:
        commands[args.command](args)
    except requests.RequestException as e:
        print(f"❌ API Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
