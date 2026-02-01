"""Tests for setup wizard functionality."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
import json
from unittest.mock import patch
from setup import load_sources, save_sources, get_default_sources, setup_language, setup_markets


def test_load_sources_missing_file(tmp_path, monkeypatch):
    """Test loading non-existent sources returns defaults."""
    sources_file = tmp_path / "sources.json"
    
    # Patch both path constants to use temp file
    monkeypatch.setattr("setup.SOURCES_FILE", sources_file)
    
    # File doesn't exist, so load_sources should call get_default_sources
    sources = load_sources()
    
    assert isinstance(sources, dict)
    assert "rss_feeds" in sources  # Default structure has rss_feeds


def test_save_sources(tmp_path, monkeypatch):
    """Test saving sources to JSON."""
    sources_file = tmp_path / "sources.json"
    monkeypatch.setattr("setup.SOURCES_FILE", sources_file)
    
    sources = {
        "rss_feeds": {
            "test_source": {
                "name": "Test",
                "enabled": True,
                "top": "https://example.com/rss"
            }
        }
    }
    
    save_sources(sources)
    
    assert sources_file.exists()
    with open(sources_file) as f:
        saved = json.load(f)
    
    assert saved["rss_feeds"]["test_source"]["enabled"] is True


def test_get_default_sources():
    """Test default sources structure."""
    sources = get_default_sources()
    
    assert isinstance(sources, dict)
    assert "rss_feeds" in sources
    # Should have common sources like wsj, barrons, cnbc
    feeds = sources["rss_feeds"]
    assert any("wsj" in k.lower() or "barrons" in k.lower() or "cnbc" in k.lower()
               for k in feeds.keys())


@patch("setup.prompt", side_effect=["en"])
@patch("setup.save_sources")
def test_setup_language(mock_save, mock_prompt):
    """Test language setup function."""
    sources = {"language": {"supported": ["en", "de"], "default": "de"}}
    setup_language(sources)
    
    # Should have called prompt
    mock_prompt.assert_called()
    # Language should be updated
    assert sources["language"]["default"] == "en"


@patch("setup.prompt_bool", side_effect=[True, False])
@patch("setup.save_sources")
def test_setup_markets(mock_save, mock_prompt):
    """Test markets setup function."""
    sources = {"markets": {"us": {"enabled": False}, "eu": {"enabled": False}}}
    setup_markets(sources)
    
    # Should have prompted (at least once for US)
    assert mock_prompt.called
