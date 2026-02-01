"""
Alert manager for congressional trade alerts
"""
import json
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests

logger = logging.getLogger(__name__)

class AlertManager:
    """Manages alerts for congressional trades"""
    
    def __init__(self, config):
        self.config = config
        self.alert_config = config.get_alert_config()
        self.storage_config = config.get_storage_config()
        
        # Alert history tracking
        self.sent_alerts = set()
        self.load_alert_history()
        
        logger.info("Alert manager initialized")
    
    def load_alert_history(self):
        """Load previously sent alerts"""
        try:
            data_dir = self.storage_config.get("data_directory", "data/congress_trades")
            history_file = os.path.join(data_dir, "alert_history.json")
            
            if os.path.exists(history_file):
                with open(history_file, 'r') as f:
                    history = json.load(f)
                
                # Convert list to set for faster lookups
                self.sent_alerts = set(history.get("sent_alerts", []))
                
                # Clean old alerts (older than 30 days)
                cutoff_date = datetime.now() - timedelta(days=30)
                self.sent_alerts = {
                    alert_id for alert_id in self.sent_alerts
                    if self.parse_alert_date(alert_id) > cutoff_date
                }
                
                logger.info(f"Loaded {len(self.sent_alerts)} recent alerts from history")
                
        except Exception as e:
            logger.error(f"Error loading alert history: {e}")
            self.sent_alerts = set()
    
    def save_alert_history(self):
        """Save alert history to file"""
        try:
            data_dir = self.storage_config.get("data_directory", "data/congress_trades")
            os.makedirs(data_dir, exist_ok=True)
            
            history_file = os.path.join(data_dir, "alert_history.json")
            
            history = {
                "sent_alerts": list(self.sent_alerts),
                "last_updated": datetime.now().isoformat()
            }
            
            with open(history_file, 'w') as f:
                json.dump(history, f, indent=2)
            
            logger.debug(f"Saved alert history with {len(self.sent_alerts)} alerts")
            
        except Exception as e:
            logger.error(f"Error saving alert history: {e}")
    
    def parse_alert_date(self, alert_id):
        """Parse date from alert ID"""
        try:
            # Alert ID format: politician_ticker_date_type_amount
            parts = alert_id.split('_')
            if len(parts) >= 3:
                date_str = parts[2]
                return datetime.strptime(date_str, "%Y%m%d")
        except (ValueError, IndexError):
            pass
        return datetime.now() - timedelta(days=365)  # Default to old date
    
    def generate_alert_id(self, trade):
        """Generate unique alert ID for a trade"""
        try:
            politician = trade.get("politician", "").replace(" ", "_").replace("-", "_")
            ticker = trade.get("ticker", "").replace(" ", "_")
            
            # Format date
            trans_date = trade.get("transaction_date", "")
            if isinstance(trans_date, datetime):
                date_str = trans_date.strftime("%Y%m%d")
            else:
                date_str = str(trans_date).replace("-", "").replace("/", "")[:8]
            
            trans_type = trade.get("transaction_type", "").lower()
            amount = int(trade.get("amount", 0))
            
            alert_id = f"{politician}_{ticker}_{date_str}_{trans_type}_{amount}"
            return alert_id
            
        except Exception as e:
            logger.error(f"Error generating alert ID: {e}")
            return f"alert_{datetime.now().timestamp()}"
    
    def should_alert(self, trade):
        """Determine if a trade should trigger an alert"""
        if not self.alert_config.get("enabled", True):
            return False
        
        # Check if we've already alerted for this trade
        alert_id = self.generate_alert_id(trade)
        if alert_id in self.sent_alerts:
            return False
        
        # Check minimum trade size
        min_size = self.alert_config.get("minimum_trade_size_alert", 50000)
        if trade.get("amount", 0) < min_size:
            return False
        
        # Check transaction type
        trans_type = trade.get("transaction_type", "").lower()
        if trans_type in ["buy", "purchase"] and not self.alert_config.get("alert_on_buys", True):
            return False
        if trans_type in ["sell", "sale"] and not self.alert_config.get("alert_on_sells", True):
            return False
        
        # Check if trade is recent (within last 7 days)
        trans_date = trade.get("transaction_date")
        if isinstance(trans_date, str):
            try:
                trans_date = datetime.fromisoformat(trans_date.replace('Z', '+00:00'))
            except ValueError:
                trans_date = None
        
        if trans_date and (datetime.now() - trans_date).days > 7:
            return False
        
        return True
    
    def format_alert_message(self, trade):
        """Format trade information into alert message"""
        politician = trade.get("politician", "Unknown")
        ticker = trade.get("ticker", "N/A")
        asset_name = trade.get("asset_name", "")
        trans_type = trade.get("transaction_type", "").upper()
        amount = trade.get("amount", 0)
        trans_date = trade.get("transaction_date", "")
        source = trade.get("source", "Unknown")
        
        # Format date
        if isinstance(trans_date, datetime):
            date_str = trans_date.strftime("%Y-%m-%d")
        else:
            date_str = str(trans_date)
        
        # Format amount
        if amount >= 1000000:
            amount_str = f"${amount/1000000:.2f}M"
        elif amount >= 1000:
            amount_str = f"${amount/1000:.1f}K"
        else:
            amount_str = f"${amount:,.0f}"
        
        message = f"""
🚨 **CONGRESSIONAL TRADE ALERT** 🚨

**Politician:** {politician}
**Action:** {trans_type} {ticker} ({asset_name})
**Amount:** {amount_str}
**Date:** {date_str}
**Source:** {source}

**Details:**
- Ticker: {ticker}
- Transaction Type: {trans_type}
- Reported Amount: ${amount:,.2f}
- Data Source: {source}

This trade exceeds the alert threshold of ${self.alert_config.get('minimum_trade_size_alert', 50000):,.0f}.
"""
        
        return message.strip()
    
    def send_telegram_alert(self, message):
        """Send alert via Telegram bot"""
        try:
            bot_token = self.alert_config.get("telegram_bot_token", "")
            chat_id = self.alert_config.get("telegram_chat_id", "")
            
            if not bot_token or not chat_id:
                logger.warning("Telegram bot not configured")
                return False
            
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "Markdown",
                "disable_web_page_preview": True
            }
            
            response = requests.post(url, json=payload, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram alert sent successfully")
                return True
            else:
                logger.error(f"Telegram API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
            return False
    
    def send_email_alert(self, message, subject="Congressional Trade Alert"):
        """Send alert via email"""
        try:
            if not self.alert_config.get("email_alerts", False):
                return False
            
            email_from = self.alert_config.get("email_from", "")
            email_to = self.alert_config.get("email_to", "")
            smtp_server = self.alert_config.get("smtp_server", "")
            
            if not all([email_from, email_to, smtp_server]):
                logger.warning("Email alert configuration incomplete")
                return False
            
            # Create message
            msg = MIMEMultipart()
            msg['From'] = email_from
            msg['To'] = email_to
            msg['Subject'] = subject
            
            # Add HTML and plain text versions
            html_content = message.replace('\n', '<br>')
            
            msg.attach(MIMEText(message, 'plain'))
            msg.attach(MIMEText(html_content, 'html'))
            
            # Send email
            with smtplib.SMTP(smtp_server) as server:
                server.send_message(msg)
            
            logger.info("Email alert sent successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def send_broker_integration_alert(self, trade):
        """Send alert to broker integration system (adapter pattern)"""
        try:
            alert_data = {
                "type": "congressional_trade",
                "timestamp": datetime.now().astimezone().isoformat(),
                "trade": trade,
                "action": "review_for_trading"
            }

            # Save to notifications directory for broker integration to pick up
            data_dir = self.storage_config.get("data_directory", "data")
            notifications_dir = os.path.join(data_dir, "notifications")
            os.makedirs(notifications_dir, exist_ok=True)

            filename = f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = os.path.join(notifications_dir, filename)

            with open(filepath, 'w') as f:
                json.dump(alert_data, f, indent=2)

            logger.info(f"Broker integration alert saved: {filepath}")

            # Also create a summary file for easy reading
            summary_file = os.path.join(notifications_dir, "latest_alert.txt")
            with open(summary_file, 'w') as f:
                f.write(self.format_alert_message(trade))

            return True

        except Exception as e:
            logger.error(f"Error sending broker integration alert: {e}")
            return False
    
    def process_trades_for_alerts(self, trades):
        """Process trades and send alerts for qualifying ones"""
        if not self.alert_config.get("enabled", True):
            logger.info("Alerting disabled")
            return []
        
        alerts_sent = []
        
        for trade in trades:
            try:
                if self.should_alert(trade):
                    alert_id = self.generate_alert_id(trade)
                    
                    # Format alert message
                    message = self.format_alert_message(trade)
                    
                    # Send alerts through configured channels
                    sent = False
                    
                    # Telegram
                    if self.alert_config.get("telegram_bot_token"):
                        if self.send_telegram_alert(message):
                            sent = True
                    
                    # Email
                    if self.alert_config.get("email_alerts", False):
                        if self.send_email_alert(message):
                            sent = True
                    
                    # E*TRADE integration
                    if self.send_broker_integration_alert(trade):
                        sent = True
                    
                    if sent:
                        # Mark as sent
                        self.sent_alerts.add(alert_id)
                        alerts_sent.append(trade)
                        
                        logger.info(f"Alert sent for {trade.get('politician')} - {trade.get('ticker')}")
                    
            except Exception as e:
                logger.error(f"Error processing alert for trade: {e}")
                continue
        
        # Save updated alert history
        if alerts_sent:
            self.save_alert_history()
        
        logger.info(f"Sent {len(alerts_sent)} alerts")
        return alerts_sent
    
    def get_alert_stats(self):
        """Get alert statistics"""
        stats = {
            "total_alerts_sent": len(self.sent_alerts),
            "alerting_enabled": self.alert_config.get("enabled", True),
            "channels": {
                "telegram": bool(self.alert_config.get("telegram_bot_token")),
                "email": self.alert_config.get("email_alerts", False),
                "broker_integration": True  # Always enabled
            },
            "thresholds": {
                "minimum_trade_size": self.alert_config.get("minimum_trade_size_alert", 50000),
                "alert_on_buys": self.alert_config.get("alert_on_buys", True),
                "alert_on_sells": self.alert_config.get("alert_on_sells", True)
            }
        }
        
        return stats