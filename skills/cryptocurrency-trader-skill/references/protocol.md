# Trading Protocol - Technical Reference

## Complete Protocol Documentation

This document provides detailed technical specifications for the AI Trading Agent's decision-making protocol.

## 10-Step Automated Analysis Workflow

### Step 1: Fetch Current Market Data
```python
df = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
```

**Data Retrieved:**
- Open, High, Low, Close prices
- Volume
- Timestamp

**Validation Checks:**
- No negative or zero prices
- OHLC logic (High ≥ Low, High ≥ Open, High ≥ Close)
- Volume > 0
- Data freshness (< 5 minutes old)
- No missing values

### Step 2: Multi-Timeframe Data Retrieval

**Standard Timeframes:**
- 15m (short-term)
- 1h (medium-term)
- 4h (long-term)

**Minimum Requirement:** 2 timeframes for valid analysis

### Step 3: Volatility Calculation (ATR)

**Average True Range (ATR) Formula:**
```
TR = max(
    High - Low,
    abs(High - Previous Close),
    abs(Low - Previous Close)
)

ATR = 14-period moving average of TR
```

**Usage:**
- Stop loss placement: Entry ± (2 × ATR)
- Take profit: Entry ± (3 × ATR)
- Position sizing adjustments

### Step 4: Stop Hunt Detection

**Not yet implemented** - Priority 1 optimization

**Planned Logic:**
- Identify recent swing highs/lows
- Detect rapid price moves beyond these levels
- Check for quick reversals
- Flag potential stop hunts

### Step 5: Support/Resistance Identification

**Not yet implemented** - Priority 1 optimization

**Planned Method:**
- Find price levels with multiple touches
- Calculate strength based on number of touches
- Identify breaks vs bounces
- Dynamic levels that adjust over time

### Step 6: Timeframe Consensus Analysis

**Current Implementation:**

```python
# Collect signals from each timeframe
for timeframe in ['15m', '1h', '4h']:
    if RSI < 30: signal = 'OVERSOLD'
    if RSI > 70: signal = 'OVERBOUGHT'
    if MACD > MACD_Signal: signal = 'BULLISH'
    if MACD < MACD_Signal: signal = 'BEARISH'

# Calculate consensus
bullish_count = signals.count('BULLISH')
bearish_count = signals.count('BEARISH')

# Decision
if bullish_count > bearish_count and avg_RSI < 60:
    action = 'LONG'
elif bearish_count > bullish_count and avg_RSI > 40:
    action = 'SHORT'
else:
    action = 'WAIT'
```

**Confidence Calculation:**
```python
confidence = (dominant_signals / total_signals) * 100
confidence = min(95, confidence)  # Cap at 95%
```

### Step 7: Position-Specific Calculations

**Entry Price:**
```python
entry_price = current_price
```

**Stop Loss (Long Position):**
```python
stop_loss = entry_price - (2 * ATR)
```

**Stop Loss (Short Position):**
```python
stop_loss = entry_price + (2 * ATR)
```

**Take Profit (Long Position):**
```python
take_profit = entry_price + (3 * ATR)
```

**Take Profit (Short Position):**
```python
take_profit = entry_price - (3 * ATR)
```

**Risk/Reward Ratio:**
```python
risk = abs(entry_price - stop_loss)
reward = abs(take_profit - entry_price)
risk_reward = round(reward / risk, 1)
```

**Position Size Calculation:**
```python
max_risk_usd = account_balance * 0.02  # 2% max risk
price_risk = abs(entry_price - stop_loss)
position_size_coin = max_risk_usd / price_risk

# Cap at 10% of account
max_position = account_balance * 0.10
position_value_usd = position_size_coin * entry_price

if position_value_usd > max_position:
    position_value_usd = max_position
    position_size_coin = position_value_usd / entry_price

# Include trading fees (0.2% minimum)
trading_fees = position_value_usd * 0.002
```

### Step 8: Confidence Scoring System

**Base Confidence:**
- Calculated from timeframe consensus (50-95%)
- Capped at 95% to prevent overconfidence

**Confidence Adjustments:**
- Single timeframe: -20%
- 2 timeframes: -10%
- 3+ timeframes: No adjustment
- Conflicting signals: -15%
- Strong RSI extreme: +10%

**Interpretation:**
- 0-40%: Do not trade
- 40-60%: Low confidence
- 60-75%: Medium confidence
- 75-90%: High confidence
- 90-95%: Very high (but triggers warning)

### Step 9: Circuit Breaker Validation

**8 Mandatory Trade Blocks:**

1. **No Clear Signal**
   ```python
   if action == 'WAIT':
       block = "⛔ No clear signal"
   ```

2. **Low Confidence**
   ```python
   if confidence < 40:
       block = "⛔ Confidence too low"
   ```

