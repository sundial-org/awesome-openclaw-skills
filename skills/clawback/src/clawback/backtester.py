"""
Backtesting engine for congressional trading strategies
Tests various entry timing, position sizing, and filtering strategies
"""
import json
import logging
import requests
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import List, Dict, Optional
import time

logger = logging.getLogger(__name__)

# Try to import yfinance for historical prices
try:
    import yfinance as yf
    HAS_YFINANCE = True
except ImportError:
    HAS_YFINANCE = False
    logger.warning("yfinance not installed - run: pip install yfinance")


@dataclass
class Trade:
    """Represents a congressional trade"""
    ticker: str
    transaction_type: str  # 'purchase' or 'sale'
    transaction_date: datetime
    disclosure_date: datetime
    amount: float
    representative: str
    chamber: str = 'house'
    is_leader: bool = False
    committee_relevant: bool = False


@dataclass
class BacktestResult:
    """Results from a backtest run"""
    strategy_name: str
    total_trades: int
    winning_trades: int
    losing_trades: int
    total_return: float
    avg_return_per_trade: float
    max_drawdown: float
    sharpe_ratio: float
    win_rate: float
    avg_holding_days: float
    best_trade: float
    worst_trade: float
    trades_detail: List[Dict]


class CongressionalBacktester:
    """Backtests congressional trading strategies"""

    # Known congressional leaders (for filtering)
    LEADERS = [
        'pelosi', 'schumer', 'mcconnell', 'jeffries', 'johnson',
        'scalise', 'thune', 'durbin', 'clark', 'aguilar'
    ]

    # Committee chairs have informational advantage
    COMMITTEE_CHAIRS = [
        'wicker', 'crapo', 'grassley', 'graham', 'murkowski',
        'collins', 'capito', 'cassidy', 'tuberville', 'cruz'
    ]

    def __init__(self, initial_capital: float = 50000):
        self.initial_capital = initial_capital
        self.price_cache = {}

    def get_historical_price(self, ticker: str, date: datetime, days_forward: int = 0) -> Optional[float]:
        """Get historical stock price using yfinance"""
        if not HAS_YFINANCE:
            return None

        cache_key = f"{ticker}_{date.strftime('%Y-%m-%d')}_{days_forward}"
        if cache_key in self.price_cache:
            return self.price_cache[cache_key]

        try:
            target_date = date + timedelta(days=days_forward)
            start = target_date - timedelta(days=5)
            end = target_date + timedelta(days=5)

            stock = yf.Ticker(ticker)
            hist = stock.history(start=start.strftime('%Y-%m-%d'),
                                end=end.strftime('%Y-%m-%d'))

            if hist.empty:
                return None

            # Find closest trading day
            target_str = target_date.strftime('%Y-%m-%d')
            if target_str in hist.index.strftime('%Y-%m-%d').tolist():
                price = hist.loc[target_str]['Close']
            else:
                # Get the first available price after target
                price = hist['Close'].iloc[0]

            self.price_cache[cache_key] = float(price)
            return float(price)

        except Exception as e:
            logger.debug(f"Error getting price for {ticker}: {e}")
            return None

    def calculate_return(self, ticker: str, entry_date: datetime,
                        exit_days: int, is_purchase: bool) -> Optional[float]:
        """Calculate return for a trade"""
        entry_price = self.get_historical_price(ticker, entry_date)
        exit_price = self.get_historical_price(ticker, entry_date, exit_days)

        if entry_price is None or exit_price is None:
            return None

        if is_purchase:
            return (exit_price - entry_price) / entry_price
        else:
            # For sales, we're betting stock goes down
            return (entry_price - exit_price) / entry_price

    def is_leader(self, representative: str) -> bool:
        """Check if representative is in leadership"""
        rep_lower = representative.lower()
        return any(leader in rep_lower for leader in self.LEADERS)

    def is_committee_chair(self, representative: str) -> bool:
        """Check if representative is a committee chair"""
        rep_lower = representative.lower()
        return any(chair in rep_lower for chair in self.COMMITTEE_CHAIRS)

    def run_strategy(self, trades: List[Trade], strategy_name: str,
                    entry_delay_days: int = 0,
                    holding_period_days: int = 45,
                    min_trade_size: float = 0,
                    leaders_only: bool = False,
                    purchases_only: bool = True,
                    max_positions: int = 20,
                    position_size_pct: float = 0.05) -> BacktestResult:
        """
        Run a backtest with specific strategy parameters

        Args:
            trades: List of congressional trades
            strategy_name: Name for this strategy
            entry_delay_days: Days to wait after disclosure before entering
            holding_period_days: How long to hold positions
            min_trade_size: Minimum trade size to consider
            leaders_only: Only follow congressional leaders
            purchases_only: Only follow purchases (not sales)
            max_positions: Maximum concurrent positions
            position_size_pct: Position size as % of portfolio
        """
        results = []
        capital = self.initial_capital
        peak_capital = capital
        max_drawdown = 0
        active_positions = []

        # Sort trades by disclosure date
        sorted_trades = sorted(trades, key=lambda t: t.disclosure_date)

        for trade in sorted_trades:
            # Apply filters
            if purchases_only and trade.transaction_type != 'purchase':
                continue
            if min_trade_size > 0 and trade.amount < min_trade_size:
                continue
            if leaders_only and not self.is_leader(trade.representative):
                continue

            # Check position limits
            if len(active_positions) >= max_positions:
                continue

            # Calculate entry date (disclosure + delay)
            entry_date = trade.disclosure_date + timedelta(days=entry_delay_days)

            # Skip if entry date is in the future
            if entry_date > datetime.now():
                continue

            # Calculate return
            trade_return = self.calculate_return(
                trade.ticker,
                entry_date,
                holding_period_days,
                trade.transaction_type == 'purchase'
            )

            if trade_return is None:
                continue

            # Calculate P&L
            position_size = capital * position_size_pct
            pnl = position_size * trade_return
            capital += pnl

            # Track drawdown
            if capital > peak_capital:
                peak_capital = capital
            drawdown = (peak_capital - capital) / peak_capital
            if drawdown > max_drawdown:
                max_drawdown = drawdown

            results.append({
                'ticker': trade.ticker,
                'representative': trade.representative,
                'entry_date': entry_date.strftime('%Y-%m-%d'),
                'return': trade_return,
                'pnl': pnl,
                'capital_after': capital
            })

            # Rate limit API calls
            time.sleep(0.1)

        if not results:
            return BacktestResult(
                strategy_name=strategy_name,
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
                total_return=0,
                avg_return_per_trade=0,
                max_drawdown=0,
                sharpe_ratio=0,
                win_rate=0,
                avg_holding_days=holding_period_days,
                best_trade=0,
                worst_trade=0,
                trades_detail=[]
            )

        # Calculate statistics
        returns = [r['return'] for r in results]
        winning = [r for r in returns if r > 0]
        losing = [r for r in returns if r <= 0]

        total_return = (capital - self.initial_capital) / self.initial_capital
        avg_return = sum(returns) / len(returns) if returns else 0
        win_rate = len(winning) / len(returns) if returns else 0

        # Simplified Sharpe (assuming risk-free rate of 0)
        import statistics
        if len(returns) > 1:
            std_dev = statistics.stdev(returns)
            sharpe = (avg_return / std_dev) * (252 / holding_period_days) ** 0.5 if std_dev > 0 else 0
        else:
            sharpe = 0

        return BacktestResult(
            strategy_name=strategy_name,
            total_trades=len(results),
            winning_trades=len(winning),
            losing_trades=len(losing),
            total_return=total_return,
            avg_return_per_trade=avg_return,
            max_drawdown=max_drawdown,
            sharpe_ratio=sharpe,
            win_rate=win_rate,
            avg_holding_days=holding_period_days,
            best_trade=max(returns) if returns else 0,
            worst_trade=min(returns) if returns else 0,
            trades_detail=results
        )

    def compare_strategies(self, trades: List[Trade]) -> List[BacktestResult]:
        """
        Compare multiple trading strategies

        Returns results sorted by total return
        """
        strategies = [
            # Strategy 1: Immediate entry, 45-day hold (baseline)
            {
                'name': 'Baseline: Immediate Entry, 45d Hold',
                'entry_delay_days': 0,
                'holding_period_days': 45,
                'min_trade_size': 0,
                'leaders_only': False,
                'purchases_only': True
            },
            # Strategy 2: 9-day delay (research-backed optimal)
            {
                'name': 'Research Optimal: 9d Delay, 45d Hold',
                'entry_delay_days': 9,
                'holding_period_days': 45,
                'min_trade_size': 0,
                'leaders_only': False,
                'purchases_only': True
            },
            # Strategy 3: Leaders only
            {
                'name': 'Leaders Only: 9d Delay, 45d Hold',
                'entry_delay_days': 9,
                'holding_period_days': 45,
                'min_trade_size': 0,
                'leaders_only': True,
                'purchases_only': True
            },
            # Strategy 4: Large trades only ($100K+)
            {
                'name': 'Large Trades ($100K+): 9d Delay',
                'entry_delay_days': 9,
                'holding_period_days': 45,
                'min_trade_size': 100000,
                'leaders_only': False,
                'purchases_only': True
            },
            # Strategy 5: Short hold (2 weeks)
            {
                'name': 'Short Hold: 9d Delay, 14d Hold',
                'entry_delay_days': 9,
                'holding_period_days': 14,
                'min_trade_size': 0,
                'leaders_only': False,
                'purchases_only': True
            },
            # Strategy 6: Long hold (90 days)
            {
                'name': 'Long Hold: 9d Delay, 90d Hold',
                'entry_delay_days': 9,
                'holding_period_days': 90,
                'min_trade_size': 0,
                'leaders_only': False,
                'purchases_only': True
            },
            # Strategy 7: Include sales (contrarian on sales)
            {
                'name': 'Include Sales: 9d Delay, 45d Hold',
                'entry_delay_days': 9,
                'holding_period_days': 45,
                'min_trade_size': 0,
                'leaders_only': False,
                'purchases_only': False
            },
            # Strategy 8: Pelosi-only
            {
                'name': 'Pelosi Only: 9d Delay, 45d Hold',
                'entry_delay_days': 9,
                'holding_period_days': 45,
                'min_trade_size': 0,
                'leaders_only': False,  # Will filter in custom logic
                'purchases_only': True,
                'pelosi_only': True
            }
        ]

        results = []
        for strat in strategies:
            # Handle Pelosi-only special case
            if strat.get('pelosi_only'):
                pelosi_trades = [t for t in trades if 'pelosi' in t.representative.lower()]
                result = self.run_strategy(
                    pelosi_trades,
                    strat['name'],
                    entry_delay_days=strat['entry_delay_days'],
                    holding_period_days=strat['holding_period_days'],
                    min_trade_size=strat['min_trade_size'],
                    leaders_only=False,
                    purchases_only=strat['purchases_only']
                )
            else:
                result = self.run_strategy(
                    trades,
                    strat['name'],
                    entry_delay_days=strat['entry_delay_days'],
                    holding_period_days=strat['holding_period_days'],
                    min_trade_size=strat['min_trade_size'],
                    leaders_only=strat['leaders_only'],
                    purchases_only=strat['purchases_only']
                )
            results.append(result)
            print(f"Completed: {strat['name']}")

        # Sort by total return
        results.sort(key=lambda r: r.total_return, reverse=True)
        return results

    def print_results(self, results: List[BacktestResult]):
        """Print backtest results in a formatted table"""
        print("\n" + "=" * 100)
        print("BACKTEST RESULTS - Congressional Trading Strategies")
        print("=" * 100)
        print(f"{'Strategy':<45} {'Trades':>7} {'Win%':>7} {'Avg Ret':>8} {'Total':>9} {'MaxDD':>7} {'Sharpe':>7}")
        print("-" * 100)

        for r in results:
            print(f"{r.strategy_name:<45} {r.total_trades:>7} {r.win_rate*100:>6.1f}% "
                  f"{r.avg_return_per_trade*100:>7.2f}% {r.total_return*100:>8.1f}% "
                  f"{r.max_drawdown*100:>6.1f}% {r.sharpe_ratio:>7.2f}")

        print("=" * 100)

        # Print best strategy details
        if results:
            best = results[0]
            print(f"\nBEST STRATEGY: {best.strategy_name}")
            print(f"  Total Return: {best.total_return*100:.1f}%")
            print(f"  Win Rate: {best.win_rate*100:.1f}%")
            print(f"  Best Trade: {best.best_trade*100:.1f}%")
            print(f"  Worst Trade: {best.worst_trade*100:.1f}%")
            print(f"  Max Drawdown: {best.max_drawdown*100:.1f}%")

            if best.trades_detail:
                print(f"\n  Top 5 Trades:")
                top_trades = sorted(best.trades_detail, key=lambda t: t['return'], reverse=True)[:5]
                for t in top_trades:
                    print(f"    {t['ticker']:6} {t['return']*100:>7.1f}%  ({t['representative'][:25]})")


