"""
Tests for the database module
"""
import json
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from database import TradingDatabase, get_database, SEED_DATA_PATH


class TestTradingDatabase:
    """Tests for TradingDatabase class"""

    def test_database_creation(self, temp_db_path):
        """Test database is created with correct schema"""
        db = TradingDatabase(temp_db_path)

        # Check file exists
        assert os.path.exists(temp_db_path)

        # Verify tables exist
        import sqlite3
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table'"
            )
            tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            'congressional_trades',
            'executed_trades',
            'positions',
            'bot_state',
            'notifications'
        }
        assert expected_tables.issubset(tables)

    def test_add_congressional_trade(self, temp_db_path, sample_congressional_trade):
        """Test adding a congressional trade"""
        db = TradingDatabase(temp_db_path)

        result = db.add_congressional_trade(sample_congressional_trade)
        assert result is True

        # Verify trade was added
        trades = db.get_recent_trades(30)
        assert len(trades) >= 1

        # Find our trade
        our_trade = next(
            (t for t in trades if t['ticker'] == 'NVDA'),
            None
        )
        assert our_trade is not None
        assert our_trade['representative'] == 'Hon. Nancy Pelosi'
        assert our_trade['transaction_type'] == 'purchase'

    def test_trade_deduplication(self, temp_db_path, sample_congressional_trade):
        """Test that duplicate trades are rejected"""
        db = TradingDatabase(temp_db_path)

        # Add trade first time
        result1 = db.add_congressional_trade(sample_congressional_trade)
        assert result1 is True

        # Try to add same trade again
        result2 = db.add_congressional_trade(sample_congressional_trade)
        assert result2 is False

        # Verify only one instance of this specific trade exists
        # Note: seed data may also contain NVDA trades
        trades = db.get_recent_trades(365)
        # Count trades with exact matching characteristics
        matching_trades = [
            t for t in trades
            if t['ticker'] == 'NVDA'
            and t['representative'] == 'Hon. Nancy Pelosi'
            and t['transaction_date'] == '01/15/2026'
        ]
        assert len(matching_trades) == 1

    def test_trade_exists_check(self, temp_db_path, sample_congressional_trade):
        """Test trade_exists method"""
        db = TradingDatabase(temp_db_path)

        # Trade doesn't exist yet
        assert db.trade_exists(sample_congressional_trade) is False

        # Add trade
        db.add_congressional_trade(sample_congressional_trade)

        # Now it should exist
        assert db.trade_exists(sample_congressional_trade) is True

    def test_mark_trade_processed(self, temp_db_path, sample_congressional_trade):
        """Test marking a trade as processed"""
        db = TradingDatabase(temp_db_path)
        db.add_congressional_trade(sample_congressional_trade)

        # Get unprocessed trades
        unprocessed = db.get_unprocessed_trades()
        assert len(unprocessed) >= 1

        trade_id = unprocessed[0]['id']

        # Mark as processed
        db.mark_trade_processed(trade_id)

        # Should no longer be in unprocessed list
        unprocessed_after = db.get_unprocessed_trades()
        trade_ids = [t['id'] for t in unprocessed_after]
        assert trade_id not in trade_ids

    def test_add_executed_trade(self, temp_db_path, sample_congressional_trade):
        """Test recording an executed trade"""
        db = TradingDatabase(temp_db_path)
        db.add_congressional_trade(sample_congressional_trade)

        trades = db.get_recent_trades(30)
        congressional_id = trades[0]['id']

        # Add executed trade
        exec_id = db.add_executed_trade(
            congressional_trade_id=congressional_id,
            ticker='NVDA',
            action='BUY',
            quantity=10,
            price=500.0,
            total_value=5000.0,
            order_id='ORDER123',
            status='filled'
        )

        assert exec_id is not None

        # Verify it was added
        executed = db.get_executed_trades(30)
        assert len(executed) >= 1
        assert executed[0]['ticker'] == 'NVDA'
        assert executed[0]['status'] == 'filled'

    def test_positions_crud(self, temp_db_path):
        """Test position CRUD operations"""
        db = TradingDatabase(temp_db_path)

        # Add position
        db.update_position('AAPL', quantity=100, avg_cost=150.0, current_price=155.0)

        # Get position
        position = db.get_position('AAPL')
        assert position is not None
        assert position['quantity'] == 100
        assert position['avg_cost'] == 150.0

        # Update position
        db.update_position('AAPL', quantity=150, avg_cost=152.0, current_price=160.0)
        position = db.get_position('AAPL')
        assert position['quantity'] == 150

        # Delete position (set quantity to 0)
        db.update_position('AAPL', quantity=0)
        position = db.get_position('AAPL')
        assert position is None

    def test_get_all_positions(self, temp_db_path):
        """Test getting all positions"""
        db = TradingDatabase(temp_db_path)

        # Add multiple positions
        db.update_position('AAPL', quantity=100, avg_cost=150.0)
        db.update_position('GOOGL', quantity=50, avg_cost=140.0)
        db.update_position('MSFT', quantity=25, avg_cost=400.0)

        positions = db.get_positions()
        assert len(positions) == 3

        symbols = {p['ticker'] for p in positions}
        assert symbols == {'AAPL', 'GOOGL', 'MSFT'}

    def test_bot_state(self, temp_db_path):
        """Test bot state storage"""
        db = TradingDatabase(temp_db_path)

        # Set string state
        db.set_state('last_check', '2026-01-31T10:00:00')
        assert db.get_state('last_check') == '2026-01-31T10:00:00'

        # Set dict state (serialized to JSON)
        db.set_state('settings', {'mode': 'auto', 'enabled': True})
        settings = db.get_state('settings')
        assert settings == {'mode': 'auto', 'enabled': True}

        # Get non-existent state with default
        assert db.get_state('nonexistent', 'default') == 'default'

    def test_last_fetch_time(self, temp_db_path):
        """Test last fetch time tracking"""
        db = TradingDatabase(temp_db_path)

        # Initially None
        assert db.get_last_fetch_time('house_clerk') is None

        # Set fetch time
        db.set_last_fetch_time('house_clerk')

        # Should now have a value
        fetch_time = db.get_last_fetch_time('house_clerk')
        assert fetch_time is not None

    def test_notifications(self, temp_db_path):
        """Test notification recording"""
        db = TradingDatabase(temp_db_path)

        # Add notification
        db.add_notification('trade_alert', 'New trade detected: NVDA')
        db.add_notification('stop_loss', 'Stop loss triggered: AAPL')

        notifications = db.get_recent_notifications(10)
        assert len(notifications) == 2

    def test_trade_stats(self, temp_db_path, sample_trades_batch):
        """Test trade statistics"""
        db = TradingDatabase(temp_db_path)

        # Add multiple trades
        for trade in sample_trades_batch:
            db.add_congressional_trade(trade)

        stats = db.get_trade_stats()

        assert stats['total_discovered'] >= 3
        assert 'by_chamber' in stats
        assert 'top_tickers' in stats

    def test_export_to_json(self, temp_db_path, sample_trades_batch):
        """Test exporting database to JSON"""
        db = TradingDatabase(temp_db_path)

        # Add data
        for trade in sample_trades_batch:
            db.add_congressional_trade(trade)

        db.update_position('AAPL', quantity=100, avg_cost=150.0)
        db.set_state('test_key', 'test_value')

        # Export
        export_path = temp_db_path.replace('.db', '_export.json')
        db.export_to_json(export_path)

        assert os.path.exists(export_path)

        with open(export_path) as f:
            exported = json.load(f)

        assert 'congressional_trades' in exported
        assert 'positions' in exported
        assert 'bot_state' in exported
        assert len(exported['congressional_trades']) >= 3

        # Cleanup
        os.remove(export_path)


