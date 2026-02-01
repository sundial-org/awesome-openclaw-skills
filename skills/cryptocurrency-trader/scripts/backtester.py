#!/usr/bin/env python3
"""
Backtesting Framework for Trading Strategy Validation

This module provides a comprehensive backtesting framework to validate
the trading strategy with historical data before risking real capital.

Key Features:
- Historical data replay
- Realistic order execution (slippage, fees)
- Position and P&L tracking
- Performance metrics (Sharpe, win rate, drawdown)
- Detailed trade logging
- Equity curve generation

Usage:
    backtester = Backtester(
        agent=EnhancedTradingAgent(balance=10000),
        initial_capital=10000,
        trading_fee=0.001,  # 0.1% taker fee
        slippage=0.0005     # 0.05% slippage
    )

    results = backtester.run(
        symbol='BTC/USDT',
        start_date='2024-01-01',
        end_date='2024-12-31',
        timeframe='1h'
    )

    print(results.summary())
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class Trade:
    """Represents a completed trade"""
    entry_time: datetime
    exit_time: datetime
    symbol: str
    side: str  # 'LONG' or 'SHORT'
    entry_price: float
    exit_price: float
    position_size: float
    pnl: float
    pnl_pct: float
    exit_reason: str  # 'TAKE_PROFIT', 'STOP_LOSS', 'SIGNAL_REVERSE', 'END_OF_DATA'
    holding_period_hours: float

    def __str__(self):
        return (f"{self.side} {self.symbol} | "
                f"Entry: ${self.entry_price:.2f} @ {self.entry_time} | "
                f"Exit: ${self.exit_price:.2f} @ {self.exit_time} | "
                f"P&L: ${self.pnl:.2f} ({self.pnl_pct:+.2f}%) | "
                f"Reason: {self.exit_reason}")


@dataclass
class Position:
    """Represents an open position"""
    symbol: str
    side: str
    entry_time: datetime
    entry_price: float
    position_size: float
    stop_loss: float
    take_profit: float

    def calculate_pnl(self, current_price: float) -> float:
        """Calculate current P&L"""
        if self.side == 'LONG':
            return (current_price - self.entry_price) * self.position_size
        else:  # SHORT
            return (self.entry_price - current_price) * self.position_size

    def calculate_pnl_pct(self, current_price: float) -> float:
        """Calculate current P&L percentage"""
        if self.side == 'LONG':
            return ((current_price - self.entry_price) / self.entry_price) * 100
        else:  # SHORT
            return ((self.entry_price - current_price) / self.entry_price) * 100

    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop loss is hit"""
        if self.side == 'LONG':
            return current_price <= self.stop_loss
        else:  # SHORT
            return current_price >= self.stop_loss

    def check_take_profit(self, current_price: float) -> bool:
        """Check if take profit is hit"""
        if self.side == 'LONG':
            return current_price >= self.take_profit
        else:  # SHORT
            return current_price <= self.take_profit


@dataclass
class BacktestResult:
    """Stores backtesting results and metrics"""
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: float
    profit_factor: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_pct: float
    avg_trade_return: float
    avg_winning_trade: float
    avg_losing_trade: float
    largest_win: float
    largest_loss: float
    trades: List[Trade] = field(default_factory=list)
    equity_curve: pd.DataFrame = field(default_factory=pd.DataFrame)

    def summary(self) -> str:
        """Generate summary report"""
        lines = [
            "=" * 70,
            "BACKTEST RESULTS SUMMARY",
            "=" * 70,
            f"\nCapital:",
            f"  Initial: ${self.initial_capital:,.2f}",
            f"  Final:   ${self.final_capital:,.2f}",
            f"  Return:  ${self.total_return:+,.2f} ({self.total_return_pct:+.2f}%)",
            f"\nTrade Statistics:",
            f"  Total Trades:    {self.total_trades}",
            f"  Winning Trades:  {self.winning_trades} ({self.win_rate:.1f}%)",
            f"  Losing Trades:   {self.losing_trades}",
            f"  Profit Factor:   {self.profit_factor:.2f}",
            f"\nPerformance Metrics:",
            f"  Sharpe Ratio:    {self.sharpe_ratio:.2f}",
            f"  Sortino Ratio:   {self.sortino_ratio:.2f}",
            f"  Max Drawdown:    ${self.max_drawdown:,.2f} ({self.max_drawdown_pct:.2f}%)",
            f"\nTrade Analysis:",
            f"  Avg Trade P&L:   ${self.avg_trade_return:+.2f}",
            f"  Avg Win:         ${self.avg_winning_trade:+.2f}",
            f"  Avg Loss:        ${self.avg_losing_trade:+.2f}",
            f"  Largest Win:     ${self.largest_win:+.2f}",
            f"  Largest Loss:    ${self.largest_loss:+.2f}",
            "=" * 70,
        ]
        return "\n".join(lines)


