#!/usr/bin/env python3
"""
Chart Pattern Detector - Extracted from PatternRecognition

Detects classic chart patterns using price action analysis.
Single Responsibility: Detect chart patterns (reversal & continuation)
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from scipy import signal
from scipy.stats import linregress
import logging

logger = logging.getLogger(__name__)


class ChartPatternDetector:
    """
    Detects chart patterns using technical analysis

    Responsibilities:
    - Detect double top/bottom patterns
    - Detect head and shoulders patterns
    - Detect wedge patterns (rising/falling)
    - Detect triangle patterns (ascending/descending/symmetrical)
    - Detect flag and pennant patterns

    All patterns include:
    - Pattern type (REVERSAL/CONTINUATION)
    - Bias (BULLISH/BEARISH/NEUTRAL)
    - Confirmation status
    - Confidence score (0-100)
    """

    def __init__(
        self,
        min_pattern_length: int = 20,
        similarity_threshold: float = 0.02
    ):
        """
        Initialize chart pattern detector

        Args:
            min_pattern_length: Minimum candles required for pattern detection
            similarity_threshold: Price similarity threshold for pattern matching (2% default)
        """
        if not isinstance(min_pattern_length, int) or min_pattern_length < 10:
            raise ValueError(f"min_pattern_length must be >= 10, got {min_pattern_length}")

        if not isinstance(similarity_threshold, (int, float)) or not (0 < similarity_threshold < 1):
            raise ValueError(f"similarity_threshold must be between 0 and 1, got {similarity_threshold}")

        self.min_pattern_length = min_pattern_length
        self.similarity_threshold = similarity_threshold

        logger.info(
            f"Initialized ChartPatternDetector "
            f"(min_length={min_pattern_length}, threshold={similarity_threshold})"
        )

    def detect_all_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect all chart patterns in the given dataframe

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected patterns with metadata
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to detect_all_patterns")
            return []

        if len(df) < self.min_pattern_length:
            logger.debug(f"Insufficient data: {len(df)} < {self.min_pattern_length}")
            return []

        all_patterns = []

        try:
            # Reversal patterns
            all_patterns.extend(self.detect_double_top_bottom(df))
            all_patterns.extend(self.detect_head_and_shoulders(df))
            all_patterns.extend(self.detect_wedges(df))

            # Continuation patterns
            all_patterns.extend(self.detect_flags_pennants(df))
            all_patterns.extend(self.detect_triangles(df))

            logger.info(f"Detected {len(all_patterns)} chart patterns")

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return []

        return all_patterns

    def detect_double_top_bottom(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect double top and double bottom reversal patterns

        Double Top: Two peaks at similar price levels with a trough between them.
        Signals potential bearish reversal when neckline (trough) is broken.

        Double Bottom: Two troughs at similar price levels with a peak between them.
        Signals potential bullish reversal when neckline (peak) is broken.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected double top/bottom patterns
        """
        patterns = []

        if len(df) < 30:
            return patterns

        try:
            # Find peaks and troughs using signal processing
            prices = df['close'].values
            peaks, _ = signal.find_peaks(prices, distance=5)
            troughs, _ = signal.find_peaks(-prices, distance=5)

            # Double Top detection
            if len(peaks) >= 2:
                for i in range(len(peaks) - 1):
                    peak1_idx = peaks[i]
                    peak2_idx = peaks[i + 1]

                    peak1_price = prices[peak1_idx]
                    peak2_price = prices[peak2_idx]

                    # Peaks should be similar (within threshold %)
                    # Protect against division by zero with price check
                    if peak1_price > 0 and abs(peak1_price - peak2_price) / peak1_price < self.similarity_threshold:
                        # Find trough between peaks
                        between_troughs = [t for t in troughs if peak1_idx < t < peak2_idx]

                        if between_troughs:
                            trough_price = prices[between_troughs[0]]
                            decline_pct = (peak1_price - trough_price) / peak1_price * 100

                            if decline_pct > 3:  # At least 3% decline between peaks
                                current_price = prices[-1]
                                neckline = trough_price

                                # Pattern is confirmed if price breaks neckline
                                confirmed = current_price < neckline

                                patterns.append({
                                    'pattern': 'Double Top',
                                    'type': 'REVERSAL',
                                    'bias': 'BEARISH',
                                    'confirmed': confirmed,
                                    'confidence': 75 if confirmed else 50,
                                    'peak_price': round(peak1_price, 2),
                                    'neckline': round(neckline, 2),
                                    'target': round(neckline - decline_pct / 100 * peak1_price, 2),
                                    'formed_at': df['timestamp'].iloc[peak2_idx]
                                })

                                logger.debug(
                                    f"Double Top detected: peaks={peak1_price:.2f}, "
                                    f"neckline={neckline:.2f}, confirmed={confirmed}"
                                )

            # Double Bottom detection
            if len(troughs) >= 2:
                for i in range(len(troughs) - 1):
                    trough1_idx = troughs[i]
                    trough2_idx = troughs[i + 1]

                    trough1_price = prices[trough1_idx]
                    trough2_price = prices[trough2_idx]

                    # Troughs should be similar (within threshold %)
                    # Protect against division by zero with price check
                    if trough1_price > 0 and abs(trough1_price - trough2_price) / trough1_price < self.similarity_threshold:
                        # Find peak between troughs
                        between_peaks = [p for p in peaks if trough1_idx < p < trough2_idx]

                        if between_peaks:
                            peak_price = prices[between_peaks[0]]
                            rise_pct = (peak_price - trough1_price) / trough1_price * 100

                            if rise_pct > 3:
                                current_price = prices[-1]
                                neckline = peak_price

                                # Pattern is confirmed if price breaks neckline
                                confirmed = current_price > neckline

                                patterns.append({
                                    'pattern': 'Double Bottom',
                                    'type': 'REVERSAL',
                                    'bias': 'BULLISH',
                                    'confirmed': confirmed,
                                    'confidence': 75 if confirmed else 50,
                                    'bottom_price': round(trough1_price, 2),
                                    'neckline': round(neckline, 2),
                                    'target': round(neckline + rise_pct / 100 * trough1_price, 2),
                                    'formed_at': df['timestamp'].iloc[trough2_idx]
                                })

                                logger.debug(
                                    f"Double Bottom detected: troughs={trough1_price:.2f}, "
                                    f"neckline={neckline:.2f}, confirmed={confirmed}"
                                )

        except Exception as e:
            logger.error(f"Error detecting double top/bottom: {e}")

        return patterns

    def detect_head_and_shoulders(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect head and shoulders reversal patterns

        Head and Shoulders: Three peaks where middle (head) is highest, outer two (shoulders)
        are approximately equal. Signals bearish reversal when neckline breaks.

        Inverse Head and Shoulders: Three troughs where middle is lowest. Signals bullish reversal.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected head and shoulders patterns
        """
        patterns = []

        if len(df) < 50:
            return patterns

        try:
            prices = df['close'].values
            peaks, _ = signal.find_peaks(prices, distance=10, prominence=prices.std())

            # Regular Head and Shoulders
            if len(peaks) >= 3:
                for i in range(len(peaks) - 2):
                    left_shoulder_idx = peaks[i]
                    head_idx = peaks[i + 1]
                    right_shoulder_idx = peaks[i + 2]

                    ls_price = prices[left_shoulder_idx]
                    head_price = prices[head_idx]
                    rs_price = prices[right_shoulder_idx]

                    # Head should be higher than shoulders
                    # Shoulders should be approximately equal (within threshold %)
                    # Protect against division by zero with price check
                    if (head_price > ls_price and head_price > rs_price and
                        ls_price > 0 and abs(ls_price - rs_price) / ls_price < 0.03):

                        # Calculate neckline (line connecting troughs between peaks)
                        neckline_price = min(
                            prices[left_shoulder_idx:head_idx].min(),
                            prices[head_idx:right_shoulder_idx].min()
                        )

                        current_price = prices[-1]
                        confirmed = current_price < neckline_price

                        head_to_neckline = head_price - neckline_price
                        target = neckline_price - head_to_neckline

                        patterns.append({
                            'pattern': 'Head and Shoulders',
                            'type': 'REVERSAL',
                            'bias': 'BEARISH',
                            'confirmed': confirmed,
                            'confidence': 80 if confirmed else 55,
                            'head_price': round(head_price, 2),
                            'left_shoulder': round(ls_price, 2),
                            'right_shoulder': round(rs_price, 2),
                            'neckline': round(neckline_price, 2),
                            'target': round(target, 2),
                            'formed_at': df['timestamp'].iloc[right_shoulder_idx]
                        })

                        logger.debug(
                            f"Head and Shoulders detected: head={head_price:.2f}, "
                            f"shoulders=[{ls_price:.2f}, {rs_price:.2f}], confirmed={confirmed}"
                        )

            # Inverse Head and Shoulders
            troughs, _ = signal.find_peaks(-prices, distance=10, prominence=prices.std())

            if len(troughs) >= 3:
                for i in range(len(troughs) - 2):
                    left_shoulder_idx = troughs[i]
                    head_idx = troughs[i + 1]
                    right_shoulder_idx = troughs[i + 2]

                    ls_price = prices[left_shoulder_idx]
                    head_price = prices[head_idx]
                    rs_price = prices[right_shoulder_idx]

                    # Protect against division by zero with price check
                    if (head_price < ls_price and head_price < rs_price and
                        ls_price > 0 and abs(ls_price - rs_price) / ls_price < 0.03):

                        neckline_price = max(
                            prices[left_shoulder_idx:head_idx].max(),
                            prices[head_idx:right_shoulder_idx].max()
                        )

                        current_price = prices[-1]
                        confirmed = current_price > neckline_price

                        neckline_to_head = neckline_price - head_price
                        target = neckline_price + neckline_to_head

                        patterns.append({
                            'pattern': 'Inverse Head and Shoulders',
                            'type': 'REVERSAL',
                            'bias': 'BULLISH',
                            'confirmed': confirmed,
                            'confidence': 80 if confirmed else 55,
                            'head_price': round(head_price, 2),
                            'left_shoulder': round(ls_price, 2),
                            'right_shoulder': round(rs_price, 2),
                            'neckline': round(neckline_price, 2),
                            'target': round(target, 2),
                            'formed_at': df['timestamp'].iloc[right_shoulder_idx]
                        })

                        logger.debug(
                            f"Inverse H&S detected: head={head_price:.2f}, "
                            f"shoulders=[{ls_price:.2f}, {rs_price:.2f}], confirmed={confirmed}"
                        )

        except Exception as e:
            logger.error(f"Error detecting head and shoulders: {e}")

        return patterns

    def detect_wedges(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect rising and falling wedge patterns

        Rising Wedge: Both trendlines rising but converging. Typically bearish reversal.
        Falling Wedge: Both trendlines falling but converging. Typically bullish reversal.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected wedge patterns
        """
        patterns = []

        if len(df) < 30:
            return patterns

        try:
            # Use last 30 candles for wedge detection
            recent_df = df.tail(30)

            # Fit trendlines to highs and lows
            highs = recent_df['high'].values
            lows = recent_df['low'].values
            x = np.arange(len(highs))

            # Upper trendline (highs)
            upper_slope, upper_intercept, _, _, _ = linregress(x, highs)

            # Lower trendline (lows)
            lower_slope, lower_intercept, _, _, _ = linregress(x, lows)

            # Rising Wedge: Both lines rising, but converging (bearish)
            if upper_slope > 0 and lower_slope > 0 and lower_slope > upper_slope:
                patterns.append({
                    'pattern': 'Rising Wedge',
                    'type': 'REVERSAL',
                    'bias': 'BEARISH',
                    'confirmed': False,
                    'confidence': 60,
                    'upper_slope': round(upper_slope, 4),
                    'lower_slope': round(lower_slope, 4),
                    'description': 'Prices rising but losing momentum - potential reversal down'
                })

                logger.debug(
                    f"Rising Wedge detected: upper_slope={upper_slope:.4f}, "
                    f"lower_slope={lower_slope:.4f}"
                )

            # Falling Wedge: Both lines falling, but converging (bullish)
            elif upper_slope < 0 and lower_slope < 0 and upper_slope < lower_slope:
                patterns.append({
                    'pattern': 'Falling Wedge',
                    'type': 'REVERSAL',
                    'bias': 'BULLISH',
                    'confirmed': False,
                    'confidence': 60,
                    'upper_slope': round(upper_slope, 4),
                    'lower_slope': round(lower_slope, 4),
                    'description': 'Prices falling but losing momentum - potential reversal up'
                })

                logger.debug(
                    f"Falling Wedge detected: upper_slope={upper_slope:.4f}, "
                    f"lower_slope={lower_slope:.4f}"
                )

        except Exception as e:
            logger.error(f"Error detecting wedges: {e}")

        return patterns

    def detect_flags_pennants(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect flag and pennant continuation patterns

        Flags and Pennants: Brief consolidation after strong trend, followed by continuation.
        Flag: Rectangular consolidation
        Pennant: Triangular consolidation

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected flag/pennant patterns
        """
        patterns = []

        if len(df) < 20:
            return patterns

        try:
            # Flags and pennants follow strong trends
            recent_returns = df['close'].pct_change().tail(20)

            # Look for strong move followed by consolidation
            first_half = recent_returns.head(10)
            second_half = recent_returns.tail(10)

            first_half_trend = first_half.sum()
            second_half_volatility = second_half.std()

            # Strong initial move (>5%)
            if abs(first_half_trend) > 0.05:
                # Followed by low volatility consolidation (<1%)
                if second_half_volatility < 0.01:
                    bias = 'BULLISH' if first_half_trend > 0 else 'BEARISH'
                    pattern_type = 'Flag' if second_half_volatility < 0.005 else 'Pennant'

                    patterns.append({
                        'pattern': pattern_type,
                        'type': 'CONTINUATION',
                        'bias': bias,
                        'confirmed': False,
                        'confidence': 65,
                        'initial_move_pct': round(first_half_trend * 100, 2),
                        'consolidation_volatility': round(second_half_volatility * 100, 2),
                        'description': f'Consolidation after strong move - expect {bias.lower()} continuation'
                    })

                    logger.debug(
                        f"{pattern_type} detected: bias={bias}, "
                        f"initial_move={first_half_trend*100:.2f}%"
                    )

        except Exception as e:
            logger.error(f"Error detecting flags/pennants: {e}")

        return patterns

    def detect_triangles(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect triangle patterns

        Ascending Triangle: Flat resistance, rising support. Typically bullish.
        Descending Triangle: Flat support, falling resistance. Typically bearish.
        Symmetrical Triangle: Both converging. Direction uncertain until breakout.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected triangle patterns
        """
        patterns = []

        if len(df) < 20:
            return patterns

        try:
            recent_df = df.tail(20)
            highs = recent_df['high'].values
            lows = recent_df['low'].values
            x = np.arange(len(highs))

            # Fit trendlines
            high_slope, _, _, _, _ = linregress(x, highs)
            low_slope, _, _, _, _ = linregress(x, lows)

            # Ascending Triangle: Flat resistance, rising support (bullish)
            if abs(high_slope) < 0.01 and low_slope > 0.01:
                patterns.append({
                    'pattern': 'Ascending Triangle',
                    'type': 'CONTINUATION',
                    'bias': 'BULLISH',
                    'confirmed': False,
                    'confidence': 70,
                    'high_slope': round(high_slope, 4),
                    'low_slope': round(low_slope, 4),
                    'description': 'Buyers pushing higher lows against resistance'
                })

                logger.debug(f"Ascending Triangle detected: low_slope={low_slope:.4f}")

            # Descending Triangle: Flat support, falling resistance (bearish)
            elif abs(low_slope) < 0.01 and high_slope < -0.01:
                patterns.append({
                    'pattern': 'Descending Triangle',
                    'type': 'CONTINUATION',
                    'bias': 'BEARISH',
                    'confirmed': False,
                    'confidence': 70,
                    'high_slope': round(high_slope, 4),
                    'low_slope': round(low_slope, 4),
                    'description': 'Sellers pushing lower highs against support'
                })

                logger.debug(f"Descending Triangle detected: high_slope={high_slope:.4f}")

            # Symmetrical Triangle: Both converging (direction uncertain)
            elif abs(high_slope + low_slope) < 0.01 and high_slope < 0 and low_slope > 0:
                patterns.append({
                    'pattern': 'Symmetrical Triangle',
                    'type': 'CONTINUATION',
                    'bias': 'NEUTRAL',
                    'confirmed': False,
                    'confidence': 55,
                    'high_slope': round(high_slope, 4),
                    'low_slope': round(low_slope, 4),
                    'description': 'Consolidation - breakout direction uncertain'
                })

                logger.debug(
                    f"Symmetrical Triangle detected: slopes=[{high_slope:.4f}, {low_slope:.4f}]"
                )

        except Exception as e:
            logger.error(f"Error detecting triangles: {e}")

        return patterns
