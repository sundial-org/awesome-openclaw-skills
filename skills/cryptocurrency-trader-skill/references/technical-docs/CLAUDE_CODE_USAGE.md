# AI Trading Skill - Claude Code Usage Guide

This guide shows how to use the AI Trading skill with Claude Code.

## Quick Start

### 1. Setup (One-time)

```bash
cd cryptocurrency-trader-skill
pip install -r requirements.txt
```

### 2. Basic Usage

**Analyze a specific cryptocurrency:**
```bash
python skill.py analyze BTC/USDT --balance 10000
```

**Scan market for best opportunities:**
```bash
python skill.py scan --balance 10000 --top 5
```

**Interactive mode:**
```bash
python skill.py interactive --balance 10000
```

**Using the shell script:**
```bash
./run.sh analyze ETH/USDT
./run.sh scan
./run.sh interactive
```

## Environment Variables

Set your default trading balance:
```bash
export TRADING_BALANCE=10000
```

Then you can omit the --balance flag:
```bash
python skill.py analyze BTC/USDT
```

## Claude Code Integration

### Method 1: Direct Invocation

When working in Claude Code, you can invoke the skill directly:

```bash
cd cryptocurrency-trader-skill
python skill.py analyze BTC/USDT --balance 10000
```

### Method 2: As a Python Module

```bash
cd ai-trading-claude-skills
python -m cryptocurrency_trader_skill analyze BTC/USDT --balance 10000
```

### Method 3: Programmatic Usage

```python
import sys
sys.path.insert(0, 'cryptocurrency-trader-skill/scripts')

from trading_agent_refactored import TradingAgent

# Initialize agent
agent = TradingAgent(balance=10000)

# Analyze specific symbol
analysis = agent.comprehensive_analysis('BTC/USDT')

# Display results
print(f"Action: {analysis['final_recommendation']['action']}")
print(f"Confidence: {analysis['final_recommendation']['confidence']}%")
```

## Command Reference

### analyze

Analyze a specific trading pair with comprehensive multi-layer validation.

```bash
python skill.py analyze <SYMBOL> [OPTIONS]
```

**Options:**
- `--balance BALANCE` - Account balance for position sizing (default: $10,000)
- `--timeframes TF...` - Timeframes to analyze (default: 15m 1h 4h)

**Examples:**
```bash
# Basic analysis
python skill.py analyze BTC/USDT --balance 10000

# Custom timeframes
python skill.py analyze ETH/USDT --balance 5000 --timeframes 5m 15m 1h

# Using environment variable
export TRADING_BALANCE=10000
python skill.py analyze SOL/USDT
```

### scan

Scan the market for best trading opportunities across multiple categories.

```bash
python skill.py scan [OPTIONS]
```

**Options:**
- `--balance BALANCE` - Account balance (default: $10,000)
- `--top N` - Number of top opportunities to return (default: 5)
- `--categories CAT...` - Specific market categories to scan

**Examples:**
```bash
# Scan for top 5 opportunities
python skill.py scan --balance 10000 --top 5

# Scan specific categories
python skill.py scan --categories "Major Coins" "AI Tokens" --top 3
```

**Market Categories:**
- Major Coins: BTC, ETH, BNB, SOL, XRP
- AI Tokens: RENDER, FET, AGIX, OCEAN, TAO
- DeFi: UNI, AAVE, MKR, CRV, COMP
- Layer 1: ADA, AVAX, DOT, ATOM, NEAR
- Layer 2: MATIC, OP, ARB, IMX, LRC
- Meme Coins: DOGE, SHIB, PEPE, FLOKI, BONK

### interactive

Enter interactive mode for exploratory analysis.

```bash
python skill.py interactive --balance 10000
```

**Interactive Commands:**
- `analyze <SYMBOL>` - Analyze a specific trading pair
- `scan` - Scan market for opportunities
- `help` - Show help
- `quit` - Exit interactive mode

**Example Session:**
```
> analyze BTC/USDT
[Comprehensive analysis displayed]

> scan 3
[Top 3 opportunities displayed]

> quit
```