def load_historical_trades_from_db(db_path: str = 'data/trading.db') -> List[Trade]:
    """Load trades from SQLite database"""
    import sqlite3

    trades = []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.execute("""
            SELECT * FROM congressional_trades
            ORDER BY disclosure_date DESC
        """)

        for row in cursor.fetchall():
            try:
                # Parse dates
                tx_date = datetime.strptime(row['transaction_date'], '%m/%d/%Y') if row['transaction_date'] else datetime.now()
                disc_date = datetime.strptime(row['disclosure_date'], '%m/%d/%Y') if row['disclosure_date'] else tx_date

                trade = Trade(
                    ticker=row['ticker'],
                    transaction_type=row['transaction_type'],
                    transaction_date=tx_date,
                    disclosure_date=disc_date,
                    amount=row['amount'] or 0,
                    representative=row['representative'] or '',
                    chamber=row['chamber'] or 'house'
                )
                trades.append(trade)
            except Exception as e:
                logger.debug(f"Error parsing trade: {e}")
                continue

    return trades


def fetch_historical_trades() -> List[Trade]:
    """Fetch historical trades from House Stock Watcher (free API)"""
    url = "https://house-stock-watcher-data.s3-us-west-2.amazonaws.com/data/all_transactions.json"

    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            logger.error(f"Failed to fetch: {response.status_code}")
            return []

        data = response.json()
        trades = []

        for item in data:
            try:
                # Parse transaction type
                tx_type = item.get('type', '').lower()
                if 'purchase' in tx_type:
                    tx_type = 'purchase'
                elif 'sale' in tx_type:
                    tx_type = 'sale'
                else:
                    continue

                # Parse dates
                tx_date_str = item.get('transaction_date', '')
                disc_date_str = item.get('disclosure_date', '')

                # Try multiple date formats
                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d']:
                    try:
                        tx_date = datetime.strptime(tx_date_str, fmt)
                        break
                    except:
                        tx_date = datetime.now() - timedelta(days=30)

                for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%Y/%m/%d']:
                    try:
                        disc_date = datetime.strptime(disc_date_str, fmt)
                        break
                    except:
                        disc_date = tx_date + timedelta(days=30)

                # Parse amount
                amount_str = item.get('amount', '$0')
                amount = parse_amount(amount_str)

                ticker = item.get('ticker', '').replace('--', '').strip()
                if not ticker or len(ticker) > 5:
                    continue

                trade = Trade(
                    ticker=ticker,
                    transaction_type=tx_type,
                    transaction_date=tx_date,
                    disclosure_date=disc_date,
                    amount=amount,
                    representative=item.get('representative', ''),
                    chamber='house'
                )
                trades.append(trade)

            except Exception as e:
                continue

        logger.info(f"Loaded {len(trades)} historical trades from House Stock Watcher")
        return trades

    except Exception as e:
        logger.error(f"Error fetching historical trades: {e}")
        return []


