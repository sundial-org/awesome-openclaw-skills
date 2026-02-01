"""
Integration between congressional trade data and broker trading bot
Uses the adapter pattern for broker-agnostic integration
"""
import json
import logging
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from ..broker_adapter import get_broker_adapter

logger = logging.getLogger(__name__)


def get_local_timestamp():
    """Get current timestamp formatted in local timezone"""
    return datetime.now().astimezone().strftime('%Y-%m-%d %H:%M:%S %Z')


class BrokerIntegration:
    """Integrates congressional trade alerts with broker trading bot (adapter pattern)"""

    def __init__(self, config_path=None):
        self.config_path = config_path or "../config/config.json"
        self.congress_config_path = "../config/congress_config.json"

        # Load configurations
        self.config = self.load_config(self.config_path)
        self.congress_config = self.load_config(self.congress_config_path)

        # Paths - use broker-agnostic "notifications" directory
        self.project_root = Path(__file__).parent.parent.parent
        self.notifications_dir = self.project_root / "data" / "notifications"
        self.notifications_dir.mkdir(parents=True, exist_ok=True)

        # Integration state
        self.processed_alerts = set()
        self.load_processed_alerts()

        # Initialize broker adapter (lazy - only when needed)
        self._broker = None

        # Get broker name from config
        self.broker_name = self.config.get('broker', {}).get('adapter', 'unknown').upper()

        logger.info(f"Broker integration initialized (adapter: {self.broker_name})")

    @property
    def broker(self):
        """Lazy initialization of broker adapter"""
        if self._broker is None:
            try:
                self._broker = get_broker_adapter(self.config)
                logger.info(f"Initialized {self._broker.BROKER_NAME} adapter")
            except Exception as e:
                logger.error(f"Failed to initialize broker adapter: {e}")
        return self._broker

    def load_config(self, config_path):
        """Load configuration from file"""
        try:
            full_path = Path(__file__).parent / config_path
            with open(full_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config {config_path}: {e}")
            return {}

    def load_processed_alerts(self):
        """Load previously processed alerts"""
        try:
            state_file = self.notifications_dir / "processed_alerts.json"
            if state_file.exists():
                with open(state_file, 'r') as f:
                    data = json.load(f)
                    self.processed_alerts = set(data.get("processed_alerts", []))

                # Clean old entries (older than 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                self.processed_alerts = {
                    alert_id for alert_id in self.processed_alerts
                    if self.parse_alert_date(alert_id) > cutoff_date
                }

                logger.info(f"Loaded {len(self.processed_alerts)} processed alerts")

        except Exception as e:
            logger.error(f"Error loading processed alerts: {e}")
            self.processed_alerts = set()

    def save_processed_alerts(self):
        """Save processed alerts to file"""
        try:
            state_file = self.notifications_dir / "processed_alerts.json"
            data = {
                "processed_alerts": list(self.processed_alerts),
                "last_updated": datetime.now().astimezone().isoformat()
            }

            with open(state_file, 'w') as f:
                json.dump(data, f, indent=2)

            logger.debug(f"Saved {len(self.processed_alerts)} processed alerts")

        except Exception as e:
            logger.error(f"Error saving processed alerts: {e}")

    def parse_alert_date(self, alert_id):
        """Parse date from alert ID"""
        try:
            # Alert ID format: alert_YYYYMMDD_HHMMSS
            if alert_id.startswith("alert_"):
                date_str = alert_id[6:20]  # Extract YYYYMMDD_HHMMSS
                return datetime.strptime(date_str, "%Y%m%d_%H%M%S")
        except (ValueError, IndexError):
            pass
        return datetime.now() - timedelta(days=365)  # Default to old date

    def check_for_new_alerts(self):
        """Check for new congressional trade alerts"""
        try:
            if not self.notifications_dir.exists():
                logger.info("No notifications directory found")
                return []

            new_alerts = []

            # Look for alert files
            for alert_file in self.notifications_dir.glob("alert_*.json"):
                alert_id = alert_file.stem

                # Skip if already processed
                if alert_id in self.processed_alerts:
                    continue

                # Load alert data
                try:
                    with open(alert_file, 'r') as f:
                        alert_data = json.load(f)

                    # Check if it's a congressional trade alert
                    if alert_data.get("type") == "congressional_trade":
                        new_alerts.append({
                            "alert_id": alert_id,
                            "file_path": str(alert_file),
                            "data": alert_data
                        })

                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(f"Error loading alert file {alert_file}: {e}")
                    continue

            logger.info(f"Found {len(new_alerts)} new congressional trade alerts")
            return new_alerts

        except Exception as e:
            logger.error(f"Error checking for new alerts: {e}")
            return []

    def process_alert_for_trading(self, alert):
        """Process a congressional trade alert for potential trading"""
        try:
            alert_id = alert["alert_id"]
            alert_data = alert["data"]
            trade = alert_data.get("trade", {})

            logger.info(f"Processing alert {alert_id}: {trade.get('politician')} - {trade.get('ticker')}")

            # Extract trade information
            politician = trade.get("politician", "")
            ticker = trade.get("ticker", "").upper()
            transaction_type = trade.get("transaction_type", "").lower()
            amount = trade.get("amount", 0)

            # Skip if missing critical information
            if not ticker or ticker == "N/A":
                logger.warning(f"Skipping alert {alert_id}: No ticker symbol")
                return False

            # Determine trading action based on transaction type
            if transaction_type in ["buy", "purchase"]:
                action = "BUY"
                reason = f"Congressional buy: {politician} purchased ${amount:,.0f} of {ticker}"
            elif transaction_type in ["sell", "sale"]:
                action = "SELL"
                reason = f"Congressional sell: {politician} sold ${amount:,.0f} of {ticker}"
            else:
                logger.warning(f"Skipping alert {alert_id}: Unknown transaction type '{transaction_type}'")
                return False

            # Check trade size threshold
            min_trade_size = self.congress_config.get("alerting", {}).get("minimum_trade_size_alert", 50000)
            if amount < min_trade_size:
                logger.info(f"Skipping alert {alert_id}: Trade amount ${amount:,.0f} below threshold ${min_trade_size:,.0f}")
                return False

            # Create trading recommendation
            recommendation = {
                "alert_id": alert_id,
                "timestamp": datetime.now().astimezone().isoformat(),
                "ticker": ticker,
                "action": action,
                "reason": reason,
                "source": "congressional_trade",
                "politician": politician,
                "trade_amount": amount,
                "trade_date": trade.get("transaction_date"),
                "confidence": self.calculate_confidence(trade),
                "broker": self.broker_name
            }

            # Save recommendation
            self.save_trading_recommendation(recommendation)

            # Mark as processed
            self.processed_alerts.add(alert_id)
            self.save_processed_alerts()

            logger.info(f"Created trading recommendation for {ticker}: {action}")
            return True

        except Exception as e:
            logger.error(f"Error processing alert {alert.get('alert_id', 'unknown')}: {e}")
            return False

    def calculate_confidence(self, trade):
        """Calculate confidence score for a trade recommendation"""
        confidence = 0.5  # Base confidence

        # Adjust based on trade size
        amount = trade.get("amount", 0)
        if amount >= 1000000:  # $1M+
            confidence += 0.3
        elif amount >= 500000:  # $500K+
            confidence += 0.2
        elif amount >= 100000:  # $100K+
            confidence += 0.1

        # Adjust based on politician
        politician = trade.get("politician", "").lower()
        if "pelosi" in politician:
            confidence += 0.2  # Nancy Pelosi trades are closely watched
        elif any(name in politician for name in ["mcconnell", "schumer", "mccarthy"]):
            confidence += 0.1

        # Adjust based on recency
        trade_date = trade.get("transaction_date")
        if trade_date:
            try:
                if isinstance(trade_date, str):
                    trade_date = datetime.fromisoformat(trade_date.replace('Z', '+00:00'))

                days_old = (datetime.now() - trade_date).days
                if days_old <= 7:
                    confidence += 0.1
                elif days_old > 30:
                    confidence -= 0.2
            except (ValueError, TypeError):
                pass

        # Cap confidence between 0.1 and 0.9
        confidence = max(0.1, min(0.9, confidence))

        return round(confidence, 2)

    def save_trading_recommendation(self, recommendation):
        """Save trading recommendation to file"""
        try:
            # Create recommendations directory
            rec_dir = self.project_root / "data" / "trading_recommendations"
            rec_dir.mkdir(parents=True, exist_ok=True)

            # Save with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"congress_{recommendation['ticker']}_{timestamp}.json"
            filepath = rec_dir / filename

            with open(filepath, 'w') as f:
                json.dump(recommendation, f, indent=2)

            # Also update latest recommendations file
            latest_file = rec_dir / "latest_congressional_recommendations.json"
            recommendations = []

            if latest_file.exists():
                try:
                    with open(latest_file, 'r') as f:
                        recommendations = json.load(f)
                except json.JSONDecodeError:
                    recommendations = []

            # Add new recommendation
            recommendations.append(recommendation)

            # Keep only last 50 recommendations
            if len(recommendations) > 50:
                recommendations = recommendations[-50:]

            with open(latest_file, 'w') as f:
                json.dump(recommendations, f, indent=2)

            logger.info(f"Saved trading recommendation to {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error saving trading recommendation: {e}")
            return False

    def process_all_new_alerts(self):
        """Process all new congressional trade alerts"""
        new_alerts = self.check_for_new_alerts()

        if not new_alerts:
            logger.info("No new alerts to process")
            return []

        processed = []
        for alert in new_alerts:
            if self.process_alert_for_trading(alert):
                processed.append(alert["alert_id"])

        logger.info(f"Processed {len(processed)} new alerts")
        return processed

    def get_trading_recommendations(self, ticker=None, limit=10):
        """Get recent trading recommendations"""
        try:
            rec_dir = self.project_root / "data" / "trading_recommendations"
            latest_file = rec_dir / "latest_congressional_recommendations.json"

            if not latest_file.exists():
                return []

            with open(latest_file, 'r') as f:
                recommendations = json.load(f)

            # Filter by ticker if specified
            if ticker:
                recommendations = [r for r in recommendations if r.get("ticker") == ticker.upper()]

            # Sort by timestamp (newest first)
            recommendations.sort(key=lambda x: x.get("timestamp", ""), reverse=True)

            # Apply limit
            return recommendations[:limit]

        except Exception as e:
            logger.error(f"Error getting trading recommendations: {e}")
            return []

    def run_continuous_monitoring(self, interval_seconds=300):
        """Run continuous monitoring for new alerts"""
        logger.info(f"Starting continuous monitoring (checking every {interval_seconds} seconds)")

        try:
            while True:
                self.process_all_new_alerts()
                time.sleep(interval_seconds)

        except KeyboardInterrupt:
            logger.info("Monitoring stopped by user")
        except Exception as e:
            logger.error(f"Monitoring error: {e}")

    def get_integration_stats(self):
        """Get integration statistics"""
        stats = {
            "broker": self.broker_name,
            "processed_alerts": len(self.processed_alerts),
            "notifications_directory": str(self.notifications_dir),
            "recommendations_directory": str(self.project_root / "data" / "trading_recommendations"),
            "config_loaded": bool(self.config and self.congress_config)
        }

        # Count recommendation files
        rec_dir = self.project_root / "data" / "trading_recommendations"
        if rec_dir.exists():
            congress_files = list(rec_dir.glob("congress_*.json"))
            stats["total_recommendations"] = len(congress_files)

        return stats


