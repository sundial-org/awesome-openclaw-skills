#!/usr/bin/env python3
"""
Indicator Calculator - Extracted from EnhancedTradingAgent

Calculates technical analysis indicators with validation.
Single Responsibility: Calculate and validate technical indicators
"""

import pandas as pd
import numpy as np
from typing import Dict
import logging

logger = logging.getLogger(__name__)


class IndicatorCalculator:
    """
    Calculates technical analysis indicators

    Responsibilities:
    - Calculate RSI, MACD, Bollinger Bands, ATR, EMA, Stochastic
    - Validate calculated indicators
    - Handle edge cases (division by zero, insufficient data)
    """

    def __init__(self, validator=None):
        """
        Initialize indicator calculator

        Args:
            validator: AdvancedValidator instance for indicator validation
        """
        self.validator = validator
        logger.info("Initialized IndicatorCalculator")

    def calculate_all(self, df: pd.DataFrame) -> Dict:
        """
        Calculate all technical indicators with validation

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary of calculated indicators or error dict
        """
        try:
            indicators = {}

            # Calculate each indicator
            indicators.update(self._calculate_rsi(df))
            indicators.update(self._calculate_macd(df))
            indicators.update(self._calculate_atr(df))
            indicators.update(self._calculate_bollinger_bands(df))
            indicators.update(self._calculate_ema(df))
            indicators.update(self._calculate_stochastic(df))
            indicators.update(self._calculate_price_volume(df))

            # Validate indicators if validator is available
            if self.validator:
                validation_report = self.validator.validate_indicators(indicators, df)

                if not validation_report['passed']:
                    logger.error("Indicator validation failed")
                    logger.error(f"Issues: {', '.join(validation_report['critical_failures'])}")
                    print(f"\n❌ INDICATOR VALIDATION FAILURE")
                    print(f"   Issues: {', '.join(validation_report['critical_failures'])}")
                    return {'error': 'Indicator validation failed'}

                if validation_report.get('warnings'):
                    for warning in validation_report['warnings']:
                        logger.warning(f"Indicator warning: {warning}")

            logger.info("Successfully calculated all indicators")
            return indicators

        except Exception as e:
            error_msg = f'Indicator calculation failed: {str(e)}'
            logger.error(error_msg)
            return {'error': error_msg}

    def _calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """
        Calculate Relative Strength Index

        Args:
            df: DataFrame with close prices
            period: RSI period (default: 14)

        Returns:
            Dictionary with 'rsi' key
        """
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        # Protect against division by zero
        rs = gain / loss.replace(0, 1e-10)
        rsi = 100 - (100 / (1 + rs))

        return {'rsi': rsi.iloc[-1]}

    def _calculate_macd(self, df: pd.DataFrame) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        Args:
            df: DataFrame with close prices

        Returns:
            Dictionary with macd, macd_signal, macd_histogram keys
        """
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        macd = exp1 - exp2
        signal = macd.ewm(span=9, adjust=False).mean()
        histogram = macd - signal

        return {
            'macd': macd.iloc[-1],
            'macd_signal': signal.iloc[-1],
            'macd_histogram': histogram.iloc[-1]
        }

    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """
        Calculate Average True Range

        Args:
            df: DataFrame with OHLC data
            period: ATR period (default: 14)

        Returns:
            Dictionary with 'atr' key
        """
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())

        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = np.max(ranges, axis=1)
        atr = true_range.rolling(period).mean()

        return {'atr': atr.iloc[-1]}

    def _calculate_bollinger_bands(self, df: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        """
        Calculate Bollinger Bands

        Args:
            df: DataFrame with close prices
            period: Moving average period (default: 20)
            std_dev: Standard deviation multiplier (default: 2)

        Returns:
            Dictionary with bb_upper, bb_middle, bb_lower keys
        """
        sma = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        bb_upper = sma + (std * std_dev)
        bb_lower = sma - (std * std_dev)

        return {
            'bb_upper': bb_upper.iloc[-1],
            'bb_middle': sma.iloc[-1],
            'bb_lower': bb_lower.iloc[-1]
        }

    def _calculate_ema(self, df: pd.DataFrame) -> Dict:
        """
        Calculate Exponential Moving Averages

        Args:
            df: DataFrame with close prices

        Returns:
            Dictionary with ema_50 and ema_200 keys
        """
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        ema_200 = df['close'].ewm(span=200, adjust=False).mean()

        return {
            'ema_50': ema_50.iloc[-1],
            'ema_200': ema_200.iloc[-1]
        }

    def _calculate_stochastic(self, df: pd.DataFrame, period: int = 14) -> Dict:
        """
        Calculate Stochastic Oscillator

        Args:
            df: DataFrame with OHLC data
            period: Stochastic period (default: 14)

        Returns:
            Dictionary with stoch_k and stoch_d keys
        """
        low_n = df['low'].rolling(period).min()
        high_n = df['high'].rolling(period).max()

        # Protect against division by zero when market is flat
        range_n = (high_n - low_n).replace(0, 1e-10)
        stoch_k = 100 * ((df['close'] - low_n) / range_n)
        stoch_d = stoch_k.rolling(3).mean()

        return {
            'stoch_k': stoch_k.iloc[-1],
            'stoch_d': stoch_d.iloc[-1]
        }

    def _calculate_price_volume(self, df: pd.DataFrame) -> Dict:
        """
        Calculate price and volume metrics

        Args:
            df: DataFrame with close and volume data

        Returns:
            Dictionary with current_price, volume, avg_volume keys
        """
        return {
            'current_price': df['close'].iloc[-1],
            'volume': df['volume'].iloc[-1],
            'avg_volume': df['volume'].mean()
        }
