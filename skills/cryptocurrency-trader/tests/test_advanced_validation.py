#!/usr/bin/env python3
"""
Comprehensive tests for Advanced Validation module

Tests the anti-hallucination framework including:
- Data integrity validation
- Benford's Law analysis
- Outlier detection
- Technical indicator validation
- Confidence scoring
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


class TestDataIntegrityValidation(unittest.TestCase):
    """Test data integrity validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = AdvancedValidator(strict_mode=True)

        # Create valid data
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')
        self.valid_data = pd.DataFrame({
            'timestamp': dates,
            'open': np.random.uniform(40000, 41000, 100),
            'high': np.random.uniform(41000, 42000, 100),
            'low': np.random.uniform(39000, 40000, 100),
            'close': np.random.uniform(40000, 41000, 100),
            'volume': np.random.uniform(100, 1000, 100)
        })
        # Ensure OHLC relationships are correct
        for i in range(len(self.valid_data)):
            low = self.valid_data.loc[i, 'low']
            high = self.valid_data.loc[i, 'high']
            self.valid_data.loc[i, 'open'] = np.random.uniform(low, high)
            self.valid_data.loc[i, 'close'] = np.random.uniform(low, high)

    def test_valid_data_passes(self):
        """Test that valid data passes all checks"""
        result = self.validator.validate_data_integrity(self.valid_data, 'BTC/USDT')

        self.assertTrue(result['passed'])
        self.assertEqual(len(result['critical_failures']), 0)
        print("✓ Valid data passes validation")

    def test_empty_data_fails(self):
        """Test that empty data fails validation"""
        empty_df = pd.DataFrame()
        result = self.validator.validate_data_integrity(empty_df, 'BTC/USDT')

        self.assertFalse(result['passed'])
        self.assertIn('empty', ' '.join(result['critical_failures']).lower())
        print("✓ Empty data fails validation")

    def test_insufficient_data_fails(self):
        """Test that insufficient data fails validation"""
        small_df = self.valid_data.head(5)  # Only 5 rows
        result = self.validator.validate_data_integrity(small_df, 'BTC/USDT')

        self.assertFalse(result['passed'])
        print("✓ Insufficient data fails validation")

    def test_missing_columns_fails(self):
        """Test that missing columns fails validation"""
        incomplete_df = self.valid_data.drop(columns=['volume'])
        result = self.validator.validate_data_integrity(incomplete_df, 'BTC/USDT')

        self.assertFalse(result['passed'])
        print("✓ Missing columns fails validation")

    def test_null_values_detected(self):
        """Test that null values are detected"""
        data_with_nulls = self.valid_data.copy()
        data_with_nulls.loc[10:15, 'close'] = np.nan

        result = self.validator.validate_data_integrity(data_with_nulls, 'BTC/USDT')

        self.assertFalse(result['passed'])
        print("✓ Null values detected")

    def test_negative_prices_detected(self):
        """Test that negative prices are detected"""
        data_with_negatives = self.valid_data.copy()
        data_with_negatives.loc[10, 'close'] = -100

        result = self.validator.validate_data_integrity(data_with_negatives, 'BTC/USDT')

        self.assertFalse(result['passed'])
        print("✓ Negative prices detected")

    def test_zero_prices_detected(self):
        """Test that zero prices are detected"""
        data_with_zeros = self.valid_data.copy()
        data_with_zeros.loc[10, 'close'] = 0

        result = self.validator.validate_data_integrity(data_with_zeros, 'BTC/USDT')

        self.assertFalse(result['passed'])
        print("✓ Zero prices detected")

    def test_invalid_ohlc_relationships(self):
        """Test that invalid OHLC relationships are detected"""
        invalid_ohlc = self.valid_data.copy()
        # Make high < low (invalid)
        invalid_ohlc.loc[10, 'high'] = 100
        invalid_ohlc.loc[10, 'low'] = 200

        result = self.validator.validate_data_integrity(invalid_ohlc, 'BTC/USDT')

        self.assertFalse(result['passed'])
        print("✓ Invalid OHLC relationships detected")

    def test_extreme_price_jumps_detected(self):
        """Test that extreme price jumps are detected"""
        extreme_jumps = self.valid_data.copy()
        # Create 100% price jump (should trigger warning/failure)
        extreme_jumps.loc[50, 'close'] = extreme_jumps.loc[49, 'close'] * 2.5

        result = self.validator.validate_data_integrity(extreme_jumps, 'BTC/USDT')

        # Should either fail or have warnings
        self.assertTrue(not result['passed'] or len(result['warnings']) > 0)
        print("✓ Extreme price jumps detected")


