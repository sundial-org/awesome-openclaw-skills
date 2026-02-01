#!/usr/bin/env python3
"""
Candlestick Pattern Detector - Extracted from PatternRecognition

Detects candlestick patterns using price action analysis.
Single Responsibility: Detect candlestick patterns
"""

from typing import Dict, List
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class CandlestickPatternDetector:
    """
    Detects candlestick patterns

    Responsibilities:
    - Detect single-candle patterns (Doji, Hammer, Shooting Star)
    - Detect multi-candle patterns (Engulfing, etc.)
    - Calculate pattern confidence scores

    All patterns include:
    - Pattern type (REVERSAL/CONTINUATION)
    - Bias (BULLISH/BEARISH/NEUTRAL)
    - Confidence score (0-100)
    """

    def __init__(
        self,
        doji_threshold: float = 0.1,
        wick_body_ratio: float = 2.0
    ):
        """
        Initialize candlestick pattern detector

        Args:
            doji_threshold: Maximum body/range ratio for Doji (0.1 = 10%)
            wick_body_ratio: Minimum wick/body ratio for Hammer/Shooting Star
        """
        if not isinstance(doji_threshold, (int, float)) or not (0 < doji_threshold < 1):
            raise ValueError(f"doji_threshold must be between 0 and 1, got {doji_threshold}")

        if not isinstance(wick_body_ratio, (int, float)) or wick_body_ratio < 1:
            raise ValueError(f"wick_body_ratio must be >= 1, got {wick_body_ratio}")

        self.doji_threshold = doji_threshold
        self.wick_body_ratio = wick_body_ratio

        logger.info(
            f"Initialized CandlestickPatternDetector "
            f"(doji_threshold={doji_threshold}, wick_ratio={wick_body_ratio})"
        )

    def detect_all_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect all candlestick patterns in the given dataframe

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected patterns with metadata
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to detect_all_patterns")
            return []

        if len(df) < 3:
            logger.debug(f"Insufficient data for candlestick patterns: {len(df)} < 3")
            return []

        all_patterns = []

        try:
            # Single-candle patterns
            all_patterns.extend(self.detect_single_candle_patterns(df))

            # Multi-candle patterns
            all_patterns.extend(self.detect_engulfing_patterns(df))

            logger.info(f"Detected {len(all_patterns)} candlestick patterns")

        except Exception as e:
            logger.error(f"Error detecting candlestick patterns: {e}")
            return []

        return all_patterns

    def detect_single_candle_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect single-candle patterns (Doji, Hammer, Shooting Star)

        Doji: Small body with significant wicks - indicates indecision
        Hammer: Small body at top, long lower wick - bullish reversal
        Shooting Star: Small body at bottom, long upper wick - bearish reversal

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected single-candle patterns
        """
        patterns = []

        if len(df) < 1:
            return patterns

        try:
            # Analyze last 3 candles
            last_3 = df.tail(3)

            for idx, row in last_3.iterrows():
                # Calculate candle properties
                body = abs(row['close'] - row['open'])
                upper_wick = row['high'] - max(row['open'], row['close'])
                lower_wick = min(row['open'], row['close']) - row['low']
                total_range = row['high'] - row['low']

                # Protect against division by zero
                if total_range <= 0:
                    continue

                timestamp = row.get('timestamp', None)

                # Doji: Small body, significant wicks
                if body / total_range < self.doji_threshold:
                    patterns.append({
                        'pattern': 'Doji',
                        'type': 'REVERSAL',
                        'bias': 'NEUTRAL',
                        'confidence': 45,
                        'body_ratio': round(body / total_range, 3),
                        'description': 'Indecision - potential trend change',
                        'timestamp': timestamp
                    })

                    logger.debug(f"Doji detected: body_ratio={body/total_range:.3f}")

                # Hammer: Small body at top, long lower wick (bullish)
                if lower_wick > self.wick_body_ratio * body and upper_wick < body:
                    patterns.append({
                        'pattern': 'Hammer',
                        'type': 'REVERSAL',
                        'bias': 'BULLISH',
                        'confidence': 60,
                        'lower_wick_ratio': round(lower_wick / (body + 1e-10), 2),
                        'description': 'Rejection of lower prices - bullish reversal',
                        'timestamp': timestamp
                    })

                    logger.debug(f"Hammer detected: lower_wick_ratio={lower_wick/(body+1e-10):.2f}")

                # Shooting Star: Small body at bottom, long upper wick (bearish)
                if upper_wick > self.wick_body_ratio * body and lower_wick < body:
                    patterns.append({
                        'pattern': 'Shooting Star',
                        'type': 'REVERSAL',
                        'bias': 'BEARISH',
                        'confidence': 60,
                        'upper_wick_ratio': round(upper_wick / (body + 1e-10), 2),
                        'description': 'Rejection of higher prices - bearish reversal',
                        'timestamp': timestamp
                    })

                    logger.debug(f"Shooting Star detected: upper_wick_ratio={upper_wick/(body+1e-10):.2f}")

        except Exception as e:
            logger.error(f"Error detecting single-candle patterns: {e}")

        return patterns

    def detect_engulfing_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect engulfing patterns (2-candle reversal patterns)

        Bullish Engulfing: Bearish candle followed by larger bullish candle
        Bearish Engulfing: Bullish candle followed by larger bearish candle

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected engulfing patterns
        """
        patterns = []

        if len(df) < 2:
            return patterns

        try:
            # Get last 2 candles
            last_2 = df.tail(2)

            if len(last_2) < 2:
                return patterns

            prev = last_2.iloc[-2]
            curr = last_2.iloc[-1]

            # Calculate candle bodies
            prev_body = abs(prev['close'] - prev['open'])
            curr_body = abs(curr['close'] - curr['open'])

            # Get timestamp
            timestamp = curr.get('timestamp', None)

            # Bullish Engulfing
            if (prev['close'] < prev['open'] and      # Previous bearish
                curr['close'] > curr['open'] and      # Current bullish
                curr_body > prev_body):               # Current engulfs previous

                patterns.append({
                    'pattern': 'Bullish Engulfing',
                    'type': 'REVERSAL',
                    'bias': 'BULLISH',
                    'confidence': 70,
                    'prev_body': round(prev_body, 2),
                    'curr_body': round(curr_body, 2),
                    'engulfing_ratio': round(curr_body / (prev_body + 1e-10), 2),
                    'description': 'Strong bullish reversal signal',
                    'timestamp': timestamp
                })

                logger.debug(
                    f"Bullish Engulfing detected: ratio={curr_body/(prev_body+1e-10):.2f}"
                )

            # Bearish Engulfing
            if (prev['close'] > prev['open'] and      # Previous bullish
                curr['close'] < curr['open'] and      # Current bearish
                curr_body > prev_body):               # Current engulfs previous

                patterns.append({
                    'pattern': 'Bearish Engulfing',
                    'type': 'REVERSAL',
                    'bias': 'BEARISH',
                    'confidence': 70,
                    'prev_body': round(prev_body, 2),
                    'curr_body': round(curr_body, 2),
                    'engulfing_ratio': round(curr_body / (prev_body + 1e-10), 2),
                    'description': 'Strong bearish reversal signal',
                    'timestamp': timestamp
                })

                logger.debug(
                    f"Bearish Engulfing detected: ratio={curr_body/(prev_body+1e-10):.2f}"
                )

        except Exception as e:
            logger.error(f"Error detecting engulfing patterns: {e}")

        return patterns

    def calculate_pattern_strength(self, pattern: Dict, df: pd.DataFrame) -> float:
        """
        Calculate overall pattern strength based on volume and trend context

        Args:
            pattern: Pattern dictionary from detect methods
            df: DataFrame with OHLCV data

        Returns:
            Strength score (0.0 to 1.0)
        """
        try:
            if df is None or df.empty or len(df) < 5:
                return pattern.get('confidence', 50) / 100

            # Base confidence
            strength = pattern.get('confidence', 50) / 100

            # Volume confirmation: Higher volume increases strength
            last_volume = df['volume'].iloc[-1]
            avg_volume = df['volume'].tail(20).mean()

            if avg_volume > 0:
                volume_ratio = last_volume / avg_volume
                if volume_ratio > 1.5:
                    strength = min(1.0, strength + 0.1)  # +10% strength
                    logger.debug(f"Volume confirmation: ratio={volume_ratio:.2f}, strength+0.1")

            # Trend context: Pattern against trend is stronger
            recent_returns = df['close'].pct_change().tail(10).sum()

            if pattern.get('bias') == 'BULLISH' and recent_returns < -0.05:
                # Bullish pattern in downtrend (reversal)
                strength = min(1.0, strength + 0.05)
                logger.debug("Bullish reversal in downtrend, strength+0.05")
            elif pattern.get('bias') == 'BEARISH' and recent_returns > 0.05:
                # Bearish pattern in uptrend (reversal)
                strength = min(1.0, strength + 0.05)
                logger.debug("Bearish reversal in uptrend, strength+0.05")

            return round(strength, 3)

        except Exception as e:
            logger.error(f"Error calculating pattern strength: {e}")
            return pattern.get('confidence', 50) / 100
