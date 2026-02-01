#!/bin/bash
#
# Setup cron jobs for Congressional Trade Mirror Bot
#
# This script installs cron jobs for:
# 1. Daily trade check (fetches new congressional disclosures)
# 2. Hourly position monitoring (stop-loss checks during market hours)
#

BOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNNER="$BOT_DIR/scripts/run_bot.sh"

echo "=========================================="
echo "Congressional Trade Bot - Cron Setup"
echo "=========================================="
echo ""
echo "Bot directory: $BOT_DIR"
echo ""

# Make runner executable
chmod +x "$RUNNER"

# Define cron jobs
# Format: minute hour day month weekday command

# 1. Daily check at 6 PM ET (after market close, when new disclosures may appear)
#    Runs Mon-Fri only
DAILY_CHECK="0 18 * * 1-5 $RUNNER check >> $BOT_DIR/logs/cron.log 2>&1"

# 2. Hourly position monitor during market hours (9:30 AM - 4 PM ET)
#    Runs every hour from 10 AM to 4 PM, Mon-Fri
HOURLY_MONITOR="0 10-16 * * 1-5 $RUNNER monitor >> $BOT_DIR/logs/cron.log 2>&1"

# 3. Morning pre-market check at 8 AM ET
#    Good time to catch overnight disclosures
MORNING_CHECK="0 8 * * 1-5 $RUNNER check >> $BOT_DIR/logs/cron.log 2>&1"

echo "Proposed cron jobs:"
echo ""
echo "1. Daily evening check (6 PM ET, Mon-Fri):"
echo "   $DAILY_CHECK"
echo ""
echo "2. Hourly position monitor (10 AM - 4 PM ET, Mon-Fri):"
echo "   $HOURLY_MONITOR"
echo ""
echo "3. Morning pre-market check (8 AM ET, Mon-Fri):"
echo "   $MORNING_CHECK"
echo ""

read -p "Install these cron jobs? (y/n): " confirm

if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo "Cancelled."
    exit 0
fi

# Backup existing crontab
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null

# Check if jobs already exist
EXISTING=$(crontab -l 2>/dev/null | grep -c "run_bot.sh")
if [ "$EXISTING" -gt 0 ]; then
    read -p "Existing bot cron jobs found. Replace them? (y/n): " replace
    if [ "$replace" == "y" ] || [ "$replace" == "Y" ]; then
        # Remove existing bot jobs
        crontab -l 2>/dev/null | grep -v "run_bot.sh" | crontab -
    else
        echo "Keeping existing jobs."
        exit 0
    fi
fi

# Add new jobs
(crontab -l 2>/dev/null; echo "# Congressional Trade Mirror Bot") | crontab -
(crontab -l 2>/dev/null; echo "$DAILY_CHECK") | crontab -
(crontab -l 2>/dev/null; echo "$HOURLY_MONITOR") | crontab -
(crontab -l 2>/dev/null; echo "$MORNING_CHECK") | crontab -

echo ""
echo "Cron jobs installed successfully!"
echo ""
echo "Current crontab:"
crontab -l | grep -A 10 "Congressional Trade"
echo ""
echo "To view logs: tail -f $BOT_DIR/logs/cron.log"
echo "To remove jobs: crontab -e (and delete the bot lines)"
echo ""
echo "IMPORTANT: Make sure you've authenticated with E*TRADE first!"
echo "Run: python3 src/main.py interactive"
echo "Then select option 1 to authenticate."
