"""
Main entry point for congressional trade data collection system
"""
import argparse
import json
import logging
import os
import signal
import sys
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from congress_data.config import CongressConfig
from congress_data.data_collector import CongressDataCollector
from congress_data.alert_manager import AlertManager
from congress_data.cron_scheduler import CongressCronScheduler

# Configure logging
def setup_logging(level=logging.INFO):
    """Set up logging configuration"""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory
    logs_dir = "logs/congress_data"
    os.makedirs(logs_dir, exist_ok=True)
    
    # Log file with date
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(logs_dir, f"congress_{date_str}.log")
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format=log_format,
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Reduce verbosity for some libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("schedule").setLevel(logging.WARNING)

class CongressDataApp:
    """Main application class for congressional data collection"""
    
    def __init__(self, config_path=None):
        self.config_path = config_path
        self.config = None
        self.data_collector = None
        self.alert_manager = None
        self.scheduler = None
        
        # Signal handling
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle termination signals"""
        logger = logging.getLogger(__name__)
        logger.info(f"Received signal {signum}, shutting down...")
        self.shutdown()
        sys.exit(0)
    
    def initialize(self):
        """Initialize the application"""
        logger = logging.getLogger(__name__)
        
        try:
            # Load configuration
            self.config = CongressConfig(self.config_path)
            logger.info(f"Configuration loaded from {self.config.config_path}")
            
            # Initialize components
            self.data_collector = CongressDataCollector(self.config)
            self.alert_manager = AlertManager(self.config)
            self.scheduler = CongressCronScheduler(self.config, self.data_collector, self.alert_manager)
            
            logger.info("Congressional data application initialized")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            return False
    
    def run_once(self):
        """Run data collection once"""
        logger = logging.getLogger(__name__)
        
        if not self.initialize():
            return False
        
        try:
            logger.info("Running one-time data collection")
            result = self.scheduler.run_once()
            
            if result.get("success", False):
                logger.info(f"Collection successful: {result.get('trades_collected', 0)} trades, {result.get('alerts_sent', 0)} alerts")
                return True
            else:
                logger.error(f"Collection failed: {result.get('error', 'Unknown error')}")
                return False
                
        except Exception as e:
            logger.error(f"Error during one-time collection: {e}")
            return False
    
    def run_scheduler(self):
        """Run the scheduled data collection"""
        logger = logging.getLogger(__name__)
        
        if not self.initialize():
            return False
        
        try:
            logger.info("Starting scheduled data collection")
            
            # Start the scheduler
            if not self.scheduler.start():
                logger.error("Failed to start scheduler")
                return False
            
            # Keep main thread alive
            logger.info("Scheduler started. Press Ctrl+C to stop.")
            
            try:
                while self.scheduler.running:
                    # Check every 5 seconds
                    import time
                    time.sleep(5)
                    
                    # Periodically save stats and clean up
                    if datetime.now().minute % 30 == 0:  # Every 30 minutes
                        self.scheduler.save_stats()
                        self.scheduler.cleanup_old_data()
                        
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
            finally:
                self.shutdown()
            
            return True
            
        except Exception as e:
            logger.error(f"Error running scheduler: {e}")
            self.shutdown()
            return False
    
    def show_stats(self):
        """Show application statistics"""
        logger = logging.getLogger(__name__)
        
        if not self.initialize():
            return False
        
        try:
            # Get scheduler stats
            scheduler_stats = self.scheduler.get_scheduler_stats()
            
            # Get alert stats
            alert_stats = self.alert_manager.get_alert_stats()
            
            # Get collection stats
            collection_stats = self.data_collector.get_collection_stats()
            
            # Print stats
            print("\n" + "="*60)
            print("CONGRESSIONAL DATA COLLECTION STATISTICS")
            print("="*60)
            
            print(f"\n📊 SCHEDULER STATS:")
            print(f"  Runs: {scheduler_stats['runs']}")
            print(f"  Successful: {scheduler_stats['successful_runs']}")
            print(f"  Failed: {scheduler_stats['failed_runs']}")
            print(f"  Success Rate: {scheduler_stats.get('success_rate', 0):.1f}%")
            print(f"  Uptime: {scheduler_stats.get('uptime_human', 'N/A')}")
            print(f"  Last Run: {scheduler_stats.get('last_run', 'Never')}")
            print(f"  Last Success: {scheduler_stats.get('last_success', 'Never')}")
            
            print(f"\n📈 COLLECTION STATS:")
            print(f"  Total Trades Collected: {scheduler_stats['total_trades_collected']}")
            print(f"  Total Alerts Sent: {scheduler_stats['total_alerts_sent']}")
            print(f"  Failed Sources: {', '.join(collection_stats.get('failed_sources', [])) or 'None'}")
            
            print(f"\n🔔 ALERT STATS:")
            print(f"  Alerting Enabled: {alert_stats['alerting_enabled']}")
            print(f"  Total Alerts Sent: {alert_stats['total_alerts_sent']}")
            print(f"  Minimum Trade Size: ${alert_stats['thresholds']['minimum_trade_size']:,.0f}")
            print(f"  Channels:")
            print(f"    - Telegram: {'✅' if alert_stats['channels']['telegram'] else '❌'}")
            print(f"    - Email: {'✅' if alert_stats['channels']['email'] else '❌'}")
            print(f"    - E*TRADE Integration: {'✅' if alert_stats['channels']['broker_integration'] else '❌'}")
            
            print(f"\n⚙️  CONFIGURATION:")
            cron_config = self.config.get_cron_config()
            print(f"  Schedule: {cron_config.get('schedule', 'N/A')}")
            print(f"  Timezone: {cron_config.get('timezone', 'N/A')}")
            print(f"  Run on Startup: {cron_config.get('run_on_startup', False)}")
            
            if scheduler_stats.get('next_scheduled_run'):
                print(f"  Next Run: {scheduler_stats['next_scheduled_run']}")
            
            print("\n" + "="*60)
            
            # Save stats to file
            stats_data = {
                "timestamp": datetime.now().isoformat(),
                "scheduler_stats": scheduler_stats,
                "alert_stats": alert_stats,
                "collection_stats": collection_stats
            }
            
            data_dir = self.config.get_storage_config().get("data_directory", "data/congress_trades")
            stats_file = os.path.join(data_dir, "current_stats.json")
            
            with open(stats_file, 'w') as f:
                json.dump(stats_data, f, indent=2)
            
            logger.info(f"Statistics saved to {stats_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error showing stats: {e}")
            return False
    
    def test_alerts(self):
        """Test alert system with sample data"""
        logger = logging.getLogger(__name__)
        
        if not self.initialize():
            return False
        
        try:
            logger.info("Testing alert system")
            
            # Create sample trade data
            sample_trade = {
                "politician": "Nancy Pelosi-P000197",
                "transaction_date": datetime.now().isoformat(),
                "ticker": "AAPL",
                "asset_name": "Apple Inc.",
                "transaction_type": "buy",
                "amount": 1000000,
                "source": "test",
                "filing_date": datetime.now().isoformat()
            }
            
            # Test alert generation
            if self.alert_manager.should_alert(sample_trade):
                logger.info("Sample trade would trigger alert")
                
                # Send test alerts
                message = self.alert_manager.format_alert_message(sample_trade)
                print(f"\n📨 TEST ALERT MESSAGE:\n{message}\n")
                
                # Test Telegram
                if self.alert_manager.alert_config.get("telegram_bot_token"):
                    logger.info("Testing Telegram alert...")
                    if self.alert_manager.send_telegram_alert("[TEST] " + message):
                        print("✅ Telegram alert sent successfully")
                    else:
                        print("❌ Telegram alert failed")
                
                # Test email
                if self.alert_manager.alert_config.get("email_alerts", False):
                    logger.info("Testing email alert...")
                    if self.alert_manager.send_email_alert("[TEST] " + message, "[TEST] Congressional Trade Alert"):
                        print("✅ Email alert sent successfully")
                    else:
                        print("❌ Email alert failed")
                
                # Test E*TRADE integration
                logger.info("Testing E*TRADE integration...")
                if self.alert_manager.send_broker_integration_alert(sample_trade):
                    print("✅ E*TRADE integration alert saved")
                else:
                    print("❌ E*TRADE integration alert failed")
                
                print("\n✅ Alert system test completed")
                return True
            else:
                logger.warning("Sample trade would not trigger alert (check thresholds)")
                return False
                
        except Exception as e:
            logger.error(f"Error testing alerts: {e}")
            return False
    
    def shutdown(self):
        """Shut down the application"""
        logger = logging.getLogger(__name__)
        
        try:
            if self.scheduler:
                self.scheduler.stop()
            
            # Save final stats
            if self.scheduler:
                self.scheduler.save_stats()
            
            logger.info("Application shutdown complete")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Congressional Trade Data Collection System")
    parser.add_argument("command", choices=["run", "once", "stats", "test-alerts", "config"],
                       help="Command to execute")
    parser.add_argument("--config", "-c", default="config/congress_config.json",
                       help="Path to configuration file")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Enable verbose logging")
    
    args = parser.parse_args()
    
    # Set up logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(log_level)
    
    logger = logging.getLogger(__name__)
    logger.info(f"Starting congressional data collection system with command: {args.command}")
    
    # Create application
    app = CongressDataApp(args.config)
    
    # Execute command
    if args.command == "run":
        success = app.run_scheduler()
    elif args.command == "once":
        success = app.run_once()
    elif args.command == "stats":
        success = app.show_stats()
    elif args.command == "test-alerts":
        success = app.test_alerts()
    elif args.command == "config":
        # Show configuration
        config = CongressConfig(args.config)
        print(json.dumps(config.config, indent=2))
        success = True
    else:
        logger.error(f"Unknown command: {args.command}")
        success = False
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()