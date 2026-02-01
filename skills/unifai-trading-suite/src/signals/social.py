"""Social signal processing using UnifAI tools.

Available UnifAI tools for social signals:
- TokenAnalysis--25--analyzeToken: Token analysis with social metrics
- Twitter--68--searchTweets: Search tweets by query
- Twitter--68--getUserTimeline: Get user's tweet timeline
- Elfa--18--getTrendingTokens: Trending tokens by KOLs on X/Twitter
- Elfa--18--getEventSummary: Event summaries from keyword mentions
- SerpAPI--21--newsSearch: Google News search
"""

import asyncio
import json
import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

from dotenv import load_dotenv
import unifai
import litellm

load_dotenv()

DEFAULT_MODEL = os.getenv("LLM_MODEL", "gemini/gemini-3-flash-preview")


class SignalType(Enum):
    """Types of social signals."""
    SENTIMENT = "sentiment"
    TRENDING = "trending"
    NEWS = "news"
    KOL_MENTIONS = "kol_mentions"
    TWITTER_SEARCH = "twitter_search"


@dataclass
class SocialSignal:
    """Represents a processed social signal."""
    signal_type: SignalType
    source: str
    data: dict[str, Any]
    raw_response: Any = None

    @property
    def sentiment_score(self) -> float | None:
        """Extract sentiment score if available."""
        return self.data.get("sentiment_score")

    @property
    def mentions_count(self) -> int | None:
        """Extract mentions count if available."""
        return self.data.get("mentions_count")

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "signal_type": self.signal_type.value,
            "source": self.source,
            "data": self.data,
        }


