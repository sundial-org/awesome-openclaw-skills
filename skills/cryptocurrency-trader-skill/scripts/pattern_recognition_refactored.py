#!/usr/bin/env python3
"""
Pattern Recognition - Refactored with Composition-Based Architecture

Drop-in replacement for original PatternRecognition class.
Uses composition to orchestrate specialized pattern detection components.

SOLID Principles Applied:
- Single Responsibility: Each component has one focused purpose
- Dependency Injection: All components injected
- Composition over Inheritance: Components composed, not inherited
"""

import pandas as pd
from typing import Dict, List
import logging

# Import extracted components
from patterns import (
    ChartPatternDetector,
    CandlestickPatternDetector,
    SupportResistanceAnalyzer,
    TrendAnalyzer,
    VolumeAnalyzer,
    MarketRegimeDetector
)

logger = logging.getLogger(__name__)


class PatternRecognition:
    """
    Refactored Pattern Recognition - Composition-Based Architecture

    Orchestrates 6 specialized components:
    1. ChartPatternDetector - Chart patterns (double top/bottom, H&S, wedges, etc.)
    2. CandlestickPatternDetector - Candlestick patterns (doji, hammer, engulfing, etc.)
    3. SupportResistanceAnalyzer - Support/resistance levels
    4. TrendAnalyzer - Multi-timeframe trend analysis
    5. VolumeAnalyzer - Volume analysis (OBV, VPT)
    6. MarketRegimeDetector - Market regime (trending vs ranging)

    This is a drop-in replacement for the original PatternRecognition class.
    All method signatures remain the same for backward compatibility.
    """

    def __init__(self, min_pattern_length: int = 10):
        """
        Initialize pattern recognition engine with composition-based architecture

        Args:
            min_pattern_length: Minimum candles required for pattern detection
        """
        if not isinstance(min_pattern_length, int) or min_pattern_length < 5:
            raise ValueError(f"min_pattern_length must be >= 5, got {min_pattern_length}")

        self.min_pattern_length = min_pattern_length
        self.detected_patterns = []

        # Initialize all specialized components via dependency injection
        self.chart_detector = ChartPatternDetector(
            min_pattern_length=min_pattern_length,
            similarity_threshold=0.02
        )

        self.candlestick_detector = CandlestickPatternDetector(
            doji_threshold=0.1,
            wick_body_ratio=2.0
        )

        self.sr_analyzer = SupportResistanceAnalyzer(
            clustering_threshold=0.02,
            min_distance=3,
            default_num_levels=3
        )

        self.trend_analyzer = TrendAnalyzer(
            short_term_period=10,
            medium_term_period=20,
            strength_period=14
        )

        self.volume_analyzer = VolumeAnalyzer(
            recent_period=10,
            high_volume_threshold=1.5,
            low_volume_threshold=0.7
        )

        self.regime_detector = MarketRegimeDetector(
            trending_threshold=0.3,
            high_vol_threshold=1.3,
            low_vol_threshold=0.7
        )

        logger.info(
            f"Initialized PatternRecognition (refactored) with "
            f"6 specialized components, min_length={min_pattern_length}"
        )

    def analyze_comprehensive(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive pattern analysis combining multiple detection methods

        5-Layer Analysis:
        1. Chart Pattern Detection (double top/bottom, H&S, wedges, triangles, flags)
        2. Support & Resistance levels
        3. Multi-timeframe Trend Analysis
        4. Volume Analysis (OBV, VPT)
        5. Market Regime Detection

        Args:
            df: DataFrame with OHLCV data (must have timestamp, open, high, low, close, volume)

        Returns:
            Dictionary with comprehensive analysis:
            - timestamp: Analysis timestamp
            - current_price: Current price
            - patterns_detected: List of detected patterns
            - support_levels: Support price levels
            - resistance_levels: Resistance price levels
            - trend_analysis: Multi-timeframe trend info
            - volume_analysis: Volume metrics and trends
            - market_regime: Market regime info
            - overall_bias: BULLISH/BEARISH/NEUTRAL
            - confidence: Confidence score (0-100)
        """
        if df is None or df.empty:
            logger.error("Empty dataframe provided to analyze_comprehensive")
            return {'error': 'Empty dataframe'}

        if len(df) < self.min_pattern_length:
            logger.warning(f"Insufficient data: {len(df)} < {self.min_pattern_length}")
            return {'error': f'Insufficient data (need {self.min_pattern_length}+ candles)'}

        try:
            # Initialize analysis result
            analysis = {
                'timestamp': df['timestamp'].iloc[-1] if 'timestamp' in df.columns else None,
                'current_price': round(df['close'].iloc[-1], 2),
                'patterns_detected': [],
                'support_levels': [],
                'resistance_levels': [],
                'trend_analysis': {},
                'volume_analysis': {},
                'market_regime': {},
                'overall_bias': 'NEUTRAL',
                'confidence': 0
            }

            # Layer 1: Chart Pattern Detection
            logger.debug("Layer 1: Detecting chart patterns...")
            patterns = self.detect_all_patterns(df)
            analysis['patterns_detected'] = patterns
            logger.info(f"Detected {len(patterns)} patterns")

            # Layer 2: Support & Resistance
            logger.debug("Layer 2: Detecting support/resistance levels...")
            sr_levels = self.detect_support_resistance(df)
            analysis['support_levels'] = sr_levels.get('support', [])
            analysis['resistance_levels'] = sr_levels.get('resistance', [])
            logger.info(
                f"Detected {len(analysis['support_levels'])} support, "
                f"{len(analysis['resistance_levels'])} resistance levels"
            )

            # Layer 3: Trend Analysis
            logger.debug("Layer 3: Analyzing trends...")
            trend = self.analyze_trend(df)
            analysis['trend_analysis'] = trend
            if not trend.get('error'):
                logger.info(
                    f"Trend: {trend['short_term']['direction']}, "
                    f"Strength: {trend['trend_strength']}"
                )

            # Layer 4: Volume Analysis
            logger.debug("Layer 4: Analyzing volume...")
            volume = self.analyze_volume(df)
            analysis['volume_analysis'] = volume
            if not volume.get('error'):
                logger.info(
                    f"Volume: {volume['volume_status']}, "
                    f"OBV: {volume['obv_trend']}, VPT: {volume['vpt_trend']}"
                )

            # Layer 5: Market Regime Detection
            logger.debug("Layer 5: Detecting market regime...")
            regime = self.detect_market_regime(df)
            analysis['market_regime'] = regime
            if not regime.get('error'):
                logger.info(
                    f"Regime: {regime['market_regime']}, "
                    f"Volatility: {regime['volatility_regime']}"
                )

            # Synthesize overall bias
            logger.debug("Synthesizing overall bias...")
            bias_synthesis = self._synthesize_bias(patterns, trend, volume, regime)
            analysis['overall_bias'] = bias_synthesis['bias']
            analysis['confidence'] = bias_synthesis['confidence']

            logger.info(
                f"Analysis complete: {analysis['overall_bias']} "
                f"with {analysis['confidence']}% confidence"
            )

            return analysis

        except Exception as e:
            logger.error(f"Error in comprehensive analysis: {e}")
            return {'error': str(e)}

    def detect_all_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect all chart and candlestick patterns

        Delegates to specialized detectors:
        - ChartPatternDetector: Chart patterns
        - CandlestickPatternDetector: Candlestick patterns

        Args:
            df: DataFrame with OHLCV data

        Returns:
            List of detected patterns with metadata
        """
        if df is None or df.empty:
            return []

        patterns = []

        try:
            # Chart patterns (double top/bottom, H&S, wedges, triangles, flags)
            chart_patterns = self.chart_detector.detect_all_patterns(df)
            patterns.extend(chart_patterns)

            # Candlestick patterns (doji, hammer, engulfing, etc.)
            candlestick_patterns = self.candlestick_detector.detect_all_patterns(df)
            patterns.extend(candlestick_patterns)

            logger.debug(
                f"Detected {len(chart_patterns)} chart patterns, "
                f"{len(candlestick_patterns)} candlestick patterns"
            )

        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")

        return patterns

    def detect_support_resistance(self, df: pd.DataFrame, num_levels: int = 3) -> Dict:
        """
        Detect key support and resistance levels

        Delegates to SupportResistanceAnalyzer.

        Args:
            df: DataFrame with OHLCV data
            num_levels: Number of levels to return

        Returns:
            Dictionary with 'support' and 'resistance' lists
        """
        if df is None or df.empty:
            return {'support': [], 'resistance': []}

        try:
            return self.sr_analyzer.detect_levels(df, num_levels)
        except Exception as e:
            logger.error(f"Error detecting support/resistance: {e}")
            return {'support': [], 'resistance': []}

    def analyze_trend(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive trend analysis with multiple timeframes

        Delegates to TrendAnalyzer.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with trend analysis for all timeframes
        """
        if df is None or df.empty or len(df) < 20:
            return {'error': 'Insufficient data for trend analysis'}

        try:
            return self.trend_analyzer.analyze_comprehensive(df)
        except Exception as e:
            logger.error(f"Error analyzing trend: {e}")
            return {'error': str(e)}

    def analyze_volume(self, df: pd.DataFrame) -> Dict:
        """
        Advanced volume analysis

        Delegates to VolumeAnalyzer.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with volume analysis (OBV, VPT, status)
        """
        if df is None or df.empty or len(df) < 20:
            return {'error': 'Insufficient data for volume analysis'}

        try:
            return self.volume_analyzer.analyze_comprehensive(df)
        except Exception as e:
            logger.error(f"Error analyzing volume: {e}")
            return {'error': str(e)}

    def detect_market_regime(self, df: pd.DataFrame) -> Dict:
        """
        Detect current market regime (trending vs ranging)

        Delegates to MarketRegimeDetector.

        Args:
            df: DataFrame with OHLCV data

        Returns:
            Dictionary with market regime and volatility info
        """
        if df is None or df.empty or len(df) < 30:
            return {'error': 'Insufficient data for regime detection'}

        try:
            return self.regime_detector.detect_regime(df)
        except Exception as e:
            logger.error(f"Error detecting market regime: {e}")
            return {'error': str(e)}

    def _synthesize_bias(
        self,
        patterns: List[Dict],
        trend: Dict,
        volume: Dict,
        regime: Dict
    ) -> Dict:
        """
        Synthesize overall market bias from all analyses

        Scoring system:
        - Patterns: Add confidence score for each bullish/bearish pattern
        - Trend: +30 for short-term direction, +20 for alignment
        - Volume: +15 for high volume confirmation
        - Final: Calculate confidence as percentage of total score

        Args:
            patterns: List of detected patterns
            trend: Trend analysis dictionary
            volume: Volume analysis dictionary
            regime: Market regime dictionary

        Returns:
            Dictionary with overall bias and confidence:
            - bias: 'BULLISH', 'BEARISH', or 'NEUTRAL'
            - confidence: Confidence score (0-100, capped at 95)
        """
        try:
            bullish_score = 0
            bearish_score = 0

            # Pattern bias: Sum confidence scores
            for pattern in patterns:
                if pattern.get('bias') == 'BULLISH':
                    bullish_score += pattern.get('confidence', 50)
                elif pattern.get('bias') == 'BEARISH':
                    bearish_score += pattern.get('confidence', 50)

            # Trend bias
            if not trend.get('error'):
                if trend.get('short_term', {}).get('direction') == 'UPTREND':
                    bullish_score += 30
                elif trend.get('short_term', {}).get('direction') == 'DOWNTREND':
                    bearish_score += 30

                # Trend alignment bonus
                if trend.get('aligned'):
                    if trend.get('short_term', {}).get('direction') == 'UPTREND':
                        bullish_score += 20
                    elif trend.get('short_term', {}).get('direction') == 'DOWNTREND':
                        bearish_score += 20

            # Volume confirmation: High volume on strong direction
            if not volume.get('error'):
                if volume.get('confirmation') and volume.get('volume_status') == 'HIGH':
                    # Add 15 to the current leading direction
                    if bullish_score > bearish_score:
                        bullish_score += 15
                    else:
                        bearish_score += 15

            # Calculate final bias
            total_score = bullish_score + bearish_score

            if total_score == 0:
                return {'bias': 'NEUTRAL', 'confidence': 0}

            if bullish_score > bearish_score:
                confidence = int((bullish_score / total_score) * 100)
                return {'bias': 'BULLISH', 'confidence': min(confidence, 95)}
            elif bearish_score > bullish_score:
                confidence = int((bearish_score / total_score) * 100)
                return {'bias': 'BEARISH', 'confidence': min(confidence, 95)}
            else:
                return {'bias': 'NEUTRAL', 'confidence': 50}

        except Exception as e:
            logger.error(f"Error synthesizing bias: {e}")
            return {'bias': 'NEUTRAL', 'confidence': 0}
