import sys
from pathlib import Path
import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from alerts import check_alerts, load_alerts, save_alerts

@pytest.fixture
def mock_alerts_data():
    return {
        "_meta": {"version": 1, "supported_currencies": ["USD", "EUR"]},
        "alerts": [
            {
                "ticker": "AAPL",
                "target_price": 150.0,
                "currency": "USD",
                "note": "Buy Apple",
                "triggered_count": 0,
                "last_triggered": None
            },
            {
                "ticker": "TSLA",
                "target_price": 200.0,
                "currency": "USD",
                "note": "Buy Tesla",
                "triggered_count": 5,
                "last_triggered": "2026-01-26T10:00:00"
            }
        ]
    }

def test_check_alerts_trigger(mock_alerts_data, monkeypatch, tmp_path):
    # Setup mock alerts file
    alerts_file = tmp_path / "alerts.json"
    monkeypatch.setattr("alerts.ALERTS_FILE", alerts_file)
    alerts_file.write_text(json.dumps(mock_alerts_data))
    
    # Mock market data: AAPL is under target, TSLA is over
    mock_quotes = {
        "AAPL": {"price": 145.0},
        "TSLA": {"price": 210.0}
    }
    
    with patch("alerts.get_fetch_market_data") as mock_fmd_getter:
        mock_fmd = Mock(return_value=mock_quotes)
        mock_fmd_getter.return_value = mock_fmd
        
        results = check_alerts()
        
        assert len(results["triggered"]) == 1
        assert results["triggered"][0]["ticker"] == "AAPL"
        assert results["triggered"][0]["current_price"] == 145.0
        
        assert len(results["watching"]) == 1
        assert results["watching"][0]["ticker"] == "TSLA"
        
        # Verify triggered count incremented for AAPL
        updated_data = json.loads(alerts_file.read_text())
        aapl_alert = next(a for a in updated_data["alerts"] if a["ticker"] == "AAPL")
        assert aapl_alert["triggered_count"] == 1
        assert aapl_alert["last_triggered"] is not None

def test_check_alerts_deduplication(mock_alerts_data, monkeypatch, tmp_path):
    # If already triggered today, triggered_count should NOT increment
    now = datetime.now()
    mock_alerts_data["alerts"][0]["last_triggered"] = now.isoformat()
    mock_alerts_data["alerts"][0]["triggered_count"] = 1
    
    alerts_file = tmp_path / "alerts.json"
    monkeypatch.setattr("alerts.ALERTS_FILE", alerts_file)
    alerts_file.write_text(json.dumps(mock_alerts_data))
    
    mock_quotes = {"AAPL": {"price": 140.0}, "TSLA": {"price": 250.0}}
    
    with patch("alerts.get_fetch_market_data") as mock_fmd_getter:
        mock_fmd = Mock(return_value=mock_quotes)
        mock_fmd_getter.return_value = mock_fmd
        
        check_alerts()
        
        updated_data = json.loads(alerts_file.read_text())
        aapl_alert = next(a for a in updated_data["alerts"] if a["ticker"] == "AAPL")
        assert aapl_alert["triggered_count"] == 1 # Still 1, didn't increment because same day

def test_check_alerts_snooze(mock_alerts_data, monkeypatch, tmp_path):
    # Snoozed alert should be ignored
    future_date = datetime.now() + timedelta(days=1)
    mock_alerts_data["alerts"][0]["snooze_until"] = future_date.isoformat()
    
    alerts_file = tmp_path / "alerts.json"
    monkeypatch.setattr("alerts.ALERTS_FILE", alerts_file)
    alerts_file.write_text(json.dumps(mock_alerts_data))
    
    mock_quotes = {"AAPL": {"price": 140.0}, "TSLA": {"price": 190.0}}
    
    with patch("alerts.get_fetch_market_data") as mock_fmd_getter:
        mock_fmd = Mock(return_value=mock_quotes)
        mock_fmd_getter.return_value = mock_fmd
        
        results = check_alerts()
        
        # AAPL is snoozed, so only TSLA should be in triggered
        assert len(results["triggered"]) == 1
        assert results["triggered"][0]["ticker"] == "TSLA"
        assert all(t["ticker"] != "AAPL" for t in results["triggered"])
