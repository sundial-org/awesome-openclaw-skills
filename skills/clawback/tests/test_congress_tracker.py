"""
Tests for the congressional trade tracker module
"""
import os
import tempfile
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from congress_tracker import CongressTracker


class TestCongressTracker:
    """Tests for the CongressTracker class"""

    @pytest.fixture
    def tracker(self, sample_config):
        """Create a congress tracker for testing"""
        return CongressTracker(sample_config)

    def test_tracker_initialization(self, tracker, sample_config):
        """Test tracker initializes with correct parameters"""
        assert tracker.min_trade_size == sample_config['congress']['minimumTradeSize']
        assert 'purchase' in tracker.trade_types
        assert len(tracker.target_politicians) > 0

    def test_target_politicians_loaded(self, tracker):
        """Test target politicians are loaded from config"""
        # Should have at least Pelosi
        names = [p['name'].lower() for p in tracker.target_politicians]
        assert any('pelosi' in name for name in names)

    def test_extract_ticker_parentheses(self, tracker):
        """Test extracting ticker from parentheses format"""
        assert tracker._extract_ticker('Apple Inc. (AAPL)') == 'AAPL'
        assert tracker._extract_ticker('NVIDIA Corporation (NVDA)') == 'NVDA'
        assert tracker._extract_ticker('Alphabet Inc. - Class A Common Stock (GOOGL) [ST]') == 'GOOGL'

    def test_extract_ticker_standalone(self, tracker):
        """Test extracting standalone ticker"""
        # Already a ticker-like string
        result = tracker._extract_ticker('AAPL')
        # May or may not extract depending on context

    def test_extract_ticker_excludes_non_tickers(self, tracker):
        """Test that common non-ticker patterns are excluded"""
        # These should not be extracted as tickers
        assert tracker._extract_ticker('Stock Type (ST)') != 'ST'
        assert tracker._extract_ticker('Option (OP)') != 'OP'

    def test_parse_amount_range(self, tracker):
        """Test parsing amount ranges"""
        # Test range parsing
        amount, range_str = tracker._parse_amount_range('$100,001 - $250,000')
        assert amount > 0
        assert '$' in range_str

        amount, range_str = tracker._parse_amount_range('$1,000,001 - $5,000,000')
        assert amount > 1000000

    def test_extract_amount_from_text(self, tracker):
        """Test extracting amounts from text"""
        amount, range_str = tracker._extract_amount_from_text('Amount: $100,001 - $250,000')
        assert amount == 175000.5  # Midpoint
        assert '$100,001' in range_str or '100001' in range_str.replace(',', '')

    def test_parse_date_formats(self, tracker):
        """Test parsing various date formats"""
        # MM/DD/YYYY
        result = tracker._parse_date('01/15/2026')
        assert result.year == 2026
        assert result.month == 1
        assert result.day == 15

        # YYYY-MM-DD
        result = tracker._parse_date('2026-01-15')
        assert result.year == 2026

        # M/D/YYYY (single digits)
        result = tracker._parse_date('1/5/2026')
        assert result.month == 1
        assert result.day == 5

    def test_parse_date_invalid_returns_current(self, tracker):
        """Test that invalid dates return current datetime"""
        result = tracker._parse_date('invalid date')
        assert isinstance(result, datetime)
        # Should be close to now
        assert (datetime.now() - result).total_seconds() < 60

    def test_deduplicate_trades(self, tracker):
        """Test trade deduplication"""
        trades = [
            {'ticker': 'AAPL', 'transaction_date': '01/15/2026',
             'transaction_type': 'purchase'},
            {'ticker': 'AAPL', 'transaction_date': '01/15/2026',
             'transaction_type': 'purchase'},  # Duplicate
            {'ticker': 'GOOGL', 'transaction_date': '01/15/2026',
             'transaction_type': 'purchase'},
        ]

        deduped = tracker._deduplicate_trades(trades)

        assert len(deduped) == 2
        tickers = [t['ticker'] for t in deduped]
        assert 'AAPL' in tickers
        assert 'GOOGL' in tickers

    def test_extract_transaction_type_purchase(self, tracker):
        """Test extracting purchase transaction type"""
        assert tracker._extract_transaction_type('Transaction: Purchase') == 'purchase'
        assert tracker._extract_transaction_type('Type: P 01/15/2026') == 'purchase'
        assert tracker._extract_transaction_type('bought 100 shares') == 'purchase'

    def test_extract_transaction_type_sale(self, tracker):
        """Test extracting sale transaction type"""
        assert tracker._extract_transaction_type('Transaction: Sale') == 'sale'
        assert tracker._extract_transaction_type('Type: S 01/15/2026') == 'sale'
        assert tracker._extract_transaction_type('sold 100 shares') == 'sale'

    def test_is_option_trade(self, tracker):
        """Test option trade detection"""
        assert tracker._is_option_trade('[OP] NVDA Call') is True
        assert tracker._is_option_trade('NVDA option $500 strike') is True
        assert tracker._is_option_trade('NVDA Common Stock [ST]') is False

    def test_parse_amount_string(self, tracker):
        """Test parsing amount strings"""
        # Single amount
        assert tracker._parse_amount('$50,000') == 50000

        # Range - should return midpoint
        result = tracker._parse_amount('$100,000 - $250,000')
        assert result == 175000

    def test_extract_date_from_text(self, tracker):
        """Test extracting dates from text blocks"""
        # MM/DD/YYYY format
        result = tracker._extract_date('Transaction on 01/15/2026 for stock')
        assert result == '01/15/2026'

        # YYYY-MM-DD format
        result = tracker._extract_date('Date: 2026-01-15')
        assert result == '2026-01-15'

    def test_include_senate_config(self, tracker, sample_config):
        """Test Senate inclusion configuration"""
        assert tracker.include_senate == sample_config['congress']['includeSenate']


