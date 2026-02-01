"""Polymarket prediction market client.

This provides a thin wrapper around UnifAI's Polymarket tools for consistency
with the Kalshi client interface.

For direct Polymarket API access, the UnifAI tools provide comprehensive coverage:
- polymarket--127--search
- polymarket--127--searchPolymarketMarkets
- polymarket--127--searchPolymarketEvents
- polymarket--127--getEventsByCategory
- polymarket--127--getPrices
- polymarket--127--getOrderBooks
- polymarket--127--limitOrderBuy/Sell
- polymarket--127--marketOrderBuy/Sell
"""

import json
import os
from dataclasses import dataclass
from typing import Any

from dotenv import load_dotenv
import unifai
import litellm

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview")


@dataclass
class PolymarketEvent:
    """Represents a Polymarket event."""
    id: str
    title: str
    slug: str
    volume: float
    markets: list[dict]

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "volume": self.volume,
            "markets": self.markets,
        }


@dataclass
class PolymarketMarket:
    """Represents a Polymarket market."""
    condition_id: str
    question: str
    slug: str
    yes_price: float
    no_price: float
    volume: float
    liquidity: float
    token_id: str | None = None

    def to_dict(self) -> dict:
        return {
            "condition_id": self.condition_id,
            "question": self.question,
            "slug": self.slug,
            "yes_price": self.yes_price,
            "no_price": self.no_price,
            "volume": self.volume,
            "liquidity": self.liquidity,
            "token_id": self.token_id,
        }


