#!/usr/bin/env python3
"""Social Signals CLI - Moltbot Skill Script.

Usage:
    python3 signals.py trending
    python3 signals.py sentiment "<token>"
    python3 signals.py news "<query>"
    python3 signals.py events "<keyword>"
    python3 signals.py analyze "<token>"
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


async def get_trending():
    """Get trending tokens from KOLs."""
    from src.signals.social import SocialSignalProcessor

    processor = SocialSignalProcessor()
    signal = await processor.get_trending_tokens(time_window="24h")

    print("## Trending Tokens (KOL Discussions)")
    print()
    print(f"Source: {signal.source}")
    print()

    data = signal.data
    if "tokens" in data:
        for token in data["tokens"][:10]:
            print(f"- **{token.get('symbol', 'N/A')}**")
            if token.get("mentions"):
                print(f"  Mentions: {token['mentions']}")
            if token.get("sentiment"):
                print(f"  Sentiment: {token['sentiment']}")
            print()
    else:
        print(json.dumps(data, indent=2)[:1000])


async def get_sentiment(token: str):
    """Get sentiment analysis for a token."""
    from src.signals.social import SocialSignalProcessor

    processor = SocialSignalProcessor()
    signal = await processor.get_token_sentiment(token)

    print(f"## Social Sentiment: {token}")
    print()
    print(f"Source: {signal.source}")
    print()

    data = signal.data
    if signal.sentiment_score is not None:
        print(f"**Sentiment Score**: {signal.sentiment_score:.2f}")
    if data.get("sentiment_label"):
        print(f"**Sentiment**: {data['sentiment_label']}")
    if data.get("social_volume"):
        print(f"**Social Volume**: {data['social_volume']}")
    if data.get("social_dominance"):
        print(f"**Social Dominance**: {data['social_dominance']}%")
    if data.get("key_topics"):
        print(f"**Key Topics**: {', '.join(data['key_topics'])}")

    print()
    print("Raw data:")
    print(json.dumps(data, indent=2)[:800])


async def search_news(query: str):
    """Search crypto news."""
    from src.signals.social import SocialSignalProcessor

    processor = SocialSignalProcessor()
    signal = await processor.get_crypto_news(query, limit=5)

    print(f"## Crypto News: {query}")
    print()
    print(f"Source: {signal.source}")
    print()

    data = signal.data
    if "articles" in data:
        for article in data["articles"]:
            print(f"- **{article.get('title', 'N/A')}**")
            if article.get("source"):
                print(f"  Source: {article['source']}")
            if article.get("snippet"):
                print(f"  {article['snippet'][:150]}...")
            print()
    else:
        print(json.dumps(data, indent=2)[:1000])

    if data.get("news_sentiment"):
        print(f"\n**Overall News Sentiment**: {data['news_sentiment']}")


async def get_events(keyword: str):
    """Get event summary from social mentions."""
    from src.signals.social import SocialSignalProcessor

    processor = SocialSignalProcessor()
    signal = await processor.get_event_summary(keyword, time_window="24h")

    print(f"## Event Summary: {keyword}")
    print()
    print(f"Source: {signal.source}")
    print()

    data = signal.data
    if data.get("summary"):
        print(f"**Summary**: {data['summary']}")
        print()
    if data.get("key_events"):
        print("**Key Events**:")
        for event in data["key_events"]:
            print(f"  - {event}")
        print()
    if data.get("sentiment_trend"):
        print(f"**Sentiment Trend**: {data['sentiment_trend']}")
    if data.get("volume_trend"):
        print(f"**Volume Trend**: {data['volume_trend']}")
    if data.get("key_influencers"):
        print(f"**Key Influencers**: {', '.join(data['key_influencers'][:5])}")


async def analyze_token(token: str):
    """Full token analysis with all signals."""
    from src.agents.trading_agent import TradingAgent

    agent = TradingAgent()
    try:
        agent.clear_history()
        response = await agent.analyze_token(token)
        print(response)
    finally:
        await agent.close()


def main():
    parser = argparse.ArgumentParser(description="Social Signals Analyzer")
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

    elif cmd == "sentiment":
        if not cmd_args:
            print("Usage: signals.py sentiment \"<token>\"")
            sys.exit(1)
        asyncio.run(get_sentiment(cmd_args[0]))

    elif cmd == "news":
        if not cmd_args:
            print("Usage: signals.py news \"<query>\"")
            sys.exit(1)
        asyncio.run(search_news(cmd_args[0]))

    elif cmd == "events":
        if not cmd_args:
            print("Usage: signals.py events \"<keyword>\"")
            sys.exit(1)
        asyncio.run(get_events(cmd_args[0]))

    elif cmd == "analyze":
        if not cmd_args:
            print("Usage: signals.py analyze \"<token>\"")
            sys.exit(1)
        asyncio.run(analyze_token(cmd_args[0]))

    else:
        print(f"Unknown command: {cmd}")
        print("Available: trending, sentiment, news, events, analyze")
        sys.exit(1)


if __name__ == "__main__":
    main()
