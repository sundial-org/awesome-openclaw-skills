#!/usr/bin/env python3
"""
Historical Accuracy Tracker

Adaptive learning system that tracks real trade outcomes and updates
indicator accuracy priors based on actual performance.

Component of Phase 2: Adaptive Learning (+0.4 reliability)
"""

import json
import os
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class TradeOutcome:
    """Record of a single trade outcome"""
    timestamp: str
    symbol: str
    action: str  # 'LONG' or 'SHORT'
    entry_price: float
    exit_price: float
    predicted_action: str
    confidence: float
    indicators_used: Dict[str, str]  # indicator -> signal ('bullish'/'bearish')
    success: bool  # True if trade was profitable
    pnl_pct: float
    duration_hours: float


@dataclass
class IndicatorAccuracy:
    """Accuracy statistics for an indicator"""
    indicator_name: str
    total_signals: int
    correct_signals: int
    accuracy: float
    last_updated: str
    symbol_specific: Optional[str] = None  # For symbol-specific tracking


class HistoricalAccuracyTracker:
    """
    Tracks trade outcomes and learns indicator accuracies over time

    Responsibilities:
    - Record trade outcomes with indicator signals
    - Calculate indicator accuracy from actual results
    - Update Bayesian priors based on performance
    - Provide symbol-specific and global accuracies
    - Persist data across sessions
    - Detect when indicators become unreliable

    Design: Single Responsibility, Open/Closed principles
    """

    # Default accuracy priors (used when no history)
    DEFAULT_ACCURACIES = {
        'RSI': 0.65,
        'MACD': 0.68,
        'Stochastic': 0.62,
        'ADX': 0.70,
        'Bollinger': 0.64,
        'EMA_Cross': 0.66,
        'Volume': 0.63,
        'ATR': 0.58,
        'OBV': 0.61,
        'Pattern': 0.67
    }

    def __init__(
        self,
        data_dir: Optional[str] = None,
        min_samples: int = 10,
        learning_rate: float = 0.3
    ):
        """
        Initialize historical accuracy tracker

        Args:
            data_dir: Directory to store accuracy data (default: .accuracy_data)
            min_samples: Minimum samples before updating accuracies
            learning_rate: Weight for new data vs historical (0-1)
        """
        self.data_dir = Path(data_dir) if data_dir else Path.home() / '.accuracy_data'
        self.min_samples = min_samples
        self.learning_rate = learning_rate

        # Create data directory
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # Load existing data
        self.accuracies: Dict[str, IndicatorAccuracy] = {}
        self.outcomes: List[TradeOutcome] = []
        self._load_data()

        logger.info(f"Initialized HistoricalAccuracyTracker (samples: {len(self.outcomes)}, "
                   f"indicators tracked: {len(self.accuracies)})")

    def _load_data(self) -> None:
        """Load accuracy data and outcomes from disk"""
        # Load accuracies
        accuracies_file = self.data_dir / 'accuracies.json'
        if accuracies_file.exists():
            try:
                with open(accuracies_file, 'r') as f:
                    data = json.load(f)
                    self.accuracies = {
                        name: IndicatorAccuracy(**acc_data)
                        for name, acc_data in data.items()
                    }
                logger.info(f"Loaded {len(self.accuracies)} indicator accuracies")
            except Exception as e:
                logger.warning(f"Failed to load accuracies: {e}")

        # Load recent outcomes (keep last 1000)
        outcomes_file = self.data_dir / 'outcomes.json'
        if outcomes_file.exists():
            try:
                with open(outcomes_file, 'r') as f:
                    data = json.load(f)
                    self.outcomes = [TradeOutcome(**outcome) for outcome in data[-1000:]]
                logger.info(f"Loaded {len(self.outcomes)} trade outcomes")
            except Exception as e:
                logger.warning(f"Failed to load outcomes: {e}")

    def _save_data(self) -> None:
        """Save accuracy data and outcomes to disk"""
        try:
            # Save accuracies
            accuracies_file = self.data_dir / 'accuracies.json'
            with open(accuracies_file, 'w') as f:
                data = {name: asdict(acc) for name, acc in self.accuracies.items()}
                json.dump(data, f, indent=2)

            # Save recent outcomes (last 1000)
            outcomes_file = self.data_dir / 'outcomes.json'
            with open(outcomes_file, 'w') as f:
                data = [asdict(outcome) for outcome in self.outcomes[-1000:]]
                json.dump(data, f, indent=2)

            logger.debug("Saved accuracy data to disk")
        except Exception as e:
            logger.error(f"Failed to save data: {e}")

    def record_trade_outcome(
        self,
        symbol: str,
        action: str,
        entry_price: float,
        exit_price: float,
        predicted_action: str,
        confidence: float,
        indicators_used: Dict[str, str],
        entry_time: Optional[datetime] = None,
        exit_time: Optional[datetime] = None
    ) -> None:
        """
        Record a trade outcome for learning

        Args:
            symbol: Trading pair
            action: Actual action taken ('LONG' or 'SHORT')
            entry_price: Entry price
            exit_price: Exit price
            predicted_action: Predicted action from indicators
            confidence: Prediction confidence (0-1)
            indicators_used: Dict of indicator -> signal ('bullish'/'bearish')
            entry_time: Entry timestamp (default: now)
            exit_time: Exit timestamp (default: now)
        """
        if entry_time is None:
            entry_time = datetime.now()
        if exit_time is None:
            exit_time = datetime.now()

        # Calculate trade success
        if action == 'LONG':
            success = exit_price > entry_price
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        else:  # SHORT
            success = exit_price < entry_price
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100

        # Calculate duration
        duration_hours = (exit_time - entry_time).total_seconds() / 3600

        # Create outcome record
        outcome = TradeOutcome(
            timestamp=entry_time.isoformat(),
            symbol=symbol,
            action=action,
            entry_price=entry_price,
            exit_price=exit_price,
            predicted_action=predicted_action,
            confidence=confidence,
            indicators_used=indicators_used,
            success=success,
            pnl_pct=pnl_pct,
            duration_hours=duration_hours
        )

        self.outcomes.append(outcome)

        # Update accuracies
        self._update_accuracies(outcome)

        # Save data
        self._save_data()

        logger.info(f"Recorded trade outcome: {symbol} {action} "
                   f"{'✓' if success else '✗'} ({pnl_pct:+.2f}%)")

    def _update_accuracies(self, outcome: TradeOutcome) -> None:
        """
        Update indicator accuracies based on trade outcome

        Args:
            outcome: TradeOutcome to learn from
        """
        # Determine if prediction matched outcome
        prediction_correct = outcome.predicted_action == outcome.action and outcome.success

        # Update each indicator that contributed to this signal
        for indicator_name, indicator_signal in outcome.indicators_used.items():
            # Check if indicator signal matched the outcome
            if outcome.action == 'LONG':
                indicator_correct = indicator_signal == 'bullish' and outcome.success
            else:  # SHORT
                indicator_correct = indicator_signal == 'bearish' and outcome.success

            # Get or create indicator accuracy record
            key = f"{indicator_name}"
            if key not in self.accuracies:
                # Initialize with default
                self.accuracies[key] = IndicatorAccuracy(
                    indicator_name=indicator_name,
                    total_signals=0,
                    correct_signals=0,
                    accuracy=self.DEFAULT_ACCURACIES.get(indicator_name, 0.60),
                    last_updated=datetime.now().isoformat()
                )

            accuracy_record = self.accuracies[key]

            # Update counts
            accuracy_record.total_signals += 1
            if indicator_correct:
                accuracy_record.correct_signals += 1

            # Update accuracy using exponential moving average
            if accuracy_record.total_signals >= self.min_samples:
                # Calculate raw accuracy
                raw_accuracy = accuracy_record.correct_signals / accuracy_record.total_signals

                # Blend with current accuracy using learning rate
                new_accuracy = (
                    (1 - self.learning_rate) * accuracy_record.accuracy +
                    self.learning_rate * raw_accuracy
                )

                accuracy_record.accuracy = new_accuracy
                accuracy_record.last_updated = datetime.now().isoformat()

                logger.debug(f"Updated {indicator_name} accuracy: {new_accuracy:.3f} "
                           f"(samples: {accuracy_record.total_signals})")

    def get_indicator_accuracy(
        self,
        indicator_name: str,
        symbol: Optional[str] = None
    ) -> float:
        """
        Get current accuracy for an indicator

        Args:
            indicator_name: Name of indicator
            symbol: Optional symbol for symbol-specific accuracy

        Returns:
            Accuracy value (0-1)
        """
        # Try symbol-specific first if requested
        if symbol:
            key = f"{indicator_name}_{symbol}"
            if key in self.accuracies:
                acc = self.accuracies[key]
                if acc.total_signals >= self.min_samples:
                    return acc.accuracy

        # Fall back to global accuracy
        key = indicator_name
        if key in self.accuracies:
            acc = self.accuracies[key]
            if acc.total_signals >= self.min_samples:
                return acc.accuracy

        # Fall back to default
        return self.DEFAULT_ACCURACIES.get(indicator_name, 0.60)

    def get_all_accuracies(self) -> Dict[str, float]:
        """
        Get all current indicator accuracies

        Returns:
            Dictionary mapping indicator name to accuracy
        """
        accuracies = {}

        # Start with defaults
        for indicator, default_acc in self.DEFAULT_ACCURACIES.items():
            accuracies[indicator] = default_acc

        # Override with learned accuracies
        for key, acc in self.accuracies.items():
            if acc.total_signals >= self.min_samples:
                accuracies[acc.indicator_name] = acc.accuracy

        return accuracies

    def get_accuracy_confidence(self, indicator_name: str) -> float:
        """
        Get confidence in accuracy estimate based on sample size

        Args:
            indicator_name: Name of indicator

        Returns:
            Confidence score (0-1)
        """
        key = indicator_name
        if key not in self.accuracies:
            return 0.0

        acc = self.accuracies[key]

        # Confidence increases with sample size (logarithmically)
        if acc.total_signals < self.min_samples:
            return 0.3

        # Scale from 0.5 to 1.0 based on samples (up to 100 samples)
        import math
        confidence = 0.5 + 0.5 * min(1.0, math.log10(acc.total_signals) / 2.0)

        return confidence

    def get_statistics(self) -> Dict:
        """
        Get overall statistics and performance metrics

        Returns:
            Dictionary with statistics
        """
        if not self.outcomes:
            return {
                'total_trades': 0,
                'successful_trades': 0,
                'win_rate': 0.0,
                'avg_pnl': 0.0,
                'indicators_tracked': len(self.accuracies)
            }

        successful = sum(1 for o in self.outcomes if o.success)
        win_rate = successful / len(self.outcomes)
        avg_pnl = sum(o.pnl_pct for o in self.outcomes) / len(self.outcomes)

        # Get indicator statistics
        indicator_stats = {}
        for name, acc in self.accuracies.items():
            if acc.total_signals >= self.min_samples:
                indicator_stats[name] = {
                    'accuracy': acc.accuracy,
                    'samples': acc.total_signals,
                    'confidence': self.get_accuracy_confidence(name)
                }

        return {
            'total_trades': len(self.outcomes),
            'successful_trades': successful,
            'win_rate': win_rate,
            'avg_pnl': avg_pnl,
            'indicators_tracked': len(self.accuracies),
            'indicator_stats': indicator_stats
        }

    def detect_unreliable_indicators(self, threshold: float = 0.50) -> List[str]:
        """
        Detect indicators that have become unreliable

        Args:
            threshold: Accuracy threshold below which indicator is unreliable

        Returns:
            List of unreliable indicator names
        """
        unreliable = []

        for name, acc in self.accuracies.items():
            if acc.total_signals >= self.min_samples:
                if acc.accuracy < threshold:
                    unreliable.append(name)
                    logger.warning(f"Indicator {name} unreliable: {acc.accuracy:.3f} < {threshold:.3f}")

        return unreliable

    def reset_indicator(self, indicator_name: str) -> None:
        """
        Reset an indicator's accuracy to default

        Args:
            indicator_name: Name of indicator to reset
        """
        if indicator_name in self.accuracies:
            del self.accuracies[indicator_name]
            logger.info(f"Reset {indicator_name} to default accuracy")
            self._save_data()

    def export_data(self, output_file: str) -> None:
        """
        Export all data to JSON file

        Args:
            output_file: Path to output file
        """
        try:
            data = {
                'accuracies': {name: asdict(acc) for name, acc in self.accuracies.items()},
                'outcomes': [asdict(outcome) for outcome in self.outcomes],
                'statistics': self.get_statistics()
            }

            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.info(f"Exported data to {output_file}")
        except Exception as e:
            logger.error(f"Failed to export data: {e}")


# Convenience functions
def create_accuracy_tracker(data_dir: Optional[str] = None) -> HistoricalAccuracyTracker:
    """
    Factory function to create HistoricalAccuracyTracker

    Args:
        data_dir: Optional data directory path

    Returns:
        HistoricalAccuracyTracker instance
    """
    return HistoricalAccuracyTracker(data_dir=data_dir)


def get_learned_accuracies(tracker: HistoricalAccuracyTracker) -> Dict[str, float]:
    """
    Get all learned indicator accuracies

    Args:
        tracker: HistoricalAccuracyTracker instance

    Returns:
        Dictionary of indicator accuracies
    """
    return tracker.get_all_accuracies()
