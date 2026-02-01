"""Enhanced trading agent with two-phase tool discovery and execution.

Integrates social signals from multiple sources for prediction market analysis.
Supports both Polymarket (via UnifAI) and Kalshi (direct API) prediction markets.
"""

import asyncio
import json
import os
from dataclasses import dataclass
from dotenv import load_dotenv
import unifai
import litellm

from src.markets.kalshi import KalshiClient, KalshiMarket

load_dotenv()

SYSTEM_PROMPT = """You are an AI trading assistant for prediction markets. You help users analyze markets, gather signals, and execute trades.

## Prediction Market Platforms

You have access to TWO prediction market platforms:

### 1. Polymarket (via UnifAI tools)
- Offshore platform on Polygon blockchain
- Categories: crypto, politics, sports, world events
- Use polymarket tools for: trending events, market search, prices, trading

### 2. Kalshi (via built-in functions)
- CFTC-regulated US prediction market
- Categories: Fed rates, GDP, CPI, economics, politics
- Use Kalshi functions for: Fed markets, economics data, regulated markets
- Note: Kalshi data is provided directly, no tool search needed

## Your Workflow

### For Polymarket queries:
1. Use `unifai_search_tools` to find polymarket tools
2. Execute the appropriate tool (search, getEventsByCategory, etc.)

### For Kalshi queries:
- Kalshi data will be injected into the conversation automatically
- Simply analyze and present the data provided

### For general prediction market queries:
- Compare data from BOTH platforms when relevant
- Note which platform each data point comes from

## Available Tools

**Polymarket (via UnifAI):**
- `polymarket--127--search`: Search markets by text
- `polymarket--127--getEventsByCategory`: Get trending, politics, crypto, etc.
- `polymarket--127--searchPolymarketMarkets`: Filter markets
- `polymarket--127--getPrices`: Get current prices

**Social Signals (via UnifAI):**
- `Elfa--18--getTrendingTokens`: KOL trending tokens on X/Twitter
- `TokenAnalysis--25--analyzeToken`: Token analysis with social metrics
- `SerpAPI--21--newsSearch`: Google News search

**Kalshi (built-in):**
- Fed interest rate markets (KXFED series)
- GDP predictions (KXGDP series)
- CPI/inflation markets
- Other economics events

## Response Format

When providing prediction market analysis:
```
## [Topic] Prediction Markets

**Polymarket:**
- [Market name]: YES $X.XX / NO $X.XX (Volume: $X)

**Kalshi:**
- [Market name]: YES $X.XX (Volume: X)

**Signal Summary**: [Synthesis of market consensus]
```

Do NOT give financial advice - present data objectively.
"""


@dataclass
class MarketSignals:
    """Aggregated market signals for analysis."""
    token: str
    price_data: dict | None = None
    social_sentiment: dict | None = None
    trending_data: dict | None = None
    news_data: dict | None = None

    def to_summary(self) -> str:
        """Generate a text summary of all signals."""
        parts = [f"## {self.token} Market Signals\n"]

        if self.price_data:
            parts.append(f"**Price**: {self.price_data}")

        if self.social_sentiment:
            parts.append(f"**Social Sentiment**: {self.social_sentiment}")

        if self.trending_data:
            parts.append(f"**Trending Data**: {self.trending_data}")

        if self.news_data:
            parts.append(f"**News**: {self.news_data}")

        return "\n".join(parts)


DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview")


