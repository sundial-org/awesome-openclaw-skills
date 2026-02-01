#!/usr/bin/env python3
"""Polymarket CLI - Moltbot Skill Script.

Usage:
    python3 polymarket.py trending
    python3 polymarket.py crypto
    python3 polymarket.py politics
    python3 polymarket.py search "<query>"
    python3 polymarket.py category <name>
"""

import argparse
import asyncio
import os
import sys
from pathlib import Path

# Add parent directories to path for imports
script_dir = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(script_dir))

from dotenv import load_dotenv

load_dotenv()


async def get_trending():
    """Get trending events from Polymarket."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        response = await agent.get_polymarket_trending()
        print("## Polymarket Trending Events")
        print()
        print(response)
    finally:
        await agent.close()


async def get_crypto():
    """Get crypto markets from Polymarket."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        response = await agent.get_polymarket_crypto()
        print("## Polymarket Crypto Markets")
        print()
        print(response)
    finally:
        await agent.close()


async def get_politics():
    """Get politics markets from Polymarket."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        agent.clear_history()
        response = await agent.chat("Get the top political prediction markets from Polymarket with current prices")
        print("## Polymarket Politics Markets")
        print()
        print(response)
    finally:
        await agent.close()


async def search_markets(query: str):
    """Search Polymarket markets."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        response = await agent.search_polymarket(query)
        print(f"## Polymarket Search: \"{query}\"")
        print()
        print(response)
    finally:
        await agent.close()


async def get_category(category: str):
    """Get markets by category."""
    from src.agents.trading_agent import TradingAgent

    valid_categories = [
        "trending", "new", "politics", "crypto", "tech",
        "culture", "sports", "world", "economy", "trump", "elections"
    ]

    if category.lower() not in valid_categories:
        print(f"Invalid category: {category}")
        print(f"Valid categories: {', '.join(valid_categories)}")
        return

    agent = TradingAgent()
    try:
        agent.clear_history()
        response = await agent.chat(f"Get the top prediction markets from Polymarket in the {category} category with current prices and volumes")
        print(f"## Polymarket {category.title()} Markets")
        print()
        print(response)
    finally:
        await agent.close()


def main():
    parser = argparse.ArgumentParser(description="Polymarket Prediction Markets")
    parser.add_argument("command", help="Command to execute")
    parser.add_argument("args", nargs="*", help="Command arguments")

    args = parser.parse_args()
    cmd = args.command.lower()
    cmd_args = args.args

    # Check environment
    if not os.getenv("UNIFAI_AGENT_API_KEY"):
        print("Error: UNIFAI_AGENT_API_KEY not set")
        sys.exit(1)

    if cmd == "trending":
        asyncio.run(get_trending())

    elif cmd == "crypto":
        asyncio.run(get_crypto())

    elif cmd == "politics":
        asyncio.run(get_politics())

    elif cmd == "search":
        if not cmd_args:
            print("Usage: polymarket.py search \"<query>\"")
            sys.exit(1)
        asyncio.run(search_markets(cmd_args[0]))

    elif cmd == "category":
        if not cmd_args:
            print("Usage: polymarket.py category <name>")
            print("Categories: trending, new, politics, crypto, tech, culture, sports, world, economy")
            sys.exit(1)
        asyncio.run(get_category(cmd_args[0]))

    else:
        print(f"Unknown command: {cmd}")
        print("Available: trending, crypto, politics, search, category")
        sys.exit(1)


if __name__ == "__main__":
    main()
