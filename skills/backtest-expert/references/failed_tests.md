# Learning from Failed Backtests

## Table of Contents

1. Why Failed Ideas Are Valuable
2. Common Failure Patterns
3. Case Study Framework
4. Red Flags Checklist

## 1. Why Failed Ideas Are Valuable

### The Value of Failures

**Key insights**:
- Failed tests save capital by preventing live implementation
- Failure patterns reveal which assumptions don't hold
- Understanding what doesn't work narrows the search space
- Failed tests build experience in recognizing fragile strategies

### Documentation Discipline

**Record for each failed idea**:
- The hypothesis being tested
- Why you thought it would work
- What the data showed
- Specific breaking points
- Lessons learned

**Purpose**: Build a library of "anti-patterns" to avoid repeating mistakes.

## 2. Common Failure Patterns

### Pattern 1: Parameter Sensitivity

**Symptom**: Strategy only works with very specific parameter values.

**Example scenario**:
- Strategy profitable with stop loss at exactly 2.5%
- Increasing to 3% or decreasing to 2% causes significant performance drop
- No "plateau" of stable performance

**Why it fails**: Real markets have noise; if small changes break the strategy, it likely captured noise, not signal.

**Lesson**: Seek strategies with stable performance across parameter ranges.

### Pattern 2: Regime-Specific Performance

**Symptom**: Strategy works brilliantly in some years, terribly in others.

**Example scenario**:
- Great performance in 2017-2019 (low volatility bull market)
- Catastrophic losses in 2020 (high volatility)
- Poor performance in 2022 (downtrend)

**Why it fails**: Strategy dependent on specific market conditions, not robust enough for diverse environments.

**Lesson**: Require acceptable (not necessarily best) performance across all regimes.

### Pattern 3: Slippage Sensitivity

**Symptom**: Strategy becomes unprofitable when realistic trading costs added.

**Example scenario**:
- Backtest shows 0.5% average gain per trade
- Adding 0.1% slippage per side (0.2% round-trip) eliminates profits
- Strategy requires unrealistic fills to be profitable

**Why it fails**: Edge too small to survive real-world friction.

**Lesson**: Edge must be large enough to survive pessimistic assumptions about costs.

### Pattern 4: Sample Size Issues

**Symptom**: Strong results based on small number of trades.

**Example scenario**:
- Backtest shows 80% win rate
- Only 15 total trades in 5 years
- A few different outcomes would dramatically change results

**Why it fails**: Insufficient data to distinguish edge from luck.

**Lesson**: Require minimum 100 trades for meaningful conclusions, preferably 200+.

### Pattern 5: Look-Ahead Bias

**Symptom**: Perfect or near-perfect backtest results.

**Example scenario**:
- Strategy shows 95%+ win rate
- Unrealistically good entry/exit timing
- Performance too good to be realistic

**Why it fails**: Likely using information not available at time of trade.

**Lesson**: Be suspicious of "too good to be true" results; audit data alignment carefully.

### Pattern 6: Over-Optimization (Curve Fitting)

**Symptom**: Complex strategy with many parameters shows excellent in-sample results but poor out-of-sample.

**Example scenario**:
- Strategy uses 8-10 different indicators with specific thresholds
- In-sample performance: 40% annual return
- Out-of-sample performance: -5% annual return
- Parameters needed constant re-optimization

**Why it fails**: Fitted to historical noise rather than genuine market structure.

**Lesson**: Prefer simple strategies with fewer parameters; demand strong out-of-sample results.

## 3. Case Study Framework

### Template for Documenting Failed Ideas

Use this framework when a backtest fails:

#### 1. Initial Hypothesis
- **What edge were you trying to capture?**
- **Why did you think this would work?**
- **What was the logical basis?**

#### 2. Implementation Details
- **Entry rules** (specific and complete)
- **Exit rules** (stop loss, profit target, time-based)
- **Position sizing**
- **Filters or conditions**