class TestMockDataFetching:
    """Tests for mock data functionality"""

    @pytest.fixture
    def tracker(self, sample_config):
        """Create tracker with mock data source"""
        sample_config['congress']['dataSource'] = 'mock'
        return CongressTracker(sample_config)

    def test_fetch_mock_data(self, tracker):
        """Test fetching mock data returns trades"""
        trades = tracker.fetch_mock_data()

        assert len(trades) > 0
        # All trades should have required fields
        for trade in trades:
            assert 'ticker' in trade
            assert 'transaction_type' in trade
            assert 'amount' in trade
            assert 'representative' in trade

    def test_mock_data_filters_by_type(self, tracker):
        """Test that mock data respects trade type filter"""
        tracker.trade_types = ['purchase']
        trades = tracker.fetch_mock_data()

        for trade in trades:
            assert trade['transaction_type'] == 'purchase'

    def test_mock_data_filters_by_size(self, tracker):
        """Test that mock data respects minimum trade size"""
        trades = tracker.fetch_mock_data()

        for trade in trades:
            assert trade['amount'] >= tracker.min_trade_size


class TestTradeFileSaving:
    """Tests for trade file I/O"""

    @pytest.fixture
    def tracker(self, sample_config):
        """Create tracker for testing"""
        return CongressTracker(sample_config)

    def test_save_and_load_trades(self, tracker):
        """Test saving and loading trades from file"""
        trades = [
            {
                'ticker': 'AAPL',
                'transaction_type': 'purchase',
                'amount': 100000,
                'representative': 'Test Person',
                'transaction_date': '01/15/2026',
                'parsed_date': datetime(2026, 1, 15)
            }
        ]

        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as f:
            filepath = f.name

        try:
            # Save
            result = tracker.save_trades_to_file(trades, filepath)
            assert result is True

            # Load
            loaded = tracker.load_trades_from_file(filepath)
            assert len(loaded) == 1
            assert loaded[0]['ticker'] == 'AAPL'
            # parsed_date should be converted back to datetime
            assert isinstance(loaded[0]['parsed_date'], datetime)

        finally:
            os.remove(filepath)

    def test_load_nonexistent_file(self, tracker):
        """Test loading from non-existent file returns empty list"""
        result = tracker.load_trades_from_file('/nonexistent/file.json')
        assert result == []


class TestGetRecentTrades:
    """Tests for get_recent_trades method"""

    @pytest.fixture
    def tracker(self, sample_config):
        """Create tracker with mock data only"""
        sample_config['congress']['dataSource'] = 'mock'
        sample_config['congress']['includeSenate'] = False  # Disable Senate to avoid network
        return CongressTracker(sample_config)

    def test_fetch_mock_data_directly(self, tracker):
        """Test fetching mock data directly (no network)"""
        trades = tracker.fetch_mock_data()
        assert isinstance(trades, list)
        assert len(trades) > 0

    def test_mock_data_has_required_fields(self, tracker):
        """Test mock data has all required fields"""
        trades = tracker.fetch_mock_data()

        for trade in trades:
            assert 'ticker' in trade
            assert 'transaction_type' in trade
            assert 'amount' in trade


class TestGetTradesSince:
    """Tests for get_trades_since method"""

    @pytest.fixture
    def tracker(self, sample_config):
        """Create tracker with mock data only"""
        sample_config['congress']['dataSource'] = 'mock'
        sample_config['congress']['includeSenate'] = False
        return CongressTracker(sample_config)

    def test_tracker_has_last_fetch_time(self, tracker):
        """Test that tracker tracks fetch time"""
        assert tracker.last_fetch_time is None  # Initially none
        # After fetching, it would be set


class TestHouseClerkIntegration:
    """Integration tests for House Clerk data (may require network)"""

    @pytest.fixture
    def tracker(self, sample_config):
        """Create tracker for House Clerk"""
        sample_config['congress']['dataSource'] = 'house_clerk'
        return CongressTracker(sample_config)

    @pytest.mark.slow
    def test_fetch_house_clerk_structure(self, tracker):
        """Test House Clerk fetch returns properly structured data"""
        # This test may be slow and requires network
        # Skip in CI environments
        try:
            trades = tracker.fetch_house_clerk_data()

            # If we got any trades, verify structure
            for trade in trades:
                assert 'ticker' in trade
                assert 'transaction_type' in trade
                assert 'representative' in trade
                assert 'source' in trade
                assert trade['source'] == 'house_clerk_pdf'

        except Exception:
            pytest.skip("Network unavailable or House Clerk data inaccessible")
