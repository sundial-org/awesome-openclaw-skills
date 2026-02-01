# Backtesting Guide

## Overview

The backtesting framework validates trading strategies with historical data **before risking real capital**. This is **CRITICAL** - never trade live without backtesting first.

## Quick Start

```python
from scripts.backtester import Backtester
from scripts.trading_agent_enhanced import EnhancedTradingAgent
import pandas as pd

# Initialize trading agent
agent = EnhancedTradingAgent(balance=10000, exchange_name='binance')

# Create backtester
backtester = Backtester(
    agent=agent,
    initial_capital=10000,
    trading_fee=0.001,   # 0.1% (typical crypto exchange)
    slippage=0.0005,     # 0.05% (realistic slippage)
    risk_per_trade=0.02, # 2% max risk per trade
    max_position_size=0.10  # 10% max position size
)

# Load historical data (must have: timestamp, open, high, low, close, volume)
# You can fetch this from exchange or load from CSV
historical_data = pd.read_csv('BTC_USDT_1h.csv')

# Run backtest
results = backtester.run(
    data=historical_data,
    symbol='BTC/USDT'
)

# View results
print(results.summary())

# Access detailed metrics
print(f"Sharpe Ratio: {results.sharpe_ratio:.2f}")
print(f"Max Drawdown: {results.max_drawdown_pct:.2f}%")
print(f"Win Rate: {results.win_rate:.1f}%")

# View all trades
for trade in results.trades:
    print(trade)

# Export equity curve
results.equity_curve.to_csv('equity_curve.csv', index=False)
```

## Key Features

### 1. Realistic Execution

**Slippage:**
- Buy orders filled at slightly higher price (+0.05% default)
- Sell orders filled at slightly lower price (-0.05% default)
- Simulates real market conditions

**Trading Fees:**
- Entry fee: 0.1% of position value
- Exit fee: 0.1% of position value
- Total friction: ~0.3% per round trip (fees + slippage)

### 2. Risk Management

**Position Sizing (2% Rule):**
```
Max Risk = Capital × 2% = $10,000 × 0.02 = $200

If Entry = $100, Stop = $95:
  Risk per unit = $5
  Position size = $200 / $5 = 40 units
  Position value = 40 × $100 = $4,000
```

**Safety Limits:**
- Max 2% of capital risked per trade
- Max 10% position size (even if risk allows more)
- Ensures portfolio diversification

### 3. Stop Loss & Take Profit

- **Intrabar Execution:** Checks if high/low touched SL/TP
- **Realistic Fills:** Uses SL/TP price, not close price
- **Priority:** Stop loss checked before take profit

### 4. Performance Metrics

**Returns:**
- Total return ($)
- Total return (%)
- Avg trade return
- Largest win/loss

**Win Rate:**
- % of profitable trades
- Avg winning trade
- Avg losing trade
- Profit factor (gross profit / gross loss)

**Risk-Adjusted Returns:**
- **Sharpe Ratio:** Return per unit of total volatility
  - > 1.0 = Good
  - > 2.0 = Excellent
  - < 0.0 = Losing money
- **Sortino Ratio:** Return per unit of downside volatility
  - Similar to Sharpe, but only penalizes downside moves
- **Max Drawdown:** Largest peak-to-trough decline
  - < 20% = Acceptable
  - > 50% = Dangerous

## Sample Output

```
======================================================================
BACKTEST RESULTS SUMMARY
======================================================================

Capital:
  Initial: $10,000.00
  Final:   $12,345.67
  Return:  +$2,345.67 (+23.46%)

Trade Statistics:
  Total Trades:    45
  Winning Trades:  28 (62.2%)
  Losing Trades:   17
  Profit Factor:   2.15

Performance Metrics:
  Sharpe Ratio:    1.85
  Sortino Ratio:   2.34
  Max Drawdown:    $876.54 (8.77%)

Trade Analysis:
  Avg Trade P&L:   +$52.13
  Avg Win:         +$145.67
  Avg Loss:        -$85.34
  Largest Win:     +$456.78
  Largest Loss:    -$234.56
======================================================================
```

## Interpreting Results

### ✅ Good Strategy Characteristics

- **Sharpe Ratio > 1.0:** Risk-adjusted returns are positive
- **Win Rate > 50%:** More winners than losers
- **Profit Factor > 1.5:** Winners are bigger than losers
- **Max Drawdown < 20%:** Manageable losses
- **Positive Total Return:** Strategy is profitable

### ❌ Poor Strategy Characteristics

- **Sharpe Ratio < 0:** Losing money
- **Win Rate < 40%:** Too many losers
- **Profit Factor < 1.0:** Losses bigger than wins
- **Max Drawdown > 50%:** Unacceptable risk
- **Negative Total Return:** Unprofitable strategy

### 🔴 **DO NOT TRADE LIVE IF:**

1. Sharpe Ratio < 1.0
2. Max Drawdown > 30%
3. Win Rate < 40%
4. Profit Factor < 1.2
5. Negative returns

## Data Requirements

Historical data must include:

