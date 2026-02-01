#!/usr/bin/env python3
"""
Market Context Analyzer

Analyzes broader cryptocurrency market conditions to provide context
for individual trading decisions.

Component of Phase 3: Market Context (+0.5 reliability)
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class MarketContextAnalyzer:
    """
    Analyzes broader market context for cryptocurrency trading

    Responsibilities:
    - Calculate BTC dominance and trend
    - Estimate crypto market fear/greed (simplified version)
    - Assess overall market regime (bull/bear/ranging)
    - Detect market-wide volatility events
    - Provide context-based trading recommendations

    Design: Single Responsibility principle
    """

    def __init__(self, exchange_name: str = 'binance'):
        """
        Initialize market context analyzer

        Args:
            exchange_name: Name of exchange to use
        """
        self.exchange_name = exchange_name
        self.exchange = self._initialize_exchange()

        logger.info(f"Initialized MarketContextAnalyzer using {exchange_name}")

    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'},
                'timeout': 30000
            })
            exchange.load_markets()
            return exchange
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise

    def analyze_market_context(self) -> Dict:
        """
        Analyze complete market context

        Returns:
            Dictionary with market context analysis
        """
        logger.info("Analyzing cryptocurrency market context...")

        context = {
            'timestamp': datetime.now().isoformat(),
            'btc_analysis': self._analyze_btc(),
            'market_regime': None,
            'fear_greed_estimate': None,
            'volatility_level': None,
            'trading_recommendation': None,
            'confidence': 0.0
        }

        # Determine market regime
        context['market_regime'] = self._determine_market_regime(context['btc_analysis'])

        # Estimate fear/greed
        context['fear_greed_estimate'] = self._estimate_fear_greed(context['btc_analysis'])

        # Assess volatility
        context['volatility_level'] = self._assess_volatility(context['btc_analysis'])

        # Generate trading recommendation
        context['trading_recommendation'] = self._generate_trading_recommendation(context)

        # Calculate confidence
        context['confidence'] = self._calculate_context_confidence(context)

        logger.info(f"Market context: {context['market_regime']}, "
                   f"Fear/Greed: {context['fear_greed_estimate']}, "
                   f"Volatility: {context['volatility_level']}")

        return context

    def _analyze_btc(self) -> Dict:
        """
        Analyze Bitcoin market conditions

        Returns:
            Dictionary with BTC analysis
        """
        try:
            # Fetch BTC/USDT data for multiple timeframes
            btc_1h = self.exchange.fetch_ohlcv('BTC/USDT', '1h', limit=168)  # 1 week
            btc_4h = self.exchange.fetch_ohlcv('BTC/USDT', '4h', limit=180)  # 1 month
            btc_1d = self.exchange.fetch_ohlcv('BTC/USDT', '1d', limit=90)   # 3 months

            # Convert to DataFrames
            df_1h = pd.DataFrame(btc_1h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df_4h = pd.DataFrame(btc_4h, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df_1d = pd.DataFrame(btc_1d, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])

            current_price = df_1h['close'].iloc[-1]

            # Calculate price changes
            price_change_24h = ((df_1h['close'].iloc[-1] - df_1h['close'].iloc[-24]) /
                               df_1h['close'].iloc[-24]) * 100

            price_change_7d = ((df_1h['close'].iloc[-1] - df_1h['close'].iloc[-168]) /
                              df_1h['close'].iloc[-168]) * 100 if len(df_1h) >= 168 else 0

            price_change_30d = ((df_1d['close'].iloc[-1] - df_1d['close'].iloc[-30]) /
                               df_1d['close'].iloc[-30]) * 100 if len(df_1d) >= 30 else 0

            # Calculate moving averages
            ma_20 = df_1d['close'].rolling(20).mean().iloc[-1]
            ma_50 = df_1d['close'].rolling(50).mean().iloc[-1] if len(df_1d) >= 50 else ma_20

            # Calculate volatility (standard deviation of returns)
            returns_1h = df_1h['close'].pct_change().dropna()
            volatility_24h = returns_1h.tail(24).std() * 100

            returns_1d = df_1d['close'].pct_change().dropna()
            volatility_30d = returns_1d.tail(30).std() * 100

            # Volume analysis
            avg_volume_7d = df_1h['volume'].tail(168).mean()
            current_volume = df_1h['volume'].tail(24).mean()
            volume_ratio = current_volume / avg_volume_7d if avg_volume_7d > 0 else 1.0

            # Trend analysis
            trend_short = 'up' if current_price > ma_20 else 'down'
            trend_long = 'up' if ma_20 > ma_50 else 'down'
            trend_aligned = (trend_short == trend_long)

            return {
                'current_price': current_price,
                'price_change_24h': price_change_24h,
                'price_change_7d': price_change_7d,
                'price_change_30d': price_change_30d,
                'ma_20': ma_20,
                'ma_50': ma_50,
                'volatility_24h': volatility_24h,
                'volatility_30d': volatility_30d,
                'volume_ratio': volume_ratio,
                'trend_short': trend_short,
                'trend_long': trend_long,
                'trend_aligned': trend_aligned,
                'success': True
            }

        except Exception as e:
            logger.error(f"Failed to analyze BTC: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _determine_market_regime(self, btc_analysis: Dict) -> str:
        """
        Determine overall market regime

        Args:
            btc_analysis: BTC analysis results

        Returns:
            Market regime: 'bull', 'bear', 'ranging', or 'unknown'
        """
        if not btc_analysis.get('success'):
            return 'unknown'

        price_change_30d = btc_analysis.get('price_change_30d', 0)
        price_change_7d = btc_analysis.get('price_change_7d', 0)
        trend_aligned = btc_analysis.get('trend_aligned', False)
        current_price = btc_analysis.get('current_price', 0)
        ma_50 = btc_analysis.get('ma_50', 0)

        # Bull market conditions
        if (price_change_30d > 10 and price_change_7d > 3 and
            trend_aligned and btc_analysis.get('trend_short') == 'up'):
            return 'bull'

        # Bear market conditions
        if (price_change_30d < -10 and price_change_7d < -3 and
            trend_aligned and btc_analysis.get('trend_short') == 'down'):
            return 'bear'

        # Ranging market (low volatility, no clear trend)
        volatility_30d = btc_analysis.get('volatility_30d', 0)
        if abs(price_change_30d) < 5 and volatility_30d < 3:
            return 'ranging'

        # Default to ranging if unclear
        return 'ranging'

    def _estimate_fear_greed(self, btc_analysis: Dict) -> Dict:
        """
        Estimate fear/greed based on price action and volatility

        This is a simplified version. Real implementation would use
        Crypto Fear & Greed Index API.

        Args:
            btc_analysis: BTC analysis results

        Returns:
            Dictionary with fear/greed estimate
        """
        if not btc_analysis.get('success'):
            return {
                'score': 50,
                'sentiment': 'neutral',
                'confidence': 0.0
            }

        # Calculate score based on multiple factors (0-100)
        score = 50  # Start neutral

        # Price momentum (±20 points)
        price_change_7d = btc_analysis.get('price_change_7d', 0)
        if price_change_7d > 10:
            score += 20  # Extreme greed
        elif price_change_7d > 5:
            score += 10  # Greed
        elif price_change_7d < -10:
            score -= 20  # Extreme fear
        elif price_change_7d < -5:
            score -= 10  # Fear

        # Volatility (±15 points) - high volatility = fear
        volatility_24h = btc_analysis.get('volatility_24h', 0)
        if volatility_24h > 5:
            score -= 15  # High volatility = fear
        elif volatility_24h > 3:
            score -= 8
        elif volatility_24h < 1.5:
            score += 8  # Low volatility = complacency

        # Volume (±10 points)
        volume_ratio = btc_analysis.get('volume_ratio', 1.0)
        if volume_ratio > 1.5:
            score += 10  # High volume = interest/greed
        elif volume_ratio < 0.7:
            score -= 5   # Low volume = fear/disinterest

        # Trend alignment (±5 points)
        if btc_analysis.get('trend_aligned'):
            if btc_analysis.get('trend_short') == 'up':
                score += 5
            else:
                score -= 5

        # Clamp to 0-100
        score = max(0, min(100, score))

        # Determine sentiment
        if score >= 75:
            sentiment = 'extreme_greed'
        elif score >= 60:
            sentiment = 'greed'
        elif score >= 45:
            sentiment = 'neutral'
        elif score >= 30:
            sentiment = 'fear'
        else:
            sentiment = 'extreme_fear'

        return {
            'score': score,
            'sentiment': sentiment,
            'confidence': 0.7  # Medium confidence (simplified method)
        }

    def _assess_volatility(self, btc_analysis: Dict) -> str:
        """
        Assess market volatility level

        Args:
            btc_analysis: BTC analysis results

        Returns:
            Volatility level: 'low', 'normal', 'high', 'extreme'
        """
        if not btc_analysis.get('success'):
            return 'unknown'

        volatility_24h = btc_analysis.get('volatility_24h', 0)

        if volatility_24h < 1.5:
            return 'low'
        elif volatility_24h < 3.0:
            return 'normal'
        elif volatility_24h < 5.0:
            return 'high'
        else:
            return 'extreme'

    def _generate_trading_recommendation(self, context: Dict) -> Dict:
        """
        Generate trading recommendation based on market context

        Args:
            context: Market context dictionary

        Returns:
            Trading recommendation dictionary
        """
        market_regime = context.get('market_regime')
        fear_greed = context.get('fear_greed_estimate', {})
        volatility = context.get('volatility_level')

        recommendation = {
            'action': 'NEUTRAL',
            'reason': [],
            'adjustments': {}
        }

        # Regime-based recommendations
        if market_regime == 'bull':
            recommendation['action'] = 'FAVORABLE'
            recommendation['reason'].append("Bull market conditions")
            recommendation['adjustments']['confidence_boost'] = 0.10

        elif market_regime == 'bear':
            recommendation['action'] = 'CAUTION'
            recommendation['reason'].append("Bear market conditions")
            recommendation['adjustments']['confidence_penalty'] = -0.10

        elif market_regime == 'ranging':
            recommendation['action'] = 'SELECTIVE'
            recommendation['reason'].append("Ranging market - be selective")
            recommendation['adjustments']['confidence_penalty'] = -0.05

        # Fear/Greed adjustments
        sentiment = fear_greed.get('sentiment')
        if sentiment == 'extreme_fear':
            recommendation['reason'].append("Extreme fear - contrarian opportunity")
            recommendation['adjustments']['risk_adjustment'] = 0.5  # Reduce position size
        elif sentiment == 'extreme_greed':
            recommendation['reason'].append("Extreme greed - caution advised")
            recommendation['adjustments']['risk_adjustment'] = 0.7  # Reduce position size

        # Volatility adjustments
        if volatility == 'extreme':
            recommendation['reason'].append("Extreme volatility - reduce exposure")
            recommendation['adjustments']['risk_adjustment'] = 0.5
            if recommendation['action'] == 'FAVORABLE':
                recommendation['action'] = 'CAUTION'
        elif volatility == 'low':
            recommendation['reason'].append("Low volatility - normal trading")

        return recommendation

    def _calculate_context_confidence(self, context: Dict) -> float:
        """
        Calculate confidence in market context analysis

        Args:
            context: Market context dictionary

        Returns:
            Confidence score (0-1)
        """
        confidence = 0.5  # Base confidence

        # Boost for successful BTC analysis
        if context.get('btc_analysis', {}).get('success'):
            confidence += 0.3

        # Boost for clear market regime
        if context.get('market_regime') in ['bull', 'bear']:
            confidence += 0.1

        # Boost for aligned trends
        btc_analysis = context.get('btc_analysis', {})
        if btc_analysis.get('trend_aligned'):
            confidence += 0.1

        return min(1.0, confidence)

    def should_trade_altcoin(
        self,
        symbol: str,
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Determine if it's favorable to trade an altcoin based on market context

        Args:
            symbol: Altcoin trading pair
            context: Pre-analyzed market context (optional)

        Returns:
            Dictionary with recommendation
        """
        if context is None:
            context = self.analyze_market_context()

        btc_analysis = context.get('btc_analysis', {})
        market_regime = context.get('market_regime')
        volatility = context.get('volatility_level')

        # Don't trade altcoins during BTC crashes
        btc_change_24h = btc_analysis.get('price_change_24h', 0)
        if btc_change_24h < -5:
            return {
                'should_trade': False,
                'reason': f"BTC declining sharply ({btc_change_24h:.1f}% in 24h) - avoid altcoins",
                'confidence': 0.8
            }

        # Don't trade during extreme volatility
        if volatility == 'extreme':
            return {
                'should_trade': False,
                'reason': "Extreme market volatility - wait for stabilization",
                'confidence': 0.7
            }

        # Favorable conditions for altcoins
        if market_regime == 'bull' and btc_analysis.get('trend_aligned'):
            return {
                'should_trade': True,
                'reason': "Bull market with stable BTC - favorable for altcoins",
                'confidence': 0.9
            }

        # Neutral to favorable
        return {
            'should_trade': True,
            'reason': "Market conditions acceptable for altcoin trading",
            'confidence': 0.6
        }


# Convenience function
def analyze_market_context(exchange_name: str = 'binance') -> Dict:
    """
    Quick market context analysis

    Args:
        exchange_name: Exchange to use

    Returns:
        Market context dictionary
    """
    analyzer = MarketContextAnalyzer(exchange_name=exchange_name)
    return analyzer.analyze_market_context()
