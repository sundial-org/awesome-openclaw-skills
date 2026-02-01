#!/usr/bin/env python3
"""
Position Sizer - Extracted from EnhancedTradingAgent

Calculates position sizes using standard risk rules and Kelly Criterion.
Single Responsibility: Calculate optimal position sizes
"""

from typing import Dict
import logging

logger = logging.getLogger(__name__)


class PositionSizer:
    """
    Calculates position sizes for trades

    Responsibilities:
    - Calculate position size using 2% risk rule
    - Calculate position size using Kelly Criterion
    - Cap position sizes to account limits
    - Estimate trading fees
    - Provide sizing recommendations
    """

    def __init__(
        self,
        analytics=None,
        max_risk_percent: float = 0.02,
        max_position_percent: float = 0.10,
        trading_fee_percent: float = 0.002
    ):
        """
        Initialize position sizer

        Args:
            analytics: AdvancedAnalytics instance for Kelly Criterion
            max_risk_percent: Maximum risk per trade (default: 2%)
            max_position_percent: Maximum position size (default: 10%)
            trading_fee_percent: Trading fee percentage (default: 0.2%)
        """
        self.analytics = analytics
        self.max_risk_percent = max_risk_percent
        self.max_position_percent = max_position_percent
        self.trading_fee_percent = trading_fee_percent
        logger.info(f"Initialized PositionSizer: max_risk={max_risk_percent:.1%}, max_pos={max_position_percent:.1%}")

    def calculate_position_size(
        self,
        entry_price: float,
        stop_loss: float,
        balance: float,
        risk_metrics: Dict = None
    ) -> Dict:
        """
        Calculate position size using multiple methods

        Args:
            entry_price: Planned entry price
            stop_loss: Stop-loss price
            balance: Account balance in USD
            risk_metrics: Optional risk metrics for Kelly Criterion

        Returns:
            Dict with position sizing:
            - standard_size_coin: Coin amount (2% risk rule)
            - standard_value_usd: USD value of position
            - risk_usd: Dollar risk amount
            - risk_percent: Risk percentage
            - kelly_conservative_usd: Kelly conservative sizing
            - kelly_aggressive_usd: Kelly aggressive sizing
            - recommendation: Sizing recommendation
            - trading_fees_est: Estimated trading fees
        """
        try:
            # Validate inputs
            if entry_price <= 0:
                return {'error': 'Invalid entry price'}

            if stop_loss <= 0:
                return {'error': 'Invalid stop loss'}

            if balance <= 0:
                return {'error': 'Invalid balance'}

            # Standard 2% risk sizing
            standard_sizing = self._calculate_standard_sizing(
                entry_price,
                stop_loss,
                balance
            )

            # Kelly Criterion sizing (if metrics available)
            kelly_sizing = self._calculate_kelly_sizing(
                balance,
                risk_metrics or {}
            )

            # Combine results
            result = {
                **standard_sizing,
                'kelly_conservative_usd': kelly_sizing.get('conservative_dollar'),
                'kelly_aggressive_usd': kelly_sizing.get('aggressive_dollar'),
                'recommendation': 'Use standard 2% risk sizing for consistent risk management',
                'trading_fees_est': round(standard_sizing['standard_value_usd'] * self.trading_fee_percent, 2)
            }

            logger.info(f"Position size: {result['standard_size_coin']:.6f} coins (${result['standard_value_usd']:.2f})")
            return result

        except Exception as e:
            logger.error(f"Position sizing failed: {e}")
            return {'error': str(e)}

    def _calculate_standard_sizing(
        self,
        entry_price: float,
        stop_loss: float,
        balance: float
    ) -> Dict:
        """
        Calculate position size using standard 2% risk rule

        Args:
            entry_price: Entry price
            stop_loss: Stop-loss price
            balance: Account balance

        Returns:
            Dict with standard sizing calculations
        """
        # Calculate maximum risk in USD
        max_risk_usd = balance * self.max_risk_percent

        # Calculate price risk per coin
        price_risk = abs(entry_price - stop_loss)

        if price_risk == 0:
            return {
                'error': 'Invalid stop loss - no risk distance',
                'standard_size_coin': 0,
                'standard_value_usd': 0,
                'risk_usd': 0,
                'risk_percent': 0
            }

        # Calculate position size in coins
        standard_size_coin = max_risk_usd / price_risk
        standard_value_usd = standard_size_coin * entry_price

        # Cap at maximum position size
        max_position = balance * self.max_position_percent
        if standard_value_usd > max_position:
            standard_value_usd = max_position
            standard_size_coin = standard_value_usd / entry_price
            logger.warning(f"Position capped at {self.max_position_percent:.1%} of balance")

        return {
            'standard_size_coin': round(standard_size_coin, 6),
            'standard_value_usd': round(standard_value_usd, 2),
            'risk_usd': round(max_risk_usd, 2),
            'risk_percent': self.max_risk_percent * 100
        }

    def _calculate_kelly_sizing(
        self,
        balance: float,
        risk_metrics: Dict
    ) -> Dict:
        """
        Calculate position size using Kelly Criterion

        Args:
            balance: Account balance
            risk_metrics: Dict with win_rate_pct and profit_factor

        Returns:
            Dict with Kelly sizing or error
        """
        if not self.analytics:
            return {'error': 'No analytics engine available'}

        win_rate_pct = risk_metrics.get('win_rate_pct', 0)
        profit_factor = risk_metrics.get('profit_factor', 0)

        # Need valid metrics for Kelly
        if win_rate_pct <= 0 or profit_factor <= 1:
            return {'error': 'Insufficient data for Kelly'}

        try:
            # Convert to proper format
            win_rate = win_rate_pct / 100
            avg_win = profit_factor / (profit_factor + 1)
            avg_loss = 1 / (profit_factor + 1)

            # Calculate Kelly sizing
            kelly_result = self.analytics.optimal_position_size_kelly(
                win_rate=win_rate,
                avg_win=avg_win,
                avg_loss=avg_loss,
                account_balance=balance,
                max_position_pct=0.20  # Kelly can be aggressive, cap at 20%
            )

            return kelly_result

        except Exception as e:
            logger.warning(f"Kelly calculation failed: {e}")
            return {'error': str(e)}

    def validate_position_size(
        self,
        position_value_usd: float,
        balance: float
    ) -> tuple[bool, str]:
        """
        Validate that position size is within acceptable limits

        Args:
            position_value_usd: Position value in USD
            balance: Account balance

        Returns:
            Tuple of (is_valid, message)
        """
        max_allowed = balance * self.max_position_percent

        if position_value_usd > max_allowed:
            return False, f"Position ${position_value_usd:.2f} exceeds maximum ${max_allowed:.2f}"

        if position_value_usd < 10:
            return False, f"Position ${position_value_usd:.2f} too small (minimum $10)"

        return True, "Position size valid"

    def get_position_limits(self, balance: float) -> Dict:
        """
        Get position size limits for account

        Args:
            balance: Account balance

        Returns:
            Dict with limits:
            - max_position_usd: Maximum position size
            - max_risk_usd: Maximum risk per trade
            - min_position_usd: Minimum position size
        """
        return {
            'max_position_usd': balance * self.max_position_percent,
            'max_risk_usd': balance * self.max_risk_percent,
            'min_position_usd': 10.0,
            'max_risk_percent': self.max_risk_percent * 100,
            'max_position_percent': self.max_position_percent * 100
        }
