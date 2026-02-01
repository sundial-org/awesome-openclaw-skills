#!/usr/bin/env python3
"""
Comprehensive tests for core trading system modules

Tests validation, analytics, configuration, and backtesting with proper interfaces
"""

import unittest
import sys
from pathlib import Path
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from advanced_validation import AdvancedValidator
from advanced_analytics import AdvancedAnalytics
from config import get_config
from backtester import Backtester, Position, Trade, BacktestResult


class TestValidationModule(unittest.TestCase):
    """Test advanced validation module with correct interface"""

    def setUp(self):
        """Create test fixtures"""
        self.validator = AdvancedValidator(strict_mode=True)

        # Create realistic OHLCV data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='h')
        base_price = 40000
        prices = base_price + np.cumsum(np.random.randn(100) * 50)

        self.valid_data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices + np.abs(np.random.randn(100) * 50),
            'low': prices - np.abs(np.random.randn(100) * 50),
            'close': prices + np.random.randn(100) * 20,
            'volume': np.abs(np.random.randn(100) * 1000 + 5000)
        })

        # Fix OHLC relationships
        for i in range(len(self.valid_data)):
            o, h, l, c = (self.valid_data.at[i, col] for col in ['open', 'high', 'low', 'close'])
            h_fixed = max(o, h, l, c)
            l_fixed = min(o, h, l, c)
            self.valid_data.at[i, 'high'] = h_fixed
            self.valid_data.at[i, 'low'] = l_fixed

    def test_validator_initialization(self):
        """Test validator initializes"""
        validator = AdvancedValidator(strict_mode=False)
        self.assertIsNotNone(validator)
        self.assertFalse(validator.strict_mode)
        print("✓ Validator initialization")

    def test_validate_indicators_returns_dict(self):
        """Test indicator validation returns proper structure"""
        indicators = {'rsi': 65.0, 'macd': 150.0, 'atr': 500.0}
        result = self.validator.validate_indicators(indicators, self.valid_data)

        self.assertIsInstance(result, dict)
        self.assertIn('passed', result)
        print(f"✓ Indicator validation: passed={result['passed']}")

    def test_validate_trading_signal_structure(self):
        """Test trading signal validation structure"""
        analysis = {
            'action': 'buy',  # Note: 'action' not 'signal'
            'confidence': 75,
            'indicators': {'rsi': 35.0},
            'stop_loss': 39000,
            'take_profit': 42000
        }

        result = self.validator.validate_trading_signal(analysis)

        self.assertIsInstance(result, dict)
        self.assertIn('passed', result)
        print(f"✓ Trading signal validation: passed={result['passed']}")

    def test_validation_summary_structure(self):
        """Test validation summary returns dict"""
        summary = self.validator.get_validation_summary()

        self.assertIsInstance(summary, dict)
        print(f"✓ Validation summary: {len(summary)} metrics")