```python
required_columns = [
    'timestamp',  # datetime - Candle timestamp
    'open',       # float - Opening price
    'high',       # float - Highest price in period
    'low',        # float - Lowest price in period
    'close',      # float - Closing price
    'volume'      # float - Trading volume
]
```

**Minimum Data:**
- At least 200+ candles (for indicator calculations)
- Preferably 1000+ candles (for statistical significance)
- 3+ months of hourly data recommended

## Fetching Historical Data

### Option 1: From Exchange (via ccxt)

```python
import ccxt
import pandas as pd
from datetime import datetime

exchange = ccxt.binance()
symbol = 'BTC/USDT'
timeframe = '1h'
since = exchange.parse8601('2024-01-01T00:00:00Z')

# Fetch OHLCV data
ohlcv = exchange.fetch_ohlcv(symbol, timeframe, since)

# Convert to DataFrame
df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')

# Save for later use
df.to_csv('BTC_USDT_1h.csv', index=False)
```

### Option 2: From CSV File

```python
df = pd.read_csv('historical_data.csv')
df['timestamp'] = pd.to_datetime(df['timestamp'])
```

## Advanced Usage

### Multiple Symbol Backtests

```python
symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT']

for symbol in symbols:
    data = load_data(symbol)  # Your data loading function
    results = backtester.run(data, symbol)
    print(f"\n{symbol}:")
    print(results.summary())
```

### Walk-Forward Analysis

Test strategy on rolling time windows:

```python
import pandas as pd

# Split data into train/test periods
train_data = historical_data['2024-01':'2024-06']
test_data = historical_data['2024-07':'2024-12']

# Backtest on training period
train_results = backtester.run(train_data, 'BTC/USDT')
print("Training Period:")
print(train_results.summary())

# Validate on test period (out-of-sample)
test_results = backtester.run(test_data, 'BTC/USDT')
print("\nTest Period:")
print(test_results.summary())

# Strategy is robust if test performance similar to train
if test_results.sharpe_ratio > 0.8 * train_results.sharpe_ratio:
    print("✅ Strategy is robust (not overfitted)")
else:
    print("⚠️  Performance degraded significantly (possible overfitting)")
```

### Visualize Equity Curve

```python
import matplotlib.pyplot as plt

# Plot equity curve
plt.figure(figsize=(12, 6))
plt.plot(results.equity_curve['timestamp'], results.equity_curve['equity'])
plt.axhline(y=10000, color='r', linestyle='--', label='Initial Capital')
plt.title('Equity Curve')
plt.xlabel('Time')
plt.ylabel('Account Value ($)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig('equity_curve.png')
plt.show()
```

### Export Trade Log

```python
# Export detailed trade log
trade_log = []
for trade in results.trades:
    trade_log.append({
        'entry_time': trade.entry_time,
        'exit_time': trade.exit_time,
        'symbol': trade.symbol,
        'side': trade.side,
        'entry_price': trade.entry_price,
        'exit_price': trade.exit_price,
        'pnl': trade.pnl,
        'pnl_pct': trade.pnl_pct,
        'exit_reason': trade.exit_reason,
        'holding_hours': trade.holding_period_hours
    })

trade_df = pd.DataFrame(trade_log)
trade_df.to_csv('trade_log.csv', index=False)
print(f"Exported {len(trade_log)} trades to trade_log.csv")
```

## Important Notes

### ⚠️  Warnings

1. **Past Performance ≠ Future Results:** Backtesting shows what WOULD have happened, not what WILL happen
2. **Overfitting Risk:** Don't optimize parameters on same data you test on
3. **Market Regimes Change:** A strategy profitable in 2024 may fail in 2025
4. **Slippage Varies:** Real slippage may be worse during volatile periods
5. **Liquidity Matters:** Small accounts get better fills than large accounts

### ✅ Best Practices

1. **Test on Multiple Periods:** Bull markets, bear markets, sideways markets
2. **Test on Multiple Assets:** BTC, ETH, alts - if strategy is robust, it works on multiple assets
3. **Use Walk-Forward Analysis:** Train on period 1, test on period 2
4. **Start Small:** Even if backtest is great, start with 1-5% of capital
5. **Monitor Live Performance:** Track if live results match backtest expectations

### 🔄 When to Stop Trading

Stop trading immediately if:
- Live win rate drops 20% below backtest
- Live Sharpe ratio < 0.5
- Max drawdown exceeds backtest max by 50%
- 5+ consecutive losers (if backtest didn't show this)
- Market regime change (e.g., bull → bear)

## Next Steps

After backtesting:

1. **✅ Sharpe > 1.0, Win Rate > 50%?** → Proceed to paper trading
2. **📄 Paper Trading:** Test with fake money for 30 days
3. **💰 Live Trading:** Start with 1-5% of capital
4. **📊 Monitor:** Track live performance vs backtest expectations
5. **🔧 Adjust:** If live performance differs, re-evaluate strategy

## Support

For issues or questions:
- Review backtest code: `cryptocurrency-trader-skill/scripts/backtester.py`
- Run tests: `python test_backtest_framework.py`
- Check logs: Review logger output for debugging

---

**Remember:** Backtesting is REQUIRED before live trading. Never risk real money on an unvalidated strategy. 🚨
