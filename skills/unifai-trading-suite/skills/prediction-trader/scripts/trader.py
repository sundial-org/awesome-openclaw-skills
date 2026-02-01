#!/usr/bin/env python3
"""Prediction Trader CLI - Moltbot Skill Script.

Usage:
    python3 trader.py compare "<topic>"
    python3 trader.py trending
    python3 trader.py analyze "<topic>"
    python3 trader.py polymarket <command> [args]
    python3 trader.py kalshi <command> [args]
"""

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

# Add parent directories to path for imports
script_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(script_dir))

from dotenv import load_dotenv

load_dotenv()


async def get_kalshi_fed():
    """Get Fed interest rate markets from Kalshi."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.get_fed_markets(limit=10)
        if not markets:
            print("No Fed markets found")
            return

        print("## Federal Reserve Interest Rate Markets (Kalshi)")
        print()
        for m in markets:
            print(f"- {m.title}")
            print(f"  YES: ${m.yes_price:.2f} ({m.yes_price*100:.0f}%) | Volume: {m.volume:,}")
            print()
    finally:
        await client.close()


async def get_kalshi_economics():
    """Get economics markets from Kalshi."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.get_economics_markets(limit=10)
        if not markets:
            print("No economics markets found")
            return

        print("## Economics Markets - GDP/CPI (Kalshi)")
        print()
        for m in markets:
            print(f"- {m.title}")
            print(f"  YES: ${m.yes_price:.2f} ({m.yes_price*100:.0f}%) | Volume: {m.volume:,}")
            print()
    finally:
        await client.close()


async def search_kalshi(query: str):
    """Search Kalshi markets."""
    from src.markets.kalshi import KalshiClient

    client = KalshiClient()
    try:
        markets = await client.search_markets(query, limit=10)
        if not markets:
            print(f"No Kalshi markets found for: {query}")
            return

        print(f"## Kalshi Search: {query}")
        print()
        for m in markets:
            print(f"- {m.title}")
            print(f"  YES: ${m.yes_price:.2f} ({m.yes_price*100:.0f}%) | Volume: {m.volume:,}")
            print()
    finally:
        await client.close()


async def get_polymarket_trending():
    """Get trending events from Polymarket."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        response = await agent.get_polymarket_trending()
        print(response)
    finally:
        await agent.close()


async def get_polymarket_crypto():
    """Get crypto markets from Polymarket."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        response = await agent.get_polymarket_crypto()
        print(response)
    finally:
        await agent.close()


async def search_polymarket(query: str):
    """Search Polymarket markets."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        response = await agent.search_polymarket(query)
        print(response)
    finally:
        await agent.close()


async def compare_markets(topic: str):
    """Compare markets across both platforms."""
    from src.markets.kalshi import KalshiClient
    from src.agents.trading_agent import TradingAgent

    print(f"## Prediction Markets: {topic}")
    print()

    # Kalshi
    print("### Kalshi (CFTC-Regulated)")
    print()
    kalshi = KalshiClient()
    try:
        markets = await kalshi.search_markets(topic, limit=5)
        if markets:
            for m in markets:
                print(f"- {m.title}")
                print(f"  YES: ${m.yes_price:.2f} | Volume: {m.volume:,}")
        else:
            print("No markets found")
    finally:
        await kalshi.close()

    print()

    # Polymarket
    print("### Polymarket")
    print()
    agent = TradingAgent()
    try:
        response = await agent.search_polymarket(topic)
        # Extract just the content part
        if "**Polymarket Search" in response:
            print(response.split("**Polymarket Search")[1].split("**")[1] if "**" in response else response)
        else:
            print(response)
    finally:
        await agent.close()


async def get_trending():
    """Get trending markets from both platforms."""
    from src.markets.kalshi import KalshiClient
    from src.agents.trading_agent import TradingAgent

    print("## Trending Prediction Markets")
    print()

    # Kalshi trending
    print("### Kalshi - High Volume Markets")
    print()
    kalshi = KalshiClient()
    try:
        markets = await kalshi.get_trending_markets(limit=5)
        if markets:
            for m in markets:
                print(f"- {m.title[:60]}")
                print(f"  YES: ${m.yes_price:.2f} | Volume: {m.volume:,}")
        else:
            print("No trending markets")
    finally:
        await kalshi.close()

    print()

    # Polymarket trending
    print("### Polymarket - Trending Events")
    print()
    agent = TradingAgent()
    try:
        response = await agent.get_polymarket_trending()
        print(response[:1000] if len(response) > 1000 else response)
    finally:
        await agent.close()


async def analyze_topic(topic: str):
    """Full analysis of a topic with social signals."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        agent.clear_history()
        response = await agent.chat(f"""Analyze prediction markets for: {topic}

1. Search both Polymarket and Kalshi for relevant markets
2. Compare the odds/probabilities across platforms
3. Note any significant differences in pricing
4. Summarize the market consensus

Be concise and data-driven.""")
        print(response)
    finally:
        await agent.close()


def main():
    parser = argparse.ArgumentParser(description="Prediction Market Trader")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()
    cmd = args.command.lower()
    cmd_args = args.args

    # Check environment
    if not os.getenv("UNIFAI_AGENT_API_KEY"):
        print("Error: UNIFAI_AGENT_API_KEY not set")
        sys.exit(1)

    if cmd == "compare":
        if not cmd_args:
            print("Usage: trader.py compare \"<topic>\"")
            sys.exit(1)
        asyncio.run(compare_markets(cmd_args[0]))

    elif cmd == "trending":
        asyncio.run(get_trending())

    elif cmd == "analyze":
        if not cmd_args:
            print("Usage: trader.py analyze \"<topic>\"")
            sys.exit(1)
        asyncio.run(analyze_topic(cmd_args[0]))

    elif cmd == "polymarket":
        if not cmd_args:
            print("Usage: trader.py polymarket <trending|crypto|search> [args]")
            sys.exit(1)

        subcmd = cmd_args[0].lower()
        if subcmd == "trending":
            asyncio.run(get_polymarket_trending())
        elif subcmd == "crypto":
            asyncio.run(get_polymarket_crypto())
        elif subcmd == "search" and len(cmd_args) > 1:
            asyncio.run(search_polymarket(cmd_args[1]))
        else:
            print("Usage: trader.py polymarket <trending|crypto|search \"query\">")
            sys.exit(1)

    elif cmd == "kalshi":
        if not cmd_args:
            print("Usage: trader.py kalshi <fed|economics|search> [args]")
            sys.exit(1)

        subcmd = cmd_args[0].lower()
        if subcmd == "fed":
            asyncio.run(get_kalshi_fed())
        elif subcmd in ("economics", "econ", "gdp", "cpi"):
            asyncio.run(get_kalshi_economics())
        elif subcmd == "search" and len(cmd_args) > 1:
            asyncio.run(search_kalshi(cmd_args[1]))
        else:
            print("Usage: trader.py kalshi <fed|economics|search \"query\">")
            sys.exit(1)

    else:
        print(f"Unknown command: {cmd}")
        print("Available: compare, trending, analyze, polymarket, kalshi")
        sys.exit(1)


if __name__ == "__main__":
    main()