def main():
    """Main entry point for broker integration"""
    import argparse

    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    parser = argparse.ArgumentParser(description="Broker Integration for Congressional Trade Data")
    parser.add_argument("command", choices=["process", "monitor", "recommendations", "stats"],
                       help="Command to execute")
    parser.add_argument("--ticker", "-t", help="Filter by ticker symbol")
    parser.add_argument("--limit", "-l", type=int, default=10,
                       help="Limit number of recommendations")
    parser.add_argument("--interval", "-i", type=int, default=300,
                       help="Monitoring interval in seconds")

    args = parser.parse_args()

    # Initialize integration
    integration = BrokerIntegration()

    if args.command == "process":
        # Process new alerts once
        processed = integration.process_all_new_alerts()
        print(f"Processed {len(processed)} new alerts")

    elif args.command == "monitor":
        # Run continuous monitoring
        integration.run_continuous_monitoring(args.interval)

    elif args.command == "recommendations":
        # Get trading recommendations
        recommendations = integration.get_trading_recommendations(args.ticker, args.limit)

        if not recommendations:
            print("No trading recommendations found")
        else:
            print(f"\n📊 Congressional Trading Recommendations ({len(recommendations)} found):")
            print("="*80)

            for i, rec in enumerate(recommendations, 1):
                print(f"\n{i}. {rec.get('ticker')} - {rec.get('action')}")
                print(f"   Reason: {rec.get('reason')}")
                print(f"   Confidence: {rec.get('confidence', 0.5):.0%}")
                print(f"   Politician: {rec.get('politician')}")
                print(f"   Trade Amount: ${rec.get('trade_amount', 0):,.0f}")
                print(f"   Date: {rec.get('timestamp', 'Unknown')}")
                print(f"   Broker: {rec.get('broker', 'Unknown')}")

            print("\n" + "="*80)

    elif args.command == "stats":
        # Get integration statistics
        stats = integration.get_integration_stats()

        print(f"\n📈 Broker Integration Statistics:")
        print("="*60)
        print(f"Broker Adapter: {stats['broker']}")
        print(f"Processed Alerts: {stats['processed_alerts']}")
        print(f"Total Recommendations: {stats.get('total_recommendations', 0)}")
        print(f"Notifications Directory: {stats['notifications_directory']}")
        print(f"Recommendations Directory: {stats['recommendations_directory']}")
        print(f"Config Loaded: {'✅' if stats['config_loaded'] else '❌'}")
        print("="*60)

    else:
        print(f"Unknown command: {args.command}")
        return False

    return True


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
