# Quick Start Guide

## Prerequisites
- Python 3.7 or higher
- E*TRADE Developer Account with Sandbox API keys
- Basic understanding of stock trading and risks

## Setup

### 1. Install Dependencies
```bash
cd etrade-pelosi-bot
python setup.py
```

Or manually:
```bash
pip install -r src/requirements.txt
```

### 2. Configure API Keys
Edit `config/config.json` with your E*TRADE Sandbox API keys:
```json
{
  "etrade": {
    "environment": "sandbox",
    "apiKey": "cde63877b06b844b59b5c23b0d3ad7f7",
    "apiSecret": "ff190254629156cb6f9fc95adcb7eb73610aeda21b76864621e4752463c42aa4",
    ...
  }
}
```

### 3. Authenticate with E*TRADE
```bash
python src/main.py auth
```
Follow the prompts to authorize the application.

## Usage

### Interactive Mode (Recommended for Testing)
```bash
python src/main.py interactive
```

### Run Single Trading Cycle
```bash
python src/main.py run
```

### Scheduled Trading
```bash
python src/main.py schedule 24
```

### Check Status
```bash
python src/main.py status
```

## Configuration Options

### Trading Parameters (`config/config.json`):
- `tradeScalePercentage`: Percentage of your account to allocate per trade (default: 0.01 = 1%)
- `maxPositionPercentage`: Maximum position size as percentage of account (default: 0.05 = 5%)
- `dailyLossLimit`: Maximum daily loss percentage (default: 0.02 = 2%)
- `marketHoursOnly`: Only trade during market hours (9:30 AM - 4:00 PM ET)

### Pelosi Tracking:
- `minimumTradeSize`: Minimum Pelosi trade size to mirror (default: $10,000)
- `pollIntervalHours`: How often to check for new trades (default: 24 hours)

## Safety Features

### Built-in Protections:
1. **Position Limits**: Prevents over-concentration in single stocks
2. **Daily Loss Limits**: Stops trading if daily losses exceed threshold
3. **Market Hours**: Only trades during regular market hours
4. **Minimum Trade Size**: Ignores small Pelosi trades
5. **Emergency Stop**: Immediate shutdown capability

### Risk Management:
- Start with `tradeScalePercentage` of 0.001 (0.1%) for testing
- Use Sandbox environment first
- Monitor logs in `logs/trading.log`
- Review trade history in `trade_history.json`

## Testing with Sandbox

### Sandbox Environment:
- Uses simulated trading with fake money
- No real orders are placed
- Perfect for testing and development

### Test Sequence:
1. Run in interactive mode
2. Check authentication works
3. Test trade calculations
4. Verify no real orders are placed
5. Review logs and trade history

## Production Readiness Checklist

Before using with real money:
- [ ] Test extensively in Sandbox
- [ ] Review and adjust risk parameters
- [ ] Set up proper logging and monitoring
- [ ] Implement backup and recovery procedures
- [ ] Consult with financial advisor
- [ ] Start with very small trade scale (0.1% or less)

## Important Notes

### Legal & Compliance:
- This is an automated trading system - use at your own risk
- Past performance is not indicative of future results
- Mirroring congressional trades has legal and ethical considerations
- Consult with legal and financial professionals

### Technical Notes:
- The system uses public data sources which may have delays
- Trade execution depends on market conditions and liquidity
- Always maintain manual override capability
- Regular monitoring is required

## Troubleshooting

### Common Issues:

1. **Authentication Failed**
   - Verify API keys are correct
   - Check internet connection
   - Ensure you're using Sandbox keys for Sandbox environment

2. **No Trades Found**
   - Check data source availability
   - Verify minimum trade size setting
   - Check network connectivity

3. **Trade Execution Failed**
   - Verify market is open (if `marketHoursOnly` is true)
   - Check account has sufficient funds
   - Review position limits

### Logs:
- Check `logs/trading.log` for detailed error messages
- Trade history saved in `trade_history.json`
- Pelosi trade data saved in `recent_pelosi_trades.json`

## Support
For issues and questions:
1. Review logs and configuration
2. Check E*TRADE API documentation
3. Consult trading system best practices
4. Consider professional implementation for production use

**Remember: Automated trading involves significant risk. Never invest money you cannot afford to lose.**