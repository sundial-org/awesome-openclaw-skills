import sys
from pathlib import Path
import pytest
from datetime import datetime, timedelta

# Add scripts to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

from ranking import calculate_score, rank_headlines, classify_category

def test_classify_category():
    assert "macro" in classify_category("Fed signals rate cut")
    assert "equities" in classify_category("Apple earnings beat")
    assert "energy" in classify_category("Oil prices surge")
    assert "tech" in classify_category("AI chip demand remains high")
    assert "geopolitics" in classify_category("US imposes new sanctions on Russia")
    assert classify_category("Weather is nice") == ["general"]

def test_calculate_score_impact():
    weights = {"market_impact": 0.4, "novelty": 0.2, "breadth": 0.2, "credibility": 0.1, "diversity": 0.1}
    category_counts = {}
    
    high_impact = {"title": "Fed announces emergency rate cut", "source": "Reuters", "published_at": datetime.now().isoformat()}
    low_impact = {"title": "Local coffee shop opens", "source": "Blog", "published_at": datetime.now().isoformat()}
    
    score_high = calculate_score(high_impact, weights, category_counts)
    score_low = calculate_score(low_impact, weights, category_counts)
    
    assert score_high > score_low

def test_rank_headlines_deduplication():
    headlines = [
        {"title": "Fed signals rate cut in March", "source": "WSJ"},
        {"title": "FED SIGNALS RATE CUT IN MARCH!!!", "source": "Reuters"}, # Dupe
        {"title": "Apple earnings are out", "source": "CNBC"}
    ]
    
    result = rank_headlines(headlines)
    
    # After dedupe, we should have 2 unique headlines
    assert result["after_dedupe"] == 2
    # must_read should contain the best ones
    assert len(result["must_read"]) <= 2

def test_rank_headlines_sorting():
    headlines = [
        {"title": "Local news", "source": "SmallBlog", "description": "Nothing much"},
        {"title": "FED EMERGENCY RATE CUT", "source": "Bloomberg", "description": "Huge market impact"},
        {"title": "Nvidia Earnings Surprise", "source": "Reuters", "description": "AI demand surges"}
    ]
    
    result = rank_headlines(headlines)
    
    # FED should be first due to macro impact + credibility
    assert "FED" in result["must_read"][0]["title"]
    assert "Nvidia" in result["must_read"][1]["title"]

def test_source_cap():
    # Test that we don't have too many items from the same source
    headlines = [
        {"title": f"Story {i}", "source": "Reuters"} for i in range(10)
    ]
    
    # Default source cap is 2
    result = rank_headlines(headlines)
    
    reuters_in_must_read = [h for h in result["must_read"] if h["source"] == "Reuters"]
    reuters_in_scan = [h for h in result["scan"] if h["source"] == "Reuters"]
    
    assert len(reuters_in_must_read) + len(reuters_in_scan) <= 2
