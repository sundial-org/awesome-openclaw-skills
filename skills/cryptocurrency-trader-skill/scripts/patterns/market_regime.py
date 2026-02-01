#!/usr/bin/env python3
"""
Market Regime Detector - Extracted from PatternRecognition

Detects market regime (trending vs ranging) and volatility conditions.
Single Responsibility: Detect market regime and volatility state
"""

from typing import Dict
import pandas as pd
import logging

logger = logging.getLogger(__name__)


class MarketRegimeDetector:
    """
    Detects current market regime and volatility conditions

    Responsibilities:
    - Detect market regime (trending vs ranging)
    - Detect volatility regime (high/normal/low)
    - Provide trading strategy recommendations
    - Calculate autocorrelation for regime classification

    Market regime detection helps traders choose appropriate strategies:
    - Trending markets: Use momentum/trend-following strategies
    - Ranging markets: Use mean-reversion strategies
    """

    def __init__(
        self,
        trending_threshold: float = 0.3,
        high_vol_threshold: float = 1.3,
        low_vol_threshold: float = 0.7,
        min_history_periods: int = 50
    ):
        """
        Initialize market regime detector

        Args:
            trending_threshold: Autocorrelation threshold for trending (default 0.3)
            high_vol_threshold: Volatility ratio for high vol regime (default 1.3x)
            low_vol_threshold: Volatility ratio for low vol regime (default 0.7x)
            min_history_periods: Minimum periods for historical volatility (default 50)
        """
        if not (0 < trending_threshold < 1):
            raise ValueError(
                f"trending_threshold must be between 0 and 1, got {trending_threshold}"
            )

        if not (0 < low_vol_threshold < high_vol_threshold):
            raise ValueError(
                f"Volatility thresholds must be 0 < low < high, got "
                f"{low_vol_threshold}, {high_vol_threshold}"
            )

        if min_history_periods < 10:
            raise ValueError(
                f"min_history_periods must be >= 10, got {min_history_periods}"
            )

        self.trending_threshold = trending_threshold
        self.high_vol_threshold = high_vol_threshold
        self.low_vol_threshold = low_vol_threshold
        self.min_history_periods = min_history_periods

        logger.info(
            f"Initialized MarketRegimeDetector (trending={trending_threshold}, "
            f"vol_thresholds=[{low_vol_threshold}, {high_vol_threshold}])"
        )

    def detect_regime(self, df: pd.DataFrame) -> Dict:
        """
        Detect current market regime (trending vs ranging)

        Uses autocorrelation to determine if market is trending or ranging:
        - High autocorrelation (>0.3): Market has momentum, use trend-following
        - Low autocorrelation (<0.3): Market is mean-reverting, use range strategies

        Also detects volatility regime (high/normal/low volatility).

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with regime information:
            - market_regime: 'TRENDING' or 'RANGING'
            - volatility_regime: 'HIGH_VOL', 'NORMAL_VOL', or 'LOW_VOL'
            - autocorrelation: Autocorrelation coefficient
            - current_volatility: Current volatility (%)
            - recommended_strategy: Strategy suggestion
        """
        if df is None or df.empty:
            logger.warning("Empty dataframe provided to detect_regime")
            return {'error': 'Empty dataframe'}

        if len(df) < 30:
            logger.debug(f"Insufficient data for regime detection: {len(df)} < 30")
            return {'error': 'Insufficient data for regime detection'}

        try:
            # Calculate returns
            returns = df['close'].pct_change().dropna()

            if len(returns) < 10:
                return {'error': 'Insufficient returns data'}

            # Calculate metrics
            volatility = returns.std()
            autocorrelation = returns.autocorr()

            # Handle NaN autocorrelation
            if pd.isna(autocorrelation):
                logger.warning("Autocorrelation is NaN, defaulting to 0")
                autocorrelation = 0.0

            # Market regime detection
            # High autocorrelation = trending (price movement persists)
            # Low autocorrelation = mean-reverting/ranging
            if abs(autocorrelation) > self.trending_threshold:
                regime = 'TRENDING'
                strategy = 'Use momentum/trend-following strategies'
            else:
                regime = 'RANGING'
                strategy = 'Use mean-reversion strategies'

            # Volatility regime detection
            vol_regime, vol_ratio = self._detect_volatility_regime(returns, volatility)

            result = {
                'market_regime': regime,
                'volatility_regime': vol_regime,
                'autocorrelation': round(autocorrelation, 3),
                'current_volatility': round(volatility * 100, 2),
                'volatility_ratio': round(vol_ratio, 2),
                'recommended_strategy': strategy
            }

            logger.info(
                f"Market regime: {regime}, Volatility: {vol_regime}, "
                f"Autocorr: {autocorrelation:.3f}"
            )

            return result

        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return {'error': str(e)}

    def _detect_volatility_regime(self, returns: pd.Series, current_vol: float) -> tuple:
        """
        Detect volatility regime (high/normal/low)

        Compares current volatility to historical average.

        Args:
            returns: Returns series
            current_vol: Current volatility

        Returns:
            Tuple of (volatility_regime, volatility_ratio)
        """
        try:
            # Calculate historical volatility if enough data
            if len(returns) >= self.min_history_periods:
                hist_vol = returns.rolling(self.min_history_periods).std().mean()
            else:
                hist_vol = current_vol

            # Protect against division by zero
            if hist_vol > 0:
                vol_ratio = current_vol / hist_vol
            else:
                logger.warning("Historical volatility is zero, defaulting ratio to 1.0")
                vol_ratio = 1.0

            # Classify volatility regime
            if vol_ratio > self.high_vol_threshold:
                vol_regime = 'HIGH_VOL'
            elif vol_ratio < self.low_vol_threshold:
                vol_regime = 'LOW_VOL'
            else:
                vol_regime = 'NORMAL_VOL'

            logger.debug(f"Volatility regime: {vol_regime}, ratio={vol_ratio:.2f}")

            return vol_regime, vol_ratio

        except Exception as e:
            logger.error(f"Error detecting volatility regime: {e}")
            return 'NORMAL_VOL', 1.0

    def calculate_regime_strength(self, df: pd.DataFrame) -> Dict:
        """
        Calculate the strength of the current market regime

        Stronger regimes are more reliable for strategy selection.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with regime strength metrics
        """
        if df is None or df.empty or len(df) < 30:
            logger.warning("Insufficient data for regime strength calculation")
            return {'strength': 0, 'confidence': 'LOW'}

        try:
            returns = df['close'].pct_change().dropna()

            if len(returns) < 10:
                return {'strength': 0, 'confidence': 'LOW'}

            # Calculate multiple autocorrelation lags
            autocorr_lag1 = returns.autocorr(lag=1)
            autocorr_lag2 = returns.autocorr(lag=2) if len(returns) > 2 else 0
            autocorr_lag5 = returns.autocorr(lag=5) if len(returns) > 5 else 0

            # Handle NaN values
            autocorr_lag1 = 0 if pd.isna(autocorr_lag1) else autocorr_lag1
            autocorr_lag2 = 0 if pd.isna(autocorr_lag2) else autocorr_lag2
            autocorr_lag5 = 0 if pd.isna(autocorr_lag5) else autocorr_lag5

            # Average absolute autocorrelation across lags
            avg_autocorr = (abs(autocorr_lag1) + abs(autocorr_lag2) + abs(autocorr_lag5)) / 3

            # Strength score (0-100)
            strength = min(100, int(avg_autocorr * 200))

            # Confidence level
            if strength > 60:
                confidence = 'HIGH'
            elif strength > 30:
                confidence = 'MEDIUM'
            else:
                confidence = 'LOW'

            result = {
                'strength': strength,
                'confidence': confidence,
                'autocorr_lag1': round(autocorr_lag1, 3),
                'autocorr_lag2': round(autocorr_lag2, 3),
                'autocorr_lag5': round(autocorr_lag5, 3),
                'avg_autocorr': round(avg_autocorr, 3)
            }

            logger.debug(f"Regime strength: {strength}, confidence: {confidence}")

            return result

        except Exception as e:
            logger.error(f"Error calculating regime strength: {e}")
            return {'strength': 0, 'confidence': 'LOW'}

    def detect_regime_change(self, df: pd.DataFrame, lookback: int = 20) -> Dict:
        """
        Detect if market regime has recently changed

        Compares current regime to recent past regime.

        Args:
            df: DataFrame with OHLCV data
            lookback: Periods to look back for comparison (default 20)

        Returns:
            Dictionary with regime change information
        """
        if df is None or df.empty or len(df) < lookback * 2:
            logger.warning("Insufficient data for regime change detection")
            return {'change_detected': False}

        try:
            # Current regime
            current_regime = self.detect_regime(df)

            if 'error' in current_regime:
                return {'change_detected': False}

            # Previous regime (using data up to lookback periods ago)
            df_past = df.iloc[:-lookback]
            previous_regime = self.detect_regime(df_past)

            if 'error' in previous_regime:
                return {'change_detected': False}

            # Detect changes
            market_changed = (
                current_regime['market_regime'] != previous_regime['market_regime']
            )
            volatility_changed = (
                current_regime['volatility_regime'] != previous_regime['volatility_regime']
            )

            change_detected = market_changed or volatility_changed

            result = {
                'change_detected': change_detected,
                'market_regime_changed': market_changed,
                'volatility_regime_changed': volatility_changed,
                'from_market_regime': previous_regime['market_regime'],
                'to_market_regime': current_regime['market_regime'],
                'from_volatility_regime': previous_regime['volatility_regime'],
                'to_volatility_regime': current_regime['volatility_regime']
            }

            if change_detected:
                logger.info(
                    f"Regime change detected: Market {previous_regime['market_regime']} → "
                    f"{current_regime['market_regime']}, "
                    f"Volatility {previous_regime['volatility_regime']} → "
                    f"{current_regime['volatility_regime']}"
                )

            return result

        except Exception as e:
            logger.error(f"Error detecting regime change: {e}")
            return {'change_detected': False}
