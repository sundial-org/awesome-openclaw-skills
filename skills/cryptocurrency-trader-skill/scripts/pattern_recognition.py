#!/usr/bin/env python3
"""
Advanced Chart Pattern Recognition and Technical Analysis Module
Implements sophisticated pattern detection with mathematical validation
"""

import pandas as pd
import numpy as np
from scipy import signal
from scipy.stats import linregress
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')


class PatternRecognition:
    """
    Advanced chart pattern recognition with mathematical rigor
    Detects reversal and continuation patterns with confidence scores
    """

    def __init__(self, min_pattern_length: int = 10):
        """
        Initialize pattern recognition engine

        Args:
            min_pattern_length: Minimum candles required for pattern detection
        """
        self.min_pattern_length = min_pattern_length
        self.detected_patterns = []

    def analyze_comprehensive(self, df: pd.DataFrame) -> Dict:
        """
        Comprehensive pattern analysis combining multiple detection methods
        Returns consolidated analysis with confidence scores
        """
        if len(df) < self.min_pattern_length:
            return {'error': f'Insufficient data (need {self.min_pattern_length}+ candles)'}

        analysis = {
            'timestamp': df['timestamp'].iloc[-1],
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
        patterns = self.detect_all_patterns(df)
        analysis['patterns_detected'] = patterns

        # Layer 2: Support & Resistance
        sr_levels = self.detect_support_resistance(df)
        analysis['support_levels'] = sr_levels['support']
        analysis['resistance_levels'] = sr_levels['resistance']

        # Layer 3: Trend Analysis
        trend = self.analyze_trend(df)
        analysis['trend_analysis'] = trend

        # Layer 4: Volume Analysis
        volume = self.analyze_volume(df)
        analysis['volume_analysis'] = volume

        # Layer 5: Market Regime Detection
        regime = self.detect_market_regime(df)
        analysis['market_regime'] = regime

        # Synthesize overall bias
        bias_synthesis = self._synthesize_bias(patterns, trend, volume, regime)
        analysis['overall_bias'] = bias_synthesis['bias']
        analysis['confidence'] = bias_synthesis['confidence']

        return analysis

    def detect_all_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect all chart patterns"""
        patterns = []

        # Reversal patterns
        patterns.extend(self._detect_double_top_bottom(df))
        patterns.extend(self._detect_head_and_shoulders(df))
        patterns.extend(self._detect_wedges(df))

        # Continuation patterns
        patterns.extend(self._detect_flags_pennants(df))
        patterns.extend(self._detect_triangles(df))

        # Candlestick patterns
        patterns.extend(self._detect_candlestick_patterns(df))

        return patterns

    def _detect_double_top_bottom(self, df: pd.DataFrame) -> List[Dict]:
        """Detect double top/bottom patterns"""
        patterns = []

        if len(df) < 30:
            return patterns

        # Find peaks and troughs using signal processing
        prices = df['close'].values
        peaks, _ = signal.find_peaks(prices, distance=5)
        troughs, _ = signal.find_peaks(-prices, distance=5)

        # Double Top detection
        if len(peaks) >= 2:
            for i in range(len(peaks) - 1):
                peak1_idx = peaks[i]
                peak2_idx = peaks[i + 1]

                peak1_price = prices[peak1_idx]
                peak2_price = prices[peak2_idx]

                # Peaks should be similar (within 2%)
                # Protect against division by zero with price check
                if peak1_price > 0 and abs(peak1_price - peak2_price) / peak1_price < 0.02:
                    # Find trough between peaks
                    between_troughs = [t for t in troughs if peak1_idx < t < peak2_idx]

                    if between_troughs:
                        trough_price = prices[between_troughs[0]]
                        decline_pct = (peak1_price - trough_price) / peak1_price * 100

                        if decline_pct > 3:  # At least 3% decline between peaks
                            current_price = prices[-1]
                            neckline = trough_price

                            # Pattern is confirmed if price breaks neckline
                            confirmed = current_price < neckline

                            patterns.append({
                                'pattern': 'Double Top',
                                'type': 'REVERSAL',
                                'bias': 'BEARISH',
                                'confirmed': confirmed,
                                'confidence': 75 if confirmed else 50,
                                'peak_price': round(peak1_price, 2),
                                'neckline': round(neckline, 2),
                                'target': round(neckline - decline_pct / 100 * peak1_price, 2),
                                'formed_at': df['timestamp'].iloc[peak2_idx]
                            })

        # Double Bottom detection
        if len(troughs) >= 2:
            for i in range(len(troughs) - 1):
                trough1_idx = troughs[i]
                trough2_idx = troughs[i + 1]

                trough1_price = prices[trough1_idx]
                trough2_price = prices[trough2_idx]

                # Troughs should be similar (within 2%)
                # Protect against division by zero with price check
                if trough1_price > 0 and abs(trough1_price - trough2_price) / trough1_price < 0.02:
                    # Find peak between troughs
                    between_peaks = [p for p in peaks if trough1_idx < p < trough2_idx]

                    if between_peaks:
                        peak_price = prices[between_peaks[0]]
                        rise_pct = (peak_price - trough1_price) / trough1_price * 100

                        if rise_pct > 3:
                            current_price = prices[-1]
                            neckline = peak_price

                            # Pattern is confirmed if price breaks neckline
                            confirmed = current_price > neckline

                            patterns.append({
                                'pattern': 'Double Bottom',
                                'type': 'REVERSAL',
                                'bias': 'BULLISH',
                                'confirmed': confirmed,
                                'confidence': 75 if confirmed else 50,
                                'bottom_price': round(trough1_price, 2),
                                'neckline': round(neckline, 2),
                                'target': round(neckline + rise_pct / 100 * trough1_price, 2),
                                'formed_at': df['timestamp'].iloc[trough2_idx]
                            })

        return patterns

    def _detect_head_and_shoulders(self, df: pd.DataFrame) -> List[Dict]:
        """Detect head and shoulders patterns"""
        patterns = []

        if len(df) < 50:
            return patterns

        prices = df['close'].values
        peaks, _ = signal.find_peaks(prices, distance=10, prominence=prices.std())

        # Need at least 3 peaks for H&S
        if len(peaks) >= 3:
            for i in range(len(peaks) - 2):
                left_shoulder_idx = peaks[i]
                head_idx = peaks[i + 1]
                right_shoulder_idx = peaks[i + 2]

                ls_price = prices[left_shoulder_idx]
                head_price = prices[head_idx]
                rs_price = prices[right_shoulder_idx]

                # Head should be higher than shoulders
                # Shoulders should be approximately equal (within 3%)
                # Protect against division by zero with price check
                if (head_price > ls_price and head_price > rs_price and
                    ls_price > 0 and abs(ls_price - rs_price) / ls_price < 0.03):

                    # Calculate neckline (line connecting troughs between peaks)
                    neckline_price = min(prices[left_shoulder_idx:head_idx].min(),
                                       prices[head_idx:right_shoulder_idx].min())

                    current_price = prices[-1]
                    confirmed = current_price < neckline_price

                    head_to_neckline = head_price - neckline_price
                    target = neckline_price - head_to_neckline

                    patterns.append({
                        'pattern': 'Head and Shoulders',
                        'type': 'REVERSAL',
                        'bias': 'BEARISH',
                        'confirmed': confirmed,
                        'confidence': 80 if confirmed else 55,
                        'head_price': round(head_price, 2),
                        'left_shoulder': round(ls_price, 2),
                        'right_shoulder': round(rs_price, 2),
                        'neckline': round(neckline_price, 2),
                        'target': round(target, 2),
                        'formed_at': df['timestamp'].iloc[right_shoulder_idx]
                    })

        # Inverse Head and Shoulders
        troughs, _ = signal.find_peaks(-prices, distance=10, prominence=prices.std())

        if len(troughs) >= 3:
            for i in range(len(troughs) - 2):
                left_shoulder_idx = troughs[i]
                head_idx = troughs[i + 1]
                right_shoulder_idx = troughs[i + 2]

                ls_price = prices[left_shoulder_idx]
                head_price = prices[head_idx]
                rs_price = prices[right_shoulder_idx]

                # Protect against division by zero with price check
                if (head_price < ls_price and head_price < rs_price and
                    ls_price > 0 and abs(ls_price - rs_price) / ls_price < 0.03):

                    neckline_price = max(prices[left_shoulder_idx:head_idx].max(),
                                       prices[head_idx:right_shoulder_idx].max())

                    current_price = prices[-1]
                    confirmed = current_price > neckline_price

                    neckline_to_head = neckline_price - head_price
                    target = neckline_price + neckline_to_head

                    patterns.append({
                        'pattern': 'Inverse Head and Shoulders',
                        'type': 'REVERSAL',
                        'bias': 'BULLISH',
                        'confirmed': confirmed,
                        'confidence': 80 if confirmed else 55,
                        'head_price': round(head_price, 2),
                        'left_shoulder': round(ls_price, 2),
                        'right_shoulder': round(rs_price, 2),
                        'neckline': round(neckline_price, 2),
                        'target': round(target, 2),
                        'formed_at': df['timestamp'].iloc[right_shoulder_idx]
                    })

        return patterns

    def _detect_wedges(self, df: pd.DataFrame) -> List[Dict]:
        """Detect rising and falling wedge patterns"""
        patterns = []

        if len(df) < 30:
            return patterns

        # Use last 30 candles for wedge detection
        recent_df = df.tail(30)

        # Fit trendlines to highs and lows
        highs = recent_df['high'].values
        lows = recent_df['low'].values
        x = np.arange(len(highs))

        # Upper trendline (highs)
        upper_slope, upper_intercept, _, _, _ = linregress(x, highs)

        # Lower trendline (lows)
        lower_slope, lower_intercept, _, _, _ = linregress(x, lows)

        # Rising Wedge: Both lines rising, but converging (bearish)
        if upper_slope > 0 and lower_slope > 0 and lower_slope > upper_slope:
            patterns.append({
                'pattern': 'Rising Wedge',
                'type': 'REVERSAL',
                'bias': 'BEARISH',
                'confirmed': False,
                'confidence': 60,
                'description': 'Prices rising but losing momentum - potential reversal down'
            })

        # Falling Wedge: Both lines falling, but converging (bullish)
        elif upper_slope < 0 and lower_slope < 0 and upper_slope < lower_slope:
            patterns.append({
                'pattern': 'Falling Wedge',
                'type': 'REVERSAL',
                'bias': 'BULLISH',
                'confirmed': False,
                'confidence': 60,
                'description': 'Prices falling but losing momentum - potential reversal up'
            })

        return patterns

    def _detect_flags_pennants(self, df: pd.DataFrame) -> List[Dict]:
        """Detect flag and pennant continuation patterns"""
        patterns = []

        if len(df) < 20:
            return patterns

        # Flags and pennants follow strong trends
        recent_returns = df['close'].pct_change().tail(20)

        # Look for strong move followed by consolidation
        first_half = recent_returns.head(10)
        second_half = recent_returns.tail(10)

        first_half_trend = first_half.sum()
        second_half_volatility = second_half.std()

        # Strong initial move (>5%)
        if abs(first_half_trend) > 0.05:
            # Followed by low volatility consolidation (<1%)
            if second_half_volatility < 0.01:
                bias = 'BULLISH' if first_half_trend > 0 else 'BEARISH'

                patterns.append({
                    'pattern': 'Flag' if second_half_volatility < 0.005 else 'Pennant',
                    'type': 'CONTINUATION',
                    'bias': bias,
                    'confirmed': False,
                    'confidence': 65,
                    'description': f'Consolidation after strong move - expect {bias.lower()} continuation'
                })

        return patterns

    def _detect_triangles(self, df: pd.DataFrame) -> List[Dict]:
        """Detect triangle patterns (ascending, descending, symmetrical)"""
        patterns = []

        if len(df) < 20:
            return patterns

        recent_df = df.tail(20)
        highs = recent_df['high'].values
        lows = recent_df['low'].values
        x = np.arange(len(highs))

        # Fit trendlines
        high_slope, _, _, _, _ = linregress(x, highs)
        low_slope, _, _, _, _ = linregress(x, lows)

        # Ascending Triangle: Flat resistance, rising support (bullish)
        if abs(high_slope) < 0.01 and low_slope > 0.01:
            patterns.append({
                'pattern': 'Ascending Triangle',
                'type': 'CONTINUATION',
                'bias': 'BULLISH',
                'confirmed': False,
                'confidence': 70,
                'description': 'Buyers pushing higher lows against resistance'
            })

        # Descending Triangle: Flat support, falling resistance (bearish)
        elif abs(low_slope) < 0.01 and high_slope < -0.01:
            patterns.append({
                'pattern': 'Descending Triangle',
                'type': 'CONTINUATION',
                'bias': 'BEARISH',
                'confirmed': False,
                'confidence': 70,
                'description': 'Sellers pushing lower highs against support'
            })

        # Symmetrical Triangle: Both converging (direction uncertain)
        elif abs(high_slope + low_slope) < 0.01 and high_slope < 0 and low_slope > 0:
            patterns.append({
                'pattern': 'Symmetrical Triangle',
                'type': 'CONTINUATION',
                'bias': 'NEUTRAL',
                'confirmed': False,
                'confidence': 55,
                'description': 'Consolidation - breakout direction uncertain'
            })

        return patterns

    def _detect_candlestick_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """Detect key candlestick patterns"""
        patterns = []

        if len(df) < 3:
            return patterns

        # Get last 3 candles
        last_3 = df.tail(3)

        # Calculate candle properties
        for idx, row in last_3.iterrows():
            body = abs(row['close'] - row['open'])
            upper_wick = row['high'] - max(row['open'], row['close'])
            lower_wick = min(row['open'], row['close']) - row['low']
            total_range = row['high'] - row['low']

            # Doji: Small body, significant wicks
            if total_range > 0 and body / total_range < 0.1:
                patterns.append({
                    'pattern': 'Doji',
                    'type': 'REVERSAL',
                    'bias': 'NEUTRAL',
                    'confidence': 45,
                    'description': 'Indecision - potential trend change'
                })

            # Hammer: Small body at top, long lower wick (bullish)
            if total_range > 0 and lower_wick > 2 * body and upper_wick < body:
                patterns.append({
                    'pattern': 'Hammer',
                    'type': 'REVERSAL',
                    'bias': 'BULLISH',
                    'confidence': 60,
                    'description': 'Rejection of lower prices - bullish reversal'
                })

            # Shooting Star: Small body at bottom, long upper wick (bearish)
            if total_range > 0 and upper_wick > 2 * body and lower_wick < body:
                patterns.append({
                    'pattern': 'Shooting Star',
                    'type': 'REVERSAL',
                    'bias': 'BEARISH',
                    'confidence': 60,
                    'description': 'Rejection of higher prices - bearish reversal'
                })

        # Engulfing patterns (need 2 candles)
        if len(last_3) >= 2:
            prev = last_3.iloc[-2]
            curr = last_3.iloc[-1]

            prev_body = abs(prev['close'] - prev['open'])
            curr_body = abs(curr['close'] - curr['open'])

            # Bullish Engulfing
            if (prev['close'] < prev['open'] and  # Previous bearish
                curr['close'] > curr['open'] and  # Current bullish
                curr_body > prev_body):           # Current engulfs previous
                patterns.append({
                    'pattern': 'Bullish Engulfing',
                    'type': 'REVERSAL',
                    'bias': 'BULLISH',
                    'confidence': 70,
                    'description': 'Strong bullish reversal signal'
                })

            # Bearish Engulfing
            if (prev['close'] > prev['open'] and  # Previous bullish
                curr['close'] < curr['open'] and  # Current bearish
                curr_body > prev_body):           # Current engulfs previous
                patterns.append({
                    'pattern': 'Bearish Engulfing',
                    'type': 'REVERSAL',
                    'bias': 'BEARISH',
                    'confidence': 70,
                    'description': 'Strong bearish reversal signal'
                })

        return patterns

    def detect_support_resistance(self, df: pd.DataFrame, num_levels: int = 3) -> Dict:
        """Detect key support and resistance levels using clustering"""
        if len(df) < 20:
            return {'support': [], 'resistance': []}

        prices = df['close'].values
        highs = df['high'].values
        lows = df['low'].values

        # Find peaks and troughs
        peaks, _ = signal.find_peaks(highs, distance=3)
        troughs, _ = signal.find_peaks(-lows, distance=3)

        # Cluster resistance levels (peaks)
        resistance_prices = highs[peaks] if len(peaks) > 0 else []

        # Cluster support levels (troughs)
        support_prices = lows[troughs] if len(troughs) > 0 else []

        # Get unique levels (cluster similar prices)
        resistance_levels = self._cluster_levels(resistance_prices, num_levels)
        support_levels = self._cluster_levels(support_prices, num_levels)

        return {
            'support': [round(level, 2) for level in support_levels],
            'resistance': [round(level, 2) for level in resistance_levels]
        }

    def _cluster_levels(self, prices: np.ndarray, num_levels: int) -> List[float]:
        """Cluster price levels to find key support/resistance"""
        if len(prices) == 0:
            return []

        # Simple clustering: group prices within 2% of each other
        clustered = []
        sorted_prices = sorted(prices, reverse=True)

        for price in sorted_prices:
            # Check if this price is similar to any existing cluster
            similar = False
            for cluster_price in clustered:
                # Protect against division by zero with price check
                if cluster_price > 0 and abs(price - cluster_price) / cluster_price < 0.02:
                    similar = True
                    break

            if not similar:
                clustered.append(price)

            if len(clustered) >= num_levels:
                break

        return clustered

    def analyze_trend(self, df: pd.DataFrame) -> Dict:
        """Comprehensive trend analysis with multiple timeframes"""
        if len(df) < 20:
            return {'error': 'Insufficient data for trend analysis'}

        prices = df['close'].values

        # Short-term trend (last 10 candles)
        short_term = self._calculate_trend(prices[-10:])

        # Medium-term trend (last 20 candles)
        medium_term = self._calculate_trend(prices[-20:]) if len(prices) >= 20 else short_term

        # Long-term trend (all data)
        long_term = self._calculate_trend(prices)

        # Calculate trend strength using ADX-like measure
        trend_strength = self._calculate_trend_strength(df)

        return {
            'short_term': short_term,
            'medium_term': medium_term,
            'long_term': long_term,
            'trend_strength': trend_strength,
            'aligned': short_term['direction'] == medium_term['direction'] == long_term['direction']
        }

    def _calculate_trend(self, prices: np.ndarray) -> Dict:
        """Calculate trend for price series"""
        x = np.arange(len(prices))
        slope, intercept, r_value, _, _ = linregress(x, prices)

        # Determine direction
        if slope > 0:
            direction = 'UPTREND'
        elif slope < 0:
            direction = 'DOWNTREND'
        else:
            direction = 'SIDEWAYS'

        # R-squared indicates trend strength
        strength = abs(r_value) ** 2

        return {
            'direction': direction,
            'slope': round(slope, 4),
            'strength': round(strength, 2),
            'r_squared': round(r_value ** 2, 2)
        }

    def _calculate_trend_strength(self, df: pd.DataFrame) -> str:
        """Calculate trend strength (ADX-like)"""
        if len(df) < 14:
            return 'INSUFFICIENT_DATA'

        # Simplified ADX calculation
        high = df['high']
        low = df['low']
        close = df['close']

        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        # Directional Movement
        plus_dm = (high - high.shift()).where((high - high.shift()) > (low.shift() - low), 0)
        minus_dm = (low.shift() - low).where((low.shift() - low) > (high - high.shift()), 0)

        # Smooth with EMA
        atr = tr.rolling(14).mean()
        plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(14).mean() / atr)

        # ADX with division by zero protection
        denominator = plus_di + minus_di
        dx = 100 * abs(plus_di - minus_di) / denominator.where(denominator > 0, 1)
        adx = dx.rolling(14).mean().iloc[-1]

        # Handle NaN or invalid ADX
        if pd.isna(adx) or not np.isfinite(adx):
            return 'INSUFFICIENT_DATA'

        if adx > 25:
            return 'STRONG'
        elif adx > 15:
            return 'MODERATE'
        else:
            return 'WEAK'

    def analyze_volume(self, df: pd.DataFrame) -> Dict:
        """Advanced volume analysis"""
        if len(df) < 20:
            return {'error': 'Insufficient data for volume analysis'}

        volume = df['volume']
        close = df['close']

        # Volume trend
        avg_volume_recent = volume.tail(10).mean()
        avg_volume_historical = volume.mean()
        volume_ratio = avg_volume_recent / avg_volume_historical if avg_volume_historical > 0 else 1

        # On-Balance Volume (OBV) with NaN handling
        obv = (volume * ((close.diff() > 0).astype(int) * 2 - 1)).fillna(0).cumsum()

        # Validate OBV values before comparison
        if pd.notna(obv.iloc[-1]) and pd.notna(obv.iloc[-10]) and len(obv) >= 10:
            obv_trend = 'INCREASING' if obv.iloc[-1] > obv.iloc[-10] else 'DECREASING'
        else:
            obv_trend = 'UNKNOWN'

        # Volume Price Trend (VPT) with NaN handling
        vpt = (volume * close.pct_change()).fillna(0).cumsum()

        # Validate VPT values before comparison
        if pd.notna(vpt.iloc[-1]) and pd.notna(vpt.iloc[-10]) and len(vpt) >= 10:
            vpt_trend = 'INCREASING' if vpt.iloc[-1] > vpt.iloc[-10] else 'DECREASING'
        else:
            vpt_trend = 'UNKNOWN'

        return {
            'current_volume': round(volume.iloc[-1], 2),
            'avg_volume': round(avg_volume_historical, 2),
            'volume_ratio': round(volume_ratio, 2),
            'volume_status': 'HIGH' if volume_ratio > 1.5 else 'NORMAL' if volume_ratio > 0.7 else 'LOW',
            'obv_trend': obv_trend,
            'vpt_trend': vpt_trend,
            'confirmation': obv_trend == vpt_trend
        }

    def detect_market_regime(self, df: pd.DataFrame) -> Dict:
        """Detect current market regime (trending vs ranging)"""
        if len(df) < 30:
            return {'error': 'Insufficient data for regime detection'}

        returns = df['close'].pct_change().dropna()

        # Calculate metrics
        volatility = returns.std()
        autocorrelation = returns.autocorr()

        # High autocorrelation = trending
        # Low autocorrelation = mean-reverting/ranging

        if abs(autocorrelation) > 0.3:
            regime = 'TRENDING'
            strategy = 'Use momentum/trend-following strategies'
        else:
            regime = 'RANGING'
            strategy = 'Use mean-reversion strategies'

        # Volatility regime
        hist_vol = returns.rolling(50).std().mean() if len(returns) >= 50 else volatility
        vol_ratio = volatility / hist_vol if hist_vol > 0 else 1

        vol_regime = 'HIGH_VOL' if vol_ratio > 1.3 else 'LOW_VOL' if vol_ratio < 0.7 else 'NORMAL_VOL'

        return {
            'market_regime': regime,
            'volatility_regime': vol_regime,
            'autocorrelation': round(autocorrelation, 3),
            'current_volatility': round(volatility * 100, 2),
            'recommended_strategy': strategy
        }

    def _synthesize_bias(
        self,
        patterns: List[Dict],
        trend: Dict,
        volume: Dict,
        regime: Dict
    ) -> Dict:
        """Synthesize overall bias from all analyses"""
        bullish_score = 0
        bearish_score = 0

        # Pattern bias
        for pattern in patterns:
            if pattern.get('bias') == 'BULLISH':
                bullish_score += pattern.get('confidence', 50)
            elif pattern.get('bias') == 'BEARISH':
                bearish_score += pattern.get('confidence', 50)

        # Trend bias
        if not trend.get('error'):
            if trend['short_term']['direction'] == 'UPTREND':
                bullish_score += 30
            elif trend['short_term']['direction'] == 'DOWNTREND':
                bearish_score += 30

            if trend.get('aligned'):
                bullish_score += 20 if trend['short_term']['direction'] == 'UPTREND' else 0
                bearish_score += 20 if trend['short_term']['direction'] == 'DOWNTREND' else 0

        # Volume confirmation
        if not volume.get('error'):
            if volume.get('confirmation') and volume.get('volume_status') == 'HIGH':
                # Add 15 to the current direction score
                if bullish_score > bearish_score:
                    bullish_score += 15
                else:
                    bearish_score += 15

        # Determine final bias
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
