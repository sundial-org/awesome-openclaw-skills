#!/usr/bin/env python3
"""
Market Scanner - Extracted from EnhancedTradingAgent

Scans multiple symbols to find best trading opportunities.
Single Responsibility: Scan market for trading opportunities
"""

from typing import Dict, List, Optional
from datetime import datetime
import time
import logging

logger = logging.getLogger(__name__)


class MarketScanner:
    """
    Scans market for trading opportunities

    Responsibilities:
    - Scan multiple symbols across categories
    - Analyze each symbol for trading opportunities
    - Calculate expected value (EV) scores
    - Rank opportunities by EV
    - Display scan results
    """

    def __init__(
        self,
        trading_agent,
        categories: Dict[str, List[str]] = None,
        rate_limit_delay: float = 0.5
    ):
        """
        Initialize market scanner

        Args:
            trading_agent: Trading agent instance for comprehensive_analysis
            categories: Dict of {category_name: [symbols]}
            rate_limit_delay: Delay between symbol scans (seconds)
        """
        self.trading_agent = trading_agent
        self.categories = categories or {
            'Major Coins': ['BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT'],
            'AI Tokens': ['RENDER/USDT', 'FET/USDT', 'AGIX/USDT', 'OCEAN/USDT', 'TAO/USDT'],
            'Layer 1': ['ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'ATOM/USDT'],
            'Layer 2': ['MATIC/USDT', 'ARB/USDT', 'OP/USDT'],
            'DeFi': ['UNI/USDT', 'AAVE/USDT', 'LINK/USDT', 'MKR/USDT'],
            'Meme': ['DOGE/USDT', 'SHIB/USDT', 'PEPE/USDT']
        }
        self.rate_limit_delay = rate_limit_delay
        logger.info(f"Initialized MarketScanner with {len(self.categories)} categories")

    def scan_market(
        self,
        categories: Optional[List[str]] = None,
        timeframes: List[str] = None,
        top_n: int = 5
    ) -> List[Dict]:
        """
        Scan market for best trading opportunities

        Analyzes multiple symbols and ranks them by expected value (EV).
        EV = (confidence/100) * risk_reward * (monte_carlo_profit_prob/100)

        Args:
            categories: List of category names to scan (None = all)
            timeframes: List of timeframes to analyze (default: ['1h', '4h'])
            top_n: Number of top opportunities to return

        Returns:
            List of top opportunities sorted by EV score, each containing:
            - symbol: Trading pair
            - category: Market category
            - ev_score: Expected value score
            - final_recommendation: Trading recommendation
            - execution_ready: Boolean if ready for execution
        """
        timeframes = timeframes or ['1h', '4h']

        logger.info(f"Starting market scan across {len(self.categories)} categories")
        print(f"\n{'='*80}")
        print(f"🔬 MARKET SCANNER - Finding Top {top_n} Opportunities")
        print(f"{'='*80}")

        all_opportunities = []
        scan_start_time = datetime.now()

        # Scan each category
        for category, symbols in self.categories.items():
            if categories and category not in categories:
                continue

            print(f"\n📊 Scanning {category}...")
            logger.info(f"Scanning category: {category}")

            # Analyze each symbol in category
            for symbol in symbols:
                try:
                    print(f"   Analyzing {symbol}...", end=" ")

                    # Get comprehensive analysis from trading agent
                    analysis = self.trading_agent.comprehensive_analysis(
                        symbol,
                        timeframes=timeframes
                    )

                    # If execution ready, calculate EV and add to opportunities
                    if analysis.get('execution_ready', False):
                        ev_score = self._calculate_ev_score(analysis)
                        analysis['ev_score'] = ev_score
                        analysis['category'] = category
                        all_opportunities.append(analysis)

                        print(f"✅ EV: {ev_score:.3f}")
                        logger.info(f"{symbol} passed - EV: {ev_score:.3f}")
                    else:
                        print(f"❌ Failed validation")

                    # Rate limiting
                    time.sleep(self.rate_limit_delay)

                except Exception as e:
                    error_msg = str(e)[:50]
                    print(f"⚠️  Error: {error_msg}")
                    logger.error(f"Failed {symbol}: {str(e)}")

        # Sort by EV score and take top N
        all_opportunities.sort(key=lambda x: x['ev_score'], reverse=True)
        top_opportunities = all_opportunities[:top_n]

        scan_duration = (datetime.now() - scan_start_time).total_seconds()

        print(f"\n{'='*80}")
        print(f"📊 SCAN COMPLETE - {len(all_opportunities)} opportunities in {scan_duration:.1f}s")
        print(f"{'='*80}")
        logger.info(f"Scan complete: {len(all_opportunities)} found, top {top_n} returned")

        return top_opportunities

    def _calculate_ev_score(self, analysis: Dict) -> float:
        """
        Calculate expected value score for an opportunity

        EV = (confidence/100) * risk_reward * (monte_carlo_profit_prob/100)

        Args:
            analysis: Comprehensive analysis result

        Returns:
            Expected value score (0.0 to ~3.0 typically)
        """
        rec = analysis.get('final_recommendation', {})

        confidence = rec.get('confidence', 0) / 100
        risk_reward = rec.get('risk_reward', 0)
        mc_prob = rec.get('monte_carlo_profit_prob', 50) / 100

        ev_score = confidence * risk_reward * mc_prob
        return round(ev_score, 3)

    def display_scan_results(self, opportunities: List[Dict]):
        """
        Display market scan results in formatted table

        Args:
            opportunities: List of opportunity dicts from scan_market()
        """
        if not opportunities:
            print("\n⚠️  No execution-ready opportunities found.")
            return

        print(f"\n{'='*80}")
        print(f"🏆 TOP TRADING OPPORTUNITIES (Ranked by EV)")
        print(f"{'='*80}\n")

        for i, analysis in enumerate(opportunities, 1):
            rec = analysis['final_recommendation']

            print(f"#{i}. {analysis['symbol']} ({analysis['category']})")
            print(f"   ⭐ EV: {analysis['ev_score']:.3f} | "
                  f"Action: {rec['action']} | "
                  f"Conf: {rec['confidence']}%")
            print(f"   💰 Entry: ${rec['entry_price']} | "
                  f"Stop: ${rec['stop_loss']} | "
                  f"Target: ${rec['take_profit']}")
            print()

    def get_category_symbols(self, category: str) -> List[str]:
        """
        Get symbols for a specific category

        Args:
            category: Category name

        Returns:
            List of symbols in category or empty list
        """
        return self.categories.get(category, [])

    def get_all_categories(self) -> List[str]:
        """
        Get list of all category names

        Returns:
            List of category names
        """
        return list(self.categories.keys())

    def add_category(self, name: str, symbols: List[str]):
        """
        Add a new category to scanner

        Args:
            name: Category name
            symbols: List of symbols
        """
        self.categories[name] = symbols
        logger.info(f"Added category '{name}' with {len(symbols)} symbols")

    def remove_category(self, name: str) -> bool:
        """
        Remove a category from scanner

        Args:
            name: Category name

        Returns:
            True if removed, False if not found
        """
        if name in self.categories:
            del self.categories[name]
            logger.info(f"Removed category '{name}'")
            return True
        return False
