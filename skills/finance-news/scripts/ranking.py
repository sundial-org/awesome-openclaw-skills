#!/usr/bin/env python3
"""
Deterministic Headline Ranking - Impact-based ranking policy.

Implements #53: Deterministic impact-based ranking for headline selection.

Scoring Rubric (weights):
- Market Impact (40%): CB decisions, earnings, sanctions, oil spikes
- Novelty (20%): New vs recycled news
- Breadth (20%): Sector-wide vs single-stock
- Credibility (10%): Source reliability
- Diversity Bonus (10%): Underrepresented categories

Output:
- MUST_READ: Top 5 stories
- SCAN: 3-5 additional stories (if quality threshold met)
"""

import re
from datetime import datetime
from difflib import SequenceMatcher


# Category keywords for classification
CATEGORY_KEYWORDS = {
    "macro": ["fed", "ecb", "boj", "central bank", "rate", "inflation", "gdp", "unemployment", "treasury", "yield", "bond"],
    "equities": ["earnings", "revenue", "profit", "eps", "guidance", "beat", "miss", "upgrade", "downgrade", "target"],
    "geopolitics": ["sanction", "tariff", "war", "conflict", "embargo", "trump", "china", "russia", "ukraine", "iran", "trade war"],
    "energy": ["oil", "opec", "crude", "gas", "energy", "brent", "wti"],
    "tech": ["ai", "chip", "semiconductor", "nvidia", "apple", "google", "microsoft", "meta", "amazon"],
}

# Source credibility scores (0-1)
SOURCE_CREDIBILITY = {
    "Wall Street Journal": 0.95,
    "WSJ": 0.95,
    "Bloomberg": 0.95,
    "Reuters": 0.90,
    "Financial Times": 0.90,
    "CNBC": 0.80,
    "Yahoo Finance": 0.70,
    "MarketWatch": 0.75,
    "Barron's": 0.85,
    "Seeking Alpha": 0.60,
    "Tagesschau": 0.85,
    "Handelsblatt": 0.80,
}

# Default config
DEFAULT_CONFIG = {
    "dedupe_threshold": 0.7,
    "must_read_count": 5,
    "scan_count": 5,
    "must_read_min_score": 0.4,
    "scan_min_score": 0.25,
    "source_cap": 2,
    "weights": {
        "market_impact": 0.40,
        "novelty": 0.20,
        "breadth": 0.20,
        "credibility": 0.10,
        "diversity": 0.10,
    },
}


def normalize_title(title: str) -> str:
    """Normalize title for comparison."""
    if not title:
        return ""
    cleaned = re.sub(r"[^a-z0-9\s]", " ", title.lower())
    tokens = cleaned.split()
    return " ".join(tokens)


def title_similarity(a: str, b: str) -> float:
    """Calculate title similarity using SequenceMatcher."""
    if not a or not b:
        return 0.0
    return SequenceMatcher(None, normalize_title(a), normalize_title(b)).ratio()


def deduplicate_headlines(headlines: list[dict], threshold: float = 0.7) -> list[dict]:
    """Remove duplicate headlines by title similarity."""
    if not headlines:
        return []
    
    unique = []
    for article in headlines:
        title = article.get("title", "")
        is_dupe = False
        for existing in unique:
            if title_similarity(title, existing.get("title", "")) > threshold:
                is_dupe = True
                break
        if not is_dupe:
            unique.append(article)
    
    return unique


def classify_category(title: str, description: str = "") -> list[str]:
    """Classify headline into categories based on keywords."""
    text = f"{title} {description}".lower()
    categories = []
    
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text:
                categories.append(category)
                break
    
    return categories if categories else ["general"]


def score_market_impact(title: str, description: str = "") -> float:
    """Score market impact (0-1)."""
    text = f"{title} {description}".lower()
    score = 0.3  # Base score
    
    # High impact indicators
    high_impact = ["fed", "rate cut", "rate hike", "earnings", "guidance", "sanctions", "war", "oil", "recession"]
    for term in high_impact:
        if term in text:
            score += 0.15
    
    # Medium impact
    medium_impact = ["profit", "revenue", "gdp", "inflation", "tariff", "merger", "acquisition"]
    for term in medium_impact:
        if term in text:
            score += 0.1
    
    return min(score, 1.0)


def score_novelty(article: dict) -> float:
    """Score novelty based on recency (0-1)."""
    published_at = article.get("published_at")
    if not published_at:
        return 0.5  # Unknown = medium
    
    try:
        if isinstance(published_at, str):
            pub_time = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
        else:
            pub_time = published_at
        
        hours_old = (datetime.now(pub_time.tzinfo) - pub_time).total_seconds() / 3600
        
        if hours_old < 2:
            return 1.0
        elif hours_old < 6:
            return 0.8
        elif hours_old < 12:
            return 0.6
        elif hours_old < 24:
            return 0.4
        else:
            return 0.2
    except Exception:
        return 0.5


def score_breadth(categories: list[str]) -> float:
    """Score breadth - sector-wide vs single-stock (0-1)."""
    # More categories = broader impact
    if "macro" in categories or "geopolitics" in categories:
        return 0.9
    if "energy" in categories:
        return 0.7
    if len(categories) > 1:
        return 0.6
    return 0.4


def score_credibility(source: str) -> float:
    """Score source credibility (0-1)."""
    return SOURCE_CREDIBILITY.get(source, 0.5)


