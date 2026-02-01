#!/usr/bin/env python3
"""
Adaptive Parameter Selector

Dynamically selects optimal analysis parameters (timeframes, indicator settings)
based on current market conditions.

Component of Phase 4: Optimization (+0.2 reliability)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class AdaptiveParameterSelector:
    """
    Selects optimal parameters based on market conditions

    Responsibilities:
    - Analyze current market regime (trending vs ranging)
    - Select optimal timeframes for analysis
    - Adjust indicator parameters for market conditions
    - Recommend analysis window sizes
    - Adapt to volatility levels

    Design: Single Responsibility, Strategy pattern
    """

    # Default timeframe sets for different regimes
    TIMEFRAME_SETS = {
        'high_volatility': ['5m', '15m', '1h'],
        'normal': ['15m', '1h', '4h'],
        'low_volatility': ['1h', '4h', '1d'],
        'strong_trend': ['1h', '4h', '1d'],
        'ranging': ['15m', '30m', '1h']
    }

    def __init__(self):
        """Initialize adaptive parameter selector"""
        logger.info("Initialized AdaptiveParameterSelector")

    def select_timeframes(
        self,
        symbol: str,
        market_data: pd.DataFrame,
        volatility: Optional[float] = None
    ) -> Dict:
        """
        Select optimal timeframes based on market conditions

        Args:
            symbol: Trading pair
            market_data: Recent market data for analysis
            volatility: Optional pre-calculated volatility

        Returns:
            Dictionary with selected timeframes and reasoning
        """
        logger.info(f"Selecting optimal timeframes for {symbol}")

        # Analyze market conditions
        conditions = self._analyze_market_conditions(market_data, volatility)

        # Select timeframes based on conditions
        timeframes = self._select_timeframes_from_conditions(conditions)

        return {
            'symbol': symbol,
            'selected_timeframes': timeframes,
            'market_conditions': conditions,
            'reasoning': self._generate_reasoning(conditions, timeframes)
        }

    def _analyze_market_conditions(
        self,
        data: pd.DataFrame,
        volatility: Optional[float] = None
    ) -> Dict:
        """
        Analyze current market conditions

        Args:
            data: Market data DataFrame
            volatility: Optional pre-calculated volatility

        Returns:
            Market conditions dictionary
        """
        conditions = {}

        # Calculate volatility if not provided
        if volatility is None:
            returns = data['close'].pct_change().dropna()
            volatility = returns.std() * np.sqrt(24) * 100  # Annualized for hourly data

        conditions['volatility'] = volatility

        # Classify volatility
        if volatility > 5.0:
            conditions['volatility_regime'] = 'high'
        elif volatility > 2.5:
            conditions['volatility_regime'] = 'normal'
        else:
            conditions['volatility_regime'] = 'low'

        # Detect trend strength
        trend_strength = self._calculate_trend_strength(data)
        conditions['trend_strength'] = trend_strength

        if trend_strength > 0.7:
            conditions['trend_regime'] = 'strong_trend'
        elif trend_strength > 0.4:
            conditions['trend_regime'] = 'moderate_trend'
        else:
            conditions['trend_regime'] = 'ranging'

        # Calculate market efficiency (how predictable)
        efficiency = self._calculate_market_efficiency(data)
        conditions['efficiency'] = efficiency

        # Overall regime
        conditions['overall_regime'] = self._determine_overall_regime(conditions)

        return conditions

    def _calculate_trend_strength(self, data: pd.DataFrame) -> float:
        """
        Calculate trend strength using ADX-like calculation

        Args:
            data: Market data

        Returns:
            Trend strength (0-1)
        """
        try:
            # Simple trend strength: correlation between price and time
            prices = data['close'].values
            time_index = np.arange(len(prices))

            if len(prices) < 2:
                return 0.0

            # Calculate correlation coefficient
            correlation = np.corrcoef(time_index, prices)[0, 1]

            # Convert to 0-1 scale (abs because we want strength not direction)
            trend_strength = abs(correlation)

            return min(1.0, max(0.0, trend_strength))

        except Exception as e:
            logger.warning(f"Failed to calculate trend strength: {e}")
            return 0.5

    def _calculate_market_efficiency(self, data: pd.DataFrame) -> float:
        """
        Calculate market efficiency ratio

        Args:
            data: Market data

        Returns:
            Efficiency ratio (0-1)
        """
        try:
            # Efficiency = (Net price change) / (Sum of absolute changes)
            prices = data['close'].values

            if len(prices) < 2:
                return 0.0

            net_change = abs(prices[-1] - prices[0])
            sum_changes = sum(abs(prices[i] - prices[i-1]) for i in range(1, len(prices)))

            if sum_changes == 0:
                return 0.0

            efficiency = net_change / sum_changes

            return min(1.0, efficiency)

        except Exception as e:
            logger.warning(f"Failed to calculate efficiency: {e}")
            return 0.5

    def _determine_overall_regime(self, conditions: Dict) -> str:
        """
        Determine overall market regime

        Args:
            conditions: Market conditions dictionary

        Returns:
            Overall regime string
        """
        volatility_regime = conditions.get('volatility_regime', 'normal')
        trend_regime = conditions.get('trend_regime', 'ranging')

        # High volatility overrides
        if volatility_regime == 'high':
            return 'high_volatility'

        # Strong trend
        if trend_regime == 'strong_trend':
            return 'strong_trend'

        # Ranging market
        if trend_regime == 'ranging':
            return 'ranging'

        # Low volatility
        if volatility_regime == 'low':
            return 'low_volatility'

        # Default
        return 'normal'

    def _select_timeframes_from_conditions(self, conditions: Dict) -> List[str]:
        """
        Select timeframes based on market conditions

        Args:
            conditions: Market conditions

        Returns:
            List of selected timeframes
        """
        regime = conditions.get('overall_regime', 'normal')

        # Get default timeframes for regime
        timeframes = self.TIMEFRAME_SETS.get(regime, self.TIMEFRAME_SETS['normal'])

        return list(timeframes)

    def _generate_reasoning(
        self,
        conditions: Dict,
        timeframes: List[str]
    ) -> str:
        """
        Generate reasoning for timeframe selection

        Args:
            conditions: Market conditions
            timeframes: Selected timeframes

        Returns:
            Reasoning string
        """
        regime = conditions.get('overall_regime', 'normal')
        volatility = conditions.get('volatility', 0)
        trend_strength = conditions.get('trend_strength', 0)

        reasoning_parts = []

        # Volatility reasoning
        vol_regime = conditions.get('volatility_regime')
        if vol_regime == 'high':
            reasoning_parts.append(
                f"High volatility ({volatility:.1f}%) detected - using shorter timeframes "
                "for faster reaction to price changes"
            )
        elif vol_regime == 'low':
            reasoning_parts.append(
                f"Low volatility ({volatility:.1f}%) detected - using longer timeframes "
                "to capture meaningful moves"
            )

        # Trend reasoning
        if trend_strength > 0.7:
            reasoning_parts.append(
                f"Strong trend detected (strength: {trend_strength:.2f}) - "
                "using longer timeframes to ride the trend"
            )
        elif trend_strength < 0.3:
            reasoning_parts.append(
                f"Ranging market detected (trend: {trend_strength:.2f}) - "
                "using shorter timeframes for quick entries/exits"
            )

        # Overall
        reasoning_parts.append(f"Selected timeframes: {', '.join(timeframes)}")

        return ' | '.join(reasoning_parts)

    def adjust_indicator_parameters(
        self,
        indicator_name: str,
        market_conditions: Dict
    ) -> Dict:
        """
        Adjust indicator parameters based on market conditions

        Args:
            indicator_name: Name of indicator
            market_conditions: Current market conditions

        Returns:
            Adjusted parameters dictionary
        """
        volatility_regime = market_conditions.get('volatility_regime', 'normal')
        trend_regime = market_conditions.get('trend_regime', 'ranging')

        # Default parameters
        params = self._get_default_parameters(indicator_name)

        # Adjust based on volatility
        if volatility_regime == 'high':
            params = self._adjust_for_high_volatility(indicator_name, params)
        elif volatility_regime == 'low':
            params = self._adjust_for_low_volatility(indicator_name, params)

        # Adjust based on trend
        if trend_regime == 'strong_trend':
            params = self._adjust_for_trending(indicator_name, params)
        elif trend_regime == 'ranging':
            params = self._adjust_for_ranging(indicator_name, params)

        return params

    def _get_default_parameters(self, indicator_name: str) -> Dict:
        """Get default parameters for indicator"""
        defaults = {
            'RSI': {'period': 14, 'overbought': 70, 'oversold': 30},
            'MACD': {'fast': 12, 'slow': 26, 'signal': 9},
            'Bollinger': {'period': 20, 'std': 2},
            'EMA': {'short': 9, 'medium': 21, 'long': 50},
            'ATR': {'period': 14},
            'Stochastic': {'period': 14, 'smooth_k': 3, 'smooth_d': 3}
        }

        return defaults.get(indicator_name, {})

    def _adjust_for_high_volatility(self, indicator: str, params: Dict) -> Dict:
        """Adjust parameters for high volatility"""
        adjusted = params.copy()

        if indicator == 'RSI':
            # Widen overbought/oversold bands
            adjusted['overbought'] = 75
            adjusted['oversold'] = 25

        elif indicator == 'Bollinger':
            # Widen bands
            adjusted['std'] = 2.5

        elif indicator == 'ATR':
            # Shorter period for faster response
            adjusted['period'] = 10

        return adjusted

    def _adjust_for_low_volatility(self, indicator: str, params: Dict) -> Dict:
        """Adjust parameters for low volatility"""
        adjusted = params.copy()

        if indicator == 'RSI':
            # Tighten overbought/oversold bands
            adjusted['overbought'] = 65
            adjusted['oversold'] = 35

        elif indicator == 'Bollinger':
            # Narrow bands
            adjusted['std'] = 1.5

        elif indicator == 'ATR':
            # Longer period
            adjusted['period'] = 20

        return adjusted

    def _adjust_for_trending(self, indicator: str, params: Dict) -> Dict:
        """Adjust parameters for trending markets"""
        adjusted = params.copy()

        if indicator == 'MACD':
            # Longer periods to avoid whipsaws
            adjusted['fast'] = 16
            adjusted['slow'] = 32

        elif indicator == 'EMA':
            # Favor longer EMAs
            adjusted['short'] = 12
            adjusted['medium'] = 26
            adjusted['long'] = 50

        return adjusted

    def _adjust_for_ranging(self, indicator: str, params: Dict) -> Dict:
        """Adjust parameters for ranging markets"""
        adjusted = params.copy()

        if indicator == 'MACD':
            # Shorter periods for faster signals
            adjusted['fast'] = 8
            adjusted['slow'] = 20

        elif indicator == 'EMA':
            # Favor shorter EMAs
            adjusted['short'] = 5
            adjusted['medium'] = 13
            adjusted['long'] = 21

        return adjusted

    def recommend_analysis_window(
        self,
        market_conditions: Dict
    ) -> Dict:
        """
        Recommend optimal analysis window size

        Args:
            market_conditions: Current market conditions

        Returns:
            Recommended window sizes
        """
        volatility_regime = market_conditions.get('volatility_regime', 'normal')
        trend_regime = market_conditions.get('trend_regime', 'ranging')

        windows = {
            'short': 24,    # For immediate signals
            'medium': 100,  # For pattern recognition
            'long': 200     # For trend analysis
        }

        # Adjust based on volatility
        if volatility_regime == 'high':
            windows['short'] = 12
            windows['medium'] = 50
            windows['long'] = 100
        elif volatility_regime == 'low':
            windows['short'] = 48
            windows['medium'] = 150
            windows['long'] = 300

        # Adjust based on trend
        if trend_regime == 'strong_trend':
            # Need more data to confirm trend
            windows['long'] = max(windows['long'], 250)

        return {
            'recommended_windows': windows,
            'reasoning': f"Adjusted for {volatility_regime} volatility and {trend_regime} market"
        }


# Convenience functions
def select_optimal_timeframes(
    symbol: str,
    market_data: pd.DataFrame
) -> List[str]:
    """
    Quick timeframe selection

    Args:
        symbol: Trading pair
        market_data: Recent market data

    Returns:
        List of optimal timeframes
    """
    selector = AdaptiveParameterSelector()
    result = selector.select_timeframes(symbol, market_data)
    return result['selected_timeframes']


def get_adaptive_parameters(
    indicator_name: str,
    market_data: pd.DataFrame
) -> Dict:
    """
    Get adaptive parameters for an indicator

    Args:
        indicator_name: Name of indicator
        market_data: Recent market data

    Returns:
        Adjusted parameters dictionary
    """
    selector = AdaptiveParameterSelector()
    conditions = selector._analyze_market_conditions(market_data)
    return selector.adjust_indicator_parameters(indicator_name, conditions)
