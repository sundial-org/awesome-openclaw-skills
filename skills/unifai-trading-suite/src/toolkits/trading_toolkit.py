"""Example trading toolkit for UnifAI.

This toolkit exposes trading-related actions that other agents can discover and use.
Run this to register your toolkit with the UnifAI network.
"""

import asyncio
import os
from dotenv import load_dotenv
import unifai

load_dotenv()


async def create_trading_toolkit():
    """Create and run a trading toolkit."""
    api_key = os.getenv("UNIFAI_TOOLKIT_API_KEY")
    if not api_key:
        raise ValueError("UNIFAI_TOOLKIT_API_KEY is required")

    toolkit = unifai.Toolkit(api_key=api_key)

    @toolkit.action(
        action="get_market_info",
        action_description="Get information about a prediction market",
        payload_description={
            "market_id": {
                "type": "string",
                "description": "The unique identifier of the market",
            },
        },
    )
    async def get_market_info(ctx: unifai.ActionContext, payload: dict = {}):
        """Fetch market information."""
        market_id = payload.get("market_id")
        if not market_id:
            return ctx.Error("market_id is required")

        # TODO: Implement actual market data fetching
        # This is a placeholder response
        return ctx.Result({
            "market_id": market_id,
            "title": "Example Market",
            "status": "open",
            "yes_price": 0.65,
            "no_price": 0.35,
            "volume": 10000,
        })

    @toolkit.action(
        action="analyze_sentiment",
        action_description="Analyze social sentiment for a topic related to prediction markets",
        payload_description={
            "topic": {
                "type": "string",
                "description": "The topic to analyze sentiment for",
            },
            "sources": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Social media sources to analyze (twitter, discord, telegram)",
            },
        },
    )
    async def analyze_sentiment(ctx: unifai.ActionContext, payload: dict = {}):
        """Analyze social sentiment for a topic."""
        topic = payload.get("topic")
        sources = payload.get("sources", ["twitter"])

        if not topic:
            return ctx.Error("topic is required")

        # TODO: Implement actual sentiment analysis
        return ctx.Result({
            "topic": topic,
            "sources": sources,
            "sentiment_score": 0.72,  # -1 to 1 scale
            "sentiment_label": "bullish",
            "confidence": 0.85,
            "sample_size": 1500,
        })

    @toolkit.action(
        action="execute_trade",
        action_description="Execute a trade on a prediction market",
        payload_description={
            "market_id": {
                "type": "string",
                "description": "The market to trade on",
            },
            "position": {
                "type": "string",
                "enum": ["yes", "no"],
                "description": "The position to take (yes or no)",
            },
            "amount": {
                "type": "number",
                "description": "Amount to trade in USD",
            },
        },
    )
    async def execute_trade(ctx: unifai.ActionContext, payload: dict = {}):
        """Execute a prediction market trade."""
        market_id = payload.get("market_id")
        position = payload.get("position")
        amount_raw = payload.get("amount")

        if not all([market_id, position, amount_raw is not None]):
            return ctx.Error("market_id, position, and amount are required")

        if position not in ["yes", "no"]:
            return ctx.Error("position must be 'yes' or 'no'")

        amount = float(amount_raw)
        if amount <= 0:
            return ctx.Error("amount must be positive")

        price = 0.65 if position == "yes" else 0.35
        # TODO: Implement actual trade execution
        # This is a simulated response
        return ctx.Result({
            "status": "success",
            "trade_id": f"trade_{market_id}_{position}_{amount}",
            "market_id": market_id,
            "position": position,
            "amount": amount,
            "price": price,
            "shares": amount / price,
        })

    @toolkit.action(
        action="get_portfolio",
        action_description="Get current portfolio positions and balances",
        payload_description={},
    )
    async def get_portfolio(ctx: unifai.ActionContext, payload: dict = {}):  # noqa: ARG001
        """Get portfolio information."""
        # TODO: Implement actual portfolio fetching
        return ctx.Result({
            "balance_usd": 1000.00,
            "positions": [
                {
                    "market_id": "market_123",
                    "title": "Example Market",
                    "position": "yes",
                    "shares": 100,
                    "avg_price": 0.60,
                    "current_price": 0.65,
                    "pnl": 5.00,
                },
            ],
            "total_value": 1065.00,
        })

    print("Starting trading toolkit...")
    print("Registered actions: get_market_info, analyze_sentiment, execute_trade, get_portfolio")
    await toolkit.run()


if __name__ == "__main__":
    asyncio.run(create_trading_toolkit())