class SocialSignalProcessor:
    """Process social signals from various sources via UnifAI."""

    TOOL_PROMPT = """You are a social signal extraction assistant. Your job is to:
1. Use the provided UnifAI tools to fetch social data
2. Extract and structure the relevant signals
3. Return the data in a clean JSON format

Always respond with valid JSON containing the extracted data."""

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key or os.getenv("UNIFAI_AGENT_API_KEY")
        if not self.api_key:
            raise ValueError("UNIFAI_AGENT_API_KEY is required")

        self.model = model or DEFAULT_MODEL
        self.tools = unifai.Tools(api_key=self.api_key)

    async def _execute_with_tools(self, prompt: str) -> dict[str, Any]:
        """Execute a prompt with UnifAI tools and return structured data."""
        available_tools = await self.tools.get_tools(dynamic_tools=True)

        messages = [
            {"role": "system", "content": self.TOOL_PROMPT},
            {"role": "user", "content": prompt},
        ]

        # Allow multiple tool call rounds
        for _ in range(3):
            response = await litellm.acompletion(
                model=self.model,
                messages=messages,
                tools=available_tools if available_tools else None,
                temperature=1.0,  # Gemini 3 requires temp=1.0 to avoid looping
            )

            message = response.choices[0].message

            if not message.tool_calls:
                # Try to parse JSON from response
                content = message.content or ""
                try:
                    # Extract JSON from response
                    if "```json" in content:
                        json_str = content.split("```json")[1].split("```")[0]
                        return json.loads(json_str)
                    elif "{" in content:
                        start = content.index("{")
                        end = content.rindex("}") + 1
                        return json.loads(content[start:end])
                except (json.JSONDecodeError, ValueError):
                    pass
                return {"raw_response": content}

            # Execute tool calls
            messages.append(message.model_dump())
            results = await self.tools.call_tools(message.tool_calls)

            for tool_call, result in zip(message.tool_calls, results):
                result_content = result if isinstance(result, str) else json.dumps(result)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": result_content,
                })

        return {"error": "Max iterations reached"}

    async def get_token_sentiment(self, token: str) -> SocialSignal:
        """Get social sentiment analysis for a token.

        Args:
            token: Token ticker (e.g., 'BTC', 'ETH') or contract address

        Returns:
            SocialSignal with sentiment data
        """
        prompt = f"""Use the TokenAnalysis tool to analyze the token: {token}

Extract and return JSON with:
- sentiment_score: overall sentiment (-1 to 1 scale, or null if unavailable)
- sentiment_label: bullish/bearish/neutral
- social_volume: number of social mentions
- social_dominance: percentage of social volume vs total market
- social_contributors: number of unique contributors
- trending_rank: if available
- key_topics: list of main discussion topics"""

        result = await self._execute_with_tools(prompt)
        return SocialSignal(
            signal_type=SignalType.SENTIMENT,
            source="TokenAnalysis",
            data=result,
            raw_response=result,
        )

    async def get_trending_tokens(
        self,
        time_window: str = "24h",
        min_mentions: int = 5,
    ) -> SocialSignal:
        """Get trending tokens from KOL discussions on X/Twitter.

        Args:
            time_window: Time window for trending (e.g., '1h', '24h', '7d')
            min_mentions: Minimum mentions to be considered trending

        Returns:
            SocialSignal with trending tokens data
        """
        prompt = f"""Use the Elfa getTrendingTokens tool to get tokens trending among web3 KOLs.
Time window: {time_window}
Minimum mentions: {min_mentions}

Return JSON with:
- tokens: list of objects containing:
  - symbol: token symbol
  - name: token name (if available)
  - mentions: number of mentions
  - sentiment: overall sentiment if available
  - change_24h: mention change vs previous period"""

        result = await self._execute_with_tools(prompt)
        return SocialSignal(
            signal_type=SignalType.TRENDING,
            source="Elfa",
            data=result,
            raw_response=result,
        )

    async def search_twitter(
        self,
        query: str,
        search_type: str = "Top",
        limit: int = 10,
    ) -> SocialSignal:
        """Search Twitter/X for relevant discussions.

        Args:
            query: Search query (e.g., '$BTC prediction market')
            search_type: 'Top' or 'Latest'
            limit: Number of results to return

        Returns:
            SocialSignal with tweet data
        """
        prompt = f"""Use the Twitter searchTweets tool to search for: {query}
Search type: {search_type}

Return JSON with:
- tweets: list of up to {limit} tweets containing:
  - text: tweet content
  - author: username
  - engagement: likes + retweets + replies
  - timestamp: when posted
- total_results: total number of results found
- overall_sentiment: quick assessment of sentiment (bullish/bearish/neutral)"""

        result = await self._execute_with_tools(prompt)
        return SocialSignal(
            signal_type=SignalType.TWITTER_SEARCH,
            source="Twitter",
            data=result,
            raw_response=result,
        )

    async def get_crypto_news(self, query: str, limit: int = 5) -> SocialSignal:
        """Get recent crypto news for a topic.

        Args:
            query: News search query
            limit: Number of articles to return

        Returns:
            SocialSignal with news data
        """
        prompt = f"""Use the SerpAPI newsSearch tool to search for crypto news: {query}

Return JSON with:
- articles: list of up to {limit} articles containing:
  - title: article headline
  - source: news source name
  - url: article URL
  - snippet: brief description
  - published: publication date
- news_sentiment: overall sentiment from headlines (bullish/bearish/neutral)"""

        result = await self._execute_with_tools(prompt)
        return SocialSignal(
            signal_type=SignalType.NEWS,
            source="SerpAPI",
            data=result,
            raw_response=result,
        )

    async def get_event_summary(
        self,
        keyword: str,
        time_window: str = "24h",
    ) -> SocialSignal:
        """Get event summary for a keyword from social mentions.

        Args:
            keyword: Keyword to track (e.g., 'Polymarket', 'Bitcoin ETF')
            time_window: Time window for summary

        Returns:
            SocialSignal with event summary
        """
        prompt = f"""Use the Elfa getEventSummary tool to get a summary of events around: {keyword}
Time window: {time_window}

Return JSON with:
- summary: brief summary of key events/discussions
- key_events: list of notable events or developments
- sentiment_trend: how sentiment has changed
- volume_trend: how discussion volume has changed
- key_influencers: notable accounts discussing this topic"""

        result = await self._execute_with_tools(prompt)
        return SocialSignal(
            signal_type=SignalType.KOL_MENTIONS,
            source="Elfa",
            data=result,
            raw_response=result,
        )

    async def get_aggregated_signals(self, token: str) -> dict[str, SocialSignal]:
        """Get all available social signals for a token.

        Args:
            token: Token ticker or address

        Returns:
            Dictionary of signal types to SocialSignal objects
        """
        # Run all signal fetches concurrently
        results = await asyncio.gather(
            self.get_token_sentiment(token),
            self.search_twitter(f"${token} crypto", limit=5),
            self.get_crypto_news(f"{token} cryptocurrency", limit=3),
            return_exceptions=True,
        )

        signals = {}
        signal_types = [SignalType.SENTIMENT, SignalType.TWITTER_SEARCH, SignalType.NEWS]

        for signal_type, result in zip(signal_types, results):
            if isinstance(result, Exception):
                signals[signal_type.value] = SocialSignal(
                    signal_type=signal_type,
                    source="error",
                    data={"error": str(result)},
                )
            else:
                signals[signal_type.value] = result

        return signals


async def demo():
    """Demo the social signal processor."""
    processor = SocialSignalProcessor()

    print("=" * 70)
    print("Social Signal Processor Demo")
    print("=" * 70)

    # Test trending tokens
    print("\n1. Getting trending tokens from KOLs...")
    trending = await processor.get_trending_tokens(time_window="24h")
    print(f"   Source: {trending.source}")
    print(f"   Data: {json.dumps(trending.data, indent=2)[:500]}...")

    # Test token sentiment
    print("\n2. Getting sentiment for SOL...")
    sentiment = await processor.get_token_sentiment("SOL")
    print(f"   Source: {sentiment.source}")
    print(f"   Data: {json.dumps(sentiment.data, indent=2)[:500]}...")

    # Test Twitter search
    print("\n3. Searching Twitter for prediction market discussions...")
    tweets = await processor.search_twitter("prediction market crypto", limit=3)
    print(f"   Source: {tweets.source}")
    print(f"   Data: {json.dumps(tweets.data, indent=2)[:500]}...")


if __name__ == "__main__":
    asyncio.run(demo())
