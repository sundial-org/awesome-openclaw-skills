"""
SQLite database for tracking trades, executions, and bot state
"""
import sqlite3
import json
import logging
import os
from datetime import datetime
from pathlib import Path

logger = logging.getLogger(__name__)

# Path to seed data (relative to project root)
SEED_DATA_PATH = Path(__file__).parent.parent / "data" / "seed" / "congressional_trades.json"


class TradingDatabase:
    """SQLite database for persistent state management"""

    def __init__(self, db_path="data/trading.db"):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        self._load_seed_data_if_empty()
        logger.info(f"Initialized database at {db_path}")

    def _init_db(self):
        """Initialize database schema"""
        with sqlite3.connect(self.db_path) as conn:
            conn.executescript("""
                -- Discovered congressional trades
                CREATE TABLE IF NOT EXISTS congressional_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trade_hash TEXT UNIQUE NOT NULL,
                    ticker TEXT NOT NULL,
                    transaction_type TEXT NOT NULL,
                    amount REAL,
                    amount_range TEXT,
                    transaction_date TEXT,
                    disclosure_date TEXT,
                    representative TEXT,
                    chamber TEXT,
                    source TEXT,
                    report_url TEXT,
                    asset_name TEXT,
                    raw_data TEXT,
                    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed INTEGER DEFAULT 0
                );

                -- Our executed trades
                CREATE TABLE IF NOT EXISTS executed_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    congressional_trade_id INTEGER,
                    ticker TEXT NOT NULL,
                    action TEXT NOT NULL,
                    quantity INTEGER,
                    price REAL,
                    total_value REAL,
                    order_id TEXT,
                    status TEXT,
                    error_message TEXT,
                    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (congressional_trade_id) REFERENCES congressional_trades(id)
                );

                -- Portfolio positions
                CREATE TABLE IF NOT EXISTS positions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT UNIQUE NOT NULL,
                    quantity INTEGER NOT NULL,
                    avg_cost REAL,
                    current_price REAL,
                    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Bot state and configuration
                CREATE TABLE IF NOT EXISTS bot_state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                -- Notifications sent
                CREATE TABLE IF NOT EXISTS notifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT NOT NULL,
                    message TEXT,
                    trade_id INTEGER,
                    sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trade_id) REFERENCES executed_trades(id)
                );

                -- Broker authentication tokens
                CREATE TABLE IF NOT EXISTS broker_tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    broker TEXT NOT NULL,
                    account_id TEXT,
                    access_token TEXT NOT NULL,
                    access_secret TEXT,
                    refresh_token TEXT,
                    token_type TEXT DEFAULT 'oauth1',
                    expires_at TIMESTAMP,
                    last_refreshed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(broker, account_id)
                );

                -- Create indexes for common queries
                CREATE INDEX IF NOT EXISTS idx_trades_ticker ON congressional_trades(ticker);
                CREATE INDEX IF NOT EXISTS idx_trades_date ON congressional_trades(disclosure_date);
                CREATE INDEX IF NOT EXISTS idx_trades_processed ON congressional_trades(processed);
                CREATE INDEX IF NOT EXISTS idx_executed_ticker ON executed_trades(ticker);
                CREATE INDEX IF NOT EXISTS idx_tokens_broker ON broker_tokens(broker);
            """)
            conn.commit()

    def _load_seed_data_if_empty(self):
        """Load seed congressional trades if database is empty"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM congressional_trades")
            count = cursor.fetchone()[0]

            if count > 0:
                logger.debug(f"Database has {count} trades, skipping seed data")
                return

        # Database is empty, load seed data
        if not SEED_DATA_PATH.exists():
            logger.debug(f"No seed data found at {SEED_DATA_PATH}")
            return

        try:
            with open(SEED_DATA_PATH, 'r') as f:
                seed_data = json.load(f)

            trades = seed_data.get('trades', [])
            loaded = 0

            for trade in trades:
                if self.add_congressional_trade(trade):
                    loaded += 1

            if loaded > 0:
                logger.info(f"Loaded {loaded} congressional trades from seed data")

        except Exception as e:
            logger.warning(f"Could not load seed data: {e}")

    def _generate_trade_hash(self, trade):
        """Generate unique hash for a trade to detect duplicates"""
        import hashlib
        key = f"{trade.get('ticker', '')}_{trade.get('transaction_date', '')}_{trade.get('transaction_type', '')}_{trade.get('representative', '')}_{trade.get('amount', '')}"
        return hashlib.md5(key.encode()).hexdigest()

    # --- Congressional Trades ---

    def add_congressional_trade(self, trade):
        """Add a discovered congressional trade (if not duplicate)"""
        trade_hash = self._generate_trade_hash(trade)

        with sqlite3.connect(self.db_path) as conn:
            try:
                # Serialize trade to JSON, handling datetime objects
                trade_copy = trade.copy()
                if 'parsed_date' in trade_copy:
                    trade_copy['parsed_date'] = trade_copy['parsed_date'].isoformat() if hasattr(trade_copy['parsed_date'], 'isoformat') else str(trade_copy['parsed_date'])

                conn.execute("""
                    INSERT INTO congressional_trades
                    (trade_hash, ticker, transaction_type, amount, amount_range,
                     transaction_date, disclosure_date, representative, chamber,
                     source, report_url, asset_name, raw_data)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    trade_hash,
                    trade.get('ticker', ''),
                    trade.get('transaction_type', ''),
                    trade.get('amount', 0),
                    trade.get('amount_range', ''),
                    trade.get('transaction_date', ''),
                    trade.get('disclosure_date', ''),
                    trade.get('representative', ''),
                    trade.get('chamber', 'house'),
                    trade.get('source', ''),
                    trade.get('report_url', trade.get('pdf_url', '')),
                    trade.get('asset_name', ''),
                    json.dumps(trade_copy, default=str)
                ))
                conn.commit()
                logger.debug(f"Added trade: {trade.get('ticker')} {trade.get('transaction_type')}")
                return True
            except sqlite3.IntegrityError:
                # Duplicate trade
                logger.debug(f"Trade already exists: {trade.get('ticker')}")
                return False

    def get_unprocessed_trades(self):
        """Get trades that haven't been executed yet"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM congressional_trades
                WHERE processed = 0
                ORDER BY disclosure_date DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def mark_trade_processed(self, trade_id):
        """Mark a congressional trade as processed"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "UPDATE congressional_trades SET processed = 1 WHERE id = ?",
                (trade_id,)
            )
            conn.commit()

    def get_recent_trades(self, days=30):
        """Get congressional trades from the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM congressional_trades
                WHERE discovered_at >= datetime('now', ?)
                ORDER BY disclosure_date DESC
            """, (f'-{days} days',))
            return [dict(row) for row in cursor.fetchall()]

    def trade_exists(self, trade):
        """Check if a trade already exists in the database"""
        trade_hash = self._generate_trade_hash(trade)
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT 1 FROM congressional_trades WHERE trade_hash = ?",
                (trade_hash,)
            )
            return cursor.fetchone() is not None

    # --- Executed Trades ---

    def add_executed_trade(self, congressional_trade_id, ticker, action, quantity,
                           price, total_value, order_id, status, error_message=None):
        """Record an executed trade"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                INSERT INTO executed_trades
                (congressional_trade_id, ticker, action, quantity, price,
                 total_value, order_id, status, error_message)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                congressional_trade_id, ticker, action, quantity, price,
                total_value, order_id, status, error_message
            ))
            conn.commit()
            return cursor.lastrowid

    def get_executed_trades(self, days=30):
        """Get executed trades from the last N days"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT e.*, c.representative, c.disclosure_date as congress_date
                FROM executed_trades e
                LEFT JOIN congressional_trades c ON e.congressional_trade_id = c.id
                WHERE e.executed_at >= datetime('now', ?)
                ORDER BY e.executed_at DESC
            """, (f'-{days} days',))
            return [dict(row) for row in cursor.fetchall()]

    def get_trade_stats(self):
        """Get trading statistics"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            stats = {}

            # Total trades discovered
            cursor = conn.execute("SELECT COUNT(*) as count FROM congressional_trades")
            stats['total_discovered'] = cursor.fetchone()['count']

            # Trades by chamber
            cursor = conn.execute("""
                SELECT chamber, COUNT(*) as count
                FROM congressional_trades
                GROUP BY chamber
            """)
            stats['by_chamber'] = {row['chamber']: row['count'] for row in cursor.fetchall()}

            # Executed trades
            cursor = conn.execute("SELECT COUNT(*) as count FROM executed_trades WHERE status = 'filled'")
            stats['total_executed'] = cursor.fetchone()['count']

            # Total value traded
            cursor = conn.execute("SELECT SUM(total_value) as total FROM executed_trades WHERE status = 'filled'")
            result = cursor.fetchone()
            stats['total_value_traded'] = result['total'] or 0

            # Most traded tickers
            cursor = conn.execute("""
                SELECT ticker, COUNT(*) as count
                FROM congressional_trades
                GROUP BY ticker
                ORDER BY count DESC
                LIMIT 10
            """)
            stats['top_tickers'] = [(row['ticker'], row['count']) for row in cursor.fetchall()]

            return stats

    # --- Positions ---

    def update_position(self, ticker, quantity, avg_cost=None, current_price=None):
        """Update or insert a position"""
        with sqlite3.connect(self.db_path) as conn:
            if quantity == 0:
                conn.execute("DELETE FROM positions WHERE ticker = ?", (ticker,))
            else:
                conn.execute("""
                    INSERT INTO positions (ticker, quantity, avg_cost, current_price, last_updated)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(ticker) DO UPDATE SET
                        quantity = excluded.quantity,
                        avg_cost = COALESCE(excluded.avg_cost, avg_cost),
                        current_price = COALESCE(excluded.current_price, current_price),
                        last_updated = CURRENT_TIMESTAMP
                """, (ticker, quantity, avg_cost, current_price))
            conn.commit()

    def get_positions(self):
        """Get all current positions"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM positions ORDER BY ticker")
            return [dict(row) for row in cursor.fetchall()]

    def get_position(self, ticker):
        """Get a specific position"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM positions WHERE ticker = ?", (ticker,))
            row = cursor.fetchone()
            return dict(row) if row else None

    # --- Bot State ---

    def set_state(self, key, value):
        """Set a bot state value"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO bot_state (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    updated_at = CURRENT_TIMESTAMP
            """, (key, json.dumps(value) if not isinstance(value, str) else value))
            conn.commit()

    def get_state(self, key, default=None):
        """Get a bot state value"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT value FROM bot_state WHERE key = ?", (key,))
            row = cursor.fetchone()
            if row:
                try:
                    return json.loads(row[0])
                except (json.JSONDecodeError, TypeError):
                    return row[0]
            return default

    def get_last_fetch_time(self, source='house_clerk'):
        """Get the last time we fetched data from a source"""
        return self.get_state(f'last_fetch_{source}')

    def set_last_fetch_time(self, source='house_clerk'):
        """Update the last fetch time for a source"""
        self.set_state(f'last_fetch_{source}', datetime.now().isoformat())

    # --- Notifications ---

    def add_notification(self, notification_type, message, trade_id=None):
        """Record a sent notification"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO notifications (type, message, trade_id)
                VALUES (?, ?, ?)
            """, (notification_type, message, trade_id))
            conn.commit()

    def get_recent_notifications(self, limit=50):
        """Get recent notifications"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM notifications
                ORDER BY sent_at DESC
                LIMIT ?
            """, (limit,))
            return [dict(row) for row in cursor.fetchall()]

    # --- Broker Tokens ---

    def save_broker_tokens(self, broker: str, access_token: str, access_secret: str = None,
                           refresh_token: str = None, account_id: str = None,
                           expires_at: datetime = None):
        """Save or update broker authentication tokens"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                INSERT INTO broker_tokens
                    (broker, account_id, access_token, access_secret, refresh_token, expires_at, last_refreshed)
                VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT(broker, account_id) DO UPDATE SET
                    access_token = excluded.access_token,
                    access_secret = excluded.access_secret,
                    refresh_token = COALESCE(excluded.refresh_token, refresh_token),
                    expires_at = excluded.expires_at,
                    last_refreshed = CURRENT_TIMESTAMP
            """, (broker, account_id or '', access_token, access_secret, refresh_token,
                  expires_at.isoformat() if expires_at else None))
            conn.commit()
            logger.debug(f"Saved tokens for {broker}")

    def get_broker_tokens(self, broker: str, account_id: str = None):
        """Retrieve broker tokens"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("""
                SELECT * FROM broker_tokens
                WHERE broker = ? AND account_id = ?
            """, (broker, account_id or ''))
            row = cursor.fetchone()
            if row:
                result = dict(row)
                # Parse expires_at back to datetime if present
                if result.get('expires_at'):
                    try:
                        result['expires_at'] = datetime.fromisoformat(result['expires_at'])
                    except:
                        pass
                return result
            return None

    def delete_broker_tokens(self, broker: str, account_id: str = None):
        """Delete broker tokens (for logout/revoke)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                DELETE FROM broker_tokens
                WHERE broker = ? AND account_id = ?
            """, (broker, account_id or ''))
            conn.commit()
            logger.info(f"Deleted tokens for {broker}")

    def get_all_broker_tokens(self):
        """Get all stored broker tokens (for refresh job)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.execute("SELECT * FROM broker_tokens")
            return [dict(row) for row in cursor.fetchall()]

    def update_token_refresh_time(self, broker: str, account_id: str = None):
        """Update the last_refreshed timestamp"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                UPDATE broker_tokens
                SET last_refreshed = CURRENT_TIMESTAMP
                WHERE broker = ? AND account_id = ?
            """, (broker, account_id or ''))
            conn.commit()

    # --- Utility ---

    def vacuum(self):
        """Optimize the database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("VACUUM")

    def export_to_json(self, filepath):
        """Export all data to JSON"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row

            data = {
                'congressional_trades': [],
                'executed_trades': [],
                'positions': [],
                'bot_state': {},
                'exported_at': datetime.now().isoformat()
            }

            for row in conn.execute("SELECT * FROM congressional_trades"):
                data['congressional_trades'].append(dict(row))

            for row in conn.execute("SELECT * FROM executed_trades"):
                data['executed_trades'].append(dict(row))

            for row in conn.execute("SELECT * FROM positions"):
                data['positions'].append(dict(row))

            for row in conn.execute("SELECT key, value FROM bot_state"):
                data['bot_state'][row['key']] = row['value']

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported database to {filepath}")


# Singleton instance
_db_instance = None


def get_database(db_path="data/trading.db"):
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = TradingDatabase(db_path)
    return _db_instance
