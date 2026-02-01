"""Kalshi prediction market API client.

Kalshi is a CFTC-regulated prediction market. This client provides access to
market data and trading functionality.

API Documentation: https://docs.kalshi.com
Base URL: https://api.elections.kalshi.com/trade-api/v2

Note: Despite the 'elections' subdomain, this API provides access to ALL Kalshi markets.
"""

import os
from dataclasses import dataclass
from datetime import datetime
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://api.elections.kalshi.com/trade-api/v2"


@dataclass
class KalshiMarket:
    """Represents a Kalshi market."""
    ticker: str
    title: str
    status: str
    yes_price: float
    no_price: float
    volume: int
    open_interest: int
    close_time: datetime | None = None
    result: str | None = None

    @classmethod
    def from_api(cls, data: dict) -> "KalshiMarket":
        """Create from API response."""
        close_time = None
        if data.get("close_time"):
            try:
                close_time = datetime.fromisoformat(data["close_time"].replace("Z", "+00:00"))
            except (ValueError, TypeError):
                pass

        return cls(
            ticker=data.get("ticker", ""),
            title=data.get("title", ""),
            status=data.get("status", ""),
            yes_price=data.get("yes_ask", 0) / 100 if data.get("yes_ask") else 0,
            no_price=data.get("no_ask", 0) / 100 if data.get("no_ask") else 0,
            volume=data.get("volume", 0),
            open_interest=data.get("open_interest", 0),
            close_time=close_time,
            result=data.get("result"),
        )

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "ticker": self.ticker,
            "title": self.title,
            "status": self.status,
            "yes_price": self.yes_price,
            "no_price": self.no_price,
            "volume": self.volume,
            "open_interest": self.open_interest,
            "close_time": self.close_time.isoformat() if self.close_time else None,
            "result": self.result,
        }


@dataclass
class KalshiOrderBook:
    """Represents orderbook data."""
    ticker: str
    yes_bids: list[dict]
    no_bids: list[dict]
    spread: float

    @classmethod
    def from_api(cls, ticker: str, data: dict) -> "KalshiOrderBook":
        """Create from API response."""
        yes_bids = data.get("yes", [])
        no_bids = data.get("no", [])

        # Calculate spread
        best_yes = yes_bids[0]["price"] / 100 if yes_bids else 0
        best_no = no_bids[0]["price"] / 100 if no_bids else 0
        spread = 1 - best_yes - best_no if best_yes and best_no else 0

        return cls(
            ticker=ticker,
            yes_bids=yes_bids,
            no_bids=no_bids,
            spread=spread,
        )


