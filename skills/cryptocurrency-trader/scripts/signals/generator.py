#!/usr/bin/env python3
"""
Signal Generator - Extracted from EnhancedTradingAgent

Generates trading signals using Bayesian probability inference.
Single Responsibility: Generate probabilistic trading signals
"""

from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals using Bayesian inference

    Responsibilities:
    - Process indicator signals from multiple timeframes
    - Apply Bayesian probability calculations
    - Incorporate pattern analysis
    - Generate probabilistic signals (bullish/bearish)
    """

    def __init__(self, analytics=None, prior_accuracies: Dict = None):
        """
        Initialize signal generator

        Args:
            analytics: AdvancedAnalytics instance for Bayesian calculations
            prior_accuracies: Dict of historical accuracy rates for each indicator
        """
        self.analytics = analytics
        self.prior_accuracies = prior_accuracies or {
            'RSI': 0.65,
            'MACD': 0.68,
            'BB': 0.62,        # Bollinger Bands
            'Volume': 0.60,
            'Trend': 0.70,
            'Pattern': 0.72
        }
        logger.info("Initialized SignalGenerator")

    def generate_signals(
        self,
        timeframe_data: Dict,
        pattern_analysis: Dict
    ) -> Dict:
        """
        Generate trading signals using Bayesian probability

        Combines multiple indicators with their historical accuracy rates
        to produce probabilistic signals.

        Args:
            timeframe_data: Dict of {timeframe: indicator_data}
            pattern_analysis: Pattern analysis results with overall_bias

        Returns:
            Dict with bayesian probability results:
            - bullish_probability: Float probability of bullish signal
            - bearish_probability: Float probability of bearish signal
            - confidence: Overall confidence score
            - signal_strength: 'STRONG', 'MODERATE', 'WEAK'
        """
        try:
            indicator_signals = []

            # Process each timeframe
            for tf, data in timeframe_data.items():
                indicator_signals.extend(self._process_timeframe_indicators(data))

            # Add pattern analysis signals
            indicator_signals.extend(self._process_pattern_signals(pattern_analysis))

            # Calculate Bayesian probability
            if self.analytics:
                bayesian_result = self.analytics.bayesian_signal_probability(
                    indicator_signals=indicator_signals,
                    prior_accuracy=self.prior_accuracies
                )
                logger.info(f"Generated signals: bullish={bayesian_result.get('bullish_probability', 0):.1f}%")
                return bayesian_result
            else:
                logger.warning("No analytics engine available, returning default signals")
                return {
                    'bullish_probability': 50,
                    'bearish_probability': 50,
                    'confidence': 0,
                    'signal_strength': 'UNKNOWN'
                }

        except Exception as e:
            logger.error(f"Signal generation failed: {e}")
            return {
                'bullish_probability': 50,
                'bearish_probability': 50,
                'confidence': 0,
                'signal_strength': 'ERROR',
                'error': str(e)
            }

    def _process_timeframe_indicators(self, data: Dict) -> List[Tuple[str, bool]]:
        """
        Process indicators for a single timeframe

        Args:
            data: Indicator data for one timeframe

        Returns:
            List of (indicator_name, bullish_signal) tuples
        """
        signals = []

        # RSI signal
        rsi = data.get('rsi', 50)
        if rsi < 30:
            signals.append(('RSI', True))  # Bullish (oversold)
        elif rsi > 70:
            signals.append(('RSI', False))  # Bearish (overbought)

        # MACD signal
        macd = data.get('macd', 0)
        macd_signal = data.get('macd_signal', 0)
        if macd > macd_signal:
            signals.append(('MACD', True))  # Bullish
        else:
            signals.append(('MACD', False))  # Bearish

        # Bollinger Bands signal
        current_price = data.get('current_price', 0)
        bb_lower = data.get('bb_lower', 0)
        bb_upper = data.get('bb_upper', 0)

        if current_price and bb_lower and current_price < bb_lower:
            signals.append(('BB', True))  # Bullish (oversold)
        elif current_price and bb_upper and current_price > bb_upper:
            signals.append(('BB', False))  # Bearish (overbought)

        # EMA crossover signal
        ema_50 = data.get('ema_50')
        ema_200 = data.get('ema_200')
        if ema_50 is not None and ema_200 is not None:
            if ema_50 > ema_200:
                signals.append(('Trend', True))  # Bullish
            else:
                signals.append(('Trend', False))  # Bearish

        # Volume confirmation
        volume = data.get('volume', 0)
        avg_volume = data.get('avg_volume', 1)
        if volume > avg_volume:
            # High volume confirms current direction
            volume_signal = macd > macd_signal
            signals.append(('Volume', volume_signal))

        return signals

    def _process_pattern_signals(self, pattern_analysis: Dict) -> List[Tuple[str, bool]]:
        """
        Process pattern analysis signals

        Args:
            pattern_analysis: Pattern analysis results

        Returns:
            List of (indicator_name, bullish_signal) tuples
        """
        signals = []

        bias = pattern_analysis.get('overall_bias', 'NEUTRAL')
        if bias == 'BULLISH':
            signals.append(('Pattern', True))
        elif bias == 'BEARISH':
            signals.append(('Pattern', False))

        return signals

    def update_prior_accuracies(self, new_accuracies: Dict):
        """
        Update prior accuracy rates based on backtesting results

        Args:
            new_accuracies: Dict of {indicator_name: accuracy_rate}
        """
        self.prior_accuracies.update(new_accuracies)
        logger.info(f"Updated prior accuracies: {self.prior_accuracies}")

    def get_prior_accuracies(self) -> Dict:
        """
        Get current prior accuracy rates

        Returns:
            Dict of indicator accuracy rates
        """
        return self.prior_accuracies.copy()
