"""
ClawBack - Trade Execution Engine
Scales congressional trades to user's account size and manages execution
Includes trailing stop-loss and risk management features
"""
import json
import logging
import time
from datetime import datetime, time as dt_time, timedelta
from decimal import Decimal, ROUND_DOWN
import math
import os
from zoneinfo import ZoneInfo

logger = logging.getLogger(__name__)


class Position:
    """Represents an open position with stop-loss tracking"""

    def __init__(self, symbol: str, quantity: int, entry_price: float,
                 entry_date: datetime, congressional_trade_id: int = None):
        self.symbol = symbol
        self.quantity = quantity
        self.entry_price = entry_price
        self.entry_date = entry_date
        self.congressional_trade_id = congressional_trade_id

        # Stop-loss tracking
        self.highest_price = entry_price  # For trailing stop
        self.stop_loss_price = None
        self.trailing_stop_active = False
        self.trailing_stop_percent = 0.05  # 5% trailing stop

    def update_price(self, current_price: float):
        """Update position with current price, adjust trailing stop"""
        if current_price > self.highest_price:
            self.highest_price = current_price

            # If trailing stop is active, update stop price
            if self.trailing_stop_active:
                self.stop_loss_price = self.highest_price * (1 - self.trailing_stop_percent)

    def check_stop_loss(self, current_price: float) -> bool:
        """Check if stop-loss has been triggered"""
        if self.stop_loss_price and current_price <= self.stop_loss_price:
            return True
        return False

    def get_unrealized_pnl(self, current_price: float) -> float:
        """Calculate unrealized P&L"""
        return (current_price - self.entry_price) * self.quantity

    def get_unrealized_pnl_percent(self, current_price: float) -> float:
        """Calculate unrealized P&L as percentage"""
        return (current_price - self.entry_price) / self.entry_price

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        return {
            'symbol': self.symbol,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'entry_date': self.entry_date.isoformat(),
            'highest_price': self.highest_price,
            'stop_loss_price': self.stop_loss_price,
            'trailing_stop_active': self.trailing_stop_active,
            'congressional_trade_id': self.congressional_trade_id
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create Position from dictionary"""
        pos = cls(
            symbol=data['symbol'],
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            entry_date=datetime.fromisoformat(data['entry_date']),
            congressional_trade_id=data.get('congressional_trade_id')
        )
        pos.highest_price = data.get('highest_price', pos.entry_price)
        pos.stop_loss_price = data.get('stop_loss_price')
        pos.trailing_stop_active = data.get('trailing_stop_active', False)
        return pos


class TradeEngine:
    """Calculates and executes scaled trades with risk management"""

    def __init__(self, broker_client, config):
        self.broker = broker_client
        self.config = config

        # Trading parameters
        self.trade_scale = Decimal(str(config['trading'].get('tradeScalePercentage', 0.05)))
        self.max_position_pct = Decimal(str(config['trading'].get('maxPositionPercentage', 0.05)))
        self.max_positions = config['trading'].get('maxPositions', 20)
        self.daily_loss_limit = Decimal(str(config['trading'].get('dailyLossLimit', 0.03)))

        # Risk management parameters
        risk_config = config.get('riskManagement', {})
        self.position_stop_loss = Decimal(str(risk_config.get('positionStopLoss', 0.08)))
        self.trailing_stop_activation = Decimal(str(risk_config.get('trailingStopActivation', 0.10)))
        self.trailing_stop_percent = Decimal(str(risk_config.get('trailingStopPercent', 0.05)))
        self.max_drawdown = Decimal(str(risk_config.get('maxDrawdown', 0.15)))
        self.consecutive_loss_limit = risk_config.get('consecutiveLossLimit', 3)

        # Strategy parameters
        strategy_config = config.get('strategy', {})
        self.entry_delay_days = strategy_config.get('entryDelayDays', 3)
        self.holding_period_days = strategy_config.get('holdingPeriodDays', 30)

        # Market hours (NYSE operates in America/New_York timezone)
        self.market_hours_only = config['trading'].get('marketHoursOnly', True)
        self.market_timezone = ZoneInfo(config['trading'].get('marketTimezone', 'America/New_York'))
        self.market_open = self._parse_time(config['trading'].get('marketOpen', '09:30'))
        self.market_close = self._parse_time(config['trading'].get('marketClose', '16:00'))

        # State tracking
        self.daily_pnl = Decimal('0')
        self.positions: dict[str, Position] = {}  # symbol -> Position
        self.trade_history = []
        self.consecutive_losses = 0
        self.peak_portfolio_value = None

        # Load saved positions
        self._load_positions()

        logger.info("Initialized trade engine with risk management")
    
    def _parse_time(self, time_str):
        """Parse time string like '09:30' to time object"""
        try:
            hour, minute = map(int, time_str.split(':'))
            return dt_time(hour, minute)
        except (ValueError, AttributeError):
            logger.warning(f"Invalid time format: {time_str}, using default 09:30")
            return dt_time(9, 30)
    
    def is_market_open(self):
        """Check if current time is within NYSE market hours"""
        if not self.market_hours_only:
            return True

        # Get current time in market timezone (NYSE = America/New_York)
        now_market = datetime.now(self.market_timezone)
        current_time = now_market.time()

        # Check if weekday (Mon-Fri)
        if now_market.weekday() >= 5:  # 5 = Saturday, 6 = Sunday
            return False

        # Check time
        return self.market_open <= current_time <= self.market_close

    def get_next_market_open(self):
        """Get the next market open time as a datetime in local timezone"""
        now_market = datetime.now(self.market_timezone)
        local_tz = datetime.now().astimezone().tzinfo

        # Start with today's market open
        next_open = now_market.replace(
            hour=self.market_open.hour,
            minute=self.market_open.minute,
            second=0,
            microsecond=0
        )

        # If market already opened today, move to tomorrow
        if now_market.time() >= self.market_open:
            next_open += timedelta(days=1)

        # Skip weekends
        while next_open.weekday() >= 5:
            next_open += timedelta(days=1)

        # Convert to local timezone for scheduling
        return next_open.astimezone(local_tz)

    def seconds_until_market_open(self):
        """Get seconds until next market open"""
        next_open = self.get_next_market_open()
        now = datetime.now(next_open.tzinfo)
        delta = next_open - now
        return max(0, delta.total_seconds())
    
    def calculate_scaled_trade(self, congress_trade, account_balance):
        """
        Calculate scaled trade based on congressional trade amount
        Returns: symbol, quantity, action, estimated_cost
        """
        try:
            symbol = congress_trade['ticker'].upper()
            action = 'BUY' if congress_trade['transaction_type'] == 'purchase' else 'SELL'
            congress_amount = Decimal(str(congress_trade['amount']))
            
            # Get current quote for price
            quote = self.broker.get_quote(symbol)
            if not quote:
                logger.warning(f"No quote available for {symbol}")
                return None
            
            current_price = Decimal(str(quote['last_price']))
            
            # Calculate target investment amount
            # Scale congressional trade by configured percentage
            target_amount = account_balance * self.trade_scale
            
            # Calculate quantity (round down to whole shares)
            quantity = (target_amount / current_price).quantize(Decimal('1.'), rounding=ROUND_DOWN)
            
            # Ensure minimum of 1 share
            if quantity < 1:
                logger.info(f"Target amount too small for {symbol}: ${target_amount:.2f} at ${current_price:.2f}")
                return None
            
            estimated_cost = quantity * current_price
            
            logger.info(f"Calculated trade: {action} {quantity} shares of {symbol} at ~${current_price:.2f} (${estimated_cost:.2f})")
            
            return {
                'symbol': symbol,
                'quantity': int(quantity),
                'action': action,
                'estimated_price': float(current_price),
                'estimated_cost': float(estimated_cost),
                'congress_amount': float(congress_amount),
                'scale_factor': float(self.trade_scale)
            }
            
        except Exception as e:
            logger.error(f"Error calculating scaled trade: {e}")
            return None
    
    def check_position_limits(self, symbol, quantity, action, account_value):
        """Check if trade violates position limits"""
        try:
            # Get current positions
            positions = self.broker.get_positions()
            
            # Find existing position for this symbol
            current_position = 0
            for pos in positions:
                if pos['symbol'] == symbol:
                    current_position = pos['quantity']
                    current_value = pos['market_value']
                    break
            
            # Calculate new position
            if action == 'BUY':
                new_position = current_position + quantity
            else:  # SELL
                new_position = current_position - quantity
            
            # Get current quote for value calculation
            quote = self.broker.get_quote(symbol)
            if not quote:
                logger.warning(f"No quote for {symbol}, skipping limit check")
                return True
            
            current_price = Decimal(str(quote['last_price']))
            position_value = abs(new_position) * current_price
            
            # Check max position percentage
            max_position_value = account_value * self.max_position_pct
            
            if position_value > max_position_value:
                logger.warning(
                    f"Position limit exceeded: ${position_value:.2f} > ${max_position_value:.2f} "
                    f"({float(self.max_position_pct)*100:.1f}% of account)"
                )
                return False
            
            # Check if selling more than owned
            if action == 'SELL' and quantity > current_position:
                logger.warning(f"Attempting to sell {quantity} shares but only own {current_position}")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error checking position limits: {e}")
            return False
    
    def check_daily_loss_limit(self):
        """Check if daily loss limit has been exceeded"""
        # Note: This is a simplified check
        # In production, you'd want more sophisticated P&L tracking
        if self.daily_pnl < -abs(self.daily_loss_limit):
            logger.error(f"Daily loss limit exceeded: ${self.daily_pnl:.2f}")
            return False
        return True
    
    def execute_trade(self, trade_calculation):
        """Execute a calculated trade"""
        try:
            # Check market hours
            if not self.is_market_open():
                logger.warning("Market is closed, skipping trade execution")
                return False
            
            # Check daily loss limit
            if not self.check_daily_loss_limit():
                logger.warning("Daily loss limit exceeded, skipping trade")
                return False
            
            # Get account balance for limit checks
            balance_info = self.broker.get_account_balance()
            if not balance_info:
                logger.error("Could not get account balance")
                return False
            
            account_value = Decimal(str(balance_info['total_value']))
            
            # Check position limits
            if not self.check_position_limits(
                trade_calculation['symbol'],
                trade_calculation['quantity'],
                trade_calculation['action'],
                account_value
            ):
                logger.warning("Trade violates position limits")
                return False
            
            # Prepare order details
            order_details = {
                'symbol': trade_calculation['symbol'],
                'quantity': trade_calculation['quantity'],
                'action': trade_calculation['action'],
                'price_type': 'MARKET',  # Start with market orders
                'order_type': 'EQ'
            }
            
            # Execute order
            success = self.broker.place_order(
                self.broker.account_id,
                order_details
            )
            
            if success:
                # Record trade
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': trade_calculation['symbol'],
                    'action': trade_calculation['action'],
                    'quantity': trade_calculation['quantity'],
                    'estimated_price': trade_calculation['estimated_price'],
                    'estimated_cost': trade_calculation['estimated_cost'],
                    'congress_amount': trade_calculation.get('congress_amount'),
                    'scale_factor': trade_calculation.get('scale_factor'),
                    'status': 'executed'
                }

                self.trade_history.append(trade_record)
                logger.info(f"Trade executed successfully: {trade_calculation['action']} "
                          f"{trade_calculation['quantity']} {trade_calculation['symbol']}")

                # Track position for stop-loss management
                if trade_calculation['action'] == 'BUY':
                    self.add_position(
                        symbol=trade_calculation['symbol'],
                        quantity=trade_calculation['quantity'],
                        entry_price=trade_calculation['estimated_price'],
                        congressional_trade_id=trade_calculation.get('congressional_trade_id')
                    )
                    self.consecutive_losses = 0  # Reset on successful buy
                elif trade_calculation['action'] == 'SELL':
                    self.remove_position(
                        symbol=trade_calculation['symbol'],
                        quantity=trade_calculation['quantity']
                    )

                return True
            else:
                logger.error("Failed to execute trade")
                return False
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            return False
    
    def process_congressional_trades(self, congress_trades):
        """Process multiple congressional trades"""
        try:
            # Get current account balance
            balance_info = self.broker.get_account_balance()
            if not balance_info:
                logger.error("Could not get account balance")
                return []
            
            account_balance = Decimal(str(balance_info['cash_available']))
            logger.info(f"Processing trades with account balance: ${account_balance:.2f}")
            
            executed_trades = []
            
            for congress_trade in congress_trades:
                # Calculate scaled trade
                trade_calc = self.calculate_scaled_trade(congress_trade, account_balance)
                
                if not trade_calc:
                    continue
                
                # Execute trade
                if self.execute_trade(trade_calc):
                    executed_trades.append(trade_calc)
                    
                    # Update account balance for next calculation
                    # This is approximate - real balance would update after trade
                    account_balance -= Decimal(str(trade_calc['estimated_cost']))
                    
                    # Small delay between trades
                    time.sleep(2)
            
            logger.info(f"Executed {len(executed_trades)} trades")
            return executed_trades
            
        except Exception as e:
            logger.error(f"Error processing congressional trades: {e}")
            return []
    
    def save_trade_history(self, filename='trade_history.json'):
        """Save trade history to file"""
        try:
            with open(filename, 'w') as f:
                json.dump(self.trade_history, f, indent=2, default=str)
            
            logger.info(f"Saved {len(self.trade_history)} trades to {filename}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving trade history: {e}")
            return False
    
    def load_trade_history(self, filename='trade_history.json'):
        """Load trade history from file"""
        try:
            with open(filename, 'r') as f:
                self.trade_history = json.load(f)
            
            logger.info(f"Loaded {len(self.trade_history)} trades from {filename}")
            return True
            
        except (FileNotFoundError, json.JSONDecodeError):
            logger.warning(f"Could not load trade history from {filename}")
            self.trade_history = []
            return False
        except Exception as e:
            logger.error(f"Error loading trade history: {e}")
            return False
    
    def get_trade_summary(self):
        """Get summary of trading activity"""
        total_trades = len(self.trade_history)
        buy_trades = sum(1 for t in self.trade_history if t['action'] == 'BUY')
        sell_trades = total_trades - buy_trades

        total_cost = sum(t.get('estimated_cost', 0) for t in self.trade_history)

        return {
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'total_estimated_cost': total_cost,
            'last_trade': self.trade_history[-1] if self.trade_history else None,
            'daily_pnl': float(self.daily_pnl),
            'open_positions': len(self.positions),
            'consecutive_losses': self.consecutive_losses
        }

    # ==================== POSITION MANAGEMENT ====================

    def _load_positions(self):
        """Load saved positions from file"""
        positions_file = 'data/positions.json'
        try:
            if os.path.exists(positions_file):
                with open(positions_file, 'r') as f:
                    data = json.load(f)
                for symbol, pos_data in data.items():
                    self.positions[symbol] = Position.from_dict(pos_data)
                logger.info(f"Loaded {len(self.positions)} positions from file")
        except Exception as e:
            logger.warning(f"Could not load positions: {e}")

    def _save_positions(self):
        """Save positions to file"""
        positions_file = 'data/positions.json'
        try:
            os.makedirs('data', exist_ok=True)
            data = {symbol: pos.to_dict() for symbol, pos in self.positions.items()}
            with open(positions_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save positions: {e}")

    def add_position(self, symbol: str, quantity: int, entry_price: float,
                    congressional_trade_id: int = None):
        """Add or update a position"""
        if symbol in self.positions:
            # Average into existing position
            existing = self.positions[symbol]
            total_qty = existing.quantity + quantity
            avg_price = ((existing.entry_price * existing.quantity) +
                        (entry_price * quantity)) / total_qty
            existing.quantity = total_qty
            existing.entry_price = avg_price
        else:
            # Create new position
            pos = Position(
                symbol=symbol,
                quantity=quantity,
                entry_price=entry_price,
                entry_date=datetime.now(),
                congressional_trade_id=congressional_trade_id
            )
            # Set initial stop-loss (fixed percentage below entry)
            pos.stop_loss_price = entry_price * (1 - float(self.position_stop_loss))
            self.positions[symbol] = pos

        self._save_positions()
        logger.info(f"Added position: {quantity} {symbol} @ ${entry_price:.2f}")

    def remove_position(self, symbol: str, quantity: int = None):
        """Remove or reduce a position"""
        if symbol not in self.positions:
            return

        pos = self.positions[symbol]
        if quantity is None or quantity >= pos.quantity:
            del self.positions[symbol]
        else:
            pos.quantity -= quantity

        self._save_positions()

    # ==================== STOP-LOSS MANAGEMENT ====================

    def check_stop_losses(self) -> list:
        """Check all positions for stop-loss triggers, return symbols to sell"""
        triggered = []

        for symbol, pos in self.positions.items():
            try:
                quote = self.broker.get_quote(symbol)
                if not quote:
                    continue

                current_price = quote['last_price']

                # Update position with current price (adjusts trailing stop)
                pos.update_price(current_price)

                # Check if trailing stop should be activated
                gain_pct = pos.get_unrealized_pnl_percent(current_price)
                if gain_pct >= float(self.trailing_stop_activation) and not pos.trailing_stop_active:
                    pos.trailing_stop_active = True
                    pos.trailing_stop_percent = float(self.trailing_stop_percent)
                    pos.stop_loss_price = pos.highest_price * (1 - pos.trailing_stop_percent)
                    logger.info(f"Trailing stop activated for {symbol} at ${pos.stop_loss_price:.2f}")

                # Check if stop-loss triggered
                if pos.check_stop_loss(current_price):
                    triggered.append({
                        'symbol': symbol,
                        'quantity': pos.quantity,
                        'current_price': current_price,
                        'stop_price': pos.stop_loss_price,
                        'entry_price': pos.entry_price,
                        'pnl_percent': gain_pct * 100
                    })
                    logger.warning(f"STOP-LOSS TRIGGERED: {symbol} at ${current_price:.2f} "
                                  f"(stop: ${pos.stop_loss_price:.2f})")

            except Exception as e:
                logger.error(f"Error checking stop-loss for {symbol}: {e}")

        self._save_positions()
        return triggered

    def execute_stop_loss(self, stop_info: dict) -> bool:
        """Execute a stop-loss sell order"""
        try:
            symbol = stop_info['symbol']
            quantity = stop_info['quantity']

            logger.info(f"Executing stop-loss: SELL {quantity} {symbol}")

            order_details = {
                'symbol': symbol,
                'quantity': quantity,
                'action': 'SELL',
                'price_type': 'MARKET',
                'order_type': 'EQ'
            }

            success = self.broker.place_order(
                self.broker.account_id,
                order_details
            )

            if success:
                # Record the trade
                trade_record = {
                    'timestamp': datetime.now().isoformat(),
                    'symbol': symbol,
                    'action': 'SELL',
                    'quantity': quantity,
                    'trigger': 'STOP_LOSS',
                    'stop_price': stop_info['stop_price'],
                    'entry_price': stop_info['entry_price'],
                    'pnl_percent': stop_info['pnl_percent'],
                    'status': 'executed'
                }
                self.trade_history.append(trade_record)

                # Update consecutive losses
                if stop_info['pnl_percent'] < 0:
                    self.consecutive_losses += 1
                else:
                    self.consecutive_losses = 0

                # Remove position
                self.remove_position(symbol)

                return True
            else:
                logger.error(f"Failed to execute stop-loss for {symbol}")
                return False

        except Exception as e:
            logger.error(f"Error executing stop-loss: {e}")
            return False

    def run_stop_loss_monitor(self):
        """Run a single cycle of stop-loss monitoring"""
        if not self.is_market_open():
            return []

        triggered = self.check_stop_losses()
        executed = []

        for stop_info in triggered:
            if self.execute_stop_loss(stop_info):
                executed.append(stop_info)

        return executed

    # ==================== HOLDING PERIOD MANAGEMENT ====================

    def check_holding_periods(self) -> list:
        """Check for positions that have exceeded holding period"""
        to_sell = []
        target_hold = timedelta(days=self.holding_period_days)

        for symbol, pos in self.positions.items():
            hold_duration = datetime.now() - pos.entry_date
            if hold_duration >= target_hold:
                try:
                    quote = self.broker.get_quote(symbol)
                    current_price = quote['last_price'] if quote else pos.entry_price

                    to_sell.append({
                        'symbol': symbol,
                        'quantity': pos.quantity,
                        'current_price': current_price,
                        'entry_price': pos.entry_price,
                        'hold_days': hold_duration.days,
                        'pnl_percent': pos.get_unrealized_pnl_percent(current_price) * 100
                    })
                    logger.info(f"Position {symbol} exceeded holding period ({hold_duration.days} days)")
                except Exception as e:
                    logger.error(f"Error checking holding period for {symbol}: {e}")

        return to_sell

    # ==================== PORTFOLIO RISK MANAGEMENT ====================

    def check_portfolio_risk(self) -> dict:
        """Check overall portfolio risk metrics"""
        try:
            balance = self.broker.get_account_balance()
            if not balance:
                return {'status': 'unknown', 'message': 'Could not get balance'}

            total_value = Decimal(str(balance['total_value']))

            # Track peak value for drawdown
            if self.peak_portfolio_value is None:
                self.peak_portfolio_value = total_value
            elif total_value > self.peak_portfolio_value:
                self.peak_portfolio_value = total_value

            # Calculate drawdown
            drawdown = (self.peak_portfolio_value - total_value) / self.peak_portfolio_value

            # Risk checks
            warnings = []
            halt_trading = False

            if drawdown >= self.max_drawdown:
                warnings.append(f"MAX DRAWDOWN EXCEEDED: {drawdown*100:.1f}%")
                halt_trading = True

            if self.consecutive_losses >= self.consecutive_loss_limit:
                warnings.append(f"CONSECUTIVE LOSS LIMIT: {self.consecutive_losses} losses")
                halt_trading = True

            if len(self.positions) >= self.max_positions:
                warnings.append(f"MAX POSITIONS REACHED: {len(self.positions)}")

            return {
                'status': 'halt' if halt_trading else 'ok',
                'total_value': float(total_value),
                'peak_value': float(self.peak_portfolio_value),
                'drawdown': float(drawdown) * 100,
                'open_positions': len(self.positions),
                'consecutive_losses': self.consecutive_losses,
                'warnings': warnings
            }

        except Exception as e:
            logger.error(f"Error checking portfolio risk: {e}")
            return {'status': 'error', 'message': str(e)}

    def get_position_summary(self) -> list:
        """Get summary of all open positions"""
        summary = []

        for symbol, pos in self.positions.items():
            try:
                quote = self.broker.get_quote(symbol)
                current_price = quote['last_price'] if quote else pos.entry_price

                summary.append({
                    'symbol': symbol,
                    'quantity': pos.quantity,
                    'entry_price': pos.entry_price,
                    'current_price': current_price,
                    'market_value': current_price * pos.quantity,
                    'unrealized_pnl': pos.get_unrealized_pnl(current_price),
                    'pnl_percent': pos.get_unrealized_pnl_percent(current_price) * 100,
                    'stop_loss': pos.stop_loss_price,
                    'trailing_active': pos.trailing_stop_active,
                    'days_held': (datetime.now() - pos.entry_date).days
                })
            except Exception as e:
                logger.error(f"Error getting summary for {symbol}: {e}")

        return sorted(summary, key=lambda x: x.get('pnl_percent', 0), reverse=True)