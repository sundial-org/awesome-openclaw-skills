"""Tests for portfolio operations."""
import sys
from pathlib import Path

# Add scripts to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pytest
from portfolio import load_portfolio, save_portfolio


def test_load_portfolio_success(tmp_path, monkeypatch):
    """Test loading valid portfolio CSV."""
    portfolio_file = tmp_path / "portfolio.csv"
    portfolio_file.write_text("symbol,name,category,notes,type\nAAPL,Apple,Tech,,\nTSLA,Tesla,Auto,,\n")
    
    monkeypatch.setattr("portfolio.PORTFOLIO_FILE", portfolio_file)
    positions = load_portfolio()
    
    assert len(positions) == 2
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["name"] == "Apple"
    assert positions[1]["symbol"] == "TSLA"


def test_load_portfolio_missing_file(tmp_path, monkeypatch):
    """Test loading non-existent portfolio returns empty list."""
    portfolio_file = tmp_path / "nonexistent.csv"
    monkeypatch.setattr("portfolio.PORTFOLIO_FILE", portfolio_file)
    
    positions = load_portfolio()
    assert positions == []


def test_save_portfolio(tmp_path, monkeypatch):
    """Test saving portfolio to CSV."""
    portfolio_file = tmp_path / "portfolio.csv"
    monkeypatch.setattr("portfolio.PORTFOLIO_FILE", portfolio_file)
    
    positions = [
        {"symbol": "AAPL", "name": "Apple", "category": "Tech", "notes": "", "type": "stock"},
        {"symbol": "MSFT", "name": "Microsoft", "category": "Tech", "notes": "", "type": "stock"}
    ]
    save_portfolio(positions)
    
    content = portfolio_file.read_text()
    assert "symbol,name,category,notes,type" in content
    assert "AAPL" in content
    assert "MSFT" in content


def test_save_empty_portfolio(tmp_path, monkeypatch):
    """Test saving empty portfolio creates header."""
    portfolio_file = tmp_path / "portfolio.csv"
    monkeypatch.setattr("portfolio.PORTFOLIO_FILE", portfolio_file)
    
    save_portfolio([])
    
    content = portfolio_file.read_text()
    assert content == "symbol,name,category,notes,type\n"


def test_load_portfolio_preserves_fields(tmp_path, monkeypatch):
    """Test loading portfolio preserves all fields."""
    portfolio_file = tmp_path / "portfolio.csv"
    portfolio_file.write_text("symbol,name,category,notes,type\nAAPL,Apple Inc,Tech,Core holding,stock\n")
    monkeypatch.setattr("portfolio.PORTFOLIO_FILE", portfolio_file)
    
    positions = load_portfolio()
    
    assert len(positions) == 1
    assert positions[0]["symbol"] == "AAPL"
    assert positions[0]["name"] == "Apple Inc"
    assert positions[0]["category"] == "Tech"
    assert positions[0]["notes"] == "Core holding"
    assert positions[0]["type"] == "stock"
