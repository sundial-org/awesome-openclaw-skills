#!/usr/bin/env python3
"""
Advanced Validation and Cross-Verification Module
Implements multi-layer validation to eliminate hallucinations and ensure data accuracy
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class AdvancedValidator:
    """
    Multi-layered validation system for trading data and signals
    Ensures zero hallucination through rigorous cross-verification
    """

    def __init__(self, strict_mode: bool = True):
        """
        Initialize validator

        Args:
            strict_mode: If True, applies strictest validation rules
        """
        self.strict_mode = strict_mode
        self.validation_history = []

    def _parse_timeframe(self, timeframe: str) -> int:
        """
        Parse timeframe string to minutes

        Args:
            timeframe: Timeframe string (e.g., "15m", "1h", "4h", "1d")

        Returns:
            Number of minutes in the timeframe
        """
        if not timeframe:
            return None

        timeframe = timeframe.lower().strip()

        # Extract number and unit
        if timeframe.endswith('m'):
            return int(timeframe[:-1])
        elif timeframe.endswith('h'):
            return int(timeframe[:-1]) * 60
        elif timeframe.endswith('d'):
            return int(timeframe[:-1]) * 1440
        elif timeframe.endswith('w'):
            return int(timeframe[:-1]) * 10080
        else:
            # Try to parse as minutes
            try:
                return int(timeframe)
            except ValueError:
                return None

    def validate_data_integrity(self, df: pd.DataFrame, symbol: str, timeframe: str = None) -> Dict:
        """
        Stage 1: Deep data integrity validation
        Returns detailed validation report with multi-layer checks

        Args:
            df: OHLCV DataFrame to validate
            symbol: Trading symbol (e.g., "BTC/USDT")
            timeframe: Timeframe string (e.g., "15m", "1h", "4h") for context-aware validation

        Returns:
            Validation report dict with passed status, failures, and warnings
        """
        report = {
            'stage': 'DATA_INTEGRITY',
            'symbol': symbol,
            'timestamp': datetime.now(),
            'passed': True,
            'critical_failures': [],
            'warnings': [],
            'metrics': {}
        }

        # Layer 1: Structural validation
        structural_check = self._validate_structure(df)
        if not structural_check['passed']:
            report['critical_failures'].extend(structural_check['failures'])
            report['passed'] = False

        # Layer 2: Price logic validation
        price_check = self._validate_price_logic(df)
        if not price_check['passed']:
            report['critical_failures'].extend(price_check['failures'])
            report['passed'] = False

        # Layer 3: Statistical anomaly detection
        anomaly_check = self._detect_statistical_anomalies(df)
        if anomaly_check['anomalies_found']:
            if anomaly_check['severity'] == 'CRITICAL':
                report['critical_failures'].extend(anomaly_check['details'])
                report['passed'] = False
            else:
                report['warnings'].extend(anomaly_check['details'])

        # Layer 4: Data freshness validation (timeframe-aware)
        timeframe_minutes = self._parse_timeframe(timeframe) if timeframe else None
        freshness_check = self._validate_freshness(df, timeframe_minutes)
        if not freshness_check['passed']:
            report['critical_failures'].append(freshness_check['message'])
            report['passed'] = False

        # Layer 5: Completeness check
        completeness_check = self._validate_completeness(df)
        if not completeness_check['passed']:
            report['critical_failures'].extend(completeness_check['failures'])
            report['passed'] = False

        # Store metrics
        report['metrics'] = {
            'data_points': len(df),
            'latest_timestamp': df['timestamp'].iloc[-1],
            'data_age_seconds': freshness_check['age_seconds'],
            'missing_percentage': completeness_check['missing_percentage']
        }

        self.validation_history.append(report)
        return report

    def _validate_structure(self, df: pd.DataFrame) -> Dict:
        """Validate dataframe structure"""
        required_columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume']

        failures = []
        for col in required_columns:
            if col not in df.columns:
                failures.append(f"Missing required column: {col}")

        if len(df) < 20:
            failures.append(f"Insufficient data points: {len(df)} (minimum 20 required)")

        return {
            'passed': len(failures) == 0,
            'failures': failures
        }

    def _validate_price_logic(self, df: pd.DataFrame) -> Dict:
        """Validate OHLC price logic with mathematical rigor"""
        failures = []

        # Check 1: No negative or zero prices
        price_cols = ['open', 'high', 'low', 'close']
        for col in price_cols:
            if (df[col] <= 0).any():
                invalid_count = (df[col] <= 0).sum()
                failures.append(f"Invalid {col} prices: {invalid_count} non-positive values detected")

        # Check 2: High >= Low (fundamental OHLC logic)
        if not (df['high'] >= df['low']).all():
            violations = (~(df['high'] >= df['low'])).sum()
            failures.append(f"OHLC violation: High < Low in {violations} candles")

        # Check 3: High >= Open and High >= Close
        if not (df['high'] >= df['open']).all():
            violations = (~(df['high'] >= df['open'])).sum()
            failures.append(f"OHLC violation: High < Open in {violations} candles")

        if not (df['high'] >= df['close']).all():
            violations = (~(df['high'] >= df['close'])).sum()
            failures.append(f"OHLC violation: High < Close in {violations} candles")

        # Check 4: Low <= Open and Low <= Close
        if not (df['low'] <= df['open']).all():
            violations = (~(df['low'] <= df['open'])).sum()
            failures.append(f"OHLC violation: Low > Open in {violations} candles")

        if not (df['low'] <= df['close']).all():
            violations = (~(df['low'] <= df['close'])).sum()
            failures.append(f"OHLC violation: Low > Close in {violations} candles")

        # Check 5: Volume must be non-negative
        if (df['volume'] < 0).any():
            failures.append("Negative volume detected")

        # Check 6: Unrealistic price jumps (>50% in single candle)
        if len(df) > 1:
            returns = df['close'].pct_change().abs()
            extreme_moves = returns > 0.50
            if extreme_moves.any():
                count = extreme_moves.sum()
                max_move = returns.max() * 100
                failures.append(f"Suspicious price jumps: {count} candles with >{max_move:.1f}% moves")

        return {
            'passed': len(failures) == 0,
            'failures': failures
        }

    def _detect_statistical_anomalies(self, df: pd.DataFrame) -> Dict:
        """Advanced statistical anomaly detection using multiple methods"""
        anomalies = []
        severity = 'NONE'

        if len(df) < 30:
            return {'anomalies_found': False, 'severity': 'NONE', 'details': []}

        # Method 1: Z-score detection for returns
        returns = df['close'].pct_change().dropna()
        z_scores = np.abs(stats.zscore(returns))
        extreme_z = z_scores > 5  # More than 5 standard deviations

        if extreme_z.any():
            count = extreme_z.sum()
            max_z = z_scores.max()
            anomalies.append(f"Extreme price movements detected: {count} events with Z-score > 5 (max: {max_z:.2f})")
            severity = 'WARNING'

        # Method 2: IQR-based outlier detection for volume
        Q1 = df['volume'].quantile(0.25)
        Q3 = df['volume'].quantile(0.75)
        IQR = Q3 - Q1
        outliers = (df['volume'] < (Q1 - 3 * IQR)) | (df['volume'] > (Q3 + 3 * IQR))

        if outliers.any():
            count = outliers.sum()
            anomalies.append(f"Volume anomalies: {count} candles with extreme volume deviations")
            if count > len(df) * 0.1:  # More than 10% anomalies
                severity = 'WARNING'

        # Method 3: Monotonicity check (detects fake data)
        consecutive_increases = (df['close'].diff() > 0).rolling(10).sum()
        consecutive_decreases = (df['close'].diff() < 0).rolling(10).sum()

        if (consecutive_increases >= 10).any() or (consecutive_decreases >= 10).any():
            anomalies.append("Suspicious monotonic price pattern detected")
            severity = 'CRITICAL'

        # Method 4: Benford's Law check (detects fabricated data)
        # Extract first significant digit (1-9) from volume data
        def extract_first_digit(value):
            """Extract first significant digit for Benford's Law test"""
            if pd.isna(value) or value == 0:
                return None
            # Convert to absolute value and string, remove decimal point
            abs_str = str(abs(value)).replace('.', '').replace('e', '').replace('+', '').replace('-', '')
            # Strip leading zeros
            stripped = abs_str.lstrip('0')
            if stripped and stripped[0].isdigit():
                return int(stripped[0])
            return None

        first_digits = df['volume'].apply(extract_first_digit).dropna()

        if len(first_digits) >= 10:
            # Perform Benford's Law test only if we have enough data
            benford_expected = np.log10(1 + 1 / np.arange(1, 10))
            benford_observed = first_digits.value_counts(normalize=True).sort_index()

            if len(benford_observed) >= 5:
                # Normalize both to same sum to avoid scipy tolerance errors
                obs_vals = benford_observed.values[:5]
                exp_vals = benford_expected[:5]

                # Renormalize to same sum
                obs_sum = obs_vals.sum()
                exp_sum = exp_vals.sum()
                if obs_sum > 0 and exp_sum > 0:
                    obs_normalized = obs_vals * (exp_sum / obs_sum)

                    chi2, p_value = stats.chisquare(obs_normalized, exp_vals)
                    # Use 0.001 threshold (0.1%) - more reasonable for financial data
                    if p_value < 0.001:
                        anomalies.append(f"Data may be fabricated (Benford's Law p={p_value:.4f})")
                        severity = 'WARNING'  # Changed from CRITICAL to WARNING

        return {
            'anomalies_found': len(anomalies) > 0,
            'severity': severity,
            'details': anomalies
        }

    def _validate_freshness(self, df: pd.DataFrame, timeframe_minutes: int = None) -> Dict:
        """
        Validate data freshness with timeframe-aware thresholds

        Args:
            df: OHLCV DataFrame
            timeframe_minutes: Timeframe interval in minutes (e.g., 15 for "15m", 60 for "1h")

        Returns:
            Dict with passed status, age_seconds, and message
        """
        from datetime import timezone

        latest_time = df['timestamp'].iloc[-1]

        # Convert to UTC for consistent comparison
        if latest_time.tzinfo is not None:
            latest_time_utc = latest_time.astimezone(timezone.utc)
        else:
            # Assume UTC if no timezone info
            latest_time_utc = latest_time.replace(tzinfo=timezone.utc)

        current_time_utc = datetime.now(timezone.utc)
        age_seconds = (current_time_utc - latest_time_utc).total_seconds()

        # Timeframe-aware max age calculation
        if timeframe_minutes:
            # Allow 1.5x timeframe in strict mode, 2.0x in normal mode
            # This accounts for the fact that the latest closed candle can be up to
            # 1 full timeframe old in normal market conditions
            multiplier = 1.5 if self.strict_mode else 2.0
            max_age = int(timeframe_minutes * 60 * multiplier)  # Convert minutes to seconds
        else:
            # Fallback to fixed thresholds if no timeframe provided (backward compatibility)
            # In strict mode, data must be <5 minutes old
            # In normal mode, data must be <15 minutes old
            max_age = 300 if self.strict_mode else 900

        return {
            'passed': age_seconds < max_age,
            'age_seconds': age_seconds,
            'message': f"Data is {age_seconds/60:.1f} minutes old (max: {max_age/60:.1f} minutes)" if age_seconds >= max_age else ""
        }

    def _validate_completeness(self, df: pd.DataFrame) -> Dict:
        """Validate data completeness"""
        failures = []

        # Check for NaN values
        total_cells = df.shape[0] * df.shape[1]
        missing_cells = df.isnull().sum().sum()
        missing_percentage = (missing_cells / total_cells) * 100

        if missing_cells > 0:
            failures.append(f"Missing data: {missing_cells} cells ({missing_percentage:.2f}%)")

        # Check for constant values (potential data freeze)
        for col in ['open', 'high', 'low', 'close']:
            if df[col].nunique() == 1:
                failures.append(f"Constant {col} values detected - potential data freeze")

        return {
            'passed': len(failures) == 0,
            'failures': failures,
            'missing_percentage': missing_percentage
        }

    def validate_indicators(self, indicators: Dict, df: pd.DataFrame) -> Dict:
        """
        Stage 2: Validate calculated indicators
        Ensures mathematical correctness and realistic ranges
        """
        report = {
            'stage': 'INDICATOR_VALIDATION',
            'timestamp': datetime.now(),
            'passed': True,
            'critical_failures': [],
            'warnings': []
        }

        # Validate RSI
        if 'rsi' in indicators:
            if not (0 <= indicators['rsi'] <= 100):
                report['critical_failures'].append(f"Invalid RSI: {indicators['rsi']} (must be 0-100)")
                report['passed'] = False
            elif indicators['rsi'] == 0 or indicators['rsi'] == 100:
                report['warnings'].append(f"Extreme RSI value: {indicators['rsi']}")

        # Validate MACD
        if 'macd' in indicators and 'current_price' in indicators:
            price = indicators['current_price']
            if abs(indicators['macd']) > price * 0.1:  # MACD shouldn't exceed 10% of price
                report['warnings'].append(f"Unusually large MACD: {indicators['macd']}")

        # Validate ATR
        if 'atr' in indicators:
            if indicators['atr'] < 0:
                report['critical_failures'].append(f"Invalid ATR: {indicators['atr']} (must be positive)")
                report['passed'] = False
            elif indicators['atr'] == 0:
                report['warnings'].append("ATR is zero - indicates no volatility or data issue")

        # Validate Bollinger Bands
        if all(k in indicators for k in ['bb_upper', 'bb_lower', 'current_price']):
            if indicators['bb_upper'] <= indicators['bb_lower']:
                report['critical_failures'].append("Invalid Bollinger Bands: Upper <= Lower")
                report['passed'] = False

        # Cross-verify indicator consistency
        if 'rsi' in indicators and len(df) >= 14:
            # Recalculate RSI to verify
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            # Protect against division by zero
            rs = gain / loss.replace(0, 1e-10)
            calculated_rsi = 100 - (100 / (1 + rs.iloc[-1]))

            if abs(calculated_rsi - indicators['rsi']) > 1.0:
                report['warnings'].append(f"RSI calculation mismatch: {calculated_rsi:.1f} vs {indicators['rsi']:.1f}")

        self.validation_history.append(report)
        return report

    def validate_trading_signal(self, analysis: Dict) -> Dict:
        """
        Stage 3: Validate trading signals and recommendations
        Final checkpoint before signal generation
        """
        report = {
            'stage': 'SIGNAL_VALIDATION',
            'timestamp': datetime.now(),
            'passed': True,
            'critical_failures': [],
            'warnings': [],
            'risk_score': 0
        }

        # Validate action
        if analysis.get('action') not in ['LONG', 'SHORT', 'WAIT']:
            report['critical_failures'].append(f"Invalid action: {analysis.get('action')}")
            report['passed'] = False

        # Validate confidence
        confidence = analysis.get('confidence', 0)
        if not isinstance(confidence, (int, float)) or not (0 <= confidence <= 100):
            report['critical_failures'].append(f"Invalid confidence: {confidence}")
            report['passed'] = False

        # Validate price levels
        entry = analysis.get('entry_price')
        stop_loss = analysis.get('stop_loss')
        take_profit = analysis.get('take_profit')

        if analysis.get('action') in ['LONG', 'SHORT']:
            if not all([entry, stop_loss, take_profit]):
                report['critical_failures'].append("Missing price levels for trade signal")
                report['passed'] = False
            elif entry <= 0 or stop_loss <= 0 or take_profit <= 0:
                report['critical_failures'].append("Invalid price levels (must be positive)")
                report['passed'] = False
            else:
                # Validate price level logic for LONG
                if analysis['action'] == 'LONG':
                    if stop_loss >= entry:
                        report['critical_failures'].append("Invalid LONG: Stop loss must be below entry")
                        report['passed'] = False
                    if take_profit <= entry:
                        report['critical_failures'].append("Invalid LONG: Take profit must be above entry")
                        report['passed'] = False

                # Validate price level logic for SHORT
                elif analysis['action'] == 'SHORT':
                    if stop_loss <= entry:
                        report['critical_failures'].append("Invalid SHORT: Stop loss must be above entry")
                        report['passed'] = False
                    if take_profit >= entry:
                        report['critical_failures'].append("Invalid SHORT: Take profit must be below entry")
                        report['passed'] = False

        # Validate risk/reward ratio
        risk_reward = analysis.get('risk_reward', 0)
        if risk_reward < 0:
            report['critical_failures'].append(f"Invalid risk/reward: {risk_reward}")
            report['passed'] = False
        elif 0 < risk_reward < 1.5:
            report['warnings'].append(f"Poor risk/reward ratio: {risk_reward}")
            report['risk_score'] += 30

        # Calculate overall risk score
        if confidence < 50:
            report['risk_score'] += 40
        elif confidence > 85:
            report['risk_score'] += 20
            report['warnings'].append("High confidence may indicate overconfidence")

        if len(analysis.get('timeframe_data', {})) < 2:
            report['risk_score'] += 50
            report['warnings'].append("Insufficient timeframe confirmation")

        self.validation_history.append(report)
        return report

    def cross_verify_analysis(self, analyses: List[Dict]) -> Dict:
        """
        Stage 4: Cross-verification across multiple analyses
        Ensures consistency and detects conflicts
        """
        if len(analyses) < 2:
            return {'verified': True, 'confidence_adjustment': 0, 'notes': []}

        report = {
            'verified': True,
            'confidence_adjustment': 0,
            'notes': [],
            'consensus_strength': 0
        }

        # Check action consensus
        actions = [a.get('action') for a in analyses if a.get('action')]
        if len(set(actions)) > 1:
            report['notes'].append(f"Mixed signals detected: {dict(pd.Series(actions).value_counts())}")
            report['confidence_adjustment'] -= 20
        else:
            report['consensus_strength'] += 30

        # Check confidence consistency
        confidences = [a.get('confidence', 0) for a in analyses]
        if len(confidences) > 1:
            confidence_std = np.std(confidences)
            if confidence_std > 20:
                report['notes'].append(f"High confidence variance: ±{confidence_std:.1f}%")
                report['confidence_adjustment'] -= 10
            else:
                report['consensus_strength'] += 20

        # Check price level consistency
        entries = [a.get('entry_price') for a in analyses if a.get('entry_price')]
        if len(entries) > 1:
            entry_variance = np.std(entries) / np.mean(entries)
            if entry_variance > 0.02:  # More than 2% variance
                report['notes'].append(f"Entry price inconsistency: {entry_variance*100:.2f}% variance")
                report['confidence_adjustment'] -= 5

        report['consensus_strength'] = min(100, report['consensus_strength'])
        return report

    def get_validation_summary(self) -> Dict:
        """Get summary of all validations performed"""
        total = len(self.validation_history)
        if total == 0:
            return {'total_validations': 0}

        passed = sum(1 for v in self.validation_history if v.get('passed', False))

        return {
            'total_validations': total,
            'passed': passed,
            'failed': total - passed,
            'success_rate': (passed / total) * 100 if total > 0 else 0,
            'stages_validated': list(set(v['stage'] for v in self.validation_history))
        }
