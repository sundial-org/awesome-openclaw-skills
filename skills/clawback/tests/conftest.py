"""
Pytest fixtures and configuration for ClawBack tests
"""
import json
import os
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def temp_db_path():
    """Create a temporary database path"""
    with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
        yield f.name
    # Cleanup
    if os.path.exists(f.name):
        os.remove(f.name)


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "broker": {
            "adapter": "etrade",
            "credentials": {
                "apiKey": "test-api-key",
                "apiSecret": "test-api-secret"
            }
        },
        "trading": {
            "accountId": "test-account-123",
            "initialCapital": 50000,
            "tradeScalePercentage": 0.05,
            "maxPositionPercentage": 0.05,
            "maxPositions": 20,
            "dailyLossLimit": 0.03,
            "portfolioStopLoss": 0.15,
            "positionStopLoss": 0.08,
            "tradeDelayDays": 3,
            "holdingPeriodDays": 30,
            "marketHoursOnly": False,
            "marketOpen": "09:30",
            "marketClose": "16:00"
        },
        "strategy": {
            "entryDelayDays": 3,
            "holdingPeriodDays": 30,
            "purchasesOnly": True,
            "minimumTradeSize": 50000,
            "maxSectorExposure": 0.25,
            "prioritizeLeadership": True,
            "multiMemberBonus": True
        },
        "congress": {
            "dataSource": "official",
            "pollIntervalHours": 24,
            "minimumTradeSize": 50000,
            "tradeTypes": ["purchase"],
            "includeSenate": True,
            "targetPoliticians": [
                {"name": "Nancy Pelosi", "chamber": "house", "priority": 1}
            ]
        },
        "riskManagement": {
            "maxDrawdown": 0.15,
            "dailyLossLimit": 0.03,
            "positionStopLoss": 0.08,
            "trailingStopActivation": 0.10,
            "trailingStopPercent": 0.05,
            "consecutiveLossLimit": 3
        },
        "logging": {
            "level": "DEBUG",
            "file": "/tmp/test_trading.log",
            "maxSize": "10MB",
            "maxFiles": 10
        },
        "database": {
            "path": "data/trading.db"
        }
    }


@pytest.fixture
def sample_congressional_trade():
    """Sample congressional trade for testing"""
    return {
        "ticker": "NVDA",
        "transaction_type": "purchase",
        "amount": 250000.5,
        "amount_range": "$100,001 - $250,000",
        "transaction_date": "01/15/2026",
        "disclosure_date": "01/20/2026",
        "representative": "Hon. Nancy Pelosi",
        "chamber": "house",
        "source": "house_clerk_pdf",
        "report_url": "https://disclosures-clerk.house.gov/example.pdf",
        "asset_name": "NVIDIA Corporation - Common Stock"
    }


@pytest.fixture
def sample_trades_batch():
    """Batch of sample trades for testing"""
    return [
        {
            "ticker": "AAPL",
            "transaction_type": "purchase",
            "amount": 500000,
            "representative": "Hon. Nancy Pelosi",
            "chamber": "house",
            "transaction_date": "01/10/2026",
            "disclosure_date": "01/15/2026",
            "source": "house_clerk_pdf"
        },
        {
            "ticker": "GOOGL",
            "transaction_type": "purchase",
            "amount": 250000,
            "representative": "Dan Crenshaw",
            "chamber": "house",
            "transaction_date": "01/11/2026",
            "disclosure_date": "01/16/2026",
            "source": "house_clerk_pdf"
        },
        {
            "ticker": "MSFT",
            "transaction_type": "sale",
            "amount": 100000,
            "representative": "Tommy Tuberville",
            "chamber": "senate",
            "transaction_date": "01/12/2026",
            "disclosure_date": "01/17/2026",
            "source": "senate_efd"
        }
    ]


@pytest.fixture
def mock_broker():
    """Mock broker adapter for testing"""
    broker = MagicMock()
    broker.BROKER_NAME = "MockBroker"
    broker.is_authenticated = True
    broker.account_id = "test-account-123"

    # Mock account balance
    broker.get_account_balance.return_value = {
        'cash_available': 25000.0,
        'total_value': 50000.0
    }

    # Mock positions
    broker.get_positions.return_value = []

    # Mock quotes
    def mock_quote(symbol):
        quotes = {
            'NVDA': {'symbol': 'NVDA', 'last_price': 500.0, 'bid': 499.50, 'ask': 500.50},
            'AAPL': {'symbol': 'AAPL', 'last_price': 180.0, 'bid': 179.90, 'ask': 180.10},
            'GOOGL': {'symbol': 'GOOGL', 'last_price': 140.0, 'bid': 139.90, 'ask': 140.10},
            'MSFT': {'symbol': 'MSFT', 'last_price': 400.0, 'bid': 399.90, 'ask': 400.10},
        }
        return quotes.get(symbol.upper())

    broker.get_quote.side_effect = mock_quote

    # Mock order placement
    broker.place_order.return_value = True
    broker.validate_order.return_value = (True, "")

    return broker


@pytest.fixture
def temp_config_file(sample_config):
    """Create a temporary config file"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_config, f)
        yield f.name
    if os.path.exists(f.name):
        os.remove(f.name)