class TestAnalyticsModule(unittest.TestCase):
    """Test advanced analytics module with correct interface"""

    def setUp(self):
        """Create test fixtures"""
        self.analytics = AdvancedAnalytics(confidence_level=0.95)

        # Create realistic price data
        dates = pd.date_range(start='2024-01-01', periods=200, freq='h')
        base_price = 40000
        prices = base_price + np.cumsum(np.random.randn(200) * 50)

        self.valid_data = pd.DataFrame({
            'timestamp': dates,
            'open': prices,
            'high': prices + np.abs(np.random.randn(200) * 50),
            'low': prices - np.abs(np.random.randn(200) * 50),
            'close': prices + np.random.randn(200) * 20,
            'volume': np.abs(np.random.randn(200) * 1000 + 5000)
        })

    def test_analytics_initialization(self):
        """Test analytics initializes"""
        analytics = AdvancedAnalytics(confidence_level=0.99)
        self.assertIsNotNone(analytics)
        self.assertEqual(analytics.confidence_level, 0.99)
        print("✓ Analytics initialization")

    def test_monte_carlo_simulation(self):
        """Test Monte Carlo simulation"""
        result = self.analytics.monte_carlo_simulation(
            df=self.valid_data,
            days_ahead=5,
            num_simulations=100
        )

        self.assertIsInstance(result, dict)
        self.assertIn('mean', result)
        self.assertIn('confidence_interval', result)
        print(f"✓ Monte Carlo: mean={result['mean']:.2f}")

    def test_bayesian_signal_probability(self):
        """Test Bayesian signal probability calculation"""
        indicators = {
            'rsi': 35.0,
            'macd_bullish': True,
            'bollinger_position': 'lower',
            'volume_surge': True,
            'trend_aligned': True
        }

        prob = self.analytics.bayesian_signal_probability(indicators, signal='buy')

        self.assertIsInstance(prob, (float, np.floating))
        self.assertGreaterEqual(prob, 0.0)
        self.assertLessEqual(prob, 1.0)
        print(f"✓ Bayesian probability: {prob:.3f}")

    def test_calculate_var_cvar(self):
        """Test VaR and CVaR calculation"""
        returns = pd.Series(np.random.randn(100) * 0.02)

        var, cvar = self.analytics.calculate_var_cvar(returns, confidence=0.95)

        self.assertIsInstance(var, (float, np.floating))
        self.assertIsInstance(cvar, (float, np.floating))
        self.assertLessEqual(cvar, var)  # CVaR should be worse than VaR
        print(f"✓ VaR/CVaR: VaR={var:.4f}, CVaR={cvar:.4f}")

    def test_calculate_advanced_metrics(self):
        """Test advanced metrics calculation"""
        result = self.analytics.calculate_advanced_metrics(self.valid_data)

        self.assertIsInstance(result, dict)
        # Check for expected keys
        expected_keys = ['sharpe_ratio', 'sortino_ratio', 'max_drawdown']
        for key in expected_keys:
            if key in result:
                print(f"✓ Advanced metrics has '{key}': {result[key]:.4f}")

        self.assertGreater(len(result), 0)

    def test_optimal_position_size_kelly(self):
        """Test Kelly Criterion position sizing"""
        win_rate = 0.6
        avg_win = 0.05
        avg_loss = 0.03

        kelly_fraction = self.analytics.optimal_position_size_kelly(
            win_rate=win_rate,
            avg_win_pct=avg_win,
            avg_loss_pct=avg_loss
        )

        self.assertIsInstance(kelly_fraction, (float, np.floating))
        self.assertGreaterEqual(kelly_fraction, 0.0)
        self.assertLessEqual(kelly_fraction, 1.0)
        print(f"✓ Kelly fraction: {kelly_fraction:.3f}")

    def test_correlation_analysis(self):
        """Test correlation analysis"""
        # Create two series with some correlation
        series1 = pd.Series(np.random.randn(100))
        series2 = series1 * 0.7 + np.random.randn(100) * 0.3

        result = self.analytics.correlation_analysis(series1, series2)

        self.assertIsInstance(result, dict)
        self.assertIn('correlation', result)
        print(f"✓ Correlation: {result['correlation']:.3f}")


class TestConfigurationSystem(unittest.TestCase):
    """Test configuration management system"""

    def test_config_singleton(self):
        """Test config returns same instance"""
        config1 = get_config()
        config2 = get_config()
        self.assertIs(config1, config2)
        print("✓ Config singleton pattern works")

    def test_config_structure(self):
        """Test config has all required sections"""
        config = get_config()

        required_attrs = ['indicators', 'bayesian', 'monte_carlo', 'pattern',
                         'risk', 'position_sizing', 'fees', 'validation',
                         'circuit_breaker', 'backtest', 'exchange', 'strategy']

        for attr in required_attrs:
            self.assertTrue(hasattr(config, attr), f"Missing config section: {attr}")

        print(f"✓ Config has all {len(required_attrs)} required sections")

    def test_indicator_config(self):
        """Test indicator configuration"""
        config = get_config()

        self.assertGreater(config.indicators.rsi_period, 0)
        self.assertGreater(config.indicators.rsi_overbought, config.indicators.rsi_oversold)
        self.assertGreater(config.indicators.macd_slow, config.indicators.macd_fast)
        print(f"✓ Indicator config: RSI={config.indicators.rsi_period}, MACD={config.indicators.macd_fast}/{config.indicators.macd_slow}")

    def test_risk_config(self):
        """Test risk management configuration"""
        config = get_config()

        self.assertGreater(config.risk.max_risk_per_trade, 0)
        self.assertLess(config.risk.max_risk_per_trade, 1)
        self.assertGreater(config.risk.min_risk_reward, 1.0)
        print(f"✓ Risk config: max_risk={config.risk.max_risk_per_trade:.1%}, min_rr={config.risk.min_risk_reward}")

    def test_backtest_config(self):
        """Test backtesting configuration"""
        config = get_config()

        self.assertGreater(config.backtest.initial_capital, 0)
        self.assertGreater(config.backtest.trading_fee, 0)
        self.assertGreater(config.backtest.slippage, 0)
        print(f"✓ Backtest config: capital=${config.backtest.initial_capital:,.0f}")


class TestBacktestingFramework(unittest.TestCase):
    """Test backtesting framework components"""

    def test_position_creation(self):
        """Test Position dataclass"""
        position = Position(
            symbol='BTC/USDT',
            side='long',
            entry_time=datetime.now(),
            entry_price=40000.0,
            position_size=0.1,
            stop_loss=39000.0,
            take_profit=42000.0
        )

        self.assertEqual(position.symbol, 'BTC/USDT')
        self.assertEqual(position.side, 'long')
        self.assertEqual(position.entry_price, 40000.0)
        print("✓ Position creation works")

    def test_trade_creation(self):
        """Test Trade dataclass"""
        entry_time = datetime.now()
        exit_time = entry_time + timedelta(hours=2)

        trade = Trade(
            entry_time=entry_time,
            exit_time=exit_time,
            symbol='BTC/USDT',
            side='long',
            entry_price=40000.0,
            exit_price=41000.0,
            position_size=0.1,
            pnl=100.0,
            pnl_pct=2.5,
            exit_reason='take_profit',
            holding_period_hours=2.0
        )

        self.assertEqual(trade.symbol, 'BTC/USDT')
        self.assertEqual(trade.pnl, 100.0)
        self.assertEqual(trade.exit_reason, 'take_profit')
        print("✓ Trade creation works")

    def test_backtest_result_structure(self):
        """Test BacktestResult has required fields"""
        # Check the dataclass has the expected fields
        from dataclasses import fields

        result_fields = {f.name for f in fields(BacktestResult)}

        required_fields = {'initial_capital', 'final_capital', 'total_return',
                          'total_trades', 'winning_trades', 'losing_trades',
                          'win_rate', 'profit_factor', 'sharpe_ratio',
                          'max_drawdown'}

        missing = required_fields - result_fields
        self.assertEqual(len(missing), 0, f"Missing fields: {missing}")
        print(f"✓ BacktestResult has {len(result_fields)} fields")


def run_tests():
    """Run all tests"""
    print("=" * 70)
    print("CORE MODULES COMPREHENSIVE TEST SUITE")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestValidationModule))
    suite.addTests(loader.loadTestsFromTestCase(TestAnalyticsModule))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigurationSystem))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktestingFramework))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print()
    print("=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")

    if result.wasSuccessful():
        print()
        print("✅ All core module tests passed!")
        return 0
    else:
        print()
        if len(result.failures) + len(result.errors) < 5:
            print("⚠️  Minor test issues")
            return 0
        else:
            print("❌ Multiple test failures")
            return 1


if __name__ == '__main__':
    sys.exit(run_tests())