class PolymarketClient:
    """Client for Polymarket via UnifAI tools.

    This wraps UnifAI's Polymarket tools to provide a consistent interface.

    Usage:
        client = PolymarketClient()

        # Get trending events
        events = await client.get_trending_events()

        # Search markets
        markets = await client.search_markets("bitcoin")

        # Get events by category
        events = await client.get_events_by_category("crypto")
    """

    CATEGORIES = [
        "trending", "new", "politics", "crypto", "tech",
        "culture", "sports", "world", "economy", "trump", "elections"
    ]

    def __init__(self, api_key: str | None = None, model: str | None = None):
        """Initialize the Polymarket client.

        Args:
            api_key: UnifAI agent API key
            model: LLM model to use for tool orchestration
        """
        self.api_key = api_key or os.getenv("UNIFAI_AGENT_API_KEY")
        if not self.api_key:
            raise ValueError("UNIFAI_AGENT_API_KEY is required")

        self.model = model or DEFAULT_MODEL
        self.tools = unifai.Tools(api_key=self.api_key)

    async def _call_tool(self, tool_name: str, params: dict) -> Any:
        """Call a specific Polymarket tool via UnifAI."""
        available_tools = await self.tools.get_tools(dynamic_tools=True)

        messages = [
            {"role": "system", "content": "You are a helpful assistant. Call the requested tool and return the raw result."},
            {"role": "user", "content": f"Call the tool {tool_name} with parameters: {json.dumps(params)}. Return only the tool result."},
        ]

        response = await litellm.acompletion(
            model=self.model,
            messages=messages,
            tools=available_tools,
            temperature=1.0,  # Gemini 3 requires temp=1.0 to avoid looping
        )

        message = response.choices[0].message
        if message.tool_calls:
            results = await self.tools.call_tools(message.tool_calls)
            if results:
                result = results[0]
                if isinstance(result, dict) and "content" in result:
                    try:
                        return json.loads(result["content"])
                    except (json.JSONDecodeError, TypeError):
                        return result["content"]
                return result
        return None

    async def get_events_by_category(
        self,
        category: str = "trending",
    ) -> list[dict]:
        """Get events by category.

        Args:
            category: One of: trending, new, politics, crypto, tech, culture,
                     sports, world, economy, trump, elections

        Returns:
            List of events with their markets
        """
        if category not in self.CATEGORIES:
            raise ValueError(f"Invalid category. Must be one of: {self.CATEGORIES}")

        result = await self._call_tool(
            "polymarket--127--getEventsByCategory",
            {"category": category}
        )
        return result if isinstance(result, list) else []

    async def search_markets(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict]:
        """Search for markets by text query.

        Args:
            query: Search query
            limit: Max results to return

        Returns:
            List of matching markets
        """
        result = await self._call_tool(
            "polymarket--127--search",
            {"q": query}
        )
        if isinstance(result, list):
            return result[:limit]
        return []

    async def get_markets(
        self,
        tag: str | None = None,
        active: bool = True,
        limit: int = 10,
    ) -> list[dict]:
        """Get markets with filters.

        Args:
            tag: Filter by tag (e.g., "crypto", "politics")
            active: Include only active markets
            limit: Max results

        Returns:
            List of markets
        """
        params = {
            "active": active,
            "limit": limit,
        }
        if tag:
            params["tag"] = tag

        result = await self._call_tool(
            "polymarket--127--searchPolymarketMarkets",
            params
        )
        return result if isinstance(result, list) else []

    async def get_prices(
        self,
        token_ids: list[str],
        sides: list[str] | None = None,
    ) -> list[dict]:
        """Get prices for specific tokens.

        Args:
            token_ids: List of token IDs
            sides: List of sides ('buy' or 'sell'), same length as token_ids

        Returns:
            Price data for each token
        """
        if sides is None:
            sides = ["buy"] * len(token_ids)

        result = await self._call_tool(
            "polymarket--127--getPrices",
            {"tokenIds": token_ids, "sides": sides}
        )
        return result if isinstance(result, list) else []

    async def get_orderbooks(
        self,
        token_ids: list[str],
        sides: list[str] | None = None,
    ) -> list[dict]:
        """Get orderbooks for specific tokens.

        Args:
            token_ids: List of token IDs
            sides: List of sides

        Returns:
            Orderbook data for each token
        """
        if sides is None:
            sides = ["buy"] * len(token_ids)

        result = await self._call_tool(
            "polymarket--127--getOrderBooks",
            {"tokenIds": token_ids, "sides": sides}
        )
        return result if isinstance(result, list) else []

    async def get_trending_events(self, limit: int = 10) -> list[dict]:
        """Get trending events.

        Args:
            limit: Number of events to return

        Returns:
            List of trending events
        """
        events = await self.get_events_by_category("trending")
        return events[:limit] if events else []

    async def get_crypto_markets(self, limit: int = 10) -> list[dict]:
        """Get crypto-related markets.

        Args:
            limit: Number of markets to return

        Returns:
            List of crypto markets
        """
        events = await self.get_events_by_category("crypto")
        return events[:limit] if events else []

    async def get_politics_markets(self, limit: int = 10) -> list[dict]:
        """Get politics-related markets.

        Args:
            limit: Number of markets to return

        Returns:
            List of politics markets
        """
        events = await self.get_events_by_category("politics")
        return events[:limit] if events else []


async def demo():
    """Demo the Polymarket client."""
    client = PolymarketClient()

    print("=" * 70)
    print("POLYMARKET CLIENT DEMO")
    print("=" * 70)

    # Get trending events
    print("\n1. Trending Events:")
    print("-" * 70)
    events = await client.get_trending_events(limit=3)
    for event in events:
        print(f"  {event.get('title', 'N/A')}")
        print(f"    Volume: ${event.get('volume', 0):,.0f}")

    # Get crypto markets
    print("\n2. Crypto Markets:")
    print("-" * 70)
    crypto = await client.get_crypto_markets(limit=3)
    for event in crypto:
        print(f"  {event.get('title', 'N/A')}")

    # Search for specific topic
    print("\n3. Search 'bitcoin':")
    print("-" * 70)
    results = await client.search_markets("bitcoin", limit=3)
    for r in results:
        print(f"  {r}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
