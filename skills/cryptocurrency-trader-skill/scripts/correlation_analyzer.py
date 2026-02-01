#!/usr/bin/env python3
"""
Correlation Analyzer

Analyzes correlations between cryptocurrency assets for portfolio
risk management and diversification.

Component of Phase 3: Market Context (+0.3 reliability)
"""

import ccxt
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from scipy import stats
import logging

logger = logging.getLogger(__name__)


class CorrelationAnalyzer:
    """
    Analyzes correlations between cryptocurrency assets

    Responsibilities:
    - Calculate correlation matrices between assets
    - Identify highly correlated pairs
    - Assess portfolio concentration risk
    - Recommend diversification opportunities
    - Detect correlation regime changes

    Design: Single Responsibility, Dependency Injection
    """

    # Major cryptocurrency pairs for correlation analysis
    MAJOR_PAIRS = [
        'BTC/USDT',
        'ETH/USDT',
        'BNB/USDT',
        'XRP/USDT',
        'SOL/USDT',
        'ADA/USDT',
        'DOGE/USDT',
        'MATIC/USDT'
    ]

    def __init__(
        self,
        exchange_name: str = 'binance',
        lookback_days: int = 30,
        correlation_threshold: float = 0.7
    ):
        """
        Initialize correlation analyzer

        Args:
            exchange_name: Name of exchange to use
            lookback_days: Days of history for correlation calculation
            correlation_threshold: Threshold for high correlation warning
        """
        self.exchange_name = exchange_name
        self.lookback_days = lookback_days
        self.correlation_threshold = correlation_threshold
        self.exchange = self._initialize_exchange()

        logger.info(f"Initialized CorrelationAnalyzer (lookback: {lookback_days}d, "
                   f"threshold: {correlation_threshold})")

    def _initialize_exchange(self) -> ccxt.Exchange:
        """Initialize exchange connection"""
        try:
            exchange_class = getattr(ccxt, self.exchange_name)
            exchange = exchange_class({
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'},
                'timeout': 30000
            })
            exchange.load_markets()
            return exchange
        except Exception as e:
            logger.error(f"Failed to initialize exchange: {e}")
            raise

    def calculate_correlation_matrix(
        self,
        symbols: Optional[List[str]] = None,
        timeframe: str = '1d'
    ) -> Dict:
        """
        Calculate correlation matrix for given symbols

        Args:
            symbols: List of trading pairs (default: MAJOR_PAIRS)
            timeframe: Timeframe for calculation

        Returns:
            Dictionary with correlation matrix and analysis
        """
        if symbols is None:
            symbols = self.MAJOR_PAIRS

        logger.info(f"Calculating correlation matrix for {len(symbols)} pairs")

        # Fetch price data for all symbols
        price_data = {}
        for symbol in symbols:
            try:
                ohlcv = self.exchange.fetch_ohlcv(
                    symbol,
                    timeframe,
                    limit=self.lookback_days
                )
                df = pd.DataFrame(
                    ohlcv,
                    columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
                )
                price_data[symbol] = df['close']
            except Exception as e:
                logger.warning(f"Failed to fetch {symbol}: {e}")

        if len(price_data) < 2:
            return {
                'success': False,
                'error': 'Insufficient data for correlation analysis'
            }

        # Create DataFrame with all prices
        prices_df = pd.DataFrame(price_data)

        # Calculate returns
        returns_df = prices_df.pct_change().dropna()

        # Calculate correlation matrix
        correlation_matrix = returns_df.corr()

        # Analyze correlations
        analysis = self._analyze_correlation_matrix(correlation_matrix, symbols)

        return {
            'success': True,
            'correlation_matrix': correlation_matrix.to_dict(),
            'returns_data': returns_df,
            'analysis': analysis
        }

    def _analyze_correlation_matrix(
        self,
        correlation_matrix: pd.DataFrame,
        symbols: List[str]
    ) -> Dict:
        """
        Analyze correlation matrix for insights

        Args:
            correlation_matrix: Correlation matrix DataFrame
            symbols: List of symbols

        Returns:
            Analysis dictionary
        """
        high_correlations = []
        low_correlations = []
        negative_correlations = []

        # Analyze pairwise correlations
        for i in range(len(symbols)):
            for j in range(i + 1, len(symbols)):
                symbol_i = symbols[i]
                symbol_j = symbols[j]

                if symbol_i in correlation_matrix.index and symbol_j in correlation_matrix.columns:
                    corr = correlation_matrix.loc[symbol_i, symbol_j]

                    # High positive correlation
                    if corr >= self.correlation_threshold:
                        high_correlations.append({
                            'pair': (symbol_i, symbol_j),
                            'correlation': corr,
                            'risk': 'HIGH'
                        })

                    # Low correlation (good for diversification)
                    elif abs(corr) < 0.3:
                        low_correlations.append({
                            'pair': (symbol_i, symbol_j),
                            'correlation': corr,
                            'benefit': 'DIVERSIFICATION'
                        })

                    # Negative correlation (hedging opportunity)
                    elif corr < -0.3:
                        negative_correlations.append({
                            'pair': (symbol_i, symbol_j),
                            'correlation': corr,
                            'benefit': 'HEDGING'
                        })

        # Calculate average correlation
        # Get upper triangle of correlation matrix (excluding diagonal)
        mask = np.triu(np.ones_like(correlation_matrix, dtype=bool), k=1)
        correlations = correlation_matrix.where(mask).values.flatten()
        correlations = correlations[~np.isnan(correlations)]

        avg_correlation = np.mean(correlations) if len(correlations) > 0 else 0.0

        return {
            'high_correlations': high_correlations,
            'low_correlations': low_correlations,
            'negative_correlations': negative_correlations,
            'average_correlation': avg_correlation,
            'market_coupling': self._assess_market_coupling(avg_correlation)
        }

    def _assess_market_coupling(self, avg_correlation: float) -> str:
        """
        Assess how tightly coupled the market is

        Args:
            avg_correlation: Average correlation across all pairs

        Returns:
            Market coupling assessment
        """
        if avg_correlation > 0.8:
            return 'EXTREME - Market moving as one (high risk)'
        elif avg_correlation > 0.6:
            return 'HIGH - Strong correlation across assets'
        elif avg_correlation > 0.4:
            return 'MODERATE - Normal market correlation'
        elif avg_correlation > 0.2:
            return 'LOW - Good diversification potential'
        else:
            return 'VERY LOW - Assets moving independently'

    def analyze_symbol_correlation(
        self,
        target_symbol: str,
        reference_symbols: Optional[List[str]] = None,
        timeframe: str = '1d'
    ) -> Dict:
        """
        Analyze correlation of target symbol with reference symbols

        Args:
            target_symbol: Symbol to analyze
            reference_symbols: Symbols to compare against (default: BTC, ETH)
            timeframe: Timeframe for analysis

        Returns:
            Correlation analysis for target symbol
        """
        if reference_symbols is None:
            reference_symbols = ['BTC/USDT', 'ETH/USDT']

        # Add target to list
        all_symbols = [target_symbol] + reference_symbols

        # Calculate correlation matrix
        result = self.calculate_correlation_matrix(all_symbols, timeframe)

        if not result.get('success'):
            return result

        correlation_matrix = pd.DataFrame(result['correlation_matrix'])

        # Extract correlations for target symbol
        target_correlations = {}
        for ref_symbol in reference_symbols:
            if target_symbol in correlation_matrix.index and ref_symbol in correlation_matrix.columns:
                target_correlations[ref_symbol] = correlation_matrix.loc[target_symbol, ref_symbol]

        # Generate interpretation
        interpretation = self._interpret_symbol_correlations(
            target_symbol,
            target_correlations
        )

        return {
            'success': True,
            'target_symbol': target_symbol,
            'correlations': target_correlations,
            'interpretation': interpretation
        }

    def _interpret_symbol_correlations(
        self,
        symbol: str,
        correlations: Dict[str, float]
    ) -> Dict:
        """
        Interpret symbol correlations

        Args:
            symbol: Target symbol
            correlations: Dictionary of correlations

        Returns:
            Interpretation dictionary
        """
        # Get BTC correlation if available
        btc_corr = correlations.get('BTC/USDT', 0.0)
        eth_corr = correlations.get('ETH/USDT', 0.0)

        interpretation = {
            'btc_dependency': None,
            'eth_dependency': None,
            'independence_score': None,
            'risk_assessment': None,
            'trading_implications': []
        }

        # BTC dependency
        if abs(btc_corr) > 0.8:
            interpretation['btc_dependency'] = 'VERY HIGH'
            interpretation['trading_implications'].append(
                "Highly dependent on BTC - consider BTC trend before trading"
            )
        elif abs(btc_corr) > 0.6:
            interpretation['btc_dependency'] = 'HIGH'
            interpretation['trading_implications'].append(
                "Strongly correlated with BTC - monitor BTC movements"
            )
        elif abs(btc_corr) > 0.4:
            interpretation['btc_dependency'] = 'MODERATE'
        else:
            interpretation['btc_dependency'] = 'LOW'
            interpretation['trading_implications'].append(
                "Low BTC correlation - good diversification candidate"
            )

        # ETH dependency
        if abs(eth_corr) > 0.8:
            interpretation['eth_dependency'] = 'VERY HIGH'
        elif abs(eth_corr) > 0.6:
            interpretation['eth_dependency'] = 'HIGH'
        elif abs(eth_corr) > 0.4:
            interpretation['eth_dependency'] = 'MODERATE'
        else:
            interpretation['eth_dependency'] = 'LOW'

        # Independence score (0-100, higher = more independent)
        avg_corr = np.mean([abs(c) for c in correlations.values()])
        independence_score = (1 - avg_corr) * 100
        interpretation['independence_score'] = independence_score

        # Risk assessment
        if avg_corr > 0.8:
            interpretation['risk_assessment'] = 'HIGH - Very correlated, limited diversification benefit'
        elif avg_corr > 0.6:
            interpretation['risk_assessment'] = 'MODERATE - Some diversification benefit'
        else:
            interpretation['risk_assessment'] = 'LOW - Good diversification potential'

        return interpretation

    def detect_correlation_regime_change(
        self,
        symbol: str,
        short_window: int = 7,
        long_window: int = 30
    ) -> Dict:
        """
        Detect if correlation regime has changed recently

        Args:
            symbol: Symbol to analyze
            short_window: Short-term correlation window (days)
            long_window: Long-term correlation window (days)

        Returns:
            Regime change analysis
        """
        try:
            # Fetch price data
            target_data = self.exchange.fetch_ohlcv(symbol, '1d', limit=long_window + 10)
            btc_data = self.exchange.fetch_ohlcv('BTC/USDT', '1d', limit=long_window + 10)

            # Convert to DataFrames
            target_df = pd.DataFrame(
                target_data,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )
            btc_df = pd.DataFrame(
                btc_data,
                columns=['timestamp', 'open', 'high', 'low', 'close', 'volume']
            )

            # Calculate returns
            target_returns = target_df['close'].pct_change().dropna()
            btc_returns = btc_df['close'].pct_change().dropna()

            # Calculate short-term correlation
            short_corr = target_returns.tail(short_window).corr(
                btc_returns.tail(short_window)
            )

            # Calculate long-term correlation
            long_corr = target_returns.tail(long_window).corr(
                btc_returns.tail(long_window)
            )

            # Detect regime change
            correlation_change = short_corr - long_corr
            regime_changed = abs(correlation_change) > 0.3

            return {
                'success': True,
                'symbol': symbol,
                'short_term_correlation': short_corr,
                'long_term_correlation': long_corr,
                'correlation_change': correlation_change,
                'regime_changed': regime_changed,
                'interpretation': self._interpret_regime_change(
                    short_corr,
                    long_corr,
                    correlation_change,
                    regime_changed
                )
            }

        except Exception as e:
            logger.error(f"Failed to detect regime change: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def _interpret_regime_change(
        self,
        short_corr: float,
        long_corr: float,
        change: float,
        regime_changed: bool
    ) -> str:
        """
        Interpret correlation regime change

        Args:
            short_corr: Short-term correlation
            long_corr: Long-term correlation
            change: Correlation change
            regime_changed: Whether regime changed

        Returns:
            Interpretation string
        """
        if not regime_changed:
            return f"Stable correlation regime (recent: {short_corr:.2f}, historical: {long_corr:.2f})"

        if change > 0.3:
            return (f"ALERT: Correlation increased sharply from {long_corr:.2f} to {short_corr:.2f}. "
                   "Asset becoming more BTC-dependent - reduced diversification benefit.")

        elif change < -0.3:
            return (f"ALERT: Correlation decreased sharply from {long_corr:.2f} to {short_corr:.2f}. "
                   "Asset decoupling from BTC - potential diversification opportunity.")

        return "Correlation regime stable"

    def get_diversification_recommendations(
        self,
        current_holdings: List[str]
    ) -> Dict:
        """
        Recommend assets for diversification based on current holdings

        Args:
            current_holdings: List of currently held symbols

        Returns:
            Diversification recommendations
        """
        # Calculate correlations for current holdings
        result = self.calculate_correlation_matrix(
            symbols=current_holdings + self.MAJOR_PAIRS
        )

        if not result.get('success'):
            return result

        correlation_matrix = pd.DataFrame(result['correlation_matrix'])

        # Find assets with low correlation to current holdings
        recommendations = []

        for candidate in self.MAJOR_PAIRS:
            if candidate in current_holdings:
                continue

            # Calculate average correlation with current holdings
            correlations = []
            for holding in current_holdings:
                if candidate in correlation_matrix.index and holding in correlation_matrix.columns:
                    corr = abs(correlation_matrix.loc[candidate, holding])
                    correlations.append(corr)

            if correlations:
                avg_corr = np.mean(correlations)

                # Low correlation = good diversification
                if avg_corr < 0.5:
                    recommendations.append({
                        'symbol': candidate,
                        'avg_correlation': avg_corr,
                        'diversification_score': (1 - avg_corr) * 100,
                        'benefit': 'HIGH' if avg_corr < 0.3 else 'MODERATE'
                    })

        # Sort by diversification score (descending)
        recommendations.sort(key=lambda x: x['diversification_score'], reverse=True)

        return {
            'success': True,
            'current_holdings': current_holdings,
            'recommendations': recommendations[:5],  # Top 5
            'summary': f"Found {len(recommendations)} diversification opportunities"
        }


# Convenience functions
def analyze_correlation(
    symbol: str,
    exchange_name: str = 'binance'
) -> Dict:
    """
    Quick correlation analysis for a symbol

    Args:
        symbol: Trading pair to analyze
        exchange_name: Exchange to use

    Returns:
        Correlation analysis
    """
    analyzer = CorrelationAnalyzer(exchange_name=exchange_name)
    return analyzer.analyze_symbol_correlation(symbol)


def calculate_portfolio_correlation(
    symbols: List[str],
    exchange_name: str = 'binance'
) -> Dict:
    """
    Calculate correlation matrix for portfolio

    Args:
        symbols: List of symbols in portfolio
        exchange_name: Exchange to use

    Returns:
        Correlation matrix and analysis
    """
    analyzer = CorrelationAnalyzer(exchange_name=exchange_name)
    return analyzer.calculate_correlation_matrix(symbols)