class TradingAgent:
    """Enhanced trading agent with Polymarket (UnifAI) and Kalshi integration."""

    def __init__(
        self,
        agent_api_key: str | None = None,
        model: str | None = None,
    ):
        self.api_key = agent_api_key or os.getenv("UNIFAI_AGENT_API_KEY")
        if not self.api_key:
            raise ValueError("UNIFAI_AGENT_API_KEY is required")

        self.model = model or DEFAULT_MODEL
        self.tools = unifai.Tools(api_key=self.api_key)
        self.kalshi = KalshiClient()
        self.conversation_history: list[dict] = []
        self.discovered_tools_cache: dict = {}

    async def get_tools(self) -> list:
        """Get dynamic tools from UnifAI."""
        return await self.tools.get_tools(dynamic_tools=True)

    async def execute_tool_calls(self, tool_calls) -> list:
        """Execute tool calls and return results."""
        return await self.tools.call_tools(tool_calls)

    async def close(self):
        """Close connections."""
        await self.kalshi.close()

    # =========================================================================
    # Kalshi Methods
    # =========================================================================

    async def get_kalshi_fed_markets(self, limit: int = 10) -> list[KalshiMarket]:
        """Get Federal Reserve interest rate markets from Kalshi.

        Args:
            limit: Number of markets to return

        Returns:
            List of Fed-related markets
        """
        return await self.kalshi.get_fed_markets(limit=limit)

    async def get_kalshi_economics_markets(self, limit: int = 10) -> list[KalshiMarket]:
        """Get economics markets (GDP, CPI) from Kalshi.

        Args:
            limit: Number of markets to return

        Returns:
            List of economics markets
        """
        return await self.kalshi.get_economics_markets(limit=limit)

    async def search_kalshi(self, query: str, limit: int = 10) -> list[KalshiMarket]:
        """Search Kalshi markets.

        Args:
            query: Search query
            limit: Number of results

        Returns:
            List of matching markets
        """
        return await self.kalshi.search_markets(query, limit=limit)

    async def get_kalshi_trending(self, limit: int = 10) -> list[KalshiMarket]:
        """Get trending/high-volume Kalshi markets.

        Args:
            limit: Number of markets

        Returns:
            List of markets sorted by volume
        """
        return await self.kalshi.get_trending_markets(limit=limit)

    def _format_kalshi_markets(self, markets: list[KalshiMarket], title: str) -> str:
        """Format Kalshi markets for display."""
        if not markets:
            return f"**{title}**: No markets found"

        lines = [f"**{title}** (Kalshi - CFTC Regulated):\n"]
        for m in markets:
            lines.append(f"- {m.title[:60]}")
            lines.append(f"  YES: ${m.yes_price:.2f} | Volume: {m.volume:,}")
        return "\n".join(lines)

    # =========================================================================
    # Polymarket Methods (using static tools to avoid rate limits)
    # =========================================================================

    async def _call_polymarket_tool(self, tool_name: str, params: dict) -> str:
        """Call a Polymarket tool directly using static tools."""
        try:
            # Use static tools instead of dynamic to avoid search rate limits
            static_tools = await self.tools.get_tools(
                dynamic_tools=False,
                static_toolkits=["127"]  # Polymarket toolkit ID
            )

            messages = [
                {"role": "user", "content": f"Call {tool_name} with params: {json.dumps(params)}"},
            ]

            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                tools=static_tools if static_tools else None,
                temperature=1.0,  # Gemini 3 requires temp=1.0
            )

            message = response.choices[0].message
            if message.tool_calls:
                results = await self.tools.call_tools(message.tool_calls)
                if results:
                    return str(results[0])
            return message.content or "No response"
        except Exception as e:
            return f"Error calling Polymarket: {str(e)}"

    async def get_polymarket_trending(self) -> str:
        """Get trending events from Polymarket.

        Returns:
            Formatted trending events
        """
        try:
            result = await self._call_polymarket_tool(
                "polymarket--127--getEventsByCategory",
                {"category": "trending"}
            )

            # Check for errors
            if "error" in result.lower() or "failed" in result.lower():
                return """**Polymarket Trending Events**

UnifAI Polymarket API is currently unavailable (rate limited).

**Alternative: Use Kalshi** (CFTC-regulated)
- Click "Fed Rates" for interest rate predictions
- Click "GDP / CPI" for economics predictions

Or try again later for Polymarket data."""

            return f"**Polymarket Trending Events**\n\n{result}"
        except Exception as e:
            return f"""**Polymarket Trending Events**

Error: API temporarily unavailable.

**Alternative: Use Kalshi** for regulated prediction markets."""

    async def get_polymarket_crypto(self) -> str:
        """Get crypto markets from Polymarket.

        Returns:
            Formatted crypto markets
        """
        try:
            result = await self._call_polymarket_tool(
                "polymarket--127--getEventsByCategory",
                {"category": "crypto"}
            )

            if "error" in result.lower() or "failed" in result.lower():
                return """**Polymarket Crypto Markets**

UnifAI Polymarket API is currently unavailable (rate limited).

**Alternative: Use Kalshi** (CFTC-regulated)
- Search for "bitcoin" or "crypto" in Kalshi
- Or check economics markets for macro predictions

Or try again later for Polymarket data."""

            return f"**Polymarket Crypto Markets**\n\n{result}"
        except Exception as e:
            return f"""**Polymarket Crypto Markets**

Error: API temporarily unavailable.

**Alternative: Use Kalshi** for regulated prediction markets."""

    async def search_polymarket(self, query: str) -> str:
        """Search Polymarket markets.

        Args:
            query: Search query

        Returns:
            Formatted search results
        """
        try:
            result = await self._call_polymarket_tool(
                "polymarket--127--search",
                {"q": query}
            )

            if "error" in result.lower() or "failed" in result.lower():
                return f"""**Polymarket Search: {query}**

UnifAI Polymarket API is currently unavailable.

Try searching on Kalshi instead, or try again later."""

            return f"**Polymarket Search: {query}**\n\n{result}"
        except Exception as e:
            return f"""**Polymarket Search: {query}**

Error: API temporarily unavailable."""

    # =========================================================================
    # Combined Prediction Market Methods
    # =========================================================================

    async def get_prediction_markets(self, topic: str) -> str:
        """Get prediction markets from both Polymarket and Kalshi.

        Args:
            topic: Topic to search for

        Returns:
            Combined analysis from both platforms
        """
        # Get Kalshi data directly
        kalshi_results = await self.search_kalshi(topic, limit=5)
        kalshi_text = self._format_kalshi_markets(kalshi_results, f"Kalshi Markets for '{topic}'")

        # Get Polymarket data via chat
        polymarket_prompt = f"""Search Polymarket for prediction markets related to: {topic}

Use the polymarket search tool and return the top 5 results with:
- Market question
- Current YES/NO prices
- Volume if available

Format clearly."""

        polymarket_text = await self.chat(polymarket_prompt)

        return f"""## Prediction Markets: {topic}

### Kalshi (CFTC-Regulated)
{kalshi_text}

### Polymarket
{polymarket_text}
"""

    async def get_fed_prediction_markets(self) -> str:
        """Get Fed interest rate predictions from Kalshi.

        Returns:
            Formatted Fed market data
        """
        markets = await self.get_kalshi_fed_markets(limit=10)
        return self._format_kalshi_markets(markets, "Federal Reserve Interest Rate Markets")

    async def get_economics_prediction_markets(self) -> str:
        """Get economics predictions (GDP, CPI) from Kalshi.

        Returns:
            Formatted economics market data
        """
        markets = await self.get_kalshi_economics_markets(limit=10)
        return self._format_kalshi_markets(markets, "Economics Markets (GDP, CPI)")

    async def compare_platforms(self, topic: str) -> str:
        """Compare prediction market data from both platforms.

        Args:
            topic: Topic to compare

        Returns:
            Side-by-side comparison
        """
        # Inject Kalshi data into conversation
        kalshi_markets = await self.search_kalshi(topic, limit=5)
        kalshi_context = self._format_kalshi_markets(kalshi_markets, "Kalshi Results")

        comparison_prompt = f"""Compare prediction markets for: {topic}

I have Kalshi data:
{kalshi_context}

Now search Polymarket for the same topic and provide a comparison:
1. Which markets exist on each platform
2. Price differences if same/similar markets exist
3. Volume comparison
4. Which platform has more relevant markets for this topic

Be concise and data-driven."""

        return await self.chat(comparison_prompt)

    async def analyze_token(self, token: str) -> str:
        """Perform comprehensive token analysis with multiple signals.

        Args:
            token: Token ticker (e.g., 'SOL', 'ETH') or address

        Returns:
            Structured analysis with price and social signals
        """
        analysis_prompt = f"""Perform a comprehensive analysis of {token}. Follow these steps:

1. First, get the current price using Birdeye or similar price tool
2. Then, check if it's trending among KOLs using Elfa getTrendingTokens
3. Get social metrics using TokenAnalysis if available
4. Search for recent news about {token}

Synthesize all signals into a structured analysis report with:
- Current price and 24h change
- Social signal summary (KOL mentions, sentiment)
- News summary
- Overall signal assessment (bullish/bearish/neutral signals)

Be thorough but concise. Present facts, not advice."""

        return await self.chat(analysis_prompt)

    async def get_trending_signals(self) -> str:
        """Get current trending tokens and social signals.

        Returns:
            Summary of trending tokens from KOL discussions
        """
        trending_prompt = """Get the current trending tokens from web3 KOLs on X/Twitter.

Use the Elfa getTrendingTokens tool to fetch tokens that are being discussed.

For the top 3-5 trending tokens, provide:
- Token symbol and name
- Number of mentions
- Overall sentiment
- Why it might be trending (if discernible)

Format as a clear, scannable list."""

        return await self.chat(trending_prompt)

    async def get_market_sentiment(self, topic: str) -> str:
        """Get market sentiment for a topic or event.

        Args:
            topic: Topic to analyze (e.g., 'Bitcoin ETF', 'Solana DeFi')

        Returns:
            Sentiment analysis from multiple sources
        """
        sentiment_prompt = f"""Analyze the current market sentiment around: {topic}

1. Search for recent news about this topic
2. Check social mentions and KOL discussions if applicable
3. Look for any related prediction market activity

Provide:
- Overall sentiment (bullish/bearish/neutral)
- Key drivers of sentiment
- Notable recent developments
- Confidence level in the assessment"""

        return await self.chat(sentiment_prompt)

    async def chat(self, user_message: str) -> str:
        """Process a user message with two-phase tool workflow."""
        # Add system prompt if this is the first message
        if not self.conversation_history:
            self.conversation_history.append({
                "role": "system",
                "content": SYSTEM_PROMPT,
            })

        self.conversation_history.append({
            "role": "user",
            "content": user_message,
        })

        available_tools = await self.get_tools()

        # Allow multiple rounds of tool calls
        max_iterations = 5
        for _ in range(max_iterations):
            response = await litellm.acompletion(
                model=self.model,
                messages=self.conversation_history,
                tools=available_tools if available_tools else None,
                temperature=1.0,  # Gemini 3 requires temp=1.0 to avoid looping
            )

            assistant_message = response.choices[0].message

            if not assistant_message.tool_calls:
                # No more tool calls, return final response
                # Use model_dump() to serialize, LiteLLM handles thought signatures in tool_call_id
                self.conversation_history.append(assistant_message.model_dump())
                return assistant_message.content or ""

            # Process tool calls - preserve thought signatures via full message serialization
            # LiteLLM stores thought signatures in tool_call.id as: call_xxx__thought__<signature>
            self.conversation_history.append(assistant_message.model_dump())

            tool_results = await self.execute_tool_calls(assistant_message.tool_calls)

            # Add tool results to conversation - use the exact tool_call.id which contains thought signature
            for tool_call, result in zip(assistant_message.tool_calls, tool_results):
                result_content = result if isinstance(result, str) else json.dumps(result)
                self.conversation_history.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,  # Contains thought signature if present
                    "content": result_content,
                })

        # Max iterations reached
        return "I've made several tool calls but couldn't complete the task. Please try a more specific query."

    def clear_history(self):
        """Clear conversation history for a new session."""
        self.conversation_history = []
        self.discovered_tools_cache = {}


