#!/usr/bin/env python3
"""
Configuration Management System

Loads and validates configuration from config.yaml
Provides type-safe access to all parameters
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class IndicatorConfig:
    """Technical indicator parameters"""
    rsi_period: int = 14
    rsi_overbought: int = 70
    rsi_oversold: int = 30
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    bb_period: int = 20
    bb_std: float = 2.0
    atr_period: int = 14
    ema_short: int = 50
    ema_long: int = 200
    stoch_k: int = 14
    stoch_d: int = 3


@dataclass
class BayesianConfig:
    """Bayesian signal generation parameters"""
    rsi_accuracy: float = 0.65
    macd_accuracy: float = 0.68
    bollinger_accuracy: float = 0.62
    volume_accuracy: float = 0.60
    trend_accuracy: float = 0.70
    pattern_accuracy: float = 0.65
    initial_prior: float = 0.50


@dataclass
class MonteCarloConfig:
    """Monte Carlo simulation parameters"""
    num_simulations: int = 10000
    days_ahead: int = 5
    max_exponent: float = 5.0
    min_data_points: int = 30


@dataclass
class PatternConfig:
    """Pattern recognition parameters"""
    min_pattern_length: int = 10
    peak_distance: int = 5
    peak_prominence_std: float = 1.0
    double_top_similarity: float = 0.02
    head_shoulders_similarity: float = 0.03
    wedge_decline: float = 0.03
    num_sr_levels: int = 5
    sr_cluster_threshold: float = 0.02
    sr_min_touches: int = 2


@dataclass
class RiskConfig:
    """Risk management parameters"""
    max_risk_per_trade: float = 0.02
    max_position_size: float = 0.10
    min_risk_reward: float = 1.5
    stop_loss_atr_mult: float = 2.0
    take_profit_atr_mult: float = 3.0


@dataclass
class PositionSizingConfig:
    """Position sizing parameters"""
    default_method: str = "standard"
    kelly_fraction: float = 0.25


@dataclass
class FeeConfig:
    """Trading fees and costs"""
    trading_fee: float = 0.001
    slippage: float = 0.0005


@dataclass
class ValidationConfig:
    """Validation framework parameters"""
    strict_mode: bool = True
    min_data_points: int = 20
    max_z_score: float = 5.0
    iqr_multiplier: float = 3.0
    max_price_jump: float = 0.50
    benford_p_value: float = 0.001
    benford_min_samples: int = 10
    max_age_minutes: int = 5
    rsi_min: float = 0.0
    rsi_max: float = 100.0
    min_atr: float = 0.0
    max_macd_pct: float = 0.10
    min_confidence: int = 40
    max_confidence: int = 95


@dataclass
class CircuitBreakerConfig:
    """Circuit breaker parameters"""
    enabled: bool = True
    low_confidence: int = 40
    poor_risk_reward: float = 1.5
    stale_data_minutes: int = 5
    min_timeframes: int = 2
    max_position_size: float = 0.10
    max_risk: float = 0.02
    negative_sharpe: bool = True
    extreme_z_score: float = 5.0
    min_confidence_variance: float = 0.20


@dataclass
class BacktestConfig:
    """Backtesting parameters"""
    initial_capital: float = 10000
    trading_fee: float = 0.001
    slippage: float = 0.0005
    risk_per_trade: float = 0.02
    max_position_size: float = 0.10
    min_sharpe_ratio: float = 1.0
    min_win_rate: float = 0.50
    min_profit_factor: float = 1.5
    max_drawdown: float = 0.20


@dataclass
class ExchangeConfig:
    """Exchange settings"""
    default: str = "binance"
    fallbacks: List[str] = None
    timeout: int = 30000
    rate_limit: bool = True
    retry_attempts: int = 3
    retry_delay: int = 2000

    def __post_init__(self):
        if self.fallbacks is None:
            self.fallbacks = ["kraken", "coinbase", "bybit"]


@dataclass
class StrategyConfig:
    """Strategy configuration"""
    name: str = "Enhanced Bayesian Pattern Strategy"
    version: str = "2.0.1"
    aggressive_mode: bool = False
    confirm_patterns: bool = True
    multi_timeframe: bool = True

    # Confidence adjustments
    pattern_confirmation_bonus: int = 10
    pattern_conflict_penalty: int = -15
    mc_favorable_bonus: int = 5
    mc_unfavorable_penalty: int = -10
    high_sharpe_bonus: int = 5
    low_sharpe_penalty: int = -10
    strong_volume_bonus: int = 5
    weak_volume_penalty: int = -5


class Config:
    """
    Configuration management system

    Loads parameters from config.yaml and provides type-safe access
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration

        Args:
            config_path: Path to config.yaml (default: ../config.yaml)
        """
        if config_path is None:
            # Default to config.yaml in parent directory
            config_path = Path(__file__).parent.parent / "config.yaml"

        self.config_path = Path(config_path)
        self._raw_config: Dict = {}

        self.load()
        self._initialize_configs()

    def load(self):
        """Load configuration from YAML file"""
        if not self.config_path.exists():
            logger.warning(f"Config file not found: {self.config_path}")
            logger.warning("Using default configuration values")
            self._raw_config = {}
            return

        try:
            with open(self.config_path, 'r') as f:
                self._raw_config = yaml.safe_load(f)
            logger.info(f"Loaded configuration from {self.config_path}")
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            logger.warning("Using default configuration values")
            self._raw_config = {}

    def _initialize_configs(self):
        """Initialize all configuration dataclasses"""
        # Indicators
        indicators = self._raw_config.get('indicators', {})
        self.indicators = IndicatorConfig(
            rsi_period=indicators.get('rsi', {}).get('period', 14),
            rsi_overbought=indicators.get('rsi', {}).get('overbought', 70),
            rsi_oversold=indicators.get('rsi', {}).get('oversold', 30),
            macd_fast=indicators.get('macd', {}).get('fast_period', 12),
            macd_slow=indicators.get('macd', {}).get('slow_period', 26),
            macd_signal=indicators.get('macd', {}).get('signal_period', 9),
            bb_period=indicators.get('bollinger_bands', {}).get('period', 20),
            bb_std=indicators.get('bollinger_bands', {}).get('std_multiplier', 2.0),
            atr_period=indicators.get('atr', {}).get('period', 14),
            ema_short=indicators.get('ema', {}).get('short_period', 50),
            ema_long=indicators.get('ema', {}).get('long_period', 200),
            stoch_k=indicators.get('stochastic', {}).get('k_period', 14),
            stoch_d=indicators.get('stochastic', {}).get('d_period', 3)
        )

        # Bayesian
        bayesian = self._raw_config.get('bayesian', {})
        priors = bayesian.get('prior_accuracies', {})
        self.bayesian = BayesianConfig(
            rsi_accuracy=priors.get('rsi', 0.65),
            macd_accuracy=priors.get('macd', 0.68),
            bollinger_accuracy=priors.get('bollinger', 0.62),
            volume_accuracy=priors.get('volume', 0.60),
            trend_accuracy=priors.get('trend', 0.70),
            pattern_accuracy=priors.get('pattern', 0.65),
            initial_prior=bayesian.get('initial_prior', 0.50)
        )

        # Monte Carlo
        mc = self._raw_config.get('monte_carlo', {})
        self.monte_carlo = MonteCarloConfig(
            num_simulations=mc.get('num_simulations', 10000),
            days_ahead=mc.get('days_ahead', 5),
            max_exponent=mc.get('max_exponent', 5.0),
            min_data_points=mc.get('min_data_points', 30)
        )

        # Patterns
        patterns = self._raw_config.get('patterns', {})
        peak_det = patterns.get('peak_detection', {})
        sim_thresh = patterns.get('similarity_thresholds', {})
        sr = patterns.get('support_resistance', {})
        self.patterns = PatternConfig(
            min_pattern_length=patterns.get('min_pattern_length', 10),
            peak_distance=peak_det.get('distance', 5),
            peak_prominence_std=peak_det.get('prominence_std', 1.0),
            double_top_similarity=sim_thresh.get('double_top_bottom', 0.02),
            head_shoulders_similarity=sim_thresh.get('head_shoulders', 0.03),
            wedge_decline=sim_thresh.get('wedge_decline', 0.03),
            num_sr_levels=sr.get('num_levels', 5),
            sr_cluster_threshold=sr.get('cluster_threshold', 0.02),
            sr_min_touches=sr.get('min_touches', 2)
        )

        # Risk
        risk = self._raw_config.get('risk', {})
        self.risk = RiskConfig(
            max_risk_per_trade=risk.get('max_risk_per_trade', 0.02),
            max_position_size=risk.get('max_position_size', 0.10),
            min_risk_reward=risk.get('min_risk_reward_ratio', 1.5),
            stop_loss_atr_mult=risk.get('stop_loss_multiplier', 2.0),
            take_profit_atr_mult=risk.get('take_profit_multiplier', 3.0)
        )

        # Position Sizing
        pos_sizing = self._raw_config.get('position_sizing', {})
        self.position_sizing = PositionSizingConfig(
            default_method=pos_sizing.get('default_method', 'standard'),
            kelly_fraction=pos_sizing.get('kelly_fraction', 0.25)
        )

        # Fees
        fees = self._raw_config.get('fees', {})
        self.fees = FeeConfig(
            trading_fee=fees.get('trading_fee', 0.001),
            slippage=fees.get('slippage', 0.0005)
        )

        # Validation
        val = self._raw_config.get('validation', {})
        data_int = val.get('data_integrity', {})
        fresh = val.get('data_freshness', {})
        ind_val = val.get('indicator_validation', {})
        sig_val = val.get('signal_validation', {})

        self.validation = ValidationConfig(
            strict_mode=val.get('strict_mode', True),
            min_data_points=data_int.get('min_data_points', 20),
            max_z_score=data_int.get('max_z_score', 5.0),
            iqr_multiplier=data_int.get('iqr_multiplier', 3.0),
            max_price_jump=data_int.get('max_price_jump', 0.50),
            benford_p_value=data_int.get('benford_p_value', 0.001),
            benford_min_samples=data_int.get('benford_min_samples', 10),
            max_age_minutes=fresh.get('max_age_minutes', 5),
            rsi_min=ind_val.get('rsi_range', [0, 100])[0],
            rsi_max=ind_val.get('rsi_range', [0, 100])[1],
            min_atr=ind_val.get('min_atr', 0.0),
            max_macd_pct=ind_val.get('max_macd_pct', 0.10),
            min_confidence=sig_val.get('min_confidence', 40),
            max_confidence=sig_val.get('max_confidence', 95)
        )

        # Circuit Breakers
        cb = self._raw_config.get('circuit_breakers', {})
        checks = cb.get('checks', {})
        self.circuit_breakers = CircuitBreakerConfig(
            enabled=cb.get('enabled', True),
            low_confidence=checks.get('low_confidence', 40),
            poor_risk_reward=checks.get('poor_risk_reward', 1.5),
            stale_data_minutes=checks.get('stale_data_minutes', 5),
            min_timeframes=checks.get('min_timeframes', 2),
            max_position_size=checks.get('max_position_size', 0.10),
            max_risk=checks.get('max_risk', 0.02),
            negative_sharpe=checks.get('negative_sharpe', True),
            extreme_z_score=checks.get('extreme_z_score', 5.0),
            min_confidence_variance=checks.get('min_confidence_variance', 0.20)
        )

        # Backtesting
        bt = self._raw_config.get('backtesting', {})
        targets = bt.get('performance_targets', {})
        self.backtest = BacktestConfig(
            initial_capital=bt.get('initial_capital', 10000),
            trading_fee=bt.get('trading_fee', 0.001),
            slippage=bt.get('slippage', 0.0005),
            risk_per_trade=bt.get('risk_per_trade', 0.02),
            max_position_size=bt.get('max_position_size', 0.10),
            min_sharpe_ratio=targets.get('min_sharpe_ratio', 1.0),
            min_win_rate=targets.get('min_win_rate', 0.50),
            min_profit_factor=targets.get('min_profit_factor', 1.5),
            max_drawdown=targets.get('max_drawdown', 0.20)
        )

        # Exchange
        exch = self._raw_config.get('exchanges', {})
        settings = exch.get('settings', {})
        self.exchange = ExchangeConfig(
            default=exch.get('default', 'binance'),
            fallbacks=exch.get('fallbacks', ['kraken', 'coinbase', 'bybit']),
            timeout=settings.get('timeout', 30000),
            rate_limit=settings.get('rate_limit', True),
            retry_attempts=settings.get('retry_attempts', 3),
            retry_delay=settings.get('retry_delay', 2000)
        )

        # Strategy
        strat = self._raw_config.get('strategy', {})
        adj = strat.get('adjustments', {})
        self.strategy = StrategyConfig(
            name=strat.get('name', 'Enhanced Bayesian Pattern Strategy'),
            version=strat.get('version', '2.0.1'),
            aggressive_mode=strat.get('aggressive_mode', False),
            confirm_patterns=strat.get('confirm_patterns', True),
            multi_timeframe=strat.get('multi_timeframe', True),
            pattern_confirmation_bonus=adj.get('pattern_confirmation', 10),
            pattern_conflict_penalty=adj.get('pattern_conflict', -15),
            mc_favorable_bonus=adj.get('monte_carlo_favorable', 5),
            mc_unfavorable_penalty=adj.get('monte_carlo_unfavorable', -10),
            high_sharpe_bonus=adj.get('high_sharpe', 5),
            low_sharpe_penalty=adj.get('low_sharpe', -10),
            strong_volume_bonus=adj.get('strong_volume', 5),
            weak_volume_penalty=adj.get('weak_volume', -5)
        )

        # Simple list/dict configs
        self.market_categories = self._raw_config.get('market_categories', {})
        self.timeframes = self._raw_config.get('timeframes', ['15m', '1h', '4h'])

        # Logging
        log_config = self._raw_config.get('logging', {})
        self.log_level = log_config.get('level', 'INFO')
        self.log_file = log_config.get('file', 'trading_agent.log')

    def get_all_symbols(self) -> List[str]:
        """Get all trading symbols from all categories"""
        symbols = []
        for category, symbol_list in self.market_categories.items():
            symbols.extend(symbol_list)
        return symbols

    def validate(self) -> bool:
        """
        Validate configuration values

        Returns:
            True if all values are valid, False otherwise
        """
        errors = []

        # Validate positive values
        if self.indicators.rsi_period <= 0:
            errors.append("RSI period must be positive")
        if self.monte_carlo.num_simulations <= 0:
            errors.append("Number of simulations must be positive")
        if self.risk.max_risk_per_trade <= 0 or self.risk.max_risk_per_trade > 1:
            errors.append("Max risk per trade must be between 0 and 1")

        # Validate ranges
        if not (0 <= self.bayesian.initial_prior <= 1):
            errors.append("Initial prior must be between 0 and 1")
        if self.validation.min_confidence < 0 or self.validation.min_confidence > 100:
            errors.append("Min confidence must be between 0 and 100")

        # Validate logic
        if self.indicators.macd_fast >= self.indicators.macd_slow:
            errors.append("MACD fast period must be less than slow period")

        if errors:
            for error in errors:
                logger.error(f"Configuration error: {error}")
            return False

        logger.info("Configuration validation passed")
        return True

    def __str__(self):
        """String representation"""
        return f"Config(strategy={self.strategy.name} v{self.strategy.version})"


# Global configuration instance
_config_instance: Optional[Config] = None


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get global configuration instance (singleton pattern)

    Args:
        config_path: Optional path to config file

    Returns:
        Config instance
    """
    global _config_instance

    if _config_instance is None:
        _config_instance = Config(config_path)

    return _config_instance


if __name__ == '__main__':
    # Test configuration loading
    config = get_config()
    print(f"Loaded configuration: {config}")
    print(f"RSI Period: {config.indicators.rsi_period}")
    print(f"Max Risk: {config.risk.max_risk_per_trade * 100}%")
    print(f"Validation passed: {config.validate()}")
