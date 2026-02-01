#!/usr/bin/env python3
"""
Multi-Source Data Aggregator

Fetches market data from multiple exchanges and cross-validates for reliability.
Enhances data integrity by detecting anomalies across sources.

Component of Phase 1: Critical Reliability Improvements (+0.2 reliability)
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class DataSourceResult:
    """Result from a single data source"""
    exchange: str
    data: Optional[pd.DataFrame]
    success: bool
    error: Optional[str] = None
    latency_ms: float = 0.0


class MultiSourceDataAggregator:
    """
    Aggregates market data from multiple exchanges with cross-validation

    Responsibilities:
    - Fetch data from multiple exchanges (Binance, Coinbase, Kraken)
    - Cross-validate prices across sources
    - Detect price anomalies and outliers
    - Select most reliable data source
    - Merge data with confidence scoring

    Design: Follows Single Responsibility and Open/Closed principles
    """

    # Supported exchanges with priority (higher = preferred)
    EXCHANGES = {
        'binance': {'priority': 3, 'class': 'binance'},
        'coinbase': {'priority': 2, 'class': 'coinbase'},
        'kraken': {'priority': 1, 'class': 'kraken'}
    }

    # Maximum allowed price deviation between exchanges (5%)
    MAX_PRICE_DEVIATION = 0.05

    def __init__(
        self,
        exchanges: Optional[List[str]] = None,
        validator=None,
        timeout: int = 30000
    ):
        """
        Initialize multi-source aggregator

        Args:
            exchanges: List of exchange names to use (default: all supported)
            validator: AdvancedValidator instance for data validation
            timeout: Request timeout in milliseconds
        """
        self.exchanges = exchanges or list(self.EXCHANGES.keys())
        self.validator = validator
        self.timeout = timeout
        self.exchange_instances = {}

        # Initialize exchange connections
        self._initialize_exchanges()

        logger.info(f"Initialized MultiSourceDataAggregator with {len(self.exchange_instances)} exchanges")

    def _initialize_exchanges(self) -> None:
        """Initialize connections to all configured exchanges"""
        for exchange_name in self.exchanges:
            if exchange_name not in self.EXCHANGES:
                logger.warning(f"Unknown exchange: {exchange_name}, skipping")
                continue

            try:
                exchange_class = getattr(ccxt, self.EXCHANGES[exchange_name]['class'])
                exchange = exchange_class({
                    'enableRateLimit': True,
                    'options': {'defaultType': 'spot'},
                    'timeout': self.timeout
                })
                # Verify connection
                exchange.load_markets()
                self.exchange_instances[exchange_name] = exchange
                logger.info(f"Connected to {exchange_name}")
            except Exception as e:
                logger.warning(f"Failed to connect to {exchange_name}: {e}")

    def fetch_multi_source(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> Dict[str, DataSourceResult]:
        """
        Fetch data from all configured exchanges

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe
            limit: Number of candles

        Returns:
            Dictionary mapping exchange name to DataSourceResult
        """
        results = {}

        for exchange_name, exchange in self.exchange_instances.items():
            import time
            start_time = time.time()

            try:
                # Fetch OHLCV data
                ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

                # Convert to DataFrame
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

                # Validate basic data integrity
                if self._validate_data(df):
                    latency = (time.time() - start_time) * 1000
                    results[exchange_name] = DataSourceResult(
                        exchange=exchange_name,
                        data=df,
                        success=True,
                        latency_ms=latency
                    )
                    logger.debug(f"Fetched {len(df)} candles from {exchange_name} ({latency:.0f}ms)")
                else:
                    results[exchange_name] = DataSourceResult(
                        exchange=exchange_name,
                        data=None,
                        success=False,
                        error="Data validation failed"
                    )

            except Exception as e:
                results[exchange_name] = DataSourceResult(
                    exchange=exchange_name,
                    data=None,
                    success=False,
                    error=str(e)
                )
                logger.warning(f"Failed to fetch from {exchange_name}: {e}")

        return results

    def _validate_data(self, df: pd.DataFrame) -> bool:
        """
        Validate basic data integrity

        Args:
            df: DataFrame to validate

        Returns:
            True if data is valid
        """
        if df is None or df.empty:
            return False

        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']
        if not all(col in df.columns for col in required_columns):
            return False

        # Check for missing values
        if df[required_columns].isnull().any().any():
            return False

        # Check OHLC logic (high >= low, etc.)
        if not (df['high'] >= df['low']).all():
            return False
        if not (df['high'] >= df['close']).all():
            return False
        if not (df['high'] >= df['open']).all():
            return False
        if not (df['low'] <= df['close']).all():
            return False
        if not (df['low'] <= df['open']).all():
            return False

        # Check for non-negative values
        if (df[['open', 'high', 'low', 'close', 'volume']] < 0).any().any():
            return False

        return True

    def cross_validate(
        self,
        results: Dict[str, DataSourceResult]
    ) -> Dict:
        """
        Cross-validate data from multiple sources

        Args:
            results: Dictionary of DataSourceResult from each exchange

        Returns:
            Dictionary with validation results and anomalies
        """
        successful_results = {
            name: result for name, result in results.items()
            if result.success and result.data is not None
        }

        if len(successful_results) < 2:
            return {
                'validation': 'insufficient_sources',
                'sources_count': len(successful_results),
                'anomalies': [],
                'confidence': 0.5 if len(successful_results) == 1 else 0.0
            }

        anomalies = []

        # Compare closing prices across exchanges
        price_comparison = {}
        for name, result in successful_results.items():
            price_comparison[name] = result.data['close'].iloc[-1]

        # Calculate price deviations
        prices = list(price_comparison.values())
        median_price = np.median(prices)

        for exchange_name, price in price_comparison.items():
            deviation = abs(price - median_price) / median_price

            if deviation > self.MAX_PRICE_DEVIATION:
                anomalies.append({
                    'exchange': exchange_name,
                    'type': 'price_deviation',
                    'price': price,
                    'median_price': median_price,
                    'deviation_pct': deviation * 100,
                    'severity': 'HIGH' if deviation > 0.1 else 'MEDIUM'
                })

        # Calculate volume consistency
        volume_comparison = {}
        for name, result in successful_results.items():
            volume_comparison[name] = result.data['volume'].iloc[-1]

        volumes = list(volume_comparison.values())
        if len(volumes) > 1:
            volume_std = np.std(volumes)
            volume_mean = np.mean(volumes)
            volume_cv = volume_std / volume_mean if volume_mean > 0 else 0

            # High coefficient of variation suggests data inconsistency
            if volume_cv > 2.0:
                anomalies.append({
                    'type': 'volume_inconsistency',
                    'coefficient_of_variation': volume_cv,
                    'volumes': volume_comparison,
                    'severity': 'LOW'
                })

        # Calculate confidence score
        confidence = self._calculate_confidence(
            len(successful_results),
            len(anomalies),
            price_comparison
        )

        return {
            'validation': 'success' if len(anomalies) == 0 else 'anomalies_detected',
            'sources_count': len(successful_results),
            'anomalies': anomalies,
            'confidence': confidence,
            'price_comparison': price_comparison,
            'median_price': median_price
        }

    def _calculate_confidence(
        self,
        sources_count: int,
        anomalies_count: int,
        prices: Dict[str, float]
    ) -> float:
        """
        Calculate confidence score for aggregated data

        Args:
            sources_count: Number of successful data sources
            anomalies_count: Number of anomalies detected
            prices: Price comparison dictionary

        Returns:
            Confidence score between 0 and 1
        """
        # Base confidence from number of sources
        if sources_count >= 3:
            base_confidence = 0.95
        elif sources_count == 2:
            base_confidence = 0.85
        else:
            base_confidence = 0.60

        # Penalty for anomalies
        anomaly_penalty = anomalies_count * 0.15

        # Bonus for price agreement
        if len(prices) >= 2:
            price_values = list(prices.values())
            price_std = np.std(price_values)
            price_mean = np.mean(price_values)
            price_cv = price_std / price_mean if price_mean > 0 else 1.0

            # Low coefficient of variation = high agreement
            if price_cv < 0.01:  # Within 1%
                base_confidence += 0.05

        confidence = max(0.0, min(1.0, base_confidence - anomaly_penalty))
        return confidence

    def get_best_source(
        self,
        results: Dict[str, DataSourceResult],
        validation: Dict
    ) -> Tuple[Optional[pd.DataFrame], str]:
        """
        Select the best data source based on validation results

        Args:
            results: Dictionary of DataSourceResult
            validation: Cross-validation results

        Returns:
            Tuple of (best_dataframe, source_name)
        """
        successful_results = {
            name: result for name, result in results.items()
            if result.success and result.data is not None
        }

        if not successful_results:
            return None, "no_sources"

        # Get exchanges with anomalies
        anomaly_exchanges = {
            anomaly['exchange']
            for anomaly in validation.get('anomalies', [])
            if 'exchange' in anomaly and anomaly['severity'] == 'HIGH'
        }

        # Filter out exchanges with high-severity anomalies
        clean_results = {
            name: result for name, result in successful_results.items()
            if name not in anomaly_exchanges
        }

        # If all have anomalies, use all (but flag it)
        sources_to_use = clean_results if clean_results else successful_results

        # Select based on priority and latency
        best_source = None
        best_score = -1

        for name, result in sources_to_use.items():
            # Priority score (0-1) from exchange config
            priority = self.EXCHANGES[name]['priority'] / 3.0

            # Latency score (0-1, lower latency = higher score)
            latency_score = max(0, 1 - (result.latency_ms / 5000))

            # Combined score
            score = (priority * 0.7) + (latency_score * 0.3)

            if score > best_score:
                best_score = score
                best_source = name

        if best_source:
            logger.info(f"Selected {best_source} as best data source (score: {best_score:.3f})")
            return successful_results[best_source].data, best_source

        return None, "no_valid_source"

    def fetch_validated_data(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> Dict:
        """
        Fetch and validate data from multiple sources, return best result

        This is the main public API method.

        Args:
            symbol: Trading pair
            timeframe: Candle timeframe
            limit: Number of candles

        Returns:
            Dictionary containing:
            - data: Best validated DataFrame
            - source: Name of selected exchange
            - validation: Cross-validation results
            - all_results: Results from all exchanges
        """
        logger.info(f"Fetching {symbol} [{timeframe}] from {len(self.exchange_instances)} exchanges")

        # Fetch from all sources
        results = self.fetch_multi_source(symbol, timeframe, limit)

        # Cross-validate
        validation = self.cross_validate(results)

        # Select best source
        best_data, best_source = self.get_best_source(results, validation)

        return {
            'data': best_data,
            'source': best_source,
            'validation': validation,
            'all_results': results,
            'success': best_data is not None
        }


# Convenience function for backward compatibility
def create_multi_source_aggregator(
    exchanges: Optional[List[str]] = None,
    validator=None
) -> MultiSourceDataAggregator:
    """
    Factory function to create MultiSourceDataAggregator

    Args:
        exchanges: List of exchange names
        validator: AdvancedValidator instance

    Returns:
        Configured MultiSourceDataAggregator instance
    """
    return MultiSourceDataAggregator(exchanges=exchanges, validator=validator)
