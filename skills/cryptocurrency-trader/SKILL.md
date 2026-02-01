---
name: cryptocurrency-trader
description: Production-grade AI trading agent for cryptocurrency markets with advanced mathematical modeling, multi-layer validation, probabilistic analysis, and zero-hallucination tolerance. Implements Bayesian inference, Monte Carlo simulations, advanced risk metrics (VaR, CVaR, Sharpe), chart pattern recognition, and comprehensive cross-verification for real-world trading application.
---

# Cryptocurrency Trading Agent Skill

## Purpose

Provide production-grade cryptocurrency trading analysis with mathematical rigor, multi-layer validation, and comprehensive risk assessment. Designed for real-world trading application with zero-hallucination tolerance through 6-stage validation pipeline.

## When to Use This Skill

Use this skill when users request:
- Analysis of specific cryptocurrency trading pairs (e.g., BTC/USDT, ETH/USDT)
- Market scanning to find best trading opportunities
- Comprehensive risk assessment with probabilistic modeling
- Trading signals with advanced pattern recognition
- Professional risk metrics (VaR, CVaR, Sharpe, Sortino)
- Monte Carlo simulations for scenario analysis
- Bayesian probability calculations for signal confidence

## Core Capabilities

### Validation & Accuracy
- 6-stage validation pipeline with zero-hallucination tolerance
- Statistical anomaly detection (Z-score, IQR, Benford's Law)
- Cross-verification across multiple timeframes
- 14 circuit breakers to prevent invalid signals

### Analysis Methods
- Bayesian inference for probability calculations
- Monte Carlo simulations (10,000 scenarios)
- GARCH volatility forecasting
- Advanced chart pattern recognition
- Multi-timeframe consensus (15m, 1h, 4h)

### Risk Management
- Value at Risk (VaR) and Conditional VaR (CVaR)
- Risk-adjusted metrics (Sharpe, Sortino, Calmar)
- Kelly Criterion position sizing
- Automated stop-loss and take-profit calculation

**Detailed capabilities:** See `references/advanced-capabilities.md`

## Prerequisites

Ensure the following before using this skill:
1. Python 3.8+ environment available
2. Internet connection for real-time market data
3. Required packages installed: `pip install -r requirements.txt`
4. User's account balance known for position sizing

## How to Use This Skill

### Quick Start Commands

**Analyze a specific cryptocurrency:**
```bash
python skill.py analyze BTC/USDT --balance 10000
```

**Scan market for best opportunities:**
```bash
python skill.py scan --top 5 --balance 10000
```

**Interactive mode for exploration:**
```bash
python skill.py interactive --balance 10000
```

### Default Parameters

- **Balance:** If not specified by user, use `--balance 10000`
- **Timeframes:** 15m, 1h, 4h (automatically analyzed)
- **Risk per trade:** 2% of balance (enforced by default)
- **Minimum risk/reward:** 1.5:1 (validated by circuit breakers)

### Common Trading Pairs

Major: BTC/USDT, ETH/USDT, BNB/USDT, SOL/USDT, XRP/USDT
AI Tokens: RENDER/USDT, FET/USDT, AGIX/USDT
Layer 1: ADA/USDT, AVAX/USDT, DOT/USDT
Layer 2: MATIC/USDT, ARB/USDT, OP/USDT
DeFi: UNI/USDT, AAVE/USDT, LINK/USDT
Meme: DOGE/USDT, SHIB/USDT, PEPE/USDT

### Workflow

1. **Gather Information**
   - Ask user for trading pair (if analyzing specific symbol)
   - Ask for account balance (or use default $10,000)
   - Confirm user wants production-grade analysis

2. **Execute Analysis**
   - Run appropriate command (analyze, scan, or interactive)
   - Wait for comprehensive analysis to complete
   - System automatically validates through 6 stages

3. **Present Results**
   - Display trading signal (LONG/SHORT/NO_TRADE)
   - Show confidence level and execution readiness
   - Explain entry, stop-loss, and take-profit prices
   - Present risk metrics and position sizing
   - Highlight validation status (6/6 passed = execution ready)

4. **Interpret Output**
   - Reference `references/output-interpretation.md` for detailed guidance
   - Translate technical metrics into user-friendly language
   - Explain risk/reward in simple terms
   - Always include risk warnings

5. **Handle Edge Cases**
   - If execution_ready = NO: Explain validation failures
   - If confidence <40%: Recommend waiting for better opportunity
   - If circuit breakers triggered: Explain specific issue
   - If network errors: Suggest retry with exponential backoff

### Output Structure

**Trading Signal:**
- Action: LONG/SHORT/NO_TRADE
- Confidence: 0-95% (integer only, no false precision)
- Entry Price: Recommended entry point
- Stop Loss: Risk management exit (always required)
- Take Profit: Profit target
- Risk/Reward: Minimum 1.5:1 ratio

**Probabilistic Analysis:**
- Bayesian probabilities (bullish/bearish)
- Monte Carlo profit probability
- Signal strength (WEAK/MODERATE/STRONG)
- Pattern bias confirmation

**Risk Assessment:**
- VaR and CVaR (Value at Risk metrics)
- Sharpe/Sortino/Calmar ratios
- Max drawdown and win rate
- Profit factor

**Position Sizing:**
- Standard (2% risk rule) - recommended
- Kelly Conservative - mathematically optimal
- Kelly Aggressive - higher risk/reward
- Trading fees estimate

**Validation Status:**
- Stages passed (must be 6/6 for execution ready)
- Circuit breakers triggered (if any)
- Warnings and critical failures

**Detailed interpretation:** See `references/output-interpretation.md`

## Presenting Results to Users

### Language Guidelines

Use beginner-friendly explanations:
- "LONG" → "Buy now, sell higher later"
- "SHORT" → "Sell now, buy back cheaper later"
- "Stop Loss" → "Automatic exit to limit loss if wrong"
- "Confidence %" → "How certain we are (higher = better)"
- "Risk/Reward" → "For every $1 risked, potential $X profit"

### Required Risk Warnings

ALWAYS include these reminders:
- Markets are unpredictable - perfect analysis can still be wrong
- Start with small amounts to learn
- Never risk more than 2% per trade (enforced automatically)
- Always use stop losses
- This is analysis, NOT financial advice
- Past performance does NOT guarantee future results
- User is solely responsible for all trading decisions

### When NOT to Trade

Advise users to avoid trading when:
- Validation status <6/6 passed
- Execution Ready flag = NO
- Confidence <60% for moderate signals, <70% for strong
- User doesn't understand the analysis
- User can't afford potential loss
- High emotional stress or fatigue

## Advanced Usage

### Programmatic Integration

For custom workflows, import directly:
```python
from scripts.trading_agent_refactored import TradingAgent

agent = TradingAgent(balance=10000)
analysis = agent.comprehensive_analysis('BTC/USDT')
print(analysis['final_recommendation'])
```

See `example_usage.py` for 5 comprehensive examples.

### Configuration

Customize behavior via `config.yaml`:
- Validation strictness (strict vs normal mode)
- Risk parameters (max risk, position limits)
- Circuit breaker thresholds
- Timeframe preferences

### Testing

Verify installation and functionality:
```bash
# Run compatibility test
./test_claude_code_compat.sh

# Run comprehensive tests
python -m pytest tests/
```

## Reference Documentation

- `references/advanced-capabilities.md` - Detailed technical capabilities
- `references/output-interpretation.md` - Comprehensive output guide
- `references/optimization.md` - Trading optimization strategies
- `references/protocol.md` - Usage protocols and best practices
- `references/psychology.md` - Trading psychology principles
- `references/user-guide.md` - End-user documentation
- `references/technical-docs/` - Implementation details and bug reports

## Architecture

**Core Modules:**
- `scripts/trading_agent_refactored.py` - Main trading agent (production)
- `scripts/advanced_validation.py` - Multi-layer validation system
- `scripts/advanced_analytics.py` - Probabilistic modeling engine
- `scripts/pattern_recognition_refactored.py` - Chart pattern recognition
- `scripts/indicators/` - Technical indicator calculations
- `scripts/market/` - Data provider and market scanner
- `scripts/risk/` - Position sizing and risk management
- `scripts/signals/` - Signal generation and recommendation

**Entry Points:**
- `skill.py` - Command-line interface (recommended)
- `__main__.py` - Python module invocation
- `example_usage.py` - Programmatic usage examples

## Version

**v2.0.1 - Production Hardened Edition**

Recent improvements:
- Fixed critical bugs (division by zero, import paths, NaN handling)
- Enhanced network retry logic with exponential backoff
- Improved logging infrastructure
- Comprehensive input validation
- UTC timezone consistency
- Benford's Law threshold optimization

**Status:** 🟢 PRODUCTION READY

See `references/technical-docs/FIXES_APPLIED.md` for complete changelog.

## Troubleshooting

**Installation issues:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Import errors:**
Ensure running from skill directory or using `skill.py` entry point.

**Network failures:**
System automatically retries with exponential backoff (3 attempts).

**Validation failures:**
Check validation report in output - explains which stage failed and why.

**For detailed debugging:**
Enable logging in `config.yaml` or check `references/technical-docs/BUG_ANALYSIS_REPORT.md`