3. **Poor Risk/Reward**
   ```python
   if risk_reward < 1.5:
       block = "⛔ Poor risk/reward ratio"
   ```

4. **Insufficient Timeframes**
   ```python
   if len(timeframe_data) < 2:
       block = "⛔ Insufficient timeframes"
   ```

5. **Stale Data**
   ```python
   if data_age > 300:  # 5 minutes
       block = "⛔ Stale data"
   ```

6. **Invalid Prices**
   ```python
   if any(price <= 0):
       block = "⛔ Invalid price data"
   ```

7. **OHLC Violation**
   ```python
   if not (high >= low and high >= open and high >= close):
       block = "⛔ OHLC logic violated"
   ```

8. **Missing Indicators**
   ```python
   if 'rsi' not in indicators or 'macd' not in indicators:
       block = "⛔ Missing critical indicators"
   ```

**4 Warning Flags** (don't block):

1. **Unrealistic Confidence**
   ```python
   if confidence > 90:
       warning = "⚠️ Unrealistically high confidence"
   ```

2. **Unrealistic R:R**
   ```python
   if risk_reward > 8:
       warning = "⚠️ Unrealistic risk/reward - verify manually"
   ```

3. **Single Timeframe**
   ```python
   if len(timeframe_data) == 1:
       warning = "⚠️ Single timeframe analysis"
   ```

4. **High Volatility**
   ```python
   if ATR > (price * 0.05):  # ATR > 5% of price
       warning = "⚠️ High volatility environment"
   ```

### Step 10: Scenario Generation

**Output Format:**
```python
{
    'symbol': 'BTC/USDT',
    'timestamp': '2025-11-11 12:00:00',
    'action': 'LONG',
    'confidence': 75,
    'current_price': 94250.00,
    'entry_price': 94250.00,
    'stop_loss': 93100.00,
    'take_profit': 96975.00,
    'risk_reward': 2.4,
    'safe_to_use': True,
    'recommendation': '✅ LONG at $94,250',
    'position_sizing': {
        'position_size_coin': 0.0174,
        'position_value_usd': 1640.00,
        'risk_usd': 200.00,
        'risk_percent': 2.0,
        'trading_fees': 3.28
    },
    'timeframe_data': {...},
    'warnings': [],
    'blocks': []
}
```

## Technical Indicators Deep Dive

### RSI (Relative Strength Index)

**Formula:**
```python
delta = close.diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))
```

**Interpretation:**
- RSI < 30: Oversold (potential buy)
- RSI > 70: Overbought (potential sell)
- RSI 30-70: Neutral

**Validation:**
- Must be between 0-100
- Invalid if outside range

### MACD (Moving Average Convergence Divergence)

**Formula:**
```python
exp1 = close.ewm(span=12, adjust=False).mean()
exp2 = close.ewm(span=26, adjust=False).mean()
macd = exp1 - exp2
signal = macd.ewm(span=9, adjust=False).mean()
```

**Interpretation:**
- MACD > Signal: Bullish
- MACD < Signal: Bearish
- Crossovers: Potential entry/exit points

### ATR (Average True Range)

**Formula:**
```python
high_low = high - low
high_close = abs(high - close.shift())
low_close = abs(low - close.shift())
ranges = pd.concat([high_low, high_close, low_close], axis=1)
true_range = np.max(ranges, axis=1)
atr = true_range.rolling(14).mean()
```

**Usage:**
- Volatility measurement
- Stop loss/take profit calculation
- Position size adjustment

**Validation:**
- Must be positive
- Invalid if negative or zero

### Bollinger Bands

**Formula:**
```python
sma = close.rolling(window=20).mean()
std = close.rolling(window=20).std()
bb_upper = sma + (std * 2)
bb_lower = sma - (std * 2)
```

**Interpretation:**
- Price near upper band: Overbought
- Price near lower band: Oversold
- Band squeeze: Low volatility (potential breakout)
- Band expansion: High volatility

## Data Validation Framework

### Price Data Validation

**Checks:**
```python
# No negative or zero prices
if (df[['open', 'high', 'low', 'close']] <= 0).any().any():
    invalid = True

# No missing values
if df.isnull().any().any():
    invalid = True

# OHLC logic
if not ((df['high'] >= df['low']).all() and 
        (df['high'] >= df['open']).all() and 
        (df['high'] >= df['close']).all()):
    invalid = True

# Data freshness
latest_time = df['timestamp'].iloc[-1]
age = (datetime.now() - latest_time).total_seconds()
if age > 300:  # 5 minutes
    invalid = True
```

### Indicator Range Validation

```python
# RSI must be 0-100
if not (0 <= rsi <= 100):
    invalid = True

# ATR must be positive
if atr < 0:
    invalid = True

# Volume must be positive
if volume <= 0:
    invalid = True
```

### Mathematical Consistency

```python
# Risk/Reward calculation
calculated_rr = abs(take_profit - entry) / abs(entry - stop_loss)
if abs(calculated_rr - reported_rr) > 0.1:
    inconsistent = True

# Position size verification
calculated_value = position_size * entry_price
if abs(calculated_value - reported_value) > 0.01:
    inconsistent = True

# Fee inclusion check
minimum_fee = position_value * 0.002
if reported_fee < minimum_fee:
    fee_missing = True
```

## Exchange Integration

### Supported Exchanges

**Primary:**
- Binance (preferred - high liquidity)

**Backup Exchanges:**
- Kraken
- Coinbase
- OKX
- Bybit
- KuCoin
- Huobi

### Connection Configuration

```python
exchange = ccxt.exchangename({
    'enableRateLimit': True,  # Respect rate limits
    'options': {'defaultType': 'spot'},  # Spot market
    'timeout': 30000,  # 30 second timeout
})
```

### Rate Limiting

**Built-in Protection:**
- `enableRateLimit: True` in CCXT
- Automatic retry with exponential backoff
- 0.5 second delay between requests in market scan

### Data Retrieval

```python
# OHLCV data
ohlcv = exchange.fetch_ohlcv(
    symbol='BTC/USDT',
    timeframe='1h',
    limit=100
)

# Returns: [[timestamp, open, high, low, close, volume], ...]
```

## Market Scanner Algorithm

### Category-Based Scanning

**6 Categories Analyzed:**
1. Major Coins (5 symbols)
2. AI Tokens (4 symbols)
3. Layer 1 (4 symbols)
4. Layer 2 (3 symbols)
5. DeFi (4 symbols)
6. Meme (3 symbols)

**Total:** 23 unique trading pairs

### Opportunity Scoring

**Expected Value Formula:**
```python
ev_score = (confidence / 100) * risk_reward
```

**Example:**
- Confidence: 80%
- Risk/Reward: 3:1
- EV Score: 0.80 × 3 = 2.4

**Ranking:**
- Sort all opportunities by EV score (descending)
- Return top 5

### Scan Process

```python
for category, symbols in categories.items():
    for symbol in symbols:
        # Analyze each symbol
        analysis = analyze_opportunity(symbol)
        
        # Only include safe trades
        if analysis['safe_to_use']:
            ev_score = (confidence / 100) * risk_reward
            opportunities.append({
                'symbol': symbol,
                'category': category,
                'ev_score': ev_score,
                **analysis
            })
        
        # Rate limiting
        time.sleep(0.5)

# Sort and return top 5
opportunities.sort(key=lambda x: x['ev_score'], reverse=True)
return opportunities[:5]
```

## Error Handling

### Network Errors

```python
try:
    data = exchange.fetch_ohlcv(symbol, timeframe)
except ccxt.NetworkError as e:
    # Try backup exchange
    # Or wait and retry
except ccxt.ExchangeError as e:
    # Symbol may not exist on exchange
    # Try different symbol format
```

### Data Errors

```python
if df is None or len(df) == 0:
    return {
        'error': 'No data available',
        'safe_to_use': False
    }

validation = validate_data(df)
if not validation['valid']:
    return {
        'error': validation['issues'],
        'safe_to_use': False
    }
```

### Calculation Errors

```python
try:
    indicators = calculate_indicators(df)
except ZeroDivisionError:
    return {'error': 'Division by zero in calculation'}
except Exception as e:
    return {'error': f'Calculation failed: {str(e)}'}
```

## Performance Considerations

### Optimization Targets

**Current Performance:**
- Single analysis: 2-3 seconds
- Market scan (23 pairs): 30-60 seconds

**Optimization Opportunities:**
1. Parallel data fetching (10x faster)
2. Cache recent data (5x faster)
3. Incremental updates (20x faster for repeated calls)

### Memory Usage

**Typical Usage:**
- Per symbol: ~50KB (100 candles × 6 values)
- Full market scan: ~1.2MB
- Indicator calculations: ~2MB temporary

**Optimization:**
- Use generators for large scans
- Clear old DataFrames after use
- Limit historical data to necessary period

## Future Enhancements

### Priority 1 (High Impact)
- Volume profile analysis
- Support/resistance detection
- Fibonacci retracements
- Stop hunt detection
- Order book analysis

### Priority 2 (Medium Impact)
- Multi-exchange price validation
- Liquidity analysis
- Funding rate analysis
- News sentiment integration
- On-chain metrics

### Priority 3 (Advanced)
- Machine learning pattern recognition
- Backtesting framework
- Portfolio optimization
- Correlation analysis
- Real-time alerts

---

**Document Version:** 1.0.0  
**Last Updated:** November 11, 2025  
**Protocol Version:** 1.0.0