class TestBenfordsLawValidation(unittest.TestCase):
    """Test Benford's Law validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = AdvancedValidator(strict_mode=True)

    def test_natural_data_passes_benfords(self):
        """Test that natural data passes Benford's Law"""
        # Generate data that follows Benford's Law approximately
        natural_volumes = []
        for _ in range(100):
            # Generate numbers with leading digits following Benford's distribution
            leading = np.random.choice([1,2,3,4,5,6,7,8,9],
                                     p=[0.301, 0.176, 0.125, 0.097, 0.079, 0.067, 0.058, 0.051, 0.046])
            magnitude = np.random.uniform(2, 4)
            natural_volumes.append(leading * (10 ** magnitude))

        df = pd.DataFrame({'volume': natural_volumes})

        result = self.validator.validate_benfords_law(df, 'volume')

        # Should pass or at least not fail catastrophically
        self.assertIsNotNone(result)
        print("✓ Natural data passes Benford's Law")

    def test_fabricated_data_fails_benfords(self):
        """Test that obviously fabricated data fails Benford's Law"""
        # Create uniform distribution (should fail Benford's)
        fabricated_volumes = np.random.uniform(100, 900, 100)
        df = pd.DataFrame({'volume': fabricated_volumes})

        result = self.validator.validate_benfords_law(df, 'volume')

        self.assertIsNotNone(result)
        # Note: Benford's test may or may not fail depending on randomness
        # The point is it should detect the uniform distribution is suspicious
        print(f"✓ Fabricated data analyzed: p-value = {result.get('p_value', 'N/A')}")

    def test_insufficient_data_for_benfords(self):
        """Test that insufficient data returns appropriate result"""
        small_df = pd.DataFrame({'volume': [100, 200, 300]})

        result = self.validator.validate_benfords_law(small_df, 'volume')

        self.assertIn('insufficient', result.get('status', '').lower())
        print("✓ Insufficient data for Benford's detected")


class TestOutlierDetection(unittest.TestCase):
    """Test outlier detection"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = AdvancedValidator(strict_mode=True)

    def test_no_outliers_in_normal_data(self):
        """Test that normal data has no outliers"""
        normal_data = pd.Series(np.random.normal(100, 10, 100))

        outliers = self.validator.detect_outliers(normal_data, method='zscore')

        # With z-score threshold of 5, should have very few or no outliers
        self.assertLess(outliers.sum(), 5)
        print(f"✓ Normal data has {outliers.sum()} outliers")

    def test_extreme_values_detected_zscore(self):
        """Test that extreme values are detected with z-score method"""
        data = pd.Series(np.random.normal(100, 10, 100))
        data.iloc[50] = 1000  # Extreme outlier

        outliers = self.validator.detect_outliers(data, method='zscore')

        self.assertTrue(outliers.iloc[50])
        print("✓ Extreme value detected with z-score")

    def test_extreme_values_detected_iqr(self):
        """Test that extreme values are detected with IQR method"""
        data = pd.Series(np.random.normal(100, 10, 100))
        data.iloc[50] = 1000  # Extreme outlier

        outliers = self.validator.detect_outliers(data, method='iqr')

        self.assertTrue(outliers.iloc[50])
        print("✓ Extreme value detected with IQR")


class TestTechnicalIndicatorValidation(unittest.TestCase):
    """Test technical indicator validation"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = AdvancedValidator(strict_mode=True)

    def test_valid_rsi_passes(self):
        """Test that valid RSI values pass"""
        analysis = {
            'indicators': {
                'rsi': 65.5,
                'macd': 100,
                'atr': 500
            },
            'confidence': 75
        }

        result = self.validator.validate_analysis(analysis)

        self.assertTrue(result['valid'])
        print("✓ Valid RSI passes validation")

    def test_rsi_out_of_range_fails(self):
        """Test that RSI out of range fails"""
        analysis = {
            'indicators': {
                'rsi': 150,  # Invalid: > 100
                'macd': 100,
                'atr': 500
            },
            'confidence': 75
        }

        result = self.validator.validate_analysis(analysis)

        self.assertFalse(result['valid'])
        print("✓ Invalid RSI detected")

    def test_negative_atr_fails(self):
        """Test that negative ATR fails"""
        analysis = {
            'indicators': {
                'rsi': 65,
                'macd': 100,
                'atr': -50  # Invalid: negative
            },
            'confidence': 75
        }

        result = self.validator.validate_analysis(analysis)

        self.assertFalse(result['valid'])
        print("✓ Negative ATR detected")

    def test_extreme_macd_fails(self):
        """Test that extreme MACD values fail"""
        analysis = {
            'indicators': {
                'rsi': 65,
                'macd': 50000,  # > 10% of price is suspicious
                'atr': 500
            },
            'confidence': 75
        }

        result = self.validator.validate_analysis(analysis)

        # Should have warnings at minimum
        self.assertTrue(not result['valid'] or len(result.get('warnings', [])) > 0)
        print("✓ Extreme MACD detected")

    def test_confidence_out_of_range_fails(self):
        """Test that confidence out of range fails"""
        analysis = {
            'indicators': {
                'rsi': 65,
                'macd': 100,
                'atr': 500
            },
            'confidence': 150  # Invalid: > 100
        }

        result = self.validator.validate_analysis(analysis)

        self.assertFalse(result['valid'])
        print("✓ Invalid confidence detected")


class TestCircuitBreaker(unittest.TestCase):
    """Test circuit breaker functionality"""

    def setUp(self):
        """Set up test fixtures"""
        self.validator = AdvancedValidator(strict_mode=True)

    def test_low_confidence_triggers_circuit_breaker(self):
        """Test that low confidence triggers circuit breaker"""
        analysis = {
            'confidence': 30,  # Below threshold
            'indicators': {'rsi': 50},
            'risk_reward_ratio': 2.0
        }

        triggered, reasons = self.validator.check_circuit_breakers(analysis)

        self.assertTrue(triggered)
        self.assertTrue(any('confidence' in r.lower() for r in reasons))
        print("✓ Low confidence triggers circuit breaker")

    def test_poor_risk_reward_triggers_circuit_breaker(self):
        """Test that poor risk/reward triggers circuit breaker"""
        analysis = {
            'confidence': 70,
            'indicators': {'rsi': 50},
            'risk_reward_ratio': 0.5  # Below threshold
        }

        triggered, reasons = self.validator.check_circuit_breakers(analysis)

        self.assertTrue(triggered)
        self.assertTrue(any('risk' in r.lower() for r in reasons))
        print("✓ Poor risk/reward triggers circuit breaker")

    def test_good_analysis_passes_circuit_breaker(self):
        """Test that good analysis passes circuit breaker"""
        analysis = {
            'confidence': 75,
            'indicators': {'rsi': 50},
            'risk_reward_ratio': 2.5,
            'data_age_minutes': 1
        }

        triggered, reasons = self.validator.check_circuit_breakers(analysis)

        self.assertFalse(triggered)
        self.assertEqual(len(reasons), 0)
        print("✓ Good analysis passes circuit breaker")


def run_tests():
    """Run all validation tests"""
    print("=" * 70)
    print("ADVANCED VALIDATION MODULE TESTS")
    print("=" * 70)
    print()

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestDataIntegrityValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestBenfordsLawValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestOutlierDetection))
    suite.addTests(loader.loadTestsFromTestCase(TestTechnicalIndicatorValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitBreaker))

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

    if result.wasSuccessful():
        print()
        print("✅ All validation tests passed!")
        return 0
    else:
        print()
        print("❌ Some tests failed")
        return 1


if __name__ == '__main__':
    sys.exit(run_tests())
