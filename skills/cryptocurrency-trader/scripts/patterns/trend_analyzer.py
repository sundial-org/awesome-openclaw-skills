#!/usr/bin/env python3
"""
Trend Analyzer - Extracted from PatternRecognition

Analyzes price trends using linear regression and ADX-like measures.
Single Responsibility: Detect and analyze price trends
"""

from typing import Dict
import pandas as pd
import numpy as np
from scipy.stats import linregress
import logging

logger = logging.getLogger(__name__)


class TrendAnalyzer:
    """
    Analyzes price trends across multiple timeframes

    Responsibilities:
    - Calculate trend direction (uptrend/downtrend/sideways)
    - Calculate trend strength using ADX-like measure
    - Analyze multiple timeframes (short/medium/long-term)
    - Detect trend alignment across timeframes

    Uses linear regression for trend direction and simplified ADX
    for trend strength measurement.
    """

    def __init__(
        self,
        short_term_period: int = 10,
        medium_term_period: int = 20,
        strength_period: int = 14,
        strong_adx_threshold: float = 25.0,
        moderate_adx_threshold: float = 15.0
    ):
        """
        Initialize trend analyzer

        Args:
            short_term_period: Candles for short-term trend (default 10)
            medium_term_period: Candles for medium-term trend (default 20)
            strength_period: Period for ADX calculation (default 14)
            strong_adx_threshold: ADX threshold for strong trend (default 25)
            moderate_adx_threshold: ADX threshold for moderate trend (default 15)
        """
        if short_term_period < 5 or medium_term_period < 10 or strength_period < 5:
            raise ValueError(
                f"Periods must be >= 5, 10, 5 respectively, got "
                f"{short_term_period}, {medium_term_period}, {strength_period}"
            )

        if not (0 < moderate_adx_threshold < strong_adx_threshold < 100):
            raise ValueError(
                f"ADX thresholds must be 0 < moderate < strong < 100, got "
                f"{moderate_adx_threshold}, {strong_adx_threshold}"
            )

        self.short_term_period = short_term_period
        self.medium_term_period = medium_term_period
        self.strength_period = strength_period
        self.strong_adx_threshold = strong_adx_threshold
        self.moderate_adx_threshold = moderate_adx_threshold

        logger.info(
            f"Initialized TrendAnalyzer (short={short_term_period}, "
            f"medium={medium_term_period}, strength={strength_period})"
        )

    def analyze_comprehensive(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive trend analysis with multiple timeframes

        Analyzes trends across short, medium, and long timeframes,
        calculates trend strength, and detects alignment.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with trend analysis for all timeframes:
            - short_term: Short-term trend info
            - medium_term: Medium-term trend info
            - long_term: Long-term trend info
            - trend_strength: Overall trend strength (STRONG/MODERATE/WEAK)
            - aligned: Boolean if all trends aligned in same direction
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to analyze_comprehensive")
            return {'error': 'Empty dataframe'}

        if len(df) < 20:
            logger.debug(f"Insufficient data for trend analysis: {len(df)} < 20")
            return {'error': 'Insufficient data for trend analysis'}

        try:
            prices = df['close'].values

            # Short-term trend (last N candles)
            short_term = self._calculate_trend(prices[-self.short_term_period:])

            # Medium-term trend (last M candles)
            if len(prices) >= self.medium_term_period:
                medium_term = self._calculate_trend(prices[-self.medium_term_period:])
            else:
                medium_term = short_term

            # Long-term trend (all data)
            long_term = self._calculate_trend(prices)

            # Calculate trend strength using ADX-like measure
            trend_strength = self._calculate_trend_strength(df)

            # Check if all trends aligned in same direction
            aligned = (
                short_term['direction'] == medium_term['direction'] == long_term['direction']
            )

            result = {
                'short_term': short_term,
                'medium_term': medium_term,
                'long_term': long_term,
                'trend_strength': trend_strength,
                'aligned': aligned
            }

            logger.info(
                f"Trend analysis: short={short_term['direction']}, "
                f"medium={medium_term['direction']}, long={long_term['direction']}, "
                f"strength={trend_strength}, aligned={aligned}"
            )

            return result

        except Exception as e:
            logger.error(f"Error in comprehensive trend analysis: {e}")
            return {'error': str(e)}

    def _calculate_trend(self, prices: np.ndarray) -> Dict:
        """
        Calculate trend for price series using linear regression

        Args:
            prices: Array of prices

        Returns:
            Dictionary with trend direction, slope, strength, and R²
        """
        if prices is None or len(prices) < 2:
            return {
                'direction': 'INSUFFICIENT_DATA',
                'slope': 0.0,
                'strength': 0.0,
                'r_squared': 0.0
            }

        try:
            x = np.arange(len(prices))
            slope, intercept, r_value, _, _ = linregress(x, prices)

            # Determine direction based on slope
            if slope > 0.01:  # Small threshold to filter noise
                direction = 'UPTREND'
            elif slope < -0.01:
                direction = 'DOWNTREND'
            else:
                direction = 'SIDEWAYS'

            # R-squared indicates how well prices fit the trend line
            strength = abs(r_value) ** 2

            result = {
                'direction': direction,
                'slope': round(slope, 4),
                'strength': round(strength, 2),
                'r_squared': round(r_value ** 2, 2)
            }

            logger.debug(
                f"Trend calculated: {direction}, slope={slope:.4f}, R²={r_value**2:.2f}"
            )

            return result

        except Exception as e:
            logger.error(f"Error calculating trend: {e}")
            return {
                'direction': 'ERROR',
                'slope': 0.0,
                'strength': 0.0,
                'r_squared': 0.0
            }

    def _calculate_trend_strength(self, df: pd.DataFrame) -> str:
        """
        Calculate trend strength using simplified ADX (Average Directional Index)

        ADX measures trend strength regardless of direction:
        - ADX > 25: Strong trend
        - ADX 15-25: Moderate trend
        - ADX < 15: Weak trend or ranging

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Trend strength: 'STRONG', 'MODERATE', 'WEAK', or 'INSUFFICIENT_DATA'
        """
        if df is None or df.empty or len(df) < self.strength_period:
            return 'INSUFFICIENT_DATA'

        try:
            # Extract price data
            high = df['high']
            low = df['low']
            close = df['close']

            # Calculate True Range (TR)
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

            # Calculate Directional Movement (DM)
            plus_dm = (high - high.shift()).where(
                (high - high.shift()) > (low.shift() - low), 0
            )
            minus_dm = (low.shift() - low).where(
                (low.shift() - low) > (high - high.shift()), 0
            )

            # Smooth with rolling mean (similar to EMA)
            period = self.strength_period
            atr = tr.rolling(period).mean()
            plus_di = 100 * (plus_dm.rolling(period).mean() / atr)
            minus_di = 100 * (minus_dm.rolling(period).mean() / atr)

            # Calculate DX (Directional Index) with division by zero protection
            denominator = plus_di + minus_di
            dx = 100 * abs(plus_di - minus_di) / denominator.where(denominator > 0, 1e-10)

            # ADX is smoothed DX
            adx = dx.rolling(period).mean().iloc[-1]

            # Handle NaN or invalid ADX
            if pd.isna(adx) or not np.isfinite(adx):
                logger.warning("Invalid ADX calculated, returning INSUFFICIENT_DATA")
                return 'INSUFFICIENT_DATA'

            # Classify trend strength
            if adx > self.strong_adx_threshold:
                strength = 'STRONG'
            elif adx > self.moderate_adx_threshold:
                strength = 'MODERATE'
            else:
                strength = 'WEAK'

            logger.debug(f"ADX calculated: {adx:.2f}, strength={strength}")

            return strength

        except Exception as e:
            logger.error(f"Error calculating trend strength: {e}")
            return 'INSUFFICIENT_DATA'

    def detect_trend_change(self, df: pd.DataFrame, lookback: int = 5) -> Dict:
        """
        Detect potential trend changes

        Compares recent trend to slightly older trend to identify changes.

        Args:
            df: DataFrame with OHLCV data
            lookback: Candles to look back for comparison

        Returns:
            Dictionary with trend change information
        """
        if df is None or df.empty or len(df) < lookback * 2:
            logger.warning("Insufficient data for trend change detection")
            return {'change_detected': False, 'confidence': 0}

        try:
            prices = df['close'].values

            # Recent trend (last lookback candles)
            recent_trend = self._calculate_trend(prices[-lookback:])

            # Previous trend (lookback candles before recent)
            previous_trend = self._calculate_trend(prices[-lookback*2:-lookback])

            # Detect if direction changed
            change_detected = recent_trend['direction'] != previous_trend['direction']

            # Calculate confidence in change (based on R² values)
            if change_detected:
                confidence = min(100, int(
                    (recent_trend['r_squared'] + previous_trend['r_squared']) * 50
                ))
            else:
                confidence = 0

            result = {
                'change_detected': change_detected,
                'from_direction': previous_trend['direction'],
                'to_direction': recent_trend['direction'],
                'confidence': confidence,
                'recent_r_squared': recent_trend['r_squared'],
                'previous_r_squared': previous_trend['r_squared']
            }

            if change_detected:
                logger.info(
                    f"Trend change detected: {previous_trend['direction']} → "
                    f"{recent_trend['direction']}, confidence={confidence}%"
                )

            return result

        except Exception as e:
            logger.error(f"Error detecting trend change: {e}")
            return {'change_detected': False, 'confidence': 0}
