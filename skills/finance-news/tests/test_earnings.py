import sys
from pathlib import Path
import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from earnings import (
    fetch_all_earnings_finnhub,
    get_briefing_section,
    load_earnings_cache,
    save_earnings_cache,
    refresh_earnings
)

@pytest.fixture
def mock_finnhub_response():
    return {
        "earningsCalendar": [
            {
                "symbol": "AAPL",
                "date": "2026-02-01",
                "hour": "amc",
                "epsEstimate": 1.5,
                "revenueEstimate": 100000000,
                "quarter": 1,
                "year": 2026
            },
            {
                "symbol": "TSLA",
                "date": "2026-01-27",
                "hour": "bmo",
                "epsEstimate": 0.8,
                "revenueEstimate": 25000000,
                "quarter": 4,
                "year": 2025
            }
        ]
    }

def test_fetch_earnings_finnhub_success(mock_finnhub_response):
    with patch("earnings.urlopen") as mock_urlopen:
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(mock_finnhub_response).encode("utf-8")
        mock_resp.__enter__.return_value = mock_resp
        mock_urlopen.return_value = mock_resp
        
        with patch("earnings.get_finnhub_key", return_value="fake_key"):
            result = fetch_all_earnings_finnhub(days_ahead=30)
            
            assert "AAPL" in result
            assert result["AAPL"]["date"] == "2026-02-01"
            assert result["AAPL"]["time"] == "amc"
            assert "TSLA" in result
            assert result["TSLA"]["date"] == "2026-01-27"

def test_cache_logic(tmp_path, monkeypatch):
    cache_file = tmp_path / "earnings_calendar.json"
    monkeypatch.setattr("earnings.EARNINGS_CACHE", cache_file)
    monkeypatch.setattr("earnings.CACHE_DIR", tmp_path)
    
    test_data = {
        "last_updated": "2026-01-27T08:00:00",
        "earnings": {"AAPL": {"date": "2026-02-01"}}
    }
    
    save_earnings_cache(test_data)
    assert cache_file.exists()
    
    loaded_data = load_earnings_cache()
    assert loaded_data["earnings"]["AAPL"]["date"] == "2026-02-01"

def test_get_briefing_section_output():
    # Mock portfolio and cache to return specific earnings
    mock_portfolio = [{"symbol": "AAPL", "name": "Apple", "category": "Tech"}]
    mock_cache = {
        "last_updated": datetime.now().isoformat(),
        "earnings": {
            "AAPL": {
                "date": datetime.now().strftime("%Y-%m-%d"),
                "time": "amc",
                "eps_estimate": 1.5
            }
        }
    }
    
    with patch("earnings.load_portfolio", return_value=mock_portfolio), \
         patch("earnings.load_earnings_cache", return_value=mock_cache), \
         patch("earnings.refresh_earnings", return_value=mock_cache):
        
        section = get_briefing_section()
        assert "## 🔴 EARNINGS TODAY" in section
        assert "**AAPL**" in section
        assert "Apple" in section
        assert "after-close" in section
        assert "Est: $1.50" in section

def test_refresh_earnings_force(mock_finnhub_response):
    mock_portfolio = [{"symbol": "AAPL", "name": "Apple"}]
    
    with patch("earnings.get_finnhub_key", return_value="fake_key"), \
         patch("earnings.fetch_all_earnings_finnhub", return_value={"AAPL": mock_finnhub_response["earningsCalendar"][0]}), \
         patch("earnings.save_earnings_cache") as mock_save:
        
        refresh_earnings(mock_portfolio, force=True)
        assert mock_save.called
        args, _ = mock_save.call_args
        assert "AAPL" in args[0]["earnings"]