async def run_trading_query(query: str) -> str:
    """Run a single trading query."""
    agent = TradingAgent()
    return await agent.chat(query)


async def run_demo():
    """Run demo with both Polymarket and Kalshi integration."""
    agent = TradingAgent()

    print("=" * 70)
    print("AI Trading Agent - Prediction Markets Demo")
    print("=" * 70)

    try:
        # Demo 1: Kalshi Fed Markets
        print("\n[1] Kalshi: Federal Reserve Interest Rate Markets")
        print("-" * 70)
        try:
            response = await agent.get_fed_prediction_markets()
            print(response)
        except Exception as e:
            print(f"Error: {e}")

        # Demo 2: Kalshi Economics Markets
        print("\n[2] Kalshi: Economics Markets (GDP, CPI)")
        print("-" * 70)
        try:
            response = await agent.get_economics_prediction_markets()
            print(response)
        except Exception as e:
            print(f"Error: {e}")

        # Demo 3: Polymarket Trending
        print("\n[3] Polymarket: Trending Events")
        print("-" * 70)
        try:
            response = await agent.chat(
                "Get the top 5 trending events on Polymarket with their prices and volumes"
            )
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        agent.clear_history()

        # Demo 4: Compare Bitcoin markets
        print("\n[4] Compare: Bitcoin Prediction Markets")
        print("-" * 70)
        try:
            response = await agent.compare_platforms("bitcoin price")
            print(response)
        except Exception as e:
            print(f"Error: {e}")
        agent.clear_history()

        # Demo 5: Combined crypto query
        print("\n[5] Combined Query: Crypto markets from both platforms")
        print("-" * 70)
        try:
            # Get Kalshi crypto if available
            kalshi_crypto = await agent.search_kalshi("crypto", limit=3)
            if kalshi_crypto:
                print("Kalshi Crypto Markets:")
                for m in kalshi_crypto:
                    print(f"  - {m.title[:50]}: YES ${m.yes_price:.2f}")
            else:
                print("Kalshi: No crypto markets found")

            print("\nPolymarket Crypto Markets:")
            response = await agent.chat(
                "Get the top 3 crypto prediction markets on Polymarket"
            )
            print(response)
        except Exception as e:
            print(f"Error: {e}")

    finally:
        await agent.close()