## Output Structure

All analysis commands return comprehensive results including:

### Trading Recommendation
- **Action**: LONG, SHORT, or WAIT
- **Confidence**: 0-100% confidence score
- **Entry Price**: Recommended entry price
- **Stop Loss**: Risk management level
- **Take Profit**: Profit target
- **Risk/Reward Ratio**: Expected R:R ratio

### Pattern Analysis
- **Chart Patterns**: Double tops/bottoms, H&S, wedges, triangles
- **Candlestick Patterns**: Doji, hammer, engulfing, etc.
- **Support/Resistance**: Key price levels
- **Trend Analysis**: Multi-timeframe trend direction and strength

### Risk Metrics
- **VaR (Value at Risk)**: Potential loss at 95% confidence
- **CVaR (Conditional VaR)**: Expected shortfall
- **Sharpe Ratio**: Risk-adjusted returns
- **Maximum Drawdown**: Largest historical drawdown

### Probabilistic Analysis
- **Bayesian Signals**: Combined probability from multiple indicators
- **Monte Carlo**: 10,000-scenario price projection
- **Expected Return**: Probabilistic return estimate

### Validation Status
- **Execution Ready**: Boolean - safe to trade
- **Validation Checkpoints**: 6-stage validation results
- **Circuit Breaker Status**: Safety checks passed

## Error Handling

The skill gracefully handles errors and provides clear feedback:

```bash
# Missing required arguments
python skill.py analyze
❌ Please specify a symbol

# Invalid symbol
python skill.py analyze INVALID/PAIR --balance 10000
❌ Error during analysis: [specific error]

# Network issues
python skill.py analyze BTC/USDT --balance 10000
⚠️  Unable to fetch market data, retrying...
```

## Best Practices

1. **Always specify balance** for accurate position sizing
2. **Use multiple timeframes** for comprehensive analysis (15m, 1h, 4h)
3. **Check execution_ready flag** before trading
4. **Review validation reports** to understand any warnings
5. **Start with scan** to identify best opportunities
6. **Use interactive mode** for exploratory analysis

## Troubleshooting

### Import Errors

If you see import errors:
```bash
cd cryptocurrency-trader-skill
pip install -r requirements.txt
```

### Missing Dependencies

Ensure all required packages are installed:
- pandas, numpy, ccxt (data fetching)
- scipy, scikit-learn (statistics)
- ta (technical analysis)

### API Rate Limiting

If you hit exchange rate limits:
- Reduce scan frequency
- Use fewer timeframes
- Add delays between requests

## Advanced Usage

### Custom Configuration

Create a custom config file:
```python
# custom_config.py
CUSTOM_CONFIG = {
    'risk': {
        'max_position_size': 0.15,  # 15% max position
        'stop_loss_pct': 0.02,      # 2% stop loss
    },
    'indicators': {
        'rsi_period': 14,
        'macd_fast': 12,
        'macd_slow': 26,
    }
}
```

Then use it:
```python
from trading_agent_refactored import TradingAgent
from custom_config import CUSTOM_CONFIG

agent = TradingAgent(balance=10000, config=CUSTOM_CONFIG)
```

### Batch Analysis

Analyze multiple symbols:
```bash
for symbol in BTC/USDT ETH/USDT SOL/USDT; do
    python skill.py analyze $symbol --balance 10000
done
```

### JSON Output

For programmatic consumption:
```python
import json
from skill import analyze_symbol

result = analyze_symbol('BTC/USDT', balance=10000)
print(json.dumps(result, indent=2, default=str))
```

## Support

For issues or questions:
1. Check the main SKILL.md documentation
2. Review the refactoring documentation (TASK9_REFACTORING_SUMMARY.md)
3. Run tests to validate installation: `pytest tests/`

## Version Information

- **Current Version**: 2.0 (Refactored)
- **Python Required**: 3.8+
- **Main Components**: 14 refactored modules
- **Test Coverage**: 22+ tests for refactored components
- **Backward Compatible**: Yes (drop-in replacement)