#### 3. Test Results
- **Basic metrics**:
  - Total trades
  - Win rate
  - Average win/loss
  - Max drawdown
  - Annual returns by year
  
- **Parameter sensitivity**:
  - How results changed with parameter variations
  - Whether "plateau" of stable performance existed

- **Regime analysis**:
  - Performance in different market conditions
  - Which regimes caused problems

#### 4. Breaking Points
- **What specifically caused the strategy to fail?**
  - Slippage too high?
  - Parameter sensitivity?
  - Regime-specific?
  - Insufficient sample size?

#### 5. Lessons Learned
- **What assumptions were wrong?**
- **What would you test differently next time?**
- **Are there salvageable elements?**

### Example: Failed Momentum Reversal Strategy

#### 1. Initial Hypothesis
Tried to capture mean reversion after strong momentum moves. Hypothesis: Stocks that gap up 5%+ on earnings often pull back 2-3% before continuing, providing short-term reversal opportunity.

#### 2. Implementation
- Entry: Short when stock gaps up 5%+ on earnings at market open
- Exit: Cover at 2% profit or 3% stop loss
- Holding period: Maximum 3 days
- Filters: Market cap >$2B, average volume >500K shares

#### 3. Test Results
- 67 trades over 5 years
- Win rate: 58%
- Avg win: 2.1%, Avg loss: 3.2%
- Max drawdown: 18%
- 2019-2021: Profitable
- 2022-2023: Significant losses

#### 4. Breaking Points
- Strategy failed during strong momentum environments (2021 meme stocks)
- Stop losses hit frequently during continued upward momentum
- Gap-ups that continued higher immediately caused outsized losses
- Small sample size (67 trades) provided low statistical confidence
- Slippage on short entries during high volatility eliminated thin edge

#### 5. Lessons Learned
- Mean reversion strategies vulnerable during momentum regimes
- Need regime filter (e.g., only trade during high VIX or weak market)
- 5-year test insufficient for momentum strategies; need 10+ years
- Edge too small (2% target vs 3% stop) to survive slippage
- Better approach: Wait for actual pullback, then enter, rather than fade immediately

## 4. Red Flags Checklist

Use this checklist when evaluating any backtest:

### Data Quality Issues
- [ ] Has survivorship bias been addressed?
- [ ] Are delisted stocks included in test?
- [ ] Is data alignment correct (no look-ahead bias)?
- [ ] Are corporate actions (splits, dividends) handled correctly?

### Sample Size Concerns
- [ ] At least 100 trades? (Preferably 200+)
- [ ] At least 5 years of data? (Preferably 10+)
- [ ] Includes full market cycle?
- [ ] Tested across multiple market regimes?

### Parameter Robustness
- [ ] Does strategy work with nearby parameter values?
- [ ] Are there "plateaus" of stable performance?
- [ ] Minimal parameters (ideally <5)?
- [ ] Parameters based on logical reasoning, not pure optimization?

### Execution Realism
- [ ] Realistic commissions included?
- [ ] Slippage modeled conservatively (1.5-2x typical)?
- [ ] Worst-case fills considered?
- [ ] Order rejection/partial fills addressed?

### Performance Characteristics
- [ ] Positive expectancy in majority of years?
- [ ] Acceptable performance in all major regimes?
- [ ] No catastrophic drawdowns (>50%)?
- [ ] Edge large enough to survive friction?

### Bias Prevention
- [ ] Strategy defined before testing?
- [ ] Hypothesis has economic logic?
- [ ] Results aren't "too good to be true"?
- [ ] Out-of-sample testing performed?
- [ ] No cherry-picking of examples?

### Tool Limitations
- [ ] Aware of testing platform's interpolation methods?
- [ ] Understand how platform handles low-liquidity situations?
- [ ] Know quirks specific to data provider?

**If more than 2-3 items aren't checked, the backtest requires additional work before considering live implementation.**
