#!/usr/bin/env python3
"""
Volume Analyzer - Extracted from PatternRecognition

Analyzes volume patterns and trends using OBV and VPT indicators.
Single Responsibility: Analyze volume patterns and trends
"""

from typing import Dict
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)


class VolumeAnalyzer:
    """
    Analyzes volume patterns and trends

    Responsibilities:
    - Calculate volume metrics (average, ratio, status)
    - Calculate On-Balance Volume (OBV) trend
    - Calculate Volume Price Trend (VPT)
    - Detect volume surges and anomalies
    - Confirm price movements with volume

    Volume analysis is crucial for confirming price movements
    and detecting potential reversals.
    """

    def __init__(
        self,
        recent_period: int = 10,
        high_volume_threshold: float = 1.5,
        low_volume_threshold: float = 0.7
    ):
        """
        Initialize volume analyzer

        Args:
            recent_period: Period for recent volume comparison (default 10)
            high_volume_threshold: Threshold for high volume detection (default 1.5x)
            low_volume_threshold: Threshold for low volume detection (default 0.7x)
        """
        if recent_period < 5:
            raise ValueError(f"recent_period must be >= 5, got {recent_period}")

        if not (0 < low_volume_threshold < high_volume_threshold):
            raise ValueError(
                f"Thresholds must be 0 < low < high, got "
                f"{low_volume_threshold}, {high_volume_threshold}"
            )

        self.recent_period = recent_period
        self.high_volume_threshold = high_volume_threshold
        self.low_volume_threshold = low_volume_threshold

        logger.info(
            f"Initialized VolumeAnalyzer (recent={recent_period}, "
            f"thresholds=[{low_volume_threshold}, {high_volume_threshold}])"
        )

    def analyze_comprehensive(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive volume analysis

        Calculates volume metrics, OBV, VPT, and provides overall assessment.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with volume analysis:
            - current_volume: Current volume
            - avg_volume: Historical average volume
            - volume_ratio: Recent vs historical volume ratio
            - volume_status: HIGH/NORMAL/LOW
            - obv_trend: On-Balance Volume trend (INCREASING/DECREASING/UNKNOWN)
            - vpt_trend: Volume Price Trend (INCREASING/DECREASING/UNKNOWN)
            - confirmation: Boolean if OBV and VPT agree
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to analyze_comprehensive")
            return {'error': 'Empty dataframe'}

        if len(df) < 20:
            logger.debug(f"Insufficient data for volume analysis: {len(df)} < 20")
            return {'error': 'Insufficient data for volume analysis'}

        try:
            volume = df['volume']
            close = df['close']

            # Volume trend: Recent vs historical
            avg_volume_recent = volume.tail(self.recent_period).mean()
            avg_volume_historical = volume.mean()

            # Protect against division by zero
            if avg_volume_historical > 0:
                volume_ratio = avg_volume_recent / avg_volume_historical
            else:
                logger.warning("Historical volume is zero, defaulting ratio to 1.0")
                volume_ratio = 1.0

            # Determine volume status
            if volume_ratio > self.high_volume_threshold:
                volume_status = 'HIGH'
            elif volume_ratio > self.low_volume_threshold:
                volume_status = 'NORMAL'
            else:
                volume_status = 'LOW'

            # On-Balance Volume (OBV)
            obv_trend = self._calculate_obv_trend(volume, close)

            # Volume Price Trend (VPT)
            vpt_trend = self._calculate_vpt_trend(volume, close)

            # Check if OBV and VPT agree (confirmation)
            confirmation = obv_trend == vpt_trend and obv_trend != 'UNKNOWN'

            result = {
                'current_volume': round(volume.iloc[-1], 2),
                'avg_volume': round(avg_volume_historical, 2),
                'volume_ratio': round(volume_ratio, 2),
                'volume_status': volume_status,
                'obv_trend': obv_trend,
                'vpt_trend': vpt_trend,
                'confirmation': confirmation
            }

            logger.info(
                f"Volume analysis: status={volume_status}, ratio={volume_ratio:.2f}, "
                f"OBV={obv_trend}, VPT={vpt_trend}, confirmed={confirmation}"
            )

            return result

        except Exception as e:
            logger.error(f"Error in comprehensive volume analysis: {e}")
            return {'error': str(e)}

    def _calculate_obv_trend(self, volume: pd.Series, close: pd.Series) -> str:
        """
        Calculate On-Balance Volume trend

        OBV adds volume on up days and subtracts volume on down days.
        Rising OBV suggests accumulation, falling OBV suggests distribution.

        Args:
            volume: Volume series
            close: Close price series

        Returns:
            OBV trend: 'INCREASING', 'DECREASING', or 'UNKNOWN'
        """
        try:
            # Calculate OBV with NaN handling
            price_change = close.diff()
            direction = (price_change > 0).astype(int) * 2 - 1  # +1 for up, -1 for down
            obv = (volume * direction).fillna(0).cumsum()

            # Validate OBV values before comparison
            if len(obv) < self.recent_period:
                return 'UNKNOWN'

            obv_current = obv.iloc[-1]
            obv_past = obv.iloc[-self.recent_period]

            # Check for NaN values
            if pd.notna(obv_current) and pd.notna(obv_past):
                trend = 'INCREASING' if obv_current > obv_past else 'DECREASING'
                logger.debug(f"OBV trend: {trend} (current={obv_current:.2f}, past={obv_past:.2f})")
                return trend
            else:
                logger.warning("OBV contains NaN values")
                return 'UNKNOWN'

        except Exception as e:
            logger.error(f"Error calculating OBV trend: {e}")
            return 'UNKNOWN'

    def _calculate_vpt_trend(self, volume: pd.Series, close: pd.Series) -> str:
        """
        Calculate Volume Price Trend

        VPT combines price and volume to show the strength of price movements.
        Similar to OBV but weighted by percentage price change.

        Args:
            volume: Volume series
            close: Close price series

        Returns:
            VPT trend: 'INCREASING', 'DECREASING', or 'UNKNOWN'
        """
        try:
            # Calculate VPT with NaN handling
            price_pct_change = close.pct_change()
            vpt = (volume * price_pct_change).fillna(0).cumsum()

            # Validate VPT values before comparison
            if len(vpt) < self.recent_period:
                return 'UNKNOWN'

            vpt_current = vpt.iloc[-1]
            vpt_past = vpt.iloc[-self.recent_period]

            # Check for NaN values
            if pd.notna(vpt_current) and pd.notna(vpt_past):
                trend = 'INCREASING' if vpt_current > vpt_past else 'DECREASING'
                logger.debug(f"VPT trend: {trend} (current={vpt_current:.2f}, past={vpt_past:.2f})")
                return trend
            else:
                logger.warning("VPT contains NaN values")
                return 'UNKNOWN'

        except Exception as e:
            logger.error(f"Error calculating VPT trend: {e}")
            return 'UNKNOWN'

    def detect_volume_surge(self, df: pd.DataFrame, threshold: float = 2.0) -> Dict:
        """
        Detect volume surges (sudden high volume)

        Volume surges often precede significant price movements.

        Args:
            df: DataFrame with OHLCV data
            threshold: Multiple of average volume to consider a surge (default 2.0x)

        Returns:
            Dictionary with surge detection info
        """
        if df is None or df.empty or len(df) < 20:
            logger.warning("Insufficient data for volume surge detection")
            return {'surge_detected': False}

        try:
            volume = df['volume']
            avg_volume = volume.mean()

            current_volume = volume.iloc[-1]
            volume_ratio = current_volume / (avg_volume + 1e-10)

            surge_detected = volume_ratio > threshold

            result = {
                'surge_detected': surge_detected,
                'current_volume': round(current_volume, 2),
                'avg_volume': round(avg_volume, 2),
                'volume_ratio': round(volume_ratio, 2),
                'threshold': threshold
            }

            if surge_detected:
                logger.info(f"Volume surge detected: {volume_ratio:.2f}x average volume")

            return result

        except Exception as e:
            logger.error(f"Error detecting volume surge: {e}")
            return {'surge_detected': False}

    def calculate_volume_profile(self, df: pd.DataFrame, num_bins: int = 10) -> Dict:
        """
        Calculate volume profile (volume at different price levels)

        Volume profile shows where the most trading activity occurred.

        Args:
            df: DataFrame with OHLCV data
            num_bins: Number of price bins to create (default 10)

        Returns:
            Dictionary with volume profile data
        """
        if df is None or df.empty or len(df) < 10:
            logger.warning("Insufficient data for volume profile")
            return {'error': 'Insufficient data'}

        try:
            # Create price bins
            price_min = df['low'].min()
            price_max = df['high'].max()

            if price_min >= price_max:
                return {'error': 'Invalid price range'}

            bins = np.linspace(price_min, price_max, num_bins + 1)
            bin_labels = [(bins[i] + bins[i+1]) / 2 for i in range(num_bins)]

            # Assign each candle to a bin based on close price
            df_copy = df.copy()
            df_copy['price_bin'] = pd.cut(df_copy['close'], bins=bins, labels=bin_labels)

            # Sum volume for each bin
            volume_by_price = df_copy.groupby('price_bin', observed=True)['volume'].sum()

            # Find point of control (price with highest volume)
            poc_price = volume_by_price.idxmax()
            poc_volume = volume_by_price.max()

            result = {
                'point_of_control': round(float(poc_price), 2),
                'poc_volume': round(float(poc_volume), 2),
                'price_levels': [round(float(p), 2) for p in volume_by_price.index],
                'volumes': [round(float(v), 2) for v in volume_by_price.values]
            }

            logger.info(f"Volume profile: POC at {poc_price:.2f} with volume {poc_volume:.2f}")

            return result

        except Exception as e:
            logger.error(f"Error calculating volume profile: {e}")
            return {'error': str(e)}
