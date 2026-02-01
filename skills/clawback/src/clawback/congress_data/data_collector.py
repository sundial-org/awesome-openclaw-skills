"""
Congressional trade data collector
Fetches trade data from official government sources
"""
import json
import logging
import os
import time
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import pandas as pd

logger = logging.getLogger(__name__)

class CongressDataCollector:
    """Collects congressional trade data from official sources"""

    def __init__(self, config):
        self.config = config
        self.sources_config = config.get_source_config
        self.storage_config = config.get_storage_config()

        # Create data directories
        self.setup_directories()

        # State tracking
        self.last_fetch_time = {}
        self.failed_sources = set()

        logger.info("Congressional data collector initialized")

    def setup_directories(self):
        """Create necessary directories for data storage"""
        data_dir = self.storage_config.get("data_directory", "data/congress_trades")
        backup_dir = self.storage_config.get("backup_directory", "data/backups")

        os.makedirs(data_dir, exist_ok=True)
        os.makedirs(backup_dir, exist_ok=True)

        # Create source-specific directories
        for source in ["senate", "house"]:
            source_dir = os.path.join(data_dir, source)
            os.makedirs(source_dir, exist_ok=True)

    def fetch_senate_data(self):
        """Fetch data from Senate financial disclosures"""
        try:
            source_config = self.sources_config("senate")
            if not source_config.get("enabled", True):
                logger.info("Senate source disabled")
                return []

            url = source_config["url"]
            min_amount = source_config.get("min_trade_amount", 1000)

            logger.info(f"Fetching Senate data from {url}")

            # Note: efdsearch.senate.gov requires proper session handling
            # This is a simplified version - in production you'd need to handle:
            # 1. Session cookies
            # 2. Search parameters
            # 3. Pagination

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            # Try to get the search page first
            session = requests.Session()
            response = session.get(url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(f"Failed to access Senate site: {response.status_code}")
                self.failed_sources.add("senate")
                return []

            # Parse the page to look for trade data
            # This is a placeholder - actual implementation would need to:
            # 1. Submit search form
            # 2. Parse results
            # 3. Extract trade information

            # For now, we'll use community data sources as fallback
            trades = self.fetch_senate_community_data()

            # Filter by minimum amount
            filtered_trades = [t for t in trades if t.get("amount", 0) >= min_amount]

            logger.info(f"Found {len(filtered_trades)} Senate trades (min ${min_amount})")
            return filtered_trades

        except Exception as e:
            logger.error(f"Error fetching Senate data: {e}")
            self.failed_sources.add("senate")
            return []

    def fetch_senate_community_data(self):
        """Fetch Senate data from community sources (GitHub repositories)"""
        try:
            # Try to fetch from senate-stock-watcher-data repository
            # This is a community-maintained dataset
            community_url = "https://raw.githubusercontent.com/timothycarambat/senate-stock-watcher-data/main/data/all_transactions.json"

            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(community_url, headers=headers, timeout=30)

            if response.status_code == 200:
                data = response.json()

                trades = []
                for item in data:
                    try:
                        trade = {
                            "politician": item.get("senator", ""),
                            "transaction_date": item.get("transaction_date", ""),
                            "ticker": item.get("ticker", ""),
                            "asset_name": item.get("asset_name", ""),
                            "transaction_type": item.get("type", "").lower(),
                            "amount": self.parse_amount(item.get("amount", "0")),
                            "source": "senate_community",
                            "filing_date": item.get("filing_date", "")
                        }

                        if trade["ticker"] and trade["amount"] > 0:
                            trades.append(trade)

                    except (ValueError, KeyError) as e:
                        logger.debug(f"Error parsing Senate trade: {e}")
                        continue

                logger.info(f"Found {len(trades)} trades from Senate community data")
                return trades
            else:
                logger.warning(f"Failed to fetch community Senate data: {response.status_code}")
                return []

        except Exception as e:
            logger.error(f"Error fetching Senate community data: {e}")
            return []

    def fetch_house_data(self):
        """Fetch data from House financial disclosures"""
        try:
            source_config = self.sources_config("house")
            if not source_config.get("enabled", True):
                logger.info("House source disabled")
                return []

            url = source_config["url"]
            min_amount = source_config.get("min_trade_amount", 1000)

            logger.info(f"Fetching House data from {url}")

            # Note: disclosures-clerk.house.gov has its own interface
            # This would require proper form submission and parsing

            # For now, use community sources as fallback
            trades = self.fetch_house_community_data()

            # Filter by minimum amount
            filtered_trades = [t for t in trades if t.get("amount", 0) >= min_amount]

            logger.info(f"Found {len(filtered_trades)} House trades (min ${min_amount})")
            return filtered_trades

        except Exception as e:
            logger.error(f"Error fetching House data: {e}")
            self.failed_sources.add("house")
            return []

    def fetch_house_community_data(self):
        """Fetch House data from community sources"""
        try:
            # Placeholder for community House data
            # In production, you might use:
            # 1. Other GitHub repositories
            # 2. Web scraping with proper rate limiting

            # For now, return empty list
            return []

        except Exception as e:
            logger.error(f"Error fetching House community data: {e}")
            return []

    def parse_amount(self, amount_str):
        """Parse amount string to float"""
        try:
            if isinstance(amount_str, (int, float)):
                return float(amount_str)

            # Remove currency symbols and commas
            amount_str = str(amount_str).replace('$', '').replace(',', '').strip()

            # Handle ranges (e.g., "$1,000,001 - $5,000,000")
            if '-' in amount_str:
                parts = amount_str.split('-')
                low = float(parts[0].strip())
                high = float(parts[1].strip())
                return (low + high) / 2

            # Handle "Over $1,000,000" type strings
            if amount_str.lower().startswith('over'):
                amount_str = amount_str[4:].strip()
                return float(amount_str) * 1.5  # Estimate as 1.5x the threshold

            return float(amount_str)

        except (ValueError, AttributeError):
            return 0.0

    def filter_politicians(self, trades):
        """Filter trades based on politician configuration"""
        politician_config = self.config.get_politician_config()

        if not politician_config.get("track_all", False):
            specific_politicians = set(politician_config.get("specific_politicians", []))

            filtered_trades = []
            for trade in trades:
                politician = trade.get('politician', '')

                # Check if this politician is in our tracking list
                if any(sp.lower() in politician.lower() for sp in specific_politicians):
                    filtered_trades.append(trade)

            logger.info(f"Filtered to {len(filtered_trades)} trades from tracked politicians")
            return filtered_trades

        return trades

    def filter_by_trade_size(self, trades):
        """Filter trades by minimum size"""
        min_size = self.config.get_politician_config().get("minimum_trade_size", 10000)

        filtered_trades = [t for t in trades if t.get("amount", 0) >= min_size]

        if len(filtered_trades) < len(trades):
            logger.info(f"Filtered out {len(trades) - len(filtered_trades)} trades below ${min_size}")

        return filtered_trades

    def save_trades(self, trades, source):
        """Save trades to JSON file with timestamp"""
        try:
            if not trades:
                return False

            data_dir = self.storage_config.get("data_directory", "data/congress_trades")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{source}_{timestamp}.json"
            filepath = os.path.join(data_dir, source, filename)

            # Convert dates to strings for JSON serialization
            serializable_trades = []
            for trade in trades:
                trade_copy = trade.copy()
                # Ensure all values are JSON serializable
                for key, value in trade_copy.items():
                    if isinstance(value, datetime):
                        trade_copy[key] = value.isoformat()
                serializable_trades.append(trade_copy)

            with open(filepath, 'w') as f:
                json.dump(serializable_trades, f, indent=2)

            logger.info(f"Saved {len(trades)} {source} trades to {filepath}")

            # Update last fetch time
            self.last_fetch_time[source] = datetime.now()

            return True

        except Exception as e:
            logger.error(f"Error saving {source} trades: {e}")
            return False

    def load_recent_trades(self, source, days=7):
        """Load recent trades from storage"""
        try:
            data_dir = self.storage_config.get("data_directory", "data/congress_trades")
            source_dir = os.path.join(data_dir, source)

            if not os.path.exists(source_dir):
                return []

            cutoff_date = datetime.now() - timedelta(days=days)
            all_trades = []

            for filename in os.listdir(source_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(source_dir, filename)

                    # Check file modification time
                    file_mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if file_mtime < cutoff_date:
                        continue

                    try:
                        with open(filepath, 'r') as f:
                            trades = json.load(f)

                        # Convert date strings back to datetime objects
                        for trade in trades:
                            for key in ["transaction_date", "filing_date"]:
                                if key in trade and trade[key]:
                                    try:
                                        trade[key] = datetime.fromisoformat(trade[key].replace('Z', '+00:00'))
                                    except (ValueError, AttributeError):
                                        pass

                        all_trades.extend(trades)

                    except (json.JSONDecodeError, UnicodeDecodeError) as e:
                        logger.warning(f"Error loading {filepath}: {e}")
                        continue

            logger.info(f"Loaded {len(all_trades)} recent trades from {source}")
            return all_trades

        except Exception as e:
            logger.error(f"Error loading recent trades from {source}: {e}")
            return []

    def collect_all_data(self):
        """Collect data from all enabled sources"""
        all_trades = []

        # Collect from each source
        sources = ["senate", "house"]

        for source in sources:
            try:
                source_config = self.sources_config(source)
                if not source_config.get("enabled", True):
                    continue

                # Check if we should fetch based on interval
                last_fetch = self.last_fetch_time.get(source)
                check_interval = source_config.get("check_interval_hours", 24)

                if last_fetch and (datetime.now() - last_fetch).total_seconds() < check_interval * 3600:
                    logger.debug(f"Skipping {source} - fetched recently")
                    # Load from storage instead
                    trades = self.load_recent_trades(source, days=1)
                else:
                    # Fetch new data
                    if source == "senate":
                        trades = self.fetch_senate_data()
                    elif source == "house":
                        trades = self.fetch_house_data()
                    else:
                        trades = []

                    # Save new data
                    if trades:
                        self.save_trades(trades, source)

                # Apply filters
                trades = self.filter_politicians(trades)
                trades = self.filter_by_trade_size(trades)

                all_trades.extend(trades)

            except Exception as e:
                logger.error(f"Error collecting data from {source}: {e}")
                self.failed_sources.add(source)
                continue

        # Remove duplicates (same politician, ticker, date, type)
        unique_trades = self.deduplicate_trades(all_trades)

        logger.info(f"Total unique trades collected: {len(unique_trades)}")
        return unique_trades

    def deduplicate_trades(self, trades):
        """Remove duplicate trades"""
        unique_trades = []
        seen_keys = set()

        for trade in trades:
            # Create unique key
            key_parts = [
                trade.get("politician", ""),
                trade.get("ticker", ""),
                trade.get("transaction_date", ""),
                trade.get("transaction_type", ""),
                str(trade.get("amount", 0))
            ]
            key = "_".join(str(p) for p in key_parts)

            if key not in seen_keys:
                seen_keys.add(key)
                unique_trades.append(trade)

        return unique_trades

    def get_collection_stats(self):
        """Get statistics about data collection"""
        stats = {
            "last_fetch_times": {k: v.isoformat() if v else None for k, v in self.last_fetch_time.items()},
            "failed_sources": list(self.failed_sources),
            "total_sources_checked": len(self.last_fetch_time),
            "failed_source_count": len(self.failed_sources)
        }

        return stats