class TestSeedDataLoading:
    """Tests for seed data loading functionality"""

    def test_seed_data_loads_on_empty_db(self, temp_db_path):
        """Test that seed data is loaded when database is empty"""
        # Only run if seed data exists
        if not SEED_DATA_PATH.exists():
            pytest.skip("Seed data file not found")

        db = TradingDatabase(temp_db_path)
        stats = db.get_trade_stats()

        # Should have loaded some trades from seed
        assert stats['total_discovered'] > 0

    def test_seed_data_not_reloaded(self, temp_db_path, sample_congressional_trade):
        """Test that seed data is not loaded if database has data"""
        # First, create db with one trade
        db = TradingDatabase(temp_db_path)
        initial_count = db.get_trade_stats()['total_discovered']

        # Add our own trade
        db.add_congressional_trade(sample_congressional_trade)

        # Create new db instance (simulates restart)
        db2 = TradingDatabase(temp_db_path)
        final_count = db2.get_trade_stats()['total_discovered']

        # Should only have our added trade plus any seed data from first init
        # Not double the seed data
        assert final_count == initial_count + 1


class TestDatabaseSingleton:
    """Tests for database singleton pattern"""

    def test_get_database_returns_same_instance(self, temp_db_path):
        """Test that get_database returns singleton"""
        # Note: This test modifies global state, so use unique path
        import database
        database._db_instance = None  # Reset singleton

        db1 = get_database(temp_db_path)
        db2 = get_database(temp_db_path)

        assert db1 is db2

        # Cleanup
        database._db_instance = None
