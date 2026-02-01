#!/usr/bin/env python3
"""Kalshi CLI - Moltbot Skill Script.

Usage:
    python3 kalshi.py fed [limit]
    python3 kalshi.py economics [limit]
    python3 kalshi.py trending [limit]
    python3 kalshi.py search "<query>" [limit]
    python3 kalshi.py series
"""

import argparse
import asyncio
import sys
from pathlib import Path

# Add parent directories to path for imports
script_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(script_dir))

from dotenv import load_dotenv

load_dotenv()


def format_market(m, index: int = None):
    """Format a market for display."""
    prefix = f"{index}. " if index else "- "
    print(f"{prefix}**{m.title}**")
    print(f"   YES: ${m.yes_price:.2f} ({m.yes_price*100:.0f}% probability)")
    print(f"   Volume: {m.volume:,} contracts")
    if m.ticker:
        print(f"   Ticker: {m.ticker}")
    print()


async def get_fed_markets(limit: int = 10):
    """Get Fed interest rate markets."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.get_fed_markets(limit=limit)
        if not markets:
            print("No Fed markets found")
            return

        print("## Federal Reserve Interest Rate Markets")
        print()
        print("*CFTC-regulated prediction markets on Fed interest rate decisions*")
        print()

        for i, m in enumerate(markets, 1):
            format_market(m, i)

        print(f"---")
        print(f"*Showing {len(markets)} markets from KXFED series*")
    finally:
        await client.close()


async def get_economics_markets(limit: int = 10):
    """Get economics markets (GDP, CPI)."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.get_economics_markets(limit=limit)
        if not markets:
            print("No economics markets found")
            return

        print("## Economics Markets (GDP, CPI)")
        print()
        print("*CFTC-regulated prediction markets on US economic indicators*")
        print()

        for i, m in enumerate(markets, 1):
            format_market(m, i)

        print(f"---")
        print(f"*Showing {len(markets)} economics markets*")
    finally:
        await client.close()


async def get_trending_markets(limit: int = 10):
    """Get trending/high-volume markets."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.get_trending_markets(limit=limit)
        if not markets:
            print("No trending markets found")
            return

        print("## Trending Markets (High Volume)")
        print()
        print("*Most actively traded markets on Kalshi*")
        print()

        for i, m in enumerate(markets, 1):
            format_market(m, i)

        print(f"---")
        print(f"*Showing top {len(markets)} by volume*")
    finally:
        await client.close()


async def search_markets(query: str, limit: int = 10):
    """Search Kalshi markets."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.search_markets(query, limit=limit)
        if not markets:
            print(f"No markets found for: {query}")
            return

        print(f"## Kalshi Search: \"{query}\"")
        print()

        for i, m in enumerate(markets, 1):
            format_market(m, i)

        print(f"---")
        print(f"*Found {len(markets)} markets matching \"{query}\"*")
    finally:
        await client.close()


async def get_series():
    """Get all available series."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        series_list = await client.get_all_series()
        if not series_list:
            print("No series found")
            return

        print("## Kalshi Market Series")
        print()

        for s in series_list[:30]:
            ticker = s.get("ticker", "N/A")
            title = s.get("title", s.get("category", "N/A"))
            print(f"- **{ticker}**: {title}")

        if len(series_list) > 30:
            print(f"\n*... and {len(series_list) - 30} more series*")

        print(f"\n---")
        print(f"*Total: {len(series_list)} series available*")
    finally:
        await client.close()


def main():
    parser = argparse.ArgumentParser(description="Kalshi Prediction Markets")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()
    cmd = args.command.lower()
    cmd_args = args.args

    # Parse limit if provided
    def get_limit(default=10):
        for arg in cmd_args:
            try:
                return int(arg)
            except ValueError:
                continue
        return default

    if cmd == "fed":
        asyncio.run(get_fed_markets(get_limit()))

    elif cmd in ("economics", "econ", "gdp", "cpi"):
        asyncio.run(get_economics_markets(get_limit()))

    elif cmd == "trending":
        asyncio.run(get_trending_markets(get_limit()))

    elif cmd == "search":
        if not cmd_args:
            print("Usage: kalshi.py search \"<query>\" [limit]")
            sys.exit(1)
        query = cmd_args[0]
        limit = get_limit() if len(cmd_args) > 1 else 10
        asyncio.run(search_markets(query, limit))

    elif cmd == "series":
        asyncio.run(get_series())

    else:
        print(f"Unknown command: {cmd}")
        print("Available: fed, economics, trending, search, series")
        sys.exit(1)


if __name__ == "__main__":
    main()