class KalshiClient:
    """Client for Kalshi API.

    Provides access to market data. Trading requires authentication.

    Usage:
        client = KalshiClient()

        # Get all active markets
        markets = await client.get_markets(status="open")

        # Search markets
        markets = await client.search_markets("bitcoin")

        # Get specific market
        market = await client.get_market("BTC-25JAN-100K")

        # Get orderbook
        orderbook = await client.get_orderbook("BTC-25JAN-100K")
    """

    def __init__(self, api_key: str | None = None):
        """Initialize the Kalshi client.

        Args:
            api_key: Optional API key for authenticated endpoints
        """
        self.api_key = api_key or os.getenv("KALSHI_API_KEY")
        self.base_url = BASE_URL
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {"Accept": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def _request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make an API request."""
        client = await self._get_client()
        response = await client.request(method, endpoint, **kwargs)
        response.raise_for_status()
        return response.json()

    async def get_markets(
        self,
        series_ticker: str | None = None,
        status: str | None = None,
        limit: int = 100,
        cursor: str | None = None,
    ) -> list[KalshiMarket]:
        """Get markets with optional filters.

        Args:
            series_ticker: Filter by series (e.g., "KXBTC" for Bitcoin markets)
            status: Filter by status ("open", "closed", "settled")
            limit: Max markets to return (default 100)
            cursor: Pagination cursor

        Returns:
            List of KalshiMarket objects
        """
        params: dict[str, Any] = {"limit": limit}
        if series_ticker:
            params["series_ticker"] = series_ticker
        if status:
            params["status"] = status
        if cursor:
            params["cursor"] = cursor

        data = await self._request("GET", "/markets", params=params)
        markets = data.get("markets", [])
        return [KalshiMarket.from_api(m) for m in markets]

    async def get_market(self, ticker: str) -> KalshiMarket | None:
        """Get a specific market by ticker.

        Args:
            ticker: Market ticker (e.g., "BTC-25JAN-100K")

        Returns:
            KalshiMarket or None if not found
        """
        try:
            data = await self._request("GET", f"/markets/{ticker}")
            market_data = data.get("market", {})
            return KalshiMarket.from_api(market_data) if market_data else None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def search_markets(
        self,
        query: str,
        status: str = "open",
        limit: int = 20,
    ) -> list[KalshiMarket]:
        """Search markets by keyword.

        Args:
            query: Search query
            status: Filter by status
            limit: Max results

        Returns:
            List of matching markets
        """
        # Kalshi doesn't have a direct search endpoint, so we fetch markets
        # and filter client-side. For production, use their events endpoint.
        markets = await self.get_markets(status=status, limit=200)

        query_lower = query.lower()
        matching = [
            m for m in markets
            if query_lower in m.title.lower() or query_lower in m.ticker.lower()
        ]
        return matching[:limit]

    async def get_orderbook(self, ticker: str) -> KalshiOrderBook | None:
        """Get orderbook for a market.

        Args:
            ticker: Market ticker

        Returns:
            KalshiOrderBook or None if not found
        """
        try:
            data = await self._request("GET", f"/markets/{ticker}/orderbook")
            orderbook = data.get("orderbook", {})
            return KalshiOrderBook.from_api(ticker, orderbook) if orderbook else None
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def get_series(self, ticker: str) -> dict[str, Any] | None:
        """Get series information.

        Args:
            ticker: Series ticker (e.g., "KXBTC")

        Returns:
            Series data or None
        """
        try:
            data = await self._request("GET", f"/series/{ticker}")
            return data.get("series")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def get_event(self, ticker: str) -> dict[str, Any] | None:
        """Get event details.

        Args:
            ticker: Event ticker

        Returns:
            Event data or None
        """
        try:
            data = await self._request("GET", f"/events/{ticker}")
            return data.get("event")
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return None
            raise

    async def get_trending_markets(self, limit: int = 10) -> list[KalshiMarket]:
        """Get trending/high-volume markets.

        Args:
            limit: Number of markets to return

        Returns:
            List of markets sorted by volume
        """
        markets = await self.get_markets(status="open", limit=200)
        # Sort by volume descending
        markets.sort(key=lambda m: m.volume, reverse=True)
        return markets[:limit]

    async def get_fed_markets(self, limit: int = 10) -> list[KalshiMarket]:
        """Get Federal Reserve interest rate markets.

        Args:
            limit: Number of markets to return

        Returns:
            List of Fed-related markets
        """
        return await self.get_markets(series_ticker="KXFED", status="open", limit=limit)

    async def get_crypto_markets(self, limit: int = 10) -> list[KalshiMarket]:
        """Get cryptocurrency-related markets.

        Args:
            limit: Number of markets to return

        Returns:
            List of crypto markets
        """
        # Kalshi has various crypto series
        crypto_series = ["KXBTC", "KXETH", "KXBTCD"]
        all_markets = []
        for series in crypto_series:
            try:
                markets = await self.get_markets(series_ticker=series, status="open", limit=20)
                all_markets.extend(markets)
            except Exception:
                continue
        all_markets.sort(key=lambda m: m.volume, reverse=True)
        return all_markets[:limit]

    async def get_economics_markets(self, limit: int = 10) -> list[KalshiMarket]:
        """Get economics-related markets (CPI, GDP, etc).

        Args:
            limit: Number of markets to return

        Returns:
            List of economics markets
        """
        econ_series = ["KXCPI", "KXGDP", "CPIYOY", "KXECONSTATCORECPIYOY"]
        all_markets = []
        for series in econ_series:
            try:
                markets = await self.get_markets(series_ticker=series, status="open", limit=20)
                all_markets.extend(markets)
            except Exception:
                continue
        all_markets.sort(key=lambda m: m.volume, reverse=True)
        return all_markets[:limit]

    async def get_all_series(self) -> list[dict]:
        """Get all available series.

        Returns:
            List of series metadata
        """
        data = await self._request("GET", "/series")
        return data.get("series", [])

    async def get_events(
        self,
        status: str | None = None,
        limit: int = 20,
    ) -> list[dict]:
        """Get events.

        Args:
            status: Filter by status
            limit: Max events to return

        Returns:
            List of event data
        """
        params: dict[str, Any] = {"limit": limit}
        if status:
            params["status"] = status

        data = await self._request("GET", "/events", params=params)
        return data.get("events", [])


async def demo():
    """Demo the Kalshi client."""
    client = KalshiClient()

    try:
        print("=" * 70)
        print("KALSHI API DEMO")
        print("=" * 70)

        # Get Fed markets
        print("\n1. Federal Reserve Interest Rate Markets:")
        print("-" * 70)
        fed_markets = await client.get_fed_markets(limit=5)
        for m in fed_markets:
            print(f"  {m.ticker}")
            print(f"    {m.title[:60]}")
            print(f"    YES: ${m.yes_price:.2f} | Vol: {m.volume:,}")

        # Get economics markets
        print("\n2. Economics Markets (CPI, GDP):")
        print("-" * 70)
        econ = await client.get_economics_markets(limit=5)
        if econ:
            for m in econ:
                print(f"  {m.ticker}: {m.title[:50]}")
                print(f"    YES: ${m.yes_price:.2f}")
        else:
            print("  No active economics markets found")

        # Get events
        print("\n3. Recent Events:")
        print("-" * 70)
        events = await client.get_events(limit=10)
        categories = {}
        for e in events:
            cat = e.get("category", "Other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(e.get("title", ""))

        for cat, titles in list(categories.items())[:5]:
            print(f"  {cat}:")
            for t in titles[:2]:
                print(f"    - {t[:55]}...")

    finally:
        await client.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(demo())
