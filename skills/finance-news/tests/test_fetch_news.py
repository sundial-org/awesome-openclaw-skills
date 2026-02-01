"""Tests for RSS feed fetching and parsing."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
from fetch_news import fetch_market_data, fetch_rss, _get_best_feed_url
from utils import clamp_timeout, compute_deadline


@pytest.fixture
def sample_rss_content():
    """Load sample RSS fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_rss.xml"
    return fixture_path.read_bytes()


def test_fetch_rss_success(sample_rss_content):
    """Test successful RSS fetch and parse."""
    with patch("urllib.request.urlopen") as mock_urlopen:
        mock_response = MagicMock()
        mock_response.read.return_value = sample_rss_content
        mock_response.__enter__.return_value = mock_response
        mock_urlopen.return_value = mock_response
        
        articles = fetch_rss("https://example.com/feed.xml", timeout=7)
        
        assert len(articles) == 2
        assert articles[0]["title"] == "Apple Stock Rises 5%"
        assert articles[1]["title"] == "Tesla Announces New Model"
        assert "apple-rises" in articles[0]["link"]
        assert mock_urlopen.call_args.kwargs["timeout"] == 7


def test_fetch_rss_network_error():
    """Test RSS fetch handles network errors."""
    with patch("urllib.request.urlopen", side_effect=Exception("Network error")):
        articles = fetch_rss("https://example.com/feed.xml")
        assert articles == []


def test_get_best_feed_url_priority():
    """Test feed URL selection prioritizes 'top' key."""
    source = {
        "name": "Test Source",
        "homepage": "https://example.com",
        "top": "https://example.com/top.xml",
        "markets": "https://example.com/markets.xml"
    }
    
    url = _get_best_feed_url(source)
    assert url == "https://example.com/top.xml"


def test_get_best_feed_url_fallback():
    """Test feed URL falls back to other http URLs when priority keys missing."""
    source = {
        "name": "Test Source",
        "feed": "https://example.com/feed.xml"
    }
    
    url = _get_best_feed_url(source)
    assert url == "https://example.com/feed.xml"


def test_get_best_feed_url_none_if_no_urls():
    """Test returns None when no valid URLs found."""
    source = {
        "name": "Test Source",
        "enabled": True,
        "note": "No URLs here"
    }
    
    url = _get_best_feed_url(source)
    assert url is None


def test_get_best_feed_url_skips_non_urls():
    """Test skips non-URL values."""
    source = {
        "name": "Test Source",
        "enabled": True,
        "count": 5,
        "rss": "https://example.com/rss.xml"
    }
    
    url = _get_best_feed_url(source)
    assert url == "https://example.com/rss.xml"


def test_clamp_timeout_respects_deadline(monkeypatch):
    start = 100.0
    monkeypatch.setattr("utils.time.monotonic", lambda: start)
    deadline = compute_deadline(5)
    monkeypatch.setattr("utils.time.monotonic", lambda: 103.0)

    assert clamp_timeout(30, deadline) == 2


def test_clamp_timeout_deadline_exceeded(monkeypatch):
    start = 200.0
    monkeypatch.setattr("utils.time.monotonic", lambda: start)
    deadline = compute_deadline(1)
    monkeypatch.setattr("utils.time.monotonic", lambda: 205.0)

    with pytest.raises(TimeoutError):
        clamp_timeout(30, deadline)


def test_fetch_market_data_price_fallback(monkeypatch):
    sample = {
        "price": None,
        "open": 100,
        "prev_close": 105,
        "change_percent": None,
    }

    def fake_run(*_args, **_kwargs):
        class Result:
            returncode = 0
            stdout = json.dumps(sample)
            stderr = ""

        return Result()

    monkeypatch.setattr("fetch_news.OPENBB_BINARY", "/bin/openbb-quote")
    monkeypatch.setattr("fetch_news.subprocess.run", fake_run)

    no_fallback = fetch_market_data(["^GSPC"], allow_price_fallback=False)
    assert no_fallback["^GSPC"]["price"] is None

    with_fallback = fetch_market_data(["^GSPC"], allow_price_fallback=True)
    assert with_fallback["^GSPC"]["price"] == 100