async def interactive_session():
    """Run an interactive trading session."""
    agent = TradingAgent()

    print("=" * 70)
    print("AI Trading Assistant - Polymarket & Kalshi")
    print("=" * 70)
    print("I help you analyze prediction markets using real-time data.")
    print("")
    print("Commands:")
    print("  'quit'     - Exit")
    print("  'clear'    - Reset conversation")
    print("  'fed'      - Show Fed interest rate markets (Kalshi)")
    print("  'gdp'      - Show GDP/economics markets (Kalshi)")
    print("  'compare X'- Compare topic X across platforms")
    print("-" * 70)

    try:
        while True:
            try:
                user_input = input("\nYou: ").strip()

                if not user_input:
                    continue
                if user_input.lower() in ("quit", "exit", "q"):
                    break
                if user_input.lower() == "clear":
                    agent.clear_history()
                    print("Conversation cleared.")
                    continue
                if user_input.lower() == "fed":
                    print("\nFetching Fed markets from Kalshi...")
                    response = await agent.get_fed_prediction_markets()
                    print(response)
                    continue
                if user_input.lower() in ("gdp", "economics", "econ"):
                    print("\nFetching economics markets from Kalshi...")
                    response = await agent.get_economics_prediction_markets()
                    print(response)
                    continue
                if user_input.lower().startswith("compare "):
                    topic = user_input[8:].strip()
                    print(f"\nComparing '{topic}' across platforms...")
                    response = await agent.compare_platforms(topic)
                    print(response)
                    continue

                print("\nAgent: ", end="", flush=True)
                response = await agent.chat(user_input)
                print(response)

            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"Error: {e}")

    finally:
        await agent.close()

    print("\nGoodbye!")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        asyncio.run(run_demo())
    else:
        asyncio.run(interactive_session())
