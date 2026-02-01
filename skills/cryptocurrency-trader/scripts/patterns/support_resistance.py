#!/usr/bin/env python3
"""
Support & Resistance Analyzer - Extracted from PatternRecognition

Detects key support and resistance levels using price clustering.
Single Responsibility: Detect and cluster support/resistance levels
"""

from typing import Dict, List
import pandas as pd
import numpy as np
from scipy import signal
import logging

logger = logging.getLogger(__name__)


class SupportResistanceAnalyzer:
    """
    Detects and analyzes support and resistance levels

    Responsibilities:
    - Detect support levels (troughs)
    - Detect resistance levels (peaks)
    - Cluster similar price levels
    - Calculate level strength

    Uses signal processing to find peaks/troughs and clustering
    to identify key price levels.
    """

    def __init__(
        self,
        clustering_threshold: float = 0.02,
        min_distance: int = 3,
        default_num_levels: int = 3
    ):
        """
        Initialize support & resistance analyzer

        Args:
            clustering_threshold: Price similarity threshold for clustering (2% default)
            min_distance: Minimum distance between peaks/troughs
            default_num_levels: Default number of levels to return
        """
        if not isinstance(clustering_threshold, (int, float)) or not (0 < clustering_threshold < 1):
            raise ValueError(
                f"clustering_threshold must be between 0 and 1, got {clustering_threshold}"
            )

        if not isinstance(min_distance, int) or min_distance < 1:
            raise ValueError(f"min_distance must be >= 1, got {min_distance}")

        if not isinstance(default_num_levels, int) or default_num_levels < 1:
            raise ValueError(f"default_num_levels must be >= 1, got {default_num_levels}")

        self.clustering_threshold = clustering_threshold
        self.min_distance = min_distance
        self.default_num_levels = default_num_levels

        logger.info(
            f"Initialized SupportResistanceAnalyzer "
            f"(threshold={clustering_threshold}, distance={min_distance}, "
            f"levels={default_num_levels})"
        )

    def detect_levels(
        self,
        df: pd.DataFrame,
        num_levels: int = None
    ) -> Dict[str, List[float]]:
        """
        Detect key support and resistance levels using clustering

        Uses signal processing to find peaks (resistance) and troughs (support),
        then clusters similar prices to identify key levels.

        Args:
            df: DataFrame with OHLCV data
            num_levels: Number of levels to return (None = use default)

        Returns:
            Dictionary with 'support' and 'resistance' lists
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to detect_levels")
            return {'support': [], 'resistance': []}

        if len(df) < 20:
            logger.debug(f"Insufficient data for S/R detection: {len(df)} < 20")
            return {'support': [], 'resistance': []}

        num_levels = num_levels or self.default_num_levels

        try:
            prices = df['close'].values
            highs = df['high'].values
            lows = df['low'].values

            # Find peaks and troughs using signal processing
            peaks, _ = signal.find_peaks(highs, distance=self.min_distance)
            troughs, _ = signal.find_peaks(-lows, distance=self.min_distance)

            # Extract resistance prices (peaks)
            resistance_prices = highs[peaks] if len(peaks) > 0 else np.array([])

            # Extract support prices (troughs)
            support_prices = lows[troughs] if len(troughs) > 0 else np.array([])

            # Cluster levels to find key support/resistance
            resistance_levels = self._cluster_levels(resistance_prices, num_levels)
            support_levels = self._cluster_levels(support_prices, num_levels)

            result = {
                'support': [round(level, 2) for level in support_levels],
                'resistance': [round(level, 2) for level in resistance_levels]
            }

            logger.info(
                f"Detected {len(result['support'])} support and "
                f"{len(result['resistance'])} resistance levels"
            )

            return result

        except Exception as e:
            logger.error(f"Error detecting support/resistance levels: {e}")
            return {'support': [], 'resistance': []}

    def _cluster_levels(self, prices: np.ndarray, num_levels: int) -> List[float]:
        """
        Cluster price levels to find key support/resistance

        Groups similar prices (within clustering_threshold %) into clusters
        and returns the most significant levels.

        Args:
            prices: Array of prices to cluster
            num_levels: Maximum number of levels to return

        Returns:
            List of clustered price levels (descending order)
        """
        if prices is None or len(prices) == 0:
            return []

        try:
            # Simple clustering: group prices within threshold % of each other
            clustered = []
            sorted_prices = sorted(prices, reverse=True)

            for price in sorted_prices:
                # Check if this price is similar to any existing cluster
                similar = False

                for cluster_price in clustered:
                    # Protect against division by zero with price check
                    if cluster_price > 0:
                        price_diff_pct = abs(price - cluster_price) / cluster_price

                        if price_diff_pct < self.clustering_threshold:
                            similar = True
                            break

                # If not similar to existing clusters, create new cluster
                if not similar:
                    clustered.append(price)

                # Stop once we have enough levels
                if len(clustered) >= num_levels:
                    break

            logger.debug(
                f"Clustered {len(prices)} prices into {len(clustered)} levels"
            )

            return clustered

        except Exception as e:
            logger.error(f"Error clustering levels: {e}")
            return []

    def calculate_level_strength(
        self,
        df: pd.DataFrame,
        level: float,
        level_type: str = 'resistance'
    ) -> Dict:
        """
        Calculate the strength of a support/resistance level

        Strength is determined by:
        - Number of times price tested the level
        - Volume at the level
        - How recently the level was tested

        Args:
            df: DataFrame with OHLCV data
            level: Price level to analyze
            level_type: 'support' or 'resistance'

        Returns:
            Dictionary with strength metrics
        """
        if df is None or df.empty or level <= 0:
            logger.warning("Invalid input to calculate_level_strength")
            return {'strength': 0, 'tests': 0, 'recent': False}

        try:
            tolerance = level * 0.02  # 2% tolerance around level

            # Find candles that tested the level
            if level_type == 'resistance':
                tests = df[df['high'] >= (level - tolerance)]
            else:  # support
                tests = df[df['low'] <= (level + tolerance)]

            num_tests = len(tests)

            # Check if level was tested recently (last 20% of data)
            recent_cutoff = len(df) - max(5, int(len(df) * 0.2))
            recent_tests = tests[tests.index >= df.index[recent_cutoff]]
            is_recent = len(recent_tests) > 0

            # Calculate average volume at level tests
            avg_volume = tests['volume'].mean() if num_tests > 0 else 0
            overall_avg_volume = df['volume'].mean()

            # Strength score (0-100)
            strength = min(100, (num_tests * 10) +
                          (20 if is_recent else 0) +
                          (10 if avg_volume > overall_avg_volume else 0))

            result = {
                'strength': int(strength),
                'tests': num_tests,
                'recent': is_recent,
                'avg_volume': round(avg_volume, 2),
                'volume_ratio': round(avg_volume / (overall_avg_volume + 1e-10), 2)
            }

            logger.debug(
                f"{level_type.capitalize()} at {level:.2f}: "
                f"strength={strength}, tests={num_tests}, recent={is_recent}"
            )

            return result

        except Exception as e:
            logger.error(f"Error calculating level strength: {e}")
            return {'strength': 0, 'tests': 0, 'recent': False}

    def find_nearest_levels(
        self,
        df: pd.DataFrame,
        current_price: float,
        num_levels: int = None
    ) -> Dict:
        """
        Find nearest support and resistance levels to current price

        Args:
            df: DataFrame with OHLCV data
            current_price: Current price
            num_levels: Number of levels to detect (None = use default)

        Returns:
            Dictionary with nearest support/resistance above and below current price
        """
        if current_price <= 0:
            raise ValueError(f"current_price must be positive, got {current_price}")

        levels = self.detect_levels(df, num_levels)

        try:
            # Find nearest resistance (above current price)
            resistance_above = [r for r in levels['resistance'] if r > current_price]
            nearest_resistance = min(resistance_above) if resistance_above else None

            # Find nearest support (below current price)
            support_below = [s for s in levels['support'] if s < current_price]
            nearest_support = max(support_below) if support_below else None

            result = {
                'current_price': round(current_price, 2),
                'nearest_resistance': round(nearest_resistance, 2) if nearest_resistance else None,
                'nearest_support': round(nearest_support, 2) if nearest_support else None,
                'resistance_distance_pct': round(
                    (nearest_resistance - current_price) / current_price * 100, 2
                ) if nearest_resistance else None,
                'support_distance_pct': round(
                    (current_price - nearest_support) / current_price * 100, 2
                ) if nearest_support else None
            }

            logger.info(
                f"Nearest levels for {current_price:.2f}: "
                f"support={nearest_support:.2f if nearest_support else None}, "
                f"resistance={nearest_resistance:.2f if nearest_resistance else None}"
            )

            return result

        except Exception as e:
            logger.error(f"Error finding nearest levels: {e}")
            return {
                'current_price': round(current_price, 2),
                'nearest_resistance': None,
                'nearest_support': None,
                'resistance_distance_pct': None,
                'support_distance_pct': None
            }
