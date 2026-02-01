#!/usr/bin/env python3
"""
Backtest Validator

Performs real-time strategy validation by backtesting recent historical data.
Enhances confidence by validating current signals have historically performed well.

Component of Phase 1: Critical Reliability Improvements (+0.3 reliability)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class TradeResult:
    """Single trade result"""
    entry_time: datetime
    exit_time: datetime
    entry_price: float
    exit_price: float
    action: str  # 'LONG' or 'SHORT'
    pnl_pct: float
    win: bool
    risk_reward: float
    max_drawdown: float


@dataclass
class BacktestMetrics:
    """Comprehensive backtest metrics"""
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win_pct: float
    avg_loss_pct: float
    profit_factor: float
    sharpe_ratio: float
    max_drawdown_pct: float
    total_return_pct: float
    trades: List[TradeResult]


class BacktestValidator:
    """
    Validates trading strategies through historical backtesting

    Responsibilities:
    - Backtest signals on recent historical data (30 days)
    - Calculate performance metrics (win rate, profit factor, Sharpe)
    - Validate current signal based on historical performance
    - Adjust confidence based on backtest results
    - Detect regime changes where strategy underperforms

    Design: Single Responsibility, Dependency Injection
    """

    def __init__(
        self,
        lookback_days: int = 30,
        min_trades: int = 5,
        required_win_rate: float = 0.55,
        required_profit_factor: float = 1.3
    ):
        """
        Initialize backtest validator

        Args:
            lookback_days: Days of historical data to backtest
            min_trades: Minimum trades required for validation
            required_win_rate: Minimum win rate to pass validation
            required_profit_factor: Minimum profit factor to pass validation
        """
        self.lookback_days = lookback_days
        self.min_trades = min_trades
        self.required_win_rate = required_win_rate
        self.required_profit_factor = required_profit_factor

        logger.info(f"Initialized BacktestValidator (lookback: {lookback_days}d, "
                   f"min_trades: {min_trades}, required_wr: {required_win_rate:.0%})")

    def validate_strategy(
        self,
        historical_data: pd.DataFrame,
        signal_generator,
        current_signal: Dict
    ) -> Dict:
        """
        Validate strategy by backtesting on historical data

        Args:
            historical_data: DataFrame with OHLCV data (should be >= lookback_days)
            signal_generator: Function/object that generates signals from data
            current_signal: Current signal to validate

        Returns:
            Dictionary with validation results and adjusted confidence
        """
        logger.info(f"Validating strategy on {len(historical_data)} historical candles")

        # Run backtest
        backtest_results = self._run_backtest(historical_data, signal_generator)

        if backtest_results is None:
            return {
                'validated': False,
                'reason': 'backtest_failed',
                'confidence_adjustment': 0.0,
                'metrics': None
            }

        # Validate metrics
        validation_result = self._validate_metrics(backtest_results, current_signal)

        return validation_result

    def _run_backtest(
        self,
        data: pd.DataFrame,
        signal_generator
    ) -> Optional[BacktestMetrics]:
        """
        Run backtest on historical data

        Args:
            data: Historical OHLCV data
            signal_generator: Signal generation function/object

        Returns:
            BacktestMetrics or None if backtest fails
        """
        try:
            trades = []
            current_position = None

            # Iterate through data with sliding window
            window_size = 100  # Need enough data for indicators

            for i in range(window_size, len(data)):
                # Get historical window for signal generation
                window_data = data.iloc[:i].copy()

                # Generate signal at this point in time
                try:
                    signal = signal_generator(window_data)
                except Exception as e:
                    logger.debug(f"Signal generation failed at index {i}: {e}")
                    continue

                if signal is None:
                    continue

                action = signal.get('action', 'HOLD')
                current_price = data.iloc[i]['close']
                current_time = data.iloc[i]['timestamp']

                # Process signal
                if action in ['LONG', 'SHORT'] and current_position is None:
                    # Enter position
                    current_position = {
                        'action': action,
                        'entry_price': current_price,
                        'entry_time': current_time,
                        'stop_loss': signal.get('stop_loss', current_price * 0.98),
                        'take_profit': signal.get('take_profit', current_price * 1.04),
                        'highest_price': current_price,
                        'lowest_price': current_price
                    }

                elif current_position is not None:
                    # Update position tracking
                    current_position['highest_price'] = max(
                        current_position['highest_price'],
                        data.iloc[i]['high']
                    )
                    current_position['lowest_price'] = min(
                        current_position['lowest_price'],
                        data.iloc[i]['low']
                    )

                    # Check exit conditions
                    should_exit, exit_price = self._check_exit_conditions(
                        current_position,
                        data.iloc[i]
                    )

                    if should_exit:
                        # Close position
                        trade_result = self._create_trade_result(
                            current_position,
                            exit_price,
                            current_time
                        )
                        trades.append(trade_result)
                        current_position = None

            # Close any remaining position at the last price
            if current_position is not None:
                trade_result = self._create_trade_result(
                    current_position,
                    data.iloc[-1]['close'],
                    data.iloc[-1]['timestamp']
                )
                trades.append(trade_result)

            # Calculate metrics
            if len(trades) < self.min_trades:
                logger.warning(f"Insufficient trades in backtest: {len(trades)} < {self.min_trades}")
                return None

            metrics = self._calculate_metrics(trades)
            return metrics

        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            return None

    def _check_exit_conditions(
        self,
        position: Dict,
        current_candle: pd.Series
    ) -> Tuple[bool, float]:
        """
        Check if position should be exited

        Args:
            position: Current position dictionary
            current_candle: Current OHLC candle

        Returns:
            Tuple of (should_exit, exit_price)
        """
        action = position['action']
        entry_price = position['entry_price']
        stop_loss = position['stop_loss']
        take_profit = position['take_profit']

        if action == 'LONG':
            # Check stop loss hit
            if current_candle['low'] <= stop_loss:
                return True, stop_loss

            # Check take profit hit
            if current_candle['high'] >= take_profit:
                return True, take_profit

        elif action == 'SHORT':
            # For SHORT positions (if supported)
            if current_candle['high'] >= stop_loss:
                return True, stop_loss

            if current_candle['low'] <= take_profit:
                return True, take_profit

        return False, 0.0

    def _create_trade_result(
        self,
        position: Dict,
        exit_price: float,
        exit_time: datetime
    ) -> TradeResult:
        """
        Create TradeResult from position

        Args:
            position: Position dictionary
            exit_price: Exit price
            exit_time: Exit timestamp

        Returns:
            TradeResult object
        """
        entry_price = position['entry_price']
        action = position['action']

        # Calculate PnL
        if action == 'LONG':
            pnl_pct = ((exit_price - entry_price) / entry_price) * 100
        else:  # SHORT
            pnl_pct = ((entry_price - exit_price) / entry_price) * 100

        # Calculate max drawdown during trade
        if action == 'LONG':
            max_dd = ((position['lowest_price'] - entry_price) / entry_price) * 100
        else:
            max_dd = ((position['highest_price'] - entry_price) / entry_price) * 100

        # Calculate risk/reward
        if action == 'LONG':
            risk = abs(entry_price - position['stop_loss'])
            reward = abs(position['take_profit'] - entry_price)
        else:
            risk = abs(position['stop_loss'] - entry_price)
            reward = abs(entry_price - position['take_profit'])

        risk_reward = reward / risk if risk > 0 else 0.0

        return TradeResult(
            entry_time=position['entry_time'],
            exit_time=exit_time,
            entry_price=entry_price,
            exit_price=exit_price,
            action=action,
            pnl_pct=pnl_pct,
            win=(pnl_pct > 0),
            risk_reward=risk_reward,
            max_drawdown=abs(max_dd)
        )

    def _calculate_metrics(self, trades: List[TradeResult]) -> BacktestMetrics:
        """
        Calculate comprehensive backtest metrics

        Args:
            trades: List of TradeResult objects

        Returns:
            BacktestMetrics object
        """
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.win)
        losing_trades = total_trades - winning_trades

        win_rate = winning_trades / total_trades if total_trades > 0 else 0.0

        # Average win/loss
        wins = [t.pnl_pct for t in trades if t.win]
        losses = [abs(t.pnl_pct) for t in trades if not t.win]

        avg_win_pct = np.mean(wins) if wins else 0.0
        avg_loss_pct = np.mean(losses) if losses else 0.0

        # Profit factor
        total_wins = sum(wins) if wins else 0.0
        total_losses = sum(losses) if losses else 0.0
        profit_factor = total_wins / total_losses if total_losses > 0 else 0.0

        # Sharpe ratio (simplified - using trade returns)
        returns = [t.pnl_pct for t in trades]
        sharpe_ratio = (np.mean(returns) / np.std(returns)) if len(returns) > 1 and np.std(returns) > 0 else 0.0

        # Max drawdown
        max_drawdown_pct = max([t.max_drawdown for t in trades]) if trades else 0.0

        # Total return
        total_return_pct = sum(returns)

        return BacktestMetrics(
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            win_rate=win_rate,
            avg_win_pct=avg_win_pct,
            avg_loss_pct=avg_loss_pct,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            max_drawdown_pct=max_drawdown_pct,
            total_return_pct=total_return_pct,
            trades=trades
        )

    def _validate_metrics(
        self,
        metrics: BacktestMetrics,
        current_signal: Dict
    ) -> Dict:
        """
        Validate backtest metrics and calculate confidence adjustment

        Args:
            metrics: BacktestMetrics from backtest
            current_signal: Current signal to validate

        Returns:
            Validation result dictionary
        """
        validation_checks = []

        # Check 1: Sufficient trades
        if metrics.total_trades < self.min_trades:
            validation_checks.append({
                'check': 'trade_count',
                'passed': False,
                'value': metrics.total_trades,
                'required': self.min_trades
            })
        else:
            validation_checks.append({
                'check': 'trade_count',
                'passed': True,
                'value': metrics.total_trades,
                'required': self.min_trades
            })

        # Check 2: Win rate
        win_rate_passed = metrics.win_rate >= self.required_win_rate
        validation_checks.append({
            'check': 'win_rate',
            'passed': win_rate_passed,
            'value': metrics.win_rate,
            'required': self.required_win_rate
        })

        # Check 3: Profit factor
        pf_passed = metrics.profit_factor >= self.required_profit_factor
        validation_checks.append({
            'check': 'profit_factor',
            'passed': pf_passed,
            'value': metrics.profit_factor,
            'required': self.required_profit_factor
        })

        # Check 4: Positive total return
        positive_return = metrics.total_return_pct > 0
        validation_checks.append({
            'check': 'total_return',
            'passed': positive_return,
            'value': metrics.total_return_pct,
            'required': 0.0
        })

        # Overall validation
        all_passed = all(check['passed'] for check in validation_checks)

        # Calculate confidence adjustment
        confidence_adjustment = self._calculate_confidence_adjustment(
            metrics,
            validation_checks,
            current_signal
        )

        return {
            'validated': all_passed,
            'metrics': metrics,
            'validation_checks': validation_checks,
            'confidence_adjustment': confidence_adjustment,
            'recommendation': self._generate_recommendation(metrics, all_passed)
        }

    def _calculate_confidence_adjustment(
        self,
        metrics: BacktestMetrics,
        checks: List[Dict],
        current_signal: Dict
    ) -> float:
        """
        Calculate confidence adjustment based on backtest performance

        Args:
            metrics: BacktestMetrics
            checks: Validation checks results
            current_signal: Current signal

        Returns:
            Confidence adjustment (-0.3 to +0.2)
        """
        adjustment = 0.0

        # Positive adjustments for exceeding requirements
        if metrics.win_rate > self.required_win_rate + 0.1:
            adjustment += 0.05

        if metrics.profit_factor > self.required_profit_factor + 0.5:
            adjustment += 0.05

        if metrics.sharpe_ratio > 1.0:
            adjustment += 0.05

        # Strong positive total return
        if metrics.total_return_pct > 10.0:
            adjustment += 0.05

        # Negative adjustments for failing requirements
        checks_failed = sum(1 for check in checks if not check['passed'])

        if checks_failed == 1:
            adjustment -= 0.10
        elif checks_failed == 2:
            adjustment -= 0.20
        elif checks_failed >= 3:
            adjustment -= 0.30

        # Cap adjustment
        adjustment = max(-0.30, min(0.20, adjustment))

        return adjustment

    def _generate_recommendation(
        self,
        metrics: BacktestMetrics,
        validated: bool
    ) -> str:
        """
        Generate recommendation based on backtest results

        Args:
            metrics: BacktestMetrics
            validated: Whether validation passed

        Returns:
            Recommendation string
        """
        if not validated:
            if metrics.win_rate < self.required_win_rate:
                return f"CAUTION: Strategy win rate ({metrics.win_rate:.1%}) below requirement ({self.required_win_rate:.1%})"
            elif metrics.profit_factor < self.required_profit_factor:
                return f"CAUTION: Profit factor ({metrics.profit_factor:.2f}) below requirement ({self.required_profit_factor:.2f})"
            elif metrics.total_return_pct <= 0:
                return f"CAUTION: Strategy shows negative returns ({metrics.total_return_pct:.2f}%) in backtest"
            else:
                return "CAUTION: Strategy failed validation requirements"
        else:
            if metrics.win_rate > 0.65 and metrics.profit_factor > 2.0:
                return "EXCELLENT: Strategy shows strong historical performance"
            elif metrics.win_rate > 0.60 and metrics.profit_factor > 1.5:
                return "GOOD: Strategy validated with solid performance"
            else:
                return "ACCEPTABLE: Strategy meets minimum requirements"


# Convenience function
def validate_with_backtest(
    historical_data: pd.DataFrame,
    signal_generator,
    current_signal: Dict,
    lookback_days: int = 30
) -> Dict:
    """
    Quick validation using backtest

    Args:
        historical_data: Historical OHLCV data
        signal_generator: Signal generation function
        current_signal: Current signal to validate
        lookback_days: Days to backtest

    Returns:
        Validation result dictionary
    """
    validator = BacktestValidator(lookback_days=lookback_days)
    return validator.validate_strategy(historical_data, signal_generator, current_signal)
