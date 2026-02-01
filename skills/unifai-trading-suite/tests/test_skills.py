"""Tests for Moltbot Skills.

Run with: pytest tests/test_skills.py -v
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


# Skip tests if API keys not configured
UNIFAI_KEY = os.getenv("UNIFAI_AGENT_API_KEY")
GOOGLE_KEY = os.getenv("GOOGLE_API_KEY")

requires_unifai = pytest.mark.skipif(
    not UNIFAI_KEY,
    reason="UNIFAI_AGENT_API_KEY not set"
)
requires_google = pytest.mark.skipif(
    not GOOGLE_KEY,
    reason="GOOGLE_API_KEY not set"
)


class TestKalshiSkill:
    """Test Kalshi skill (no API key required)."""

    @pytest.mark.asyncio
    async def test_get_fed_markets(self):
        """Test fetching Fed markets."""
        from src.markets.kalshi import KalshiClient

        client = KalshiClient()
        try:
            markets = await client.get_fed_markets(limit=3)
            assert isinstance(markets, list)
            # Fed markets should exist
            if markets:
                assert hasattr(markets[0], "title")
                assert hasattr(markets[0], "yes_price")
                assert hasattr(markets[0], "volume")
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_economics_markets(self):
        """Test fetching economics markets."""
        from src.markets.kalshi import KalshiClient

        client = KalshiClient()
        try:
            markets = await client.get_economics_markets(limit=3)
            assert isinstance(markets, list)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_get_trending_markets(self):
        """Test fetching trending markets."""
        from src.markets.kalshi import KalshiClient

        client = KalshiClient()
        try:
            markets = await client.get_trending_markets(limit=5)
            assert isinstance(markets, list)
        finally:
            await client.close()

    @pytest.mark.asyncio
    async def test_search_markets(self):
        """Test searching markets."""
        from src.markets.kalshi import KalshiClient

        client = KalshiClient()
        try:
            # Search for something that should exist
            markets = await client.search_markets("fed", limit=3)
            assert isinstance(markets, list)
        finally:
            await client.close()


@requires_unifai
@requires_google
class TestTradingAgent:
    """Test Trading Agent (requires API keys)."""

    @pytest.mark.asyncio
    async def test_simple_chat(self):
        """Test simple chat without tools."""
        from src.agents.trading_agent import TradingAgent

        agent = TradingAgent()
        try:
            agent.clear_history()
            response = await agent.chat("What is 2+2?")
            assert response
            assert "4" in response
        finally:
            await agent.close()

    @pytest.mark.asyncio
    async def test_kalshi_fed_markets(self):
        """Test Kalshi Fed markets via agent."""
        from src.agents.trading_agent import TradingAgent

        agent = TradingAgent()
        try:
            response = await agent.get_fed_prediction_markets()
            assert response
            assert "Federal Reserve" in response or "Fed" in response
        finally:
            await agent.close()

    @pytest.mark.asyncio
    async def test_tool_calling(self):
        """Test that tool calling works."""
        from src.agents.trading_agent import TradingAgent

        agent = TradingAgent()
        try:
            agent.clear_history()
            response = await agent.chat("What is the current price of Bitcoin?")
            assert response
            # Should contain price info or market data
            assert any(word in response.lower() for word in ["bitcoin", "btc", "price", "$"])
        finally:
            await agent.close()


@requires_unifai
@requires_google
class TestSocialSignals:
    """Test Social Signals (requires API keys)."""

    @pytest.mark.asyncio
    async def test_get_trending_tokens(self):
        """Test getting trending tokens."""
        from src.signals.social import SocialSignalProcessor

        processor = SocialSignalProcessor()
        signal = await processor.get_trending_tokens(time_window="24h")
        assert signal.signal_type.value == "trending"
        assert signal.source == "Elfa"

    @pytest.mark.asyncio
    async def test_get_crypto_news(self):
        """Test getting crypto news."""
        from src.signals.social import SocialSignalProcessor

        processor = SocialSignalProcessor()
        signal = await processor.get_crypto_news("Bitcoin", limit=3)
        assert signal.signal_type.value == "news"
        assert signal.source == "SerpAPI"


class TestSkillScripts:
    """Test skill CLI scripts can be imported."""

    def test_kalshi_script_importable(self):
        """Test Kalshi script can be imported."""
        script_path = Path(__file__).parent.parent / "skills/kalshi-trader/scripts"
        sys.path.insert(0, str(script_path.parent.parent.parent))
        # Just verify the imports work
        from src.markets.kalshi import KalshiClient
        assert KalshiClient is not None

    def test_trader_script_importable(self):
        """Test trader script imports work."""
        from src.agents.trading_agent import TradingAgent
        assert TradingAgent is not None

    def test_signals_script_importable(self):
        """Test signals script imports work."""
        from src.signals.social import SocialSignalProcessor
        assert SocialSignalProcessor is not None


# Quick CLI test runner
if __name__ == "__main__":
    print("=" * 60)
    print("Moltbot Skills Test Suite")
    print("=" * 60)

    async def run_quick_tests():
        """Run quick tests without pytest."""
        results = []

        # Test 1: Kalshi
        print("\n[1] Testing Kalshi Client...")
        try:
            from src.markets.kalshi import KalshiClient
            client = KalshiClient()
            markets = await client.get_fed_markets(limit=2)
            await client.close()
            results.append(("Kalshi Fed Markets", True, f"Found {len(markets)} markets"))
        except Exception as e:
            results.append(("Kalshi Fed Markets", False, str(e)))

        # Test 2: Trading Agent (if keys available)
        if UNIFAI_KEY and GOOGLE_KEY:
            print("\n[2] Testing Trading Agent...")
            try:
                from src.agents.trading_agent import TradingAgent
                agent = TradingAgent()
                agent.clear_history()
                response = await agent.chat("What is 2+2?")
                await agent.close()
                passed = "4" in response
                results.append(("Trading Agent Chat", passed, response[:50]))
            except Exception as e:
                results.append(("Trading Agent Chat", False, str(e)))
        else:
            results.append(("Trading Agent Chat", None, "Skipped (no API keys)"))

        # Print results
        print("\n" + "=" * 60)
        print("Results:")
        print("-" * 60)
        for name, passed, msg in results:
            status = "PASS" if passed else ("SKIP" if passed is None else "FAIL")
            print(f"  [{status}] {name}: {msg[:40]}...")

    asyncio.run(run_quick_tests())
