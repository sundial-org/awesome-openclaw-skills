"""
ClawBack - Congressional Trade Mirror Bot
Tracks House and Senate trades, executes scaled positions via broker API
https://github.com/openclaw/clawback
"""
import json
import logging
import time
import schedule
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
import sys
import os

from .config_loader import load_config
from .broker_adapter import get_broker_adapter
from .congress_tracker import CongressTracker
from .trade_engine import TradeEngine
from .database import get_database, TradingDatabase
from .telegram_notifier import TelegramNotifier

# Configure logging
def setup_logging(config):
    """Configure logging based on config"""
    log_level = getattr(logging, config['logging']['level'].upper())
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.dirname(config['logging']['file'])
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(config['logging']['file']),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce verbosity for some libraries
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    return logging.getLogger(__name__)

class TradingBot:
    """Main trading bot controller"""

    def __init__(self, config_path='config/config.json'):
        # Load configuration with environment variable substitution
        self.config = load_config(config_path)

        # Setup logging
        self.logger = setup_logging(self.config)

        # Initialize database
        db_path = self.config.get('database', {}).get('path', 'data/trading.db')
        self.db = get_database(db_path)

        # Initialize Telegram notifier
        self.notifier = TelegramNotifier(self.config.get('notifications', {}))

        # Initialize components using adapter pattern
        self.broker = get_broker_adapter(self.config)
        self.congress_tracker = CongressTracker(self.config)
        self.trade_engine = TradeEngine(self.broker, self.config)

        # Wire up broker error notifications to Telegram
        self.broker.set_error_callback(self._handle_broker_error)

        self.logger.info(f"Using broker adapter: {self.broker.BROKER_NAME}")

        # Timezone for scheduling (default: NYSE timezone)
        schedule_config = self.config.get('schedule', {})
        self.schedule_timezone = ZoneInfo(schedule_config.get('timezone', 'America/New_York'))
        self.disclosure_check_times = schedule_config.get('disclosureCheckTimes', ['10:00', '14:00', '18:00'])

        # State
        self.is_running = False
        self.manual_mode = False
        self.pending_trades = []  # Trades waiting for market open

        # Load last check time from database
        last_check = self.db.get_state('last_check_time')
        self.last_check_time = datetime.fromisoformat(last_check) if last_check else None

        # Try to load saved access tokens
        self._load_saved_tokens()

        self.logger.info("Trading bot initialized with SQLite database")
        self.logger.info(f"Disclosure checks scheduled at: {', '.join(self.disclosure_check_times)} ET")

    def _handle_broker_error(self, operation: str, error: str, details: dict = None):
        """Handle broker API errors by sending Telegram notification"""
        self.logger.error(f"Broker error - {operation}: {error}")
        self.notifier.send_broker_error(operation, error, details, broker_name=self.broker.BROKER_NAME)

    def _get_local_timestamp(self):
        """Get current timestamp formatted in local timezone"""
        return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')

    def _load_saved_tokens(self):
        """Load saved access tokens from database or file"""
        # First try database
        account_id = self.config.get('trading', {}).get('accountId', '')
        db_tokens = self.db.get_broker_tokens(self.broker.BROKER_NAME, account_id)

        if db_tokens and db_tokens.get('access_token'):
            self.broker.set_tokens(
                db_tokens['access_token'],
                db_tokens.get('access_secret')
            )
            self.logger.info("Loaded access tokens from database")
            return

        # Fallback to JSON file (for migration)
        token_file = '.access_tokens.json'
        if os.path.exists(token_file):
            try:
                with open(token_file, 'r') as f:
                    tokens = json.load(f)
                if tokens.get('access_token'):
                    self.broker.set_tokens(
                        tokens['access_token'],
                        tokens.get('access_secret')
                    )
                    # Migrate to database
                    self._save_tokens_to_db()
                    self.logger.info("Loaded and migrated access tokens from file to database")
            except Exception as e:
                self.logger.warning(f"Could not load saved tokens: {e}")

    def _save_tokens_to_db(self):
        """Save current broker tokens to database"""
        try:
            tokens = self.broker.get_tokens()
            if tokens.get('access_token'):
                account_id = self.config.get('trading', {}).get('accountId', '')
                self.db.save_broker_tokens(
                    broker=self.broker.BROKER_NAME,
                    access_token=tokens['access_token'],
                    access_secret=tokens.get('access_secret'),
                    account_id=account_id
                )
                self.logger.debug("Saved tokens to database")
        except Exception as e:
            self.logger.warning(f"Could not save tokens to database: {e}")

    def refresh_broker_tokens(self):
        """Refresh broker access tokens to keep session alive"""
        if not self.broker.is_authenticated:
            self.logger.debug("Skipping token refresh - not authenticated")
            return False

        try:
            self.logger.info("Refreshing broker access token...")
            if self.broker.renew_access_token():
                # Update refresh timestamp in database
                account_id = self.config.get('trading', {}).get('accountId', '')
                self.db.update_token_refresh_time(self.broker.BROKER_NAME, account_id)
                self.logger.info("Successfully refreshed broker token")
                return True
            else:
                self.logger.warning("Token refresh failed - may need to re-authenticate")
                self.notifier.send_error_alert(
                    "Token Refresh Failed",
                    "Broker access token could not be renewed. Re-authentication may be required.",
                    f"Broker: {self.broker.BROKER_NAME}"
                )
                return False
        except Exception as e:
            self.logger.error(f"Error refreshing token: {e}")
            return False
    
    def authenticate(self, verifier_code=None):
        """Authenticate with broker"""
        self.logger.info(f"Starting {self.broker.BROKER_NAME} authentication...")

        # Get authorization URL
        auth_url = self.broker.get_auth_url()

        if not auth_url:
            self.logger.error("Failed to get authorization URL")
            return False

        self.logger.info(f"Please visit this URL to authorize: {auth_url}")
        self.logger.info("After authorizing, you'll get a verification code.")

        # Get verification code from user if not provided
        if not verifier_code:
            verifier_code = input("Enter the verification code: ").strip()

        # Exchange for access token
        success = self.broker.authenticate(verifier_code)

        if success:
            # Save tokens to database for persistence
            self._save_tokens_to_db()
            self.logger.info("Access tokens saved to database")

            # Get accounts
            accounts = self.broker.get_accounts()
            if accounts:
                self.logger.info(f"Found {len(accounts)} account(s)")
                for acc in accounts:
                    self.logger.info(f"  - {acc.get('accountId')}: {acc.get('accountName', acc.get('accountDesc', ''))}")
            return True
        else:
            self.logger.error("Authentication failed")
            return False
    
    def check_for_new_disclosures(self):
        """Check for new congressional disclosures and queue for trading"""
        try:
            self.logger.info("Checking for new congressional disclosures...")

            # Determine cutoff time (last check or 7 days ago)
            if self.last_check_time:
                cutoff_time = self.last_check_time
            else:
                cutoff_time = datetime.now() - timedelta(days=7)

            # Get new trades since last check
            try:
                all_trades = self.congress_tracker.get_trades_since(cutoff_time)
            except Exception as fetch_error:
                # Send Telegram alert for disclosure fetch failure
                error_msg = str(fetch_error)
                self.logger.error(f"Failed to fetch disclosures: {error_msg}")
                self.notifier.send_disclosure_error(
                    source="House Clerk / Senate eFD",
                    error_message=error_msg,
                    details={
                        "cutoff_time": cutoff_time.strftime('%Y-%m-%d %H:%M'),
                        "include_senate": self.congress_tracker.include_senate
                    }
                )
                return

            if not all_trades:
                self.logger.info("No new congressional disclosures found")
                self._update_last_check_time()
                return

            # Store new trades in database and filter out duplicates
            new_trades = []
            for trade in all_trades:
                if not self.db.trade_exists(trade):
                    self.db.add_congressional_trade(trade)
                    new_trades.append(trade)

            if not new_trades:
                self.logger.info("No new trades (all already in database)")
                self._update_last_check_time()
                return

            self.logger.info(f"Found {len(new_trades)} new congressional disclosures")

            # Log by chamber
            house_trades = [t for t in new_trades if t.get('chamber') != 'senate']
            senate_trades = [t for t in new_trades if t.get('chamber') == 'senate']
            if house_trades:
                self.logger.info(f"  House: {len(house_trades)} trades")
            if senate_trades:
                self.logger.info(f"  Senate: {len(senate_trades)} trades")

            # Save trades for reference
            self.congress_tracker.save_trades_to_file(new_trades, 'recent_congressional_trades.json')

            # Update last check time
            self._update_last_check_time()

            # Update fetch timestamps
            self.db.set_last_fetch_time('house_clerk')
            if self.congress_tracker.include_senate:
                self.db.set_last_fetch_time('senate_efd')

            # Queue trades for execution
            self.pending_trades.extend(new_trades)
            self.logger.info(f"Queued {len(new_trades)} trades for execution")

            # Send Telegram alerts for new congressional trades
            for trade in new_trades[:5]:  # Limit to first 5 to avoid spam
                self.notifier.send_congressional_alert(trade)

            # Try to execute if market is open
            self.execute_pending_trades()

        except Exception as e:
            error_msg = str(e)
            self.logger.error(f"Error checking disclosures: {error_msg}")
            self.notifier.send_disclosure_error(
                source="Disclosure Check",
                error_message=error_msg
            )
            import traceback
            traceback.print_exc()

    def execute_pending_trades(self):
        """Execute pending trades if market is open"""
        if not self.pending_trades:
            return

        if not self.trade_engine.is_market_open():
            next_open = self.trade_engine.get_next_market_open()
            self.logger.info(f"Market closed. {len(self.pending_trades)} trades queued for {next_open.strftime('%Y-%m-%d %H:%M %Z')}")
            return

        self.logger.info(f"Market open. Executing {len(self.pending_trades)} pending trades...")

        # Process and execute trades
        executed_trades = self.trade_engine.process_congressional_trades(self.pending_trades)

        if executed_trades:
            self.logger.info(f"Successfully executed {len(executed_trades)} trades")

            # Record executed trades in database
            for exec_trade in executed_trades:
                self.db.add_executed_trade(
                    congressional_trade_id=None,
                    ticker=exec_trade.get('symbol', ''),
                    action=exec_trade.get('action', ''),
                    quantity=exec_trade.get('quantity', 0),
                    price=exec_trade.get('price', 0),
                    total_value=exec_trade.get('total_value', 0),
                    order_id=exec_trade.get('order_id', ''),
                    status=exec_trade.get('status', 'unknown')
                )

            # Save trade history
            self.trade_engine.save_trade_history()
        else:
            self.logger.info("No trades were executed")

        # Clear pending trades
        self.pending_trades = []

    def check_and_process_trades(self):
        """Main trading loop: check for new congressional trades and execute"""
        self.check_for_new_disclosures()
        self.execute_pending_trades()

    def _update_last_check_time(self):
        """Update last check time in memory and database"""
        self.last_check_time = datetime.now()
        self.db.set_state('last_check_time', self.last_check_time.isoformat())
    
    def run_once(self):
        """Run one complete check and trade cycle"""
        if not self.manual_mode:
            self.logger.info("Starting single trading cycle...")
        
        # Check if authenticated
        if not self.broker.is_authenticated:
            self.logger.error("Not authenticated. Please run authenticate() first.")
            return False
        
        # Run trading cycle
        self.check_and_process_trades()
        return True
    
    def run_scheduled(self):
        """Run on a schedule based on disclosure check times and market hours"""
        self.logger.info("Starting scheduled trading bot")
        self.logger.info(f"Disclosure checks at: {', '.join(self.disclosure_check_times)} ET")
        self.logger.info(f"Market hours: {self.config['trading']['marketOpen']} - {self.config['trading']['marketClose']} ET")

        if not self.broker.is_authenticated:
            self.logger.error("Not authenticated. Please run authenticate() first.")
            return False

        # Schedule disclosure checks at configured times (in ET)
        for check_time in self.disclosure_check_times:
            # Convert ET time to local time for scheduling
            local_time = self._et_to_local_time(check_time)
            schedule.every().day.at(local_time).do(self.check_for_new_disclosures)
            self.logger.info(f"  Scheduled disclosure check at {local_time} local ({check_time} ET)")

        # Schedule market open execution check (9:35 AM ET - 5 min after open)
        market_open_local = self._et_to_local_time("09:35")
        schedule.every().day.at(market_open_local).do(self.execute_pending_trades)
        self.logger.info(f"  Scheduled market open execution at {market_open_local} local (09:35 ET)")

        # Schedule token refresh every 90 minutes (tokens expire after 2 hours of inactivity)
        schedule.every(90).minutes.do(self.refresh_broker_tokens)
        self.logger.info("  Scheduled token refresh every 90 minutes")

        # Run initial check
        self.check_for_new_disclosures()

        self.is_running = True

        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check scheduler every minute

        except KeyboardInterrupt:
            self.logger.info("Shutting down scheduled bot...")
            self.is_running = False

    def _et_to_local_time(self, time_str):
        """Convert Eastern Time string (HH:MM) to local time string"""
        hour, minute = map(int, time_str.split(':'))
        et_tz = ZoneInfo('America/New_York')
        local_tz = datetime.now().astimezone().tzinfo

        # Create a datetime in ET for today
        now = datetime.now(et_tz)
        et_datetime = now.replace(hour=hour, minute=minute, second=0, microsecond=0)

        # Convert to local time
        local_datetime = et_datetime.astimezone(local_tz)
        return local_datetime.strftime('%H:%M')
    
    def get_status(self):
        """Get current bot status"""
        status = {
            'running': self.is_running,
            'broker': self.broker.BROKER_NAME,
            'authenticated': self.broker.is_authenticated,
            'last_check': self.last_check_time.isoformat() if self.last_check_time else None,
            'account_id': self.broker.account_id,
            'trade_history_count': len(self.trade_engine.trade_history)
        }

        # Add account balance if authenticated
        if status['authenticated']:
            balance = self.broker.get_account_balance()
            if balance:
                status['account_balance'] = {
                    'cash_available': balance['cash_available'],
                    'total_value': balance['total_value']
                }

        return status

    def send_test_notification(self):
        """Send a test notification with actual system state"""
        account_balance = None

        if self.broker.is_authenticated:
            balance = self.broker.get_account_balance()
            if balance:
                account_balance = balance['total_value']

        return self.notifier.send_test_message(
            broker_name=self.broker.BROKER_NAME,
            account_balance=account_balance,
            is_authenticated=self.broker.is_authenticated
        )
    
    def emergency_stop(self):
        """Emergency stop - cancel all pending orders and stop trading"""
        self.logger.warning("EMERGENCY STOP ACTIVATED")
        self.is_running = False
        self.manual_mode = True
        
        # Note: In production, you'd want to actually cancel pending orders
        # This would require additional E*TRADE API calls
        
        self.logger.info("Trading stopped. Manual mode enabled.")
    
    def interactive_mode(self):
        """Interactive mode for testing and manual control"""
        self.logger.info("Entering interactive mode")
        self.manual_mode = True

        while True:
            print("\n" + "="*60)
            print("    ClawBack - Congressional Trade Mirror")
            print("="*60)
            print(f"  1. Authenticate with {self.broker.BROKER_NAME}")
            print("  2. Check for new congressional trades (House + Senate)")
            print("  3. Run single trading cycle")
            print("  4. Get account status")
            print("  5. Get trade history")
            print("  6. View database statistics")
            print("  7. View unprocessed trades")
            print("  ─────────── Position Management ───────────")
            print("  8. View open positions & P/L")
            print("  9. Run stop-loss check")
            print(" 10. Check portfolio risk")
            print("  ─────────── Automation ───────────")
            print(f" 11. Start scheduled trading (checks at {', '.join(self.disclosure_check_times)} ET)")
            print(" 12. Export database to JSON")
            print(" 13. Emergency stop")
            print("  0. Exit")
            print("="*60)

            choice = input("\nSelect option: ").strip()

            if choice == '1':
                self.authenticate()
            elif choice == '2':
                print("\nFetching congressional trades (this may take a moment)...")
                trades = self.congress_tracker.get_recent_trades(days=30)
                print(f"\nFound {len(trades)} recent trades:")

                # Group by chamber
                house = [t for t in trades if t.get('chamber') != 'senate']
                senate = [t for t in trades if t.get('chamber') == 'senate']

                if house:
                    print(f"\n  House ({len(house)} trades):")
                    for trade in house[:5]:
                        rep = trade.get('representative', 'Unknown')[:20]
                        print(f"    {trade['transaction_date']}: {trade['transaction_type'].upper():8} "
                              f"{trade['ticker']:6} ${trade['amount']:>10,.0f}  ({rep})")

                if senate:
                    print(f"\n  Senate ({len(senate)} trades):")
                    for trade in senate[:5]:
                        rep = trade.get('representative', 'Unknown')[:20]
                        print(f"    {trade['transaction_date']}: {trade['transaction_type'].upper():8} "
                              f"{trade['ticker']:6} ${trade['amount']:>10,.0f}  ({rep})")

                # Store in database
                new_count = 0
                for trade in trades:
                    if self.db.add_congressional_trade(trade):
                        new_count += 1
                if new_count:
                    print(f"\n  Added {new_count} new trades to database")

            elif choice == '3':
                self.run_once()
            elif choice == '4':
                status = self.get_status()
                print("\nBot Status:")
                print(json.dumps(status, indent=2, default=str))
            elif choice == '5':
                summary = self.trade_engine.get_trade_summary()
                print("\nTrade Summary:")
                print(json.dumps(summary, indent=2))
            elif choice == '6':
                stats = self.db.get_trade_stats()
                print("\n" + "="*40)
                print("  Database Statistics")
                print("="*40)
                print(f"  Total trades discovered: {stats['total_discovered']}")
                print(f"  Trades executed: {stats['total_executed']}")
                print(f"  Total value traded: ${stats['total_value_traded']:,.2f}")
                print(f"\n  By chamber:")
                for chamber, count in stats.get('by_chamber', {}).items():
                    print(f"    {chamber or 'house'}: {count}")
                print(f"\n  Top tickers:")
                for ticker, count in stats.get('top_tickers', [])[:5]:
                    print(f"    {ticker}: {count} trades")
            elif choice == '7':
                unprocessed = self.db.get_unprocessed_trades()
                print(f"\nUnprocessed trades: {len(unprocessed)}")
                for trade in unprocessed[:10]:
                    print(f"  {trade['disclosure_date']}: {trade['transaction_type'].upper():8} "
                          f"{trade['ticker']:6} ${trade['amount']:>10,.0f}  ({trade['representative'][:20]})")
            elif choice == '8':
                # View open positions
                positions = self.trade_engine.get_position_summary()
                if not positions:
                    print("\nNo open positions")
                else:
                    print(f"\n{'='*80}")
                    print(f"  Open Positions ({len(positions)})")
                    print(f"{'='*80}")
                    print(f"  {'Symbol':<8} {'Qty':>6} {'Entry':>10} {'Current':>10} {'P/L':>10} {'P/L%':>8} {'Stop':>10} {'Days':>5}")
                    print(f"  {'-'*75}")
                    total_pnl = 0
                    for p in positions:
                        stop_str = f"${p['stop_loss']:.2f}" if p['stop_loss'] else 'N/A'
                        trail = '*' if p['trailing_active'] else ''
                        print(f"  {p['symbol']:<8} {p['quantity']:>6} ${p['entry_price']:>8.2f} "
                              f"${p['current_price']:>8.2f} ${p['unrealized_pnl']:>9.2f} "
                              f"{p['pnl_percent']:>7.1f}% {stop_str:>10}{trail} {p['days_held']:>5}")
                        total_pnl += p['unrealized_pnl']
                    print(f"  {'-'*75}")
                    print(f"  Total Unrealized P/L: ${total_pnl:,.2f}")
                    print(f"  * = Trailing stop active")

            elif choice == '9':
                # Run stop-loss check
                print("\nChecking stop-losses...")
                triggered = self.trade_engine.run_stop_loss_monitor()
                if triggered:
                    print(f"\nExecuted {len(triggered)} stop-loss orders:")
                    for t in triggered:
                        print(f"  SOLD {t['symbol']}: ${t['current_price']:.2f} (P/L: {t['pnl_percent']:.1f}%)")
                else:
                    print("No stop-losses triggered")

            elif choice == '10':
                # Check portfolio risk
                risk = self.trade_engine.check_portfolio_risk()
                print(f"\n{'='*50}")
                print(f"  Portfolio Risk Status: {risk['status'].upper()}")
                print(f"{'='*50}")
                if 'total_value' in risk:
                    print(f"  Total Value:      ${risk['total_value']:,.2f}")
                    print(f"  Peak Value:       ${risk['peak_value']:,.2f}")
                    print(f"  Drawdown:         {risk['drawdown']:.1f}%")
                    print(f"  Open Positions:   {risk['open_positions']}")
                    print(f"  Consecutive Loss: {risk['consecutive_losses']}")
                    if risk['warnings']:
                        print(f"\n  WARNINGS:")
                        for w in risk['warnings']:
                            print(f"    ⚠️  {w}")

            elif choice == '11':
                print(f"\nScheduled check times: {', '.join(self.disclosure_check_times)} ET")
                print("Trades execute at market open (9:35 AM ET)")
                confirm = input("Start scheduled trading? (y/n): ").strip().lower()
                if confirm == 'y':
                    self.run_scheduled()

            elif choice == '12':
                filepath = input("Export path (default: data/export.json): ").strip() or 'data/export.json'
                self.db.export_to_json(filepath)
                print(f"Exported to {filepath}")

            elif choice == '13':
                self.emergency_stop()

            elif choice == '0':
                print("Exiting interactive mode")
                break
            else:
                print("Invalid choice")

            input("\nPress Enter to continue...")

def main():
    """Main entry point"""
    print("\n🦞 ClawBack - Congressional Trade Mirror")
    print("="*50)
    
    # Check for config file
    config_path = 'config/config.json'
    if not os.path.exists(config_path):
        print(f"Error: Config file not found at {config_path}")
        print("Please ensure config.json exists in the config directory")
        return
    
    # Create bot instance
    bot = TradingBot(config_path)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == 'auth':
            verifier = sys.argv[2] if len(sys.argv) > 2 else None
            bot.authenticate(verifier)
        elif sys.argv[1] == 'run':
            bot.run_once()
        elif sys.argv[1] == 'schedule':
            bot.run_scheduled()
        elif sys.argv[1] == 'interactive':
            bot.interactive_mode()
        elif sys.argv[1] == 'status':
            status = bot.get_status()
            print(json.dumps(status, indent=2, default=str))
        else:
            print(f"Unknown command: {sys.argv[1]}")
            print("Available commands: auth, run, schedule [hours], interactive, status")
    else:
        # Default to interactive mode
        bot.interactive_mode()

if __name__ == "__main__":
    main()