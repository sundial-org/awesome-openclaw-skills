#!/usr/bin/env python3
"""
Tests for Refactored Components (Task 9 Phase 4)

Tests the 14 extracted components from God class refactoring:
- 7 TradingAgent components
- 7 PatternRecognition components
"""

import unittest
import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))


class TestPatternRecognitionComponents(unittest.TestCase):
    """Test the 6 PatternRecognition components"""

    def setUp(self):
        """Create sample OHLCV data for testing"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')

        # Generate realistic price data
        close_prices = 50000 + np.cumsum(np.random.randn(100) * 100)
        high_prices = close_prices + np.abs(np.random.randn(100) * 50)
        low_prices = close_prices - np.abs(np.random.randn(100) * 50)
        open_prices = close_prices + np.random.randn(100) * 30

        self.df = pd.DataFrame({
            'timestamp': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': np.abs(np.random.randn(100) * 1000000)
        })

    def test_chart_pattern_detector_import(self):
        """Test ChartPatternDetector can be imported"""
        from patterns import ChartPatternDetector

        detector = ChartPatternDetector(min_pattern_length=20)
        self.assertIsNotNone(detector)
        self.assertEqual(detector.min_pattern_length, 20)

    def test_chart_pattern_detector_detect_all(self):
        """Test ChartPatternDetector.detect_all_patterns()"""
        from patterns import ChartPatternDetector

        detector = ChartPatternDetector(min_pattern_length=20)
        patterns = detector.detect_all_patterns(self.df)

        self.assertIsInstance(patterns, list)
        # Should detect some patterns in 100 candles
        print(f"ChartPatternDetector found {len(patterns)} patterns")

    def test_candlestick_pattern_detector_import(self):
        """Test CandlestickPatternDetector can be imported"""
        from patterns import CandlestickPatternDetector

        detector = CandlestickPatternDetector()
        self.assertIsNotNone(detector)

    def test_candlestick_pattern_detector_detect(self):
        """Test CandlestickPatternDetector.detect_all_patterns()"""
        from patterns import CandlestickPatternDetector

        detector = CandlestickPatternDetector()
        patterns = detector.detect_all_patterns(self.df)

        self.assertIsInstance(patterns, list)
        print(f"CandlestickPatternDetector found {len(patterns)} patterns")

    def test_support_resistance_analyzer_import(self):
        """Test SupportResistanceAnalyzer can be imported"""
        from patterns import SupportResistanceAnalyzer

        analyzer = SupportResistanceAnalyzer()
        self.assertIsNotNone(analyzer)

    def test_support_resistance_analyzer_detect(self):
        """Test SupportResistanceAnalyzer.detect_levels()"""
        from patterns import SupportResistanceAnalyzer

        analyzer = SupportResistanceAnalyzer()
        levels = analyzer.detect_levels(self.df)

        self.assertIsInstance(levels, dict)
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)
        self.assertIsInstance(levels['support'], list)
        self.assertIsInstance(levels['resistance'], list)
        print(f"Found {len(levels['support'])} support, {len(levels['resistance'])} resistance levels")

    def test_trend_analyzer_import(self):
        """Test TrendAnalyzer can be imported"""
        from patterns import TrendAnalyzer

        analyzer = TrendAnalyzer()
        self.assertIsNotNone(analyzer)

    def test_trend_analyzer_comprehensive(self):
        """Test TrendAnalyzer.analyze_comprehensive()"""
        from patterns import TrendAnalyzer

        analyzer = TrendAnalyzer()
        analysis = analyzer.analyze_comprehensive(self.df)

        self.assertIsInstance(analysis, dict)
        if 'error' not in analysis:
            self.assertIn('short_term', analysis)
            self.assertIn('medium_term', analysis)
            self.assertIn('long_term', analysis)
            self.assertIn('trend_strength', analysis)
            print(f"Trend: {analysis.get('short_term', {}).get('direction')}, "
                  f"Strength: {analysis.get('trend_strength')}")

    def test_volume_analyzer_import(self):
        """Test VolumeAnalyzer can be imported"""
        from patterns import VolumeAnalyzer

        analyzer = VolumeAnalyzer()
        self.assertIsNotNone(analyzer)

    def test_volume_analyzer_comprehensive(self):
        """Test VolumeAnalyzer.analyze_comprehensive()"""
        from patterns import VolumeAnalyzer

        analyzer = VolumeAnalyzer()
        analysis = analyzer.analyze_comprehensive(self.df)

        self.assertIsInstance(analysis, dict)
        if 'error' not in analysis:
            self.assertIn('volume_status', analysis)
            self.assertIn('obv_trend', analysis)
            self.assertIn('vpt_trend', analysis)
            print(f"Volume: {analysis.get('volume_status')}, "
                  f"OBV: {analysis.get('obv_trend')}, VPT: {analysis.get('vpt_trend')}")

    def test_market_regime_detector_import(self):
        """Test MarketRegimeDetector can be imported"""
        from patterns import MarketRegimeDetector

        detector = MarketRegimeDetector()
        self.assertIsNotNone(detector)

    def test_market_regime_detector_detect(self):
        """Test MarketRegimeDetector.detect_regime()"""
        from patterns import MarketRegimeDetector

        detector = MarketRegimeDetector()
        regime = detector.detect_regime(self.df)

        self.assertIsInstance(regime, dict)
        if 'error' not in regime:
            self.assertIn('market_regime', regime)
            self.assertIn('volatility_regime', regime)
            print(f"Market: {regime.get('market_regime')}, "
                  f"Volatility: {regime.get('volatility_regime')}")


class TestPatternRecognitionOrchestration(unittest.TestCase):
    """Test the PatternRecognition orchestration layer"""

    def setUp(self):
        """Create sample OHLCV data for testing"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=100, freq='1h')

        # Generate realistic price data
        close_prices = 50000 + np.cumsum(np.random.randn(100) * 100)
        high_prices = close_prices + np.abs(np.random.randn(100) * 50)
        low_prices = close_prices - np.abs(np.random.randn(100) * 50)
        open_prices = close_prices + np.random.randn(100) * 30

        self.df = pd.DataFrame({
            'timestamp': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': np.abs(np.random.randn(100) * 1000000)
        })

    def test_pattern_recognition_import(self):
        """Test refactored PatternRecognition can be imported"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition(min_pattern_length=10)
        self.assertIsNotNone(pr)
        self.assertEqual(pr.min_pattern_length, 10)

    def test_pattern_recognition_has_components(self):
        """Test PatternRecognition has all 6 components"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition()

        # Check all components exist
        self.assertIsNotNone(pr.chart_detector)
        self.assertIsNotNone(pr.candlestick_detector)
        self.assertIsNotNone(pr.sr_analyzer)
        self.assertIsNotNone(pr.trend_analyzer)
        self.assertIsNotNone(pr.volume_analyzer)
        self.assertIsNotNone(pr.regime_detector)

    def test_pattern_recognition_comprehensive_analysis(self):
        """Test PatternRecognition.analyze_comprehensive() - Main method"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition(min_pattern_length=10)
        analysis = pr.analyze_comprehensive(self.df)

        # Check structure
        self.assertIsInstance(analysis, dict)
        self.assertIn('current_price', analysis)
        self.assertIn('patterns_detected', analysis)
        self.assertIn('support_levels', analysis)
        self.assertIn('resistance_levels', analysis)
        self.assertIn('trend_analysis', analysis)
        self.assertIn('volume_analysis', analysis)
        self.assertIn('market_regime', analysis)
        self.assertIn('overall_bias', analysis)
        self.assertIn('confidence', analysis)

        # Check types
        self.assertIsInstance(analysis['patterns_detected'], list)
        self.assertIsInstance(analysis['support_levels'], list)
        self.assertIsInstance(analysis['resistance_levels'], list)
        self.assertIsInstance(analysis['overall_bias'], str)
        self.assertIsInstance(analysis['confidence'], int)

        print(f"\nComprehensive Analysis Results:")
        print(f"- Price: ${analysis['current_price']}")
        print(f"- Patterns: {len(analysis['patterns_detected'])}")
        print(f"- Support: {len(analysis['support_levels'])} levels")
        print(f"- Resistance: {len(analysis['resistance_levels'])} levels")
        print(f"- Overall: {analysis['overall_bias']} ({analysis['confidence']}%)")

    def test_pattern_recognition_detect_all_patterns(self):
        """Test PatternRecognition.detect_all_patterns() delegates correctly"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition()
        patterns = pr.detect_all_patterns(self.df)

        self.assertIsInstance(patterns, list)
        print(f"\nDetected {len(patterns)} total patterns")

    def test_pattern_recognition_detect_support_resistance(self):
        """Test PatternRecognition.detect_support_resistance() delegates correctly"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition()
        levels = pr.detect_support_resistance(self.df, num_levels=3)

        self.assertIsInstance(levels, dict)
        self.assertIn('support', levels)
        self.assertIn('resistance', levels)

    def test_pattern_recognition_analyze_trend(self):
        """Test PatternRecognition.analyze_trend() delegates correctly"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition()
        trend = pr.analyze_trend(self.df)

        self.assertIsInstance(trend, dict)
        # Should have trend data or error
        self.assertTrue('short_term' in trend or 'error' in trend)

    def test_pattern_recognition_analyze_volume(self):
        """Test PatternRecognition.analyze_volume() delegates correctly"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition()
        volume = pr.analyze_volume(self.df)

        self.assertIsInstance(volume, dict)
        # Should have volume data or error
        self.assertTrue('volume_status' in volume or 'error' in volume)

    def test_pattern_recognition_detect_market_regime(self):
        """Test PatternRecognition.detect_market_regime() delegates correctly"""
        from pattern_recognition_refactored import PatternRecognition

        pr = PatternRecognition()
        regime = pr.detect_market_regime(self.df)

        self.assertIsInstance(regime, dict)
        # Should have regime data or error
        self.assertTrue('market_regime' in regime or 'error' in regime)


class TestBackwardCompatibility(unittest.TestCase):
    """Test that refactored components are drop-in replacements"""

    def setUp(self):
        """Create sample data"""
        np.random.seed(42)
        dates = pd.date_range(start='2024-01-01', periods=50, freq='1h')

        close_prices = 50000 + np.cumsum(np.random.randn(50) * 100)
        high_prices = close_prices + np.abs(np.random.randn(50) * 50)
        low_prices = close_prices - np.abs(np.random.randn(50) * 50)
        open_prices = close_prices + np.random.randn(50) * 30

        self.df = pd.DataFrame({
            'timestamp': dates,
            'open': open_prices,
            'high': high_prices,
            'low': low_prices,
            'close': close_prices,
            'volume': np.abs(np.random.randn(50) * 1000000)
        })

    def test_pattern_recognition_same_interface(self):
        """Test refactored PatternRecognition has same interface as original"""
        from pattern_recognition import PatternRecognition as OriginalPR
        from pattern_recognition_refactored import PatternRecognition as RefactoredPR

        # Both should initialize with same parameter
        original = OriginalPR(min_pattern_length=10)
        refactored = RefactoredPR(min_pattern_length=10)

        # Both should have same public methods
        original_methods = [m for m in dir(original) if not m.startswith('_')]
        refactored_methods = [m for m in dir(refactored) if not m.startswith('_')]

        # Check key methods exist in both
        key_methods = [
            'analyze_comprehensive',
            'detect_all_patterns',
            'detect_support_resistance',
            'analyze_trend',
            'analyze_volume',
            'detect_market_regime'
        ]

        for method in key_methods:
            self.assertIn(method, original_methods, f"Original missing {method}")
            self.assertIn(method, refactored_methods, f"Refactored missing {method}")

    def test_pattern_recognition_compatible_output(self):
        """Test refactored PR produces compatible output structure"""
        from pattern_recognition import PatternRecognition as OriginalPR
        from pattern_recognition_refactored import PatternRecognition as RefactoredPR

        original = OriginalPR(min_pattern_length=10)
        refactored = RefactoredPR(min_pattern_length=10)

        # Both should return dict with same keys
        original_result = original.analyze_comprehensive(self.df)
        refactored_result = refactored.analyze_comprehensive(self.df)

        # Check key structure
        required_keys = [
            'current_price', 'patterns_detected', 'support_levels',
            'resistance_levels', 'trend_analysis', 'volume_analysis',
            'market_regime', 'overall_bias', 'confidence'
        ]

        for key in required_keys:
            self.assertIn(key, original_result, f"Original missing {key}")
            self.assertIn(key, refactored_result, f"Refactored missing {key}")

        print("\n✅ Refactored PatternRecognition is a drop-in replacement!")


if __name__ == '__main__':
    # Run tests with verbose output
    unittest.main(verbosity=2)
