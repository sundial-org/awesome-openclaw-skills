"""
Configuration for congressional trade data collection
"""
import json
import os

class CongressConfig:
    """Configuration for congressional trade data collection"""

    DEFAULT_CONFIG = {
        "sources": {
            "senate": {
                "enabled": True,
                "url": "https://efdsearch.senate.gov/search/",
                "check_interval_hours": 24,
                "min_trade_amount": 1000,
                "data_dir": "data/senate"
            },
            "house": {
                "enabled": True,
                "url": "https://disclosures-clerk.house.gov/FinancialDisclosure",
                "check_interval_hours": 24,
                "min_trade_amount": 1000,
                "data_dir": "data/house"
            }
        },
        "politicians": {
            "track_all": False,
            "specific_politicians": [
                "Nancy Pelosi",
                "Dan Crenshaw",
                "Tommy Tuberville",
                "Marjorie Taylor Greene"
            ],
            "minimum_trade_size": 10000,
            "tracked_positions": ["Senator", "Representative", "Speaker"]
        },
        "alerting": {
            "enabled": True,
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "email_alerts": False,
            "email_from": "",
            "email_to": "",
            "smtp_server": "",
            "minimum_trade_size_alert": 50000,
            "alert_on_buys": True,
            "alert_on_sells": True
        },
        "storage": {
            "data_directory": "data/congress_trades",
            "max_days_to_keep": 90,
            "backup_enabled": True,
            "backup_directory": "data/backups"
        },
        "cron": {
            "enabled": True,
            "schedule": "0 9 * * 1-5",  # 9 AM Monday-Friday
            "timezone": "America/New_York",
            "run_on_startup": True
        }
    }

    def __init__(self, config_path=None):
        self.config_path = config_path or "config/congress_config.json"
        self.config = self.load_config()

    def load_config(self):
        """Load configuration from file or use defaults"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    loaded_config = json.load(f)

                # Merge with defaults
                config = self.deep_merge(self.DEFAULT_CONFIG, loaded_config)
                return config
            else:
                # Create directory if it doesn't exist
                os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
                # Save default config
                self.save_config(self.DEFAULT_CONFIG)
                return self.DEFAULT_CONFIG

        except Exception as e:
            print(f"Error loading config: {e}")
            return self.DEFAULT_CONFIG

    def save_config(self, config=None):
        """Save configuration to file"""
        try:
            config = config or self.config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False

    def deep_merge(self, base, update):
        """Deep merge two dictionaries"""
        result = base.copy()

        for key, value in update.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self.deep_merge(result[key], value)
            else:
                result[key] = value

        return result

    def get_source_config(self, source_name):
        """Get configuration for a specific source"""
        return self.config.get("sources", {}).get(source_name, {})

    def get_politician_config(self):
        """Get politician tracking configuration"""
        return self.config.get("politicians", {})

    def get_alert_config(self):
        """Get alerting configuration"""
        return self.config.get("alerting", {})

    def get_storage_config(self):
        """Get storage configuration"""
        return self.config.get("storage", {})

    def get_cron_config(self):
        """Get cron job configuration"""
        return self.config.get("cron", {})

    def update_config(self, updates):
        """Update configuration with new values"""
        self.config = self.deep_merge(self.config, updates)
        return self.save_config()
