# Automated Congressional Trading System - Complete Setup

## 🎯 System Overview
A fully automated trading system that:
1. **Pulls congressional trading data** (Pelosi + Senate - Claude Code is adding Senate support)
2. **Executes trades automatically** via E*TRADE API
3. **Sends Telegram notifications** for all activities
4. **Maintains PDT compliance** for $50K brokerage account
5. **Runs on cron schedule** (9 AM weekdays)

## 📁 Files Created

### Core System Files
1. **`setup_automated_trading.sh`** - Complete setup script
2. **`src/telegram_notifier.py`** - Telegram notification system
3. **`src/pdt_safe_trader.py`** - PDT compliance engine
4. **`src/automated_trading_controller.py`** - Main controller
5. **`run_automated_trading.py`** - Main execution script

### Configuration Files
6. **Updated `config/config.json`** - $50K account with PDT limits
7. **Updated `config/congress_config.json`** - Telegram integration

### Utility Scripts
8. **`scripts/setup_cron.sh`** - Cron job setup
9. **`monitor_trading.sh`** - Monitoring dashboard
10. **`test_telegram_setup.py`** - Telegram test utility
11. **`QUICK_START_AUTOMATED.md`** - Quick start guide

## 🔧 Key Features

### 1. Telegram Notifications
- ✅ Trade execution alerts
- 📊 Congressional trade alerts  
- ⚠️ Error notifications
- 📋 Daily trading summaries
- ✅ Test mode for verification

### 2. PDT Compliance ($50K Account)
- Max 2 day trades in 5 rolling days (conservative)
- Position limits: 5% of account per symbol
- Trade limits: $2,500 max per trade
- Automatic tracking in `data/trade_history.json`

### 3. Automated Scheduling
- Cron job: 9 AM Monday-Friday
- Continuous monitoring option
- Dry-run mode for testing
- Comprehensive logging

### 4. Risk Management
- 1% of account per trade ($500)
- 10% stop-loss protection
- 20% take-profit targets
- Market hours only trading
- Max 3 trades per day

## 🚀 Quick Start Commands

```bash
# 1. Run setup script
./setup_automated_trading.sh

# 2. Test Telegram setup
python3 test_telegram_setup.py

# 3. Test complete system
./run_automated_trading.py --mode test

# 4. Run dry-run trading cycle
./run_automated_trading.py --mode once --dry-run

# 5. Setup cron automation
./scripts/setup_cron.sh

# 6. Monitor system
./monitor_trading.sh
```

## 📱 Telegram Setup Instructions

### 1. Create Telegram Bot
1. Message `@BotFather` on Telegram
2. Send `/newbot` command
3. Choose a name (e.g., "Congressional Trader")
4. Get the bot token (looks like: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### 2. Get Your Chat ID
1. Message `@userinfobot` on Telegram
2. Send `/start` command
3. Copy your numeric chat ID

### 3. Configure in Setup
Run `./setup_automated_trading.sh` and enter:
- Bot token from @BotFather
- Chat ID from @userinfobot

## 🔄 Integration with Claude Code's Senate Data

The system is designed to work seamlessly with the Senate data support that Claude Code is adding:

1. **Data Sources**: Will use both House Clerk (Pelosi) and Senate data
2. **Unified Processing**: All congressional trades processed through same pipeline
3. **Alert System**: Telegram alerts for trades from both chambers
4. **Trading Logic**: Same scaling and risk management for all trades

## 🛡️ Safety Features

### Testing First
- **Sandbox mode**: Default configuration uses E*TRADE sandbox
- **Dry-run mode**: Test without real money
- **Simulation**: Can run in simulation when API fails

### Risk Controls
- **Position limits**: Prevents over-concentration
- **Daily limits**: Caps losses and trade counts
- **Market hours**: Only trades 9:30 AM - 4:00 PM EST
- **PDT compliance**: Avoids day-trader classification

### Monitoring
- **Comprehensive logs**: `logs/trading.log`
- **Trade history**: `data/trade_history.json`
- **Dashboard**: Real-time monitoring with `./monitor_trading.sh`
- **Telegram alerts**: Immediate notification of issues

## 📊 Expected Daily Workflow

1. **9:00 AM**: Cron job triggers
2. **9:05 AM**: Fetch congressional data (Pelosi + Senate)
3. **9:10 AM**: Generate trade recommendations
4. **9:15 AM**: Check PDT compliance
5. **9:20 AM**: Execute approved trades
6. **9:25 AM**: Send Telegram trade alerts
7. **4:00 PM**: Send daily summary to Telegram

## 🚨 Emergency Procedures

### Stop Trading Immediately
```bash
# Method 1: Kill the process
pkill -f "run_automated_trading.py"

# Method 2: If running continuous mode
# Press Ctrl+C in the terminal

# Method 3: Disable cron job
crontab -e  # Remove the congressional_trading line
```

### Check Status
```bash
# View system status
./run_automated_trading.py --mode status

# Check logs
tail -f logs/trading.log

# Monitor dashboard
./monitor_trading.sh
```

## 📈 Going to Production

### 1. Sandbox Testing (1-2 weeks)
- Run in dry-run mode
- Test with small positions
- Verify Telegram notifications
- Check PDT compliance

### 2. Small Live Testing
- Start with 0.1% position sizes ($50 trades)
- Monitor execution quality
- Verify stop-loss triggers
- Test error handling

### 3. Full Deployment
- Gradually increase position sizes
- Enable all alert types
- Set up monitoring alerts
- Document performance

## 🆘 Troubleshooting

### Common Issues

1. **Telegram not working**
   - Check bot token and chat ID
   - Verify bot is started with `/start`
   - Check internet connection

2. **E*TRADE authentication failed**
   - Verify API keys in config
   - Check OAuth token files
   - Test with `python3 src/main.py auth`

3. **No trades executing**
   - Check PDT compliance status
   - Verify market hours
   - Check minimum trade size filters
   - Review congressional data availability

4. **Cron job not running**
   - Check cron service status
   - Verify script permissions
   - Check logs in `/var/log/syslog`

### Debug Commands
```bash
# Test individual components
python3 test_telegram_setup.py
python3 src/main.py auth  # Test E*TRADE
./run_automated_trading.py --mode test

# Check system
./monitor_trading.sh
./run_automated_trading.py --mode status

# View detailed logs
tail -100 logs/trading.log
```

## ✅ Success Criteria

The system is ready when:
1. ✅ Telegram test messages are received
2. ✅ E*TRADE authentication works
3. ✅ Dry-run trading cycles complete
4. ✅ Cron job is scheduled
5. ✅ Monitoring dashboard shows green status
6. ✅ Trade history is being recorded
7. ✅ PDT compliance is being tracked

## 🎉 Next Steps After Setup

1. **Run the setup script** and configure Telegram
2. **Test all components** with dry-run mode
3. **Set up cron automation** for daily execution
4. **Monitor for 1 week** in sandbox mode
5. **Review performance** and adjust parameters
6. **Go live** with small position sizes

---

**System Ready**: The complete automated congressional trading system with Telegram notifications is now built and ready for deployment! 🚀