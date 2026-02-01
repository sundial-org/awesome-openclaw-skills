"""Tests for summarize helpers."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from datetime import datetime

import summarize
from summarize import (
    MoverContext,
    SectorCluster,
    WatchpointsData,
    build_watchpoints_data,
    classify_move_type,
    detect_sector_clusters,
    format_watchpoints,
    get_index_change,
    match_headline_to_symbol,
)


class FixedDateTime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 1, 1, 15, 0)


def test_generate_briefing_auto_time_evening(capsys, monkeypatch):
    def fake_market_news(*_args, **_kwargs):
        return {
            "headlines": [
                {"source": "CNBC", "title": "Headline one", "link": "https://example.com/1"},
                {"source": "Yahoo", "title": "Headline two", "link": "https://example.com/2"},
                {"source": "CNBC", "title": "Headline three", "link": "https://example.com/3"},
            ],
            "markets": {
                "us": {
                    "name": "US Markets",
                    "indices": {
                        "^GSPC": {"name": "S&P 500", "data": {"price": 100, "change_percent": 1.0}},
                    },
                }
            },
        }

    def fake_summary(*_args, **_kwargs):
        return "OK"

    monkeypatch.setattr(summarize, "get_market_news", fake_market_news)
    monkeypatch.setattr(summarize, "get_portfolio_news", lambda *_a, **_k: None)
    monkeypatch.setattr(summarize, "summarize_with_claude", fake_summary)
    monkeypatch.setattr(summarize, "datetime", FixedDateTime)

    args = type(
        "Args",
        (),
        {
            "lang": "de",
            "style": "briefing",
            "time": None,
            "model": "claude",
            "json": False,
            "research": False,
            "deadline": None,
            "fast": False,
            "llm": False,
            "debug": False,
        },
    )()

    summarize.generate_briefing(args)
    stdout = capsys.readouterr().out
    assert "Börsen Abend-Briefing" in stdout


# --- Tests for watchpoints feature (Issue #92) ---


class TestGetIndexChange:
    def test_extracts_sp500_change(self):
        market_data = {
            "markets": {
                "us": {
                    "indices": {
                        "^GSPC": {"data": {"change_percent": -1.5}}
                    }
                }
            }
        }
        assert get_index_change(market_data) == -1.5

    def test_returns_zero_on_missing_data(self):
        assert get_index_change({}) == 0.0
        assert get_index_change({"markets": {}}) == 0.0
        assert get_index_change({"markets": {"us": {}}}) == 0.0


class TestMatchHeadlineToSymbol:
    def test_exact_symbol_match_dollar(self):
        headlines = [{"title": "Breaking: $NVDA surges on AI demand"}]
        result = match_headline_to_symbol("NVDA", "NVIDIA Corporation", headlines)
        assert result is not None
        assert "NVDA" in result["title"]

    def test_exact_symbol_match_parens(self):
        headlines = [{"title": "Tesla (TSLA) reports record deliveries"}]
        result = match_headline_to_symbol("TSLA", "Tesla Inc", headlines)
        assert result is not None

    def test_exact_symbol_match_word_boundary(self):
        headlines = [{"title": "AAPL announces new product line"}]
        result = match_headline_to_symbol("AAPL", "Apple Inc", headlines)
        assert result is not None

    def test_company_name_match(self):
        headlines = [{"title": "Apple announces record iPhone sales"}]
        result = match_headline_to_symbol("AAPL", "Apple Inc", headlines)
        assert result is not None

    def test_no_match_returns_none(self):
        headlines = [{"title": "Fed raises interest rates"}]
        result = match_headline_to_symbol("NVDA", "NVIDIA Corporation", headlines)
        assert result is None

    def test_avoids_partial_symbol_match(self):
        # "APP" should not match "application"
        headlines = [{"title": "New application launches today"}]
        result = match_headline_to_symbol("APP", "AppLovin Corp", headlines)
        assert result is None

    def test_empty_headlines(self):
        result = match_headline_to_symbol("NVDA", "NVIDIA", [])
        assert result is None


class TestDetectSectorClusters:
    def test_detects_cluster_three_stocks_same_direction(self):
        movers = [
            {"symbol": "NVDA", "change_pct": -5.0},
            {"symbol": "AMD", "change_pct": -4.0},
            {"symbol": "INTC", "change_pct": -3.0},
        ]
        portfolio_meta = {
            "NVDA": {"category": "Tech"},
            "AMD": {"category": "Tech"},
            "INTC": {"category": "Tech"},
        }
        clusters = detect_sector_clusters(movers, portfolio_meta)
        assert len(clusters) == 1
        assert clusters[0].category == "Tech"
        assert clusters[0].direction == "down"
        assert len(clusters[0].stocks) == 3

    def test_no_cluster_if_less_than_three(self):
        movers = [
            {"symbol": "NVDA", "change_pct": -5.0},
            {"symbol": "AMD", "change_pct": -4.0},
        ]
        portfolio_meta = {
            "NVDA": {"category": "Tech"},
            "AMD": {"category": "Tech"},
        }
        clusters = detect_sector_clusters(movers, portfolio_meta)
        assert len(clusters) == 0

    def test_no_cluster_if_mixed_direction(self):
        movers = [
            {"symbol": "NVDA", "change_pct": 5.0},
            {"symbol": "AMD", "change_pct": -4.0},
            {"symbol": "INTC", "change_pct": 3.0},
        ]
        portfolio_meta = {
            "NVDA": {"category": "Tech"},
            "AMD": {"category": "Tech"},
            "INTC": {"category": "Tech"},
        }
        clusters = detect_sector_clusters(movers, portfolio_meta)
        assert len(clusters) == 0


class TestClassifyMoveType:
    def test_earnings_with_keyword(self):
        headline = {"title": "Company beats Q3 earnings expectations"}
        result = classify_move_type(headline, False, 5.0, 0.1)
        assert result == "earnings"

    def test_sector_cluster(self):
        result = classify_move_type(None, True, -3.0, -0.5)
        assert result == "sector"

    def test_market_wide(self):
        result = classify_move_type(None, False, -2.0, -2.0)
        assert result == "market_wide"

    def test_company_specific_with_headline(self):
        headline = {"title": "Company announces acquisition"}
        result = classify_move_type(headline, False, 3.0, 0.1)
        assert result == "company_specific"

    def test_company_specific_large_move_no_headline(self):
        result = classify_move_type(None, False, 8.0, 0.1)
        assert result == "company_specific"

    def test_unknown_small_move_no_context(self):
        result = classify_move_type(None, False, 1.5, 0.2)
        assert result == "unknown"


class TestFormatWatchpoints:
    def test_formats_sector_cluster(self):
        cluster = SectorCluster(
            category="Tech",
            stocks=[
                MoverContext("NVDA", -5.0, 100.0, "Tech", None, "sector", None, None),
                MoverContext("AMD", -4.0, 80.0, "Tech", None, "sector", None, None),
                MoverContext("INTC", -3.0, 30.0, "Tech", None, "sector", None, None),
            ],
            avg_change=-4.0,
            direction="down",
            vs_index=-3.5,
        )
        data = WatchpointsData(
            movers=[],
            sector_clusters=[cluster],
            index_change=-0.5,
            market_wide=False,
        )
        result = format_watchpoints(data, "en", {})
        assert "Tech" in result
        assert "-4.0%" in result
        assert "vs Index" in result

    def test_formats_individual_mover_with_headline(self):
        mover = MoverContext(
            symbol="NVDA",
            change_pct=5.0,
            price=100.0,
            category="Tech",
            matched_headline={"title": "NVIDIA reports record revenue"},
            move_type="company_specific",
            vs_index=4.5,
        )
        data = WatchpointsData(
            movers=[mover],
            sector_clusters=[],
            index_change=0.5,
            market_wide=False,
        )
        result = format_watchpoints(data, "en", {})
        assert "NVDA" in result
        assert "+5.0%" in result
        assert "record revenue" in result

    def test_formats_market_wide_move_english(self):
        data = WatchpointsData(
            movers=[],
            sector_clusters=[],
            index_change=-2.0,
            market_wide=True,
        )
        result = format_watchpoints(data, "en", {})
        assert "Market-wide move" in result
        assert "S&P 500 fell 2.0%" in result

    def test_formats_market_wide_move_german(self):
        data = WatchpointsData(
            movers=[],
            sector_clusters=[],
            index_change=2.5,
            market_wide=True,
        )
        result = format_watchpoints(data, "de", {})
        assert "Breite Marktbewegung" in result
        assert "stieg 2.5%" in result

    def test_uses_label_fallbacks(self):
        mover = MoverContext(
            symbol="XYZ",
            change_pct=1.5,
            price=50.0,
            category="Other",
            matched_headline=None,
            move_type="unknown",
            vs_index=1.0,
        )
        data = WatchpointsData(
            movers=[mover],
            sector_clusters=[],
            index_change=0.5,
            market_wide=False,
        )
        labels = {"no_catalyst": " -- no news"}
        result = format_watchpoints(data, "en", labels)
        assert "XYZ" in result
        assert "no news" in result


class TestBuildWatchpointsData:
    def test_builds_complete_data_structure(self):
        movers = [
            {"symbol": "NVDA", "change_pct": -5.0, "price": 100.0},
            {"symbol": "AMD", "change_pct": -4.0, "price": 80.0},
            {"symbol": "INTC", "change_pct": -3.0, "price": 30.0},
            {"symbol": "AAPL", "change_pct": 2.0, "price": 150.0},
        ]
        headlines = [
            {"title": "NVIDIA reports weak guidance"},
            {"title": "Apple announces new product"},
        ]
        portfolio_meta = {
            "NVDA": {"category": "Tech", "name": "NVIDIA Corporation"},
            "AMD": {"category": "Tech", "name": "Advanced Micro Devices"},
            "INTC": {"category": "Tech", "name": "Intel Corporation"},
            "AAPL": {"category": "Tech", "name": "Apple Inc"},
        }
        index_change = -0.5

        result = build_watchpoints_data(movers, headlines, portfolio_meta, index_change)

        # Should detect Tech sector cluster (3 losers)
        assert len(result.sector_clusters) == 1
        assert result.sector_clusters[0].category == "Tech"
        assert result.sector_clusters[0].direction == "down"

        # All movers should be present
        assert len(result.movers) == 4

        # NVDA should have matched headline
        nvda_mover = next(m for m in result.movers if m.symbol == "NVDA")
        assert nvda_mover.matched_headline is not None
        assert "guidance" in nvda_mover.matched_headline["title"]

        # vs_index should be calculated
        assert nvda_mover.vs_index == -5.0 - (-0.5)  # -4.5

    def test_handles_empty_movers(self):
        result = build_watchpoints_data([], [], {}, 0.0)
        assert result.movers == []
        assert result.sector_clusters == []
        assert result.market_wide is False

    def test_detects_market_wide_move(self):
        result = build_watchpoints_data([], [], {}, -2.0)
        assert result.market_wide is True