class Backtester:
    """
    Backtesting framework for validating trading strategies

    Simulates realistic trading with:
    - Historical data replay
    - Order execution with slippage and fees
    - Position management (stops, targets)
    - Performance tracking
    """

    def __init__(
        self,
        agent,
        initial_capital: float = 10000,
        trading_fee: float = 0.001,  # 0.1% taker fee (typical for crypto)
        slippage: float = 0.0005,    # 0.05% slippage
        risk_per_trade: float = 0.02,  # 2% risk per trade
        max_position_size: float = 0.10  # 10% max position size
    ):
        """
        Initialize backtester

        Args:
            agent: Trading agent (EnhancedTradingAgent)
            initial_capital: Starting capital in USD
            trading_fee: Trading fee as decimal (0.001 = 0.1%)
            slippage: Price slippage as decimal (0.0005 = 0.05%)
            risk_per_trade: Max risk per trade as fraction (0.02 = 2%)
            max_position_size: Max position size as fraction (0.10 = 10%)
        """
        self.agent = agent
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.trading_fee = trading_fee
        self.slippage = slippage
        self.risk_per_trade = risk_per_trade
        self.max_position_size = max_position_size

        self.position: Optional[Position] = None
        self.trades: List[Trade] = []
        self.equity_history: List[Dict] = []

        logger.info(f"Backtester initialized with ${initial_capital:,.2f} capital")

    def apply_slippage(self, price: float, side: str) -> float:
        """Apply realistic slippage to price"""
        if side == 'LONG':
            # Buy at higher price
            return price * (1 + self.slippage)
        else:  # SHORT
            # Sell at lower price
            return price * (1 - self.slippage)

    def calculate_fees(self, position_value: float) -> float:
        """Calculate trading fees"""
        return position_value * self.trading_fee

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        side: str
    ) -> float:
        """
        Calculate position size based on risk management

        Uses 2% risk rule: risk no more than 2% of capital per trade
        """
        # Calculate risk per unit
        if side == 'LONG':
            risk_per_unit = entry_price - stop_loss
        else:  # SHORT
            risk_per_unit = stop_loss - entry_price

        if risk_per_unit <= 0:
            logger.warning(f"Invalid risk: entry={entry_price}, stop={stop_loss}")
            return 0

        # Position size based on risk
        max_risk_amount = self.capital * self.risk_per_trade
        risk_based_size = max_risk_amount / risk_per_unit

        # Position size based on max position limit
        max_position_value = self.capital * self.max_position_size
        limit_based_size = max_position_value / entry_price

        # Use smaller of the two
        position_size = min(risk_based_size, limit_based_size)

        return position_size

    def open_position(
        self,
        symbol: str,
        side: str,
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        timestamp: datetime
    ) -> bool:
        """
        Open a new position

        Returns:
            True if position opened successfully, False otherwise
        """
        # Apply slippage
        executed_price = self.apply_slippage(entry_price, side)

        # Calculate position size
        position_size = self.calculate_position_size(executed_price, stop_loss, side)

        if position_size <= 0:
            logger.warning("Position size is 0, skipping trade")
            return False

        # Calculate position value and fees
        position_value = position_size * executed_price
        fees = self.calculate_fees(position_value)

        # Check if we have enough capital
        required_capital = position_value + fees
        if required_capital > self.capital:
            logger.warning(f"Insufficient capital: need ${required_capital:.2f}, have ${self.capital:.2f}")
            return False

        # Open position
        self.position = Position(
            symbol=symbol,
            side=side,
            entry_time=timestamp,
            entry_price=executed_price,
            position_size=position_size,
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        # Deduct capital (position value + entry fees)
        self.capital -= required_capital

        logger.info(f"Opened {side} position: {position_size:.4f} @ ${executed_price:.2f} "
                   f"(SL: ${stop_loss:.2f}, TP: ${take_profit:.2f})")

        return True

    def close_position(
        self,
        exit_price: float,
        exit_reason: str,
        timestamp: datetime
    ) -> Optional[Trade]:
        """
        Close current position

        Returns:
            Trade object if position was closed, None otherwise
        """
        if not self.position:
            return None

        # Apply slippage (reverse of entry)
        executed_price = self.apply_slippage(exit_price,
                                             'SHORT' if self.position.side == 'LONG' else 'LONG')

        # Calculate P&L
        gross_pnl = self.position.calculate_pnl(executed_price)

        # Calculate fees (exit fees)
        position_value = self.position.position_size * executed_price
        fees = self.calculate_fees(position_value)

        # Net P&L after fees
        net_pnl = gross_pnl - fees
        pnl_pct = self.position.calculate_pnl_pct(executed_price)

        # Return capital + P&L
        self.capital += position_value + net_pnl

        # Calculate holding period
        holding_period = (timestamp - self.position.entry_time).total_seconds() / 3600  # hours

        # Create trade record
        trade = Trade(
            entry_time=self.position.entry_time,
            exit_time=timestamp,
            symbol=self.position.symbol,
            side=self.position.side,
            entry_price=self.position.entry_price,
            exit_price=executed_price,
            position_size=self.position.position_size,
            pnl=net_pnl,
            pnl_pct=pnl_pct,
            exit_reason=exit_reason,
            holding_period_hours=holding_period
        )

        self.trades.append(trade)

        logger.info(f"Closed {self.position.side} position: ${net_pnl:+.2f} ({pnl_pct:+.2f}%) - {exit_reason}")

        # Clear position
        self.position = None

        return trade

    def update_equity(self, timestamp: datetime, current_price: float):
        """Update equity history with current capital and unrealized P&L"""
        total_equity = self.capital

        # Add unrealized P&L if position is open
        if self.position:
            unrealized_pnl = self.position.calculate_pnl(current_price)
            total_equity += (self.position.position_size * current_price) + unrealized_pnl

        self.equity_history.append({
            'timestamp': timestamp,
            'equity': total_equity,
            'capital': self.capital,
            'unrealized_pnl': self.position.calculate_pnl(current_price) if self.position else 0
        })

    def run(
        self,
        data: pd.DataFrame,
        symbol: str = 'BTC/USDT'
    ) -> BacktestResult:
        """
        Run backtest on historical data

        Args:
            data: Historical OHLCV DataFrame with columns: timestamp, open, high, low, close, volume
            symbol: Trading pair symbol

        Returns:
            BacktestResult with performance metrics and trade history
        """
        logger.info(f"Starting backtest for {symbol} with {len(data)} candles")
        logger.info(f"Period: {data['timestamp'].iloc[0]} to {data['timestamp'].iloc[-1]}")

        # Reset state
        self.capital = self.initial_capital
        self.position = None
        self.trades = []
        self.equity_history = []

        # Iterate through each candle
        for idx in range(len(data)):
            current_candle = data.iloc[idx]
            timestamp = current_candle['timestamp']
            current_price = current_candle['close']
            high = current_candle['high']
            low = current_candle['low']

            # Check if we have a position
            if self.position:
                # Check stop loss (using intrabar low/high)
                if self.position.side == 'LONG' and low <= self.position.stop_loss:
                    self.close_position(self.position.stop_loss, 'STOP_LOSS', timestamp)
                elif self.position.side == 'SHORT' and high >= self.position.stop_loss:
                    self.close_position(self.position.stop_loss, 'STOP_LOSS', timestamp)
                # Check take profit
                elif self.position.side == 'LONG' and high >= self.position.take_profit:
                    self.close_position(self.position.take_profit, 'TAKE_PROFIT', timestamp)
                elif self.position.side == 'SHORT' and low <= self.position.take_profit:
                    self.close_position(self.position.take_profit, 'TAKE_PROFIT', timestamp)

            # Get trading signal (only if no position)
            if not self.position and idx >= 200:  # Need enough data for indicators
                # Get historical window for analysis
                window_data = data.iloc[max(0, idx-200):idx+1].copy()

                try:
                    # Run comprehensive analysis
                    analysis = self.agent.comprehensive_analysis(symbol, window_data)

                    if analysis and 'recommendation' in analysis:
                        action = analysis['recommendation'].get('action', 'WAIT')
                        confidence = analysis['recommendation'].get('confidence', 0)
                        entry_price = analysis['recommendation'].get('entry_price', current_price)
                        stop_loss = analysis['recommendation'].get('stop_loss')
                        take_profit = analysis['recommendation'].get('take_profit')

                        # Execute trade if signal is valid
                        if action in ['LONG', 'SHORT'] and confidence >= 40:
                            if stop_loss and take_profit:
                                self.open_position(
                                    symbol=symbol,
                                    side=action,
                                    entry_price=entry_price,
                                    stop_loss=stop_loss,
                                    take_profit=take_profit,
                                    timestamp=timestamp
                                )
                except Exception as e:
                    logger.error(f"Error during analysis at {timestamp}: {e}")
                    continue

            # Update equity tracking
            self.update_equity(timestamp, current_price)

        # Close any open position at end
        if self.position:
            final_price = data.iloc[-1]['close']
            final_timestamp = data.iloc[-1]['timestamp']
            self.close_position(final_price, 'END_OF_DATA', final_timestamp)

        # Calculate performance metrics
        results = self._calculate_metrics()

        logger.info(f"Backtest complete: {results.total_trades} trades, "
                   f"{results.total_return_pct:+.2f}% return")

        return results

    def _calculate_metrics(self) -> BacktestResult:
        """Calculate performance metrics from trades"""
        if not self.trades:
            logger.warning("No trades executed during backtest")
            return BacktestResult(
                initial_capital=self.initial_capital,
                final_capital=self.capital,
                total_return=0,
                total_return_pct=0,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                win_rate=0,
                profit_factor=0,
                sharpe_ratio=0,
                sortino_ratio=0,
                max_drawdown=0,
                max_drawdown_pct=0,
                avg_trade_return=0,
                avg_winning_trade=0,
                avg_losing_trade=0,
                largest_win=0,
                largest_loss=0,
                trades=[],
                equity_curve=pd.DataFrame()
            )

        # Basic metrics
        total_return = self.capital - self.initial_capital
        total_return_pct = (total_return / self.initial_capital) * 100

        winning_trades = [t for t in self.trades if t.pnl > 0]
        losing_trades = [t for t in self.trades if t.pnl <= 0]

        win_rate = (len(winning_trades) / len(self.trades)) * 100 if self.trades else 0

        # Profit factor
        gross_profit = sum(t.pnl for t in winning_trades) if winning_trades else 0
        gross_loss = abs(sum(t.pnl for t in losing_trades)) if losing_trades else 0
        profit_factor = gross_profit / gross_loss if gross_loss > 0 else 0

        # Average trades
        avg_trade = total_return / len(self.trades) if self.trades else 0
        avg_win = sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0

        # Largest win/loss
        largest_win = max((t.pnl for t in winning_trades), default=0)
        largest_loss = min((t.pnl for t in losing_trades), default=0)

        # Create equity curve DataFrame
        equity_df = pd.DataFrame(self.equity_history)

        # Sharpe ratio
        if len(equity_df) > 1:
            returns = equity_df['equity'].pct_change().dropna()
            sharpe_ratio = (returns.mean() / returns.std()) * np.sqrt(365 * 24) if returns.std() > 0 else 0

            # Sortino ratio (uses only downside deviation)
            downside_returns = returns[returns < 0]
            downside_std = downside_returns.std() if len(downside_returns) > 0 else 0
            sortino_ratio = (returns.mean() / downside_std) * np.sqrt(365 * 24) if downside_std > 0 else 0
        else:
            sharpe_ratio = 0
            sortino_ratio = 0

        # Maximum drawdown
        if len(equity_df) > 0:
            equity_curve = equity_df['equity'].values
            peak = np.maximum.accumulate(equity_curve)
            drawdown = (peak - equity_curve) / peak
            max_drawdown_pct = drawdown.max() * 100
            max_drawdown = peak[drawdown.argmax()] - equity_curve[drawdown.argmax()]
        else:
            max_drawdown = 0
            max_drawdown_pct = 0

        return BacktestResult(
            initial_capital=self.initial_capital,
            final_capital=self.capital,
            total_return=total_return,
            total_return_pct=total_return_pct,
            total_trades=len(self.trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            win_rate=win_rate,
            profit_factor=profit_factor,
            sharpe_ratio=sharpe_ratio,
            sortino_ratio=sortino_ratio,
            max_drawdown=max_drawdown,
            max_drawdown_pct=max_drawdown_pct,
            avg_trade_return=avg_trade,
            avg_winning_trade=avg_win,
            avg_losing_trade=avg_loss,
            largest_win=largest_win,
            largest_loss=largest_loss,
            trades=self.trades,
            equity_curve=equity_df
        )


if __name__ == '__main__':
    print("Backtesting Framework Module")
    print("Import this module to use the Backtester class")