def parse_amount(amount_str: str) -> float:
    """Parse amount string like '$1,000 - $15,000'"""
    try:
        amount_str = amount_str.replace('$', '').replace(',', '').strip()
        if '-' in amount_str:
            parts = amount_str.split('-')
            low = float(parts[0].strip())
            high = float(parts[1].strip())
            return (low + high) / 2
        return float(amount_str)
    except:
        return 0


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("Congressional Trading Strategy Backtester")
    print("=" * 50)

    # Check for yfinance
    if not HAS_YFINANCE:
        print("ERROR: yfinance not installed")
        print("Run: pip install yfinance")
        exit(1)

    # Fetch historical trades
    print("\nFetching historical congressional trades...")
    trades = fetch_historical_trades()

    if not trades:
        print("No trades found. Exiting.")
        exit(1)

    print(f"Loaded {len(trades)} trades")

    # Filter to last 2 years for more relevant backtest
    two_years_ago = datetime.now() - timedelta(days=730)
    recent_trades = [t for t in trades if t.disclosure_date > two_years_ago]
    print(f"Using {len(recent_trades)} trades from last 2 years")

    # Run backtester
    backtester = CongressionalBacktester(initial_capital=50000)
    print("\nRunning strategy comparisons (this may take a few minutes)...")

    results = backtester.compare_strategies(recent_trades)
    backtester.print_results(results)
