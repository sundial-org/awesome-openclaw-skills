# Output Interpretation Guide

## Understanding Trading Signals

### Action Types
- **LONG** - Buy now, sell higher later for profit
- **SHORT** - Sell now, buy back cheaper later for profit  
- **NO_TRADE** - No clear opportunity right now, patience is key

### Signal Components

**Confidence Level (0-95%)**
How certain the analysis is about this signal. Higher is better, but:
- 40-59%: Weak signal, avoid trading
- 60-69%: Moderate signal, proceed with caution
- 70-89%: Strong signal, favorable conditions
- 90-95%: Very strong signal (capped at 95% to prevent overconfidence)

**Entry Price**
Recommended price point to enter the trade.

**Stop Loss**
Automatic exit price to limit loss if trade goes wrong. Always use this!

**Take Profit**
Automatic exit price to lock in profits at target level.

**Risk/Reward Ratio**
For every $1 risked, how much profit is targeted.
- Minimum: 1.5:1 (make $1.50 for every $1 risked)
- Preferred: 2:1 or better

**Execution Ready (YES/NO)**
Binary flag indicating if all 6 validation stages passed. Only trade when YES.

## Probabilistic Analysis

**Bayesian Bullish/Bearish Probability**
Statistical likelihood of upward/downward price movement based on multiple indicators.

**Signal Strength**
- WEAK: Low confidence, multiple conflicting indicators
- MODERATE: Decent confidence, some agreement
- STRONG: High confidence, strong consensus

**Monte Carlo Profit Probability**
% chance of profit based on 10,000 simulated price scenarios.

**Pattern Bias**
Confirmation or conflict from chart pattern analysis.

## Risk Assessment Metrics

**Value at Risk (VaR)**
Maximum expected 1-day loss at 95% confidence level.
- Example: VaR of $500 means 95% confidence loss won't exceed $500

**Conditional VaR (CVaR)**
Average loss in worst 5% of scenarios (worst-case analysis).

**Sharpe Ratio**
Risk-adjusted return metric:
- <1.0: Poor risk-adjusted returns
- 1.0-2.0: Good risk-adjusted returns
- >2.0: Excellent risk-adjusted returns

**Sortino Ratio**
Similar to Sharpe but focuses only on downside risk.

**Max Drawdown**
Largest peak-to-trough decline in the analysis period.

**Win Rate**
% of profitable periods in historical data.

**Profit Factor**
Gross profit divided by gross loss:
- <1.0: Losing strategy
- 1.0-2.0: Break-even to moderate profitability
- >2.0: Strong profitability

## Position Sizing

**Standard Sizing (2% Risk Rule)**
Recommended default - risk 2% of account balance per trade.

**Kelly Conservative**
Mathematically optimal conservative sizing based on win rate and risk/reward.

**Kelly Aggressive**
Mathematically optimal aggressive sizing (higher risk, higher reward potential).

**Trading Fees**
Estimated execution costs (maker/taker fees).

## Pattern Recognition

**Detected Patterns**
Chart patterns identified with confidence scores:
- Reversal patterns suggest trend change
- Continuation patterns suggest trend continuation
- Candlestick patterns provide short-term signals

**Support/Resistance Levels**
Price levels where buying/selling pressure historically concentrated.

**Trend Analysis**
- Short-term (15m): Immediate momentum
- Medium-term (1h): Intraday trend
- Long-term (4h): Daily trend

**Market Regime**
- Trending: Clear directional movement
- Ranging: Sideways consolidation

**Volume Confirmation**
Does volume support the price movement?

## Validation Status

Shows which validation stages passed:
- Stage 1: Data Integrity ✓
- Stage 2: Indicator Validation ✓
- Stage 3: Signal Validation ✓
- Stage 4: Cross-Verification ✓
- Stage 5: Execution Readiness ✓
- Stage 6: Production Validation ✓

All 6 must pass for execution-ready status.

## Beginner-Friendly Summary

When presenting results to users, explain in simple terms:

- **What to do**: The recommended action (LONG/SHORT/WAIT)
- **How confident**: The probability it will work (confidence %)
- **How much to risk**: Position size (default 2% of balance)
- **Where to exit if wrong**: Stop loss price
- **Where to exit if right**: Take profit price
- **Is it safe to trade**: Execution ready flag (YES/NO)

## Common Questions

**Q: What confidence level should I look for?**
A: 60%+ is moderate, 70%+ is strong. Avoid anything >90% (unrealistic). Never trade below 40%.

**Q: What's a good risk/reward ratio?**
A: Minimum 1.5:1 (make $1.50 for every $1 risked). Prefer 2:1 or better.

**Q: How much should I trade?**
A: The agent enforces 2% max risk per trade and 10% max position size automatically.

**Q: What if it shows WAIT/NO_TRADE?**
A: That's normal! Most of the time, the best action is to wait for clear opportunities.

**Q: Can I trust the analysis?**
A: Use it as one input among many. Do your own research, start small, and never risk money you can't afford to lose.

## Risk Warnings

ALWAYS remember:

- Markets are unpredictable - even perfect analysis can be wrong
- Start with small amounts to learn
- Never risk more than 2% of account per trade (enforced automatically)
- Always use stop losses to protect capital
- This is analysis, NOT financial advice
- Past performance does NOT guarantee future results
- YOU are solely responsible for all trading decisions
