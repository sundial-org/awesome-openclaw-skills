#!/usr/bin/env python3
"""
Market Data Provider - Extracted from EnhancedTradingAgent

Handles exchange connections and market data fetching with validation.
Single Responsibility: Provide validated market data
"""

import ccxt
import pandas as pd
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class MarketDataProvider:
    """
    Manages exchange connections and market data fetching

    Responsibilities:
    - Initialize and maintain exchange connections
    - Fetch OHLCV data from exchanges
    - Validate data integrity
    - Handle errors and retries
    """

    def __init__(self, exchange_name: str = 'binance', validator=None):
        """
        Initialize market data provider

        Args:
            exchange_name: Name of the exchange (default: binance)
            validator: AdvancedValidator instance for data validation

        Raises:
            ConnectionError: If exchange connection fails
        """
        if not isinstance(exchange_name, str):
            raise TypeError(f"Exchange name must be string, got {type(exchange_name).__name__}")

        self.exchange_name = exchange_name
        self.validator = validator
        self.exchange = self._initialize_exchange()
        logger.info(f"Initialized MarketDataProvider for {exchange_name}")

    def _initialize_exchange(self) -> ccxt.Exchange:
        """
        Initialize exchange connection with validation

        Returns:
            Configured ccxt.Exchange instance

        Raises:
            ConnectionError: If exchange initialization fails
        """
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'},
                'timeout': 30000
            })
            # Verify connection by loading markets
            exchange.load_markets()
            logger.info(f"Successfully connected to {self.exchange_name}")
            return exchange
        except Exception as e:
            error_msg = f"Failed to initialize {self.exchange_name}: {str(e)}"
            logger.error(error_msg)
            raise ConnectionError(error_msg)

    def fetch_market_data(
        self,
        symbol: str,
        timeframe: str = '1h',
        limit: int = 200
    ) -> Optional[pd.DataFrame]:
        """
        Fetch market data with validation

        Args:
            symbol: Trading pair (e.g., 'BTC/USDT')
            timeframe: Candle timeframe (e.g., '1h', '4h', '1d')
            limit: Number of candles to fetch

        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
            None if validation fails or error occurs
        """
        try:
            # Fetch OHLCV data from exchange
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)

            # Convert to DataFrame
            df = pd.DataFrame(
                ohlcv,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

            # Validate data if validator is available
            if self.validator:
                validation_report = self.validator.validate_data_integrity(df, symbol, timeframe)

                if not validation_report['passed']:
                    logger.error(f"Validation failed for {symbol} [{timeframe}]")
                    logger.error(f"Critical issues: {', '.join(validation_report['critical_failures'])}")
                    print(f"\n❌ VALIDATION FAILURE for {symbol} [{timeframe}]")
                    print(f"   Critical Issues: {', '.join(validation_report['critical_failures'])}")
                    return None

                if validation_report['warnings']:
                    logger.warning(f"Validation warnings for {symbol} [{timeframe}]")
                    print(f"\n⚠️  VALIDATION WARNINGS for {symbol} [{timeframe}]:")
                    for warning in validation_report['warnings']:
                        logger.warning(f"  {warning}")
                        print(f"   {warning}")

            logger.info(f"Successfully fetched {len(df)} candles for {symbol} [{timeframe}]")
            return df

        except Exception as e:
            error_msg = f"Data fetch error for {symbol} [{timeframe}]: {str(e)}"
            logger.error(error_msg)
            print(f"❌ {error_msg}")
            return None

    def get_available_symbols(self) -> list:
        """
        Get list of available trading symbols

        Returns:
            List of symbol strings
        """
        try:
            markets = self.exchange.load_markets()
            return list(markets.keys())
        except Exception as e:
            logger.error(f"Failed to get available symbols: {e}")
            return []

    def get_ticker(self, symbol: str) -> Optional[dict]:
        """
        Get current ticker data for symbol

        Args:
            symbol: Trading pair

        Returns:
            Ticker dictionary or None if error
        """
        try:
            return self.exchange.fetch_ticker(symbol)
        except Exception as e:
            logger.error(f"Failed to get ticker for {symbol}: {e}")
            return None