def calculate_score(article: dict, weights: dict, category_counts: dict) -> float:
    """Calculate overall score for a headline."""
    title = article.get("title", "")
    description = article.get("description", "")
    source = article.get("source", "")
    categories = classify_category(title, description)
    article["_categories"] = categories  # Store for later use
    
    # Component scores
    impact = score_market_impact(title, description)
    novelty = score_novelty(article)
    breadth = score_breadth(categories)
    credibility = score_credibility(source)
    
    # Diversity bonus - boost underrepresented categories
    diversity = 0.0
    for cat in categories:
        if category_counts.get(cat, 0) < 1:
            diversity = 0.5
            break
        elif category_counts.get(cat, 0) < 2:
            diversity = 0.3
    
    # Weighted sum
    score = (
        impact * weights.get("market_impact", 0.4) +
        novelty * weights.get("novelty", 0.2) +
        breadth * weights.get("breadth", 0.2) +
        credibility * weights.get("credibility", 0.1) +
        diversity * weights.get("diversity", 0.1)
    )
    
    article["_score"] = round(score, 3)
    article["_impact"] = round(impact, 3)
    article["_novelty"] = round(novelty, 3)
    
    return score


def apply_source_cap(ranked: list[dict], cap: int = 2) -> list[dict]:
    """Apply source cap - max N items per outlet."""
    source_counts = {}
    result = []
    
    for article in ranked:
        source = article.get("source", "Unknown")
        if source_counts.get(source, 0) < cap:
            result.append(article)
            source_counts[source] = source_counts.get(source, 0) + 1
    
    return result


def ensure_diversity(selected: list[dict], candidates: list[dict], required: list[str]) -> list[dict]:
    """Ensure at least one headline from required categories if available."""
    result = list(selected)
    covered = set()
    
    for article in result:
        for cat in article.get("_categories", []):
            covered.add(cat)
    
    for req_cat in required:
        if req_cat not in covered:
            # Find candidate from this category
            for candidate in candidates:
                if candidate not in result and req_cat in candidate.get("_categories", []):
                    result.append(candidate)
                    covered.add(req_cat)
                    break
    
    return result


def rank_headlines(headlines: list[dict], config: dict | None = None) -> dict:
    """
    Rank headlines deterministically.
    
    Args:
        headlines: List of headline dicts with title, source, description, etc.
        config: Optional config overrides
    
    Returns:
        {"must_read": [...], "scan": [...]}
    """
    cfg = {**DEFAULT_CONFIG, **(config or {})}
    weights = cfg.get("weights", DEFAULT_CONFIG["weights"])
    
    if not headlines:
        return {"must_read": [], "scan": []}
    
    # Step 1: Deduplicate
    unique = deduplicate_headlines(headlines, cfg["dedupe_threshold"])
    
    # Step 2: Score all headlines
    category_counts = {}
    for article in unique:
        calculate_score(article, weights, category_counts)
        for cat in article.get("_categories", []):
            category_counts[cat] = category_counts.get(cat, 0) + 1
    
    # Step 3: Sort by score
    ranked = sorted(unique, key=lambda x: x.get("_score", 0), reverse=True)
    
    # Step 4: Apply source cap
    capped = apply_source_cap(ranked, cfg["source_cap"])
    
    # Step 5: Select must_read with diversity quota
    # Leave room for diversity additions by taking count-1 initially
    must_read_candidates = [a for a in capped if a.get("_score", 0) >= cfg["must_read_min_score"]]
    must_read_count = cfg["must_read_count"]
    must_read = must_read_candidates[:max(1, must_read_count - 2)]  # Reserve 2 slots for diversity
    must_read = ensure_diversity(must_read, capped, ["macro", "equities", "geopolitics"])
    must_read = must_read[:must_read_count]  # Final trim to exact count
    
    # Step 6: Select scan (additional items)
    scan_candidates = [a for a in capped if a not in must_read and a.get("_score", 0) >= cfg["scan_min_score"]]
    scan = scan_candidates[:cfg["scan_count"]]
    
    return {
        "must_read": must_read,
        "scan": scan,
        "total_processed": len(headlines),
        "after_dedupe": len(unique),
    }


if __name__ == "__main__":
    # Test with sample data
    test_headlines = [
        {"title": "Fed signals rate cut in March", "source": "WSJ", "description": "Federal Reserve hints at policy shift"},
        {"title": "Apple earnings beat expectations", "source": "CNBC", "description": "Revenue up 15%"},
        {"title": "Oil prices surge on OPEC cuts", "source": "Reuters", "description": "Brent crude hits $90"},
        {"title": "China-US trade tensions escalate", "source": "Bloomberg", "description": "New tariffs announced"},
        {"title": "Tech stocks rally on AI optimism", "source": "Yahoo Finance", "description": "Nvidia leads gains"},
        {"title": "Fed hints at rate reduction", "source": "MarketWatch", "description": "Same story as WSJ"},  # Dupe
    ]
    
    result = rank_headlines(test_headlines)
    print("MUST_READ:")
    for h in result["must_read"]:
        print(f"  [{h['_score']:.2f}] {h['title']} ({h['source']})")
    print("\nSCAN:")
    for h in result["scan"]:
        print(f"  [{h['_score']:.2f}] {h['title']} ({h['source']})")
