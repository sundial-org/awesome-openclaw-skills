"""
DataForSEO API Toolkit - Main Entry Point

Simple interface for keyword research across YouTube, landing pages, and site pages.
All results are automatically saved to the /results directory with timestamps.

Usage:
    from main import *

    # Quick keyword research
    result = keyword_research("python tutorial")

    # YouTube-specific research
    result = youtube_keyword_research("video editing tips")

    # Full analysis for content planning
    result = full_keyword_analysis(["seo tools", "keyword research"])
"""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

# Import all API modules
from api.keywords_data import (
    get_search_volume,
    get_keywords_for_site,
    get_ad_traffic_by_keywords,
    get_keywords_for_keywords
)
from api.labs import (
    get_keyword_overview,
    get_keyword_suggestions,
    get_keyword_ideas,
    get_related_keywords,
    get_bulk_keyword_difficulty,
    get_historical_search_volume,
    get_search_intent,
    get_domain_keywords,
    get_competitors
)
from api.serp import (
    get_google_serp,
    get_youtube_serp,
    get_google_maps_serp,
    get_google_news_serp,
    get_google_images_serp,
    get_featured_snippet
)
from api.trends import (
    get_trends_explore,
    get_youtube_trends,
    get_news_trends,
    get_shopping_trends,
    compare_keyword_trends,
    get_trending_now
)
from core.storage import list_results, load_result, get_latest_result


# ============================================================================
# HIGH-LEVEL CONVENIENCE FUNCTIONS
# ============================================================================

def keyword_research(
    keyword: str,
    location_name: str = None,
    include_suggestions: bool = True,
    include_related: bool = True,
    include_difficulty: bool = True
) -> Dict[str, Any]:
    """
    Comprehensive keyword research for a single keyword.

    Performs multiple API calls to gather:
    - Keyword overview (search volume, CPC, competition, search intent)
    - Keyword suggestions (optional)
    - Related keywords (optional)
    - Keyword difficulty (optional)

    Args:
        keyword: The seed keyword to research
        location_name: Target location (default: United States)
        include_suggestions: Include keyword suggestions
        include_related: Include related keywords
        include_difficulty: Include difficulty score

    Returns:
        Dict with keys: overview, suggestions, related, difficulty

    Example:
        >>> result = keyword_research("python programming")
    """
    print(f"\n🔍 Researching keyword: {keyword}")
    results = {}

    # Always get overview
    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=[keyword],
        location_name=location_name
    )

    if include_suggestions:
        print("  → Getting keyword suggestions...")
        results["suggestions"] = get_keyword_suggestions(
            keyword=keyword,
            location_name=location_name,
            limit=50
        )

    if include_related:
        print("  → Getting related keywords...")
        results["related"] = get_related_keywords(
            keyword=keyword,
            location_name=location_name,
            depth=2,
            limit=50
        )

    if include_difficulty:
        print("  → Getting keyword difficulty...")
        results["difficulty"] = get_bulk_keyword_difficulty(
            keywords=[keyword],
            location_name=location_name
        )

    print(f"✅ Research complete for: {keyword}\n")
    return results


def youtube_keyword_research(
    keyword: str,
    location_name: str = None,
    include_serp: bool = True,
    include_trends: bool = True
) -> Dict[str, Any]:
    """
    YouTube-focused keyword research.

    Gathers data specifically useful for YouTube content:
    - Keyword overview with search intent
    - YouTube SERP results (current rankings)
    - YouTube trend data
    - Keyword suggestions

    Args:
        keyword: The keyword to research for YouTube
        location_name: Target location
        include_serp: Include current YouTube rankings
        include_trends: Include YouTube trend data

    Returns:
        Dict with keys: overview, serp, trends, suggestions

    Example:
        >>> result = youtube_keyword_research("video editing tutorial")
    """
    print(f"\n🎬 YouTube keyword research: {keyword}")
    results = {}

    # Keyword overview
    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=[keyword],
        location_name=location_name,
        include_serp_info=True
    )

    # Keyword suggestions
    print("  → Getting keyword suggestions...")
    results["suggestions"] = get_keyword_suggestions(
        keyword=keyword,
        location_name=location_name,
        limit=50
    )

    if include_serp:
        print("  → Getting YouTube rankings...")
        results["youtube_serp"] = get_youtube_serp(
            keyword=keyword,
            location_name=location_name,
            depth=20
        )

    if include_trends:
        print("  → Getting YouTube trends...")
        results["youtube_trends"] = get_youtube_trends(
            keywords=[keyword],
            location_name=location_name
        )

    print(f"✅ YouTube research complete for: {keyword}\n")
    return results


def landing_page_keyword_research(
    keywords: List[str],
    competitor_domain: str = None,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Keyword research for landing page optimization.

    Gathers data useful for landing page SEO:
    - Keyword overview for target keywords
    - Search intent classification
    - Keyword difficulty
    - Google SERP analysis
    - Competitor keywords (if domain provided)

    Args:
        keywords: Target keywords for the landing page
        competitor_domain: Optional competitor domain to analyze
        location_name: Target location

    Returns:
        Dict with comprehensive landing page keyword data

    Example:
        >>> result = landing_page_keyword_research(
        ...     ["best crm software", "crm for small business"],
        ...     competitor_domain="hubspot.com"
        ... )
    """
    print(f"\n📄 Landing page keyword research: {keywords}")
    results = {}

    # Keyword overview
    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=keywords,
        location_name=location_name,
        include_serp_info=True
    )

    # Search intent
    print("  → Getting search intent...")
    results["search_intent"] = get_search_intent(
        keywords=keywords,
        location_name=location_name
    )

    # Difficulty scores
    print("  → Getting keyword difficulty...")
    results["difficulty"] = get_bulk_keyword_difficulty(
        keywords=keywords,
        location_name=location_name
    )

    # SERP analysis for primary keyword
    print("  → Getting SERP analysis...")
    results["serp"] = get_google_serp(
        keyword=keywords[0],
        location_name=location_name
    )

    # Competitor analysis
    if competitor_domain:
        print(f"  → Analyzing competitor: {competitor_domain}...")
        results["competitor_keywords"] = get_keywords_for_site(
            target_domain=competitor_domain,
            location_name=location_name
        )

    print(f"✅ Landing page research complete\n")
    return results


def full_keyword_analysis(
    keywords: List[str],
    location_name: str = None,
    include_historical: bool = True,
    include_trends: bool = True
) -> Dict[str, Any]:
    """
    Full keyword analysis for content strategy.

    Comprehensive analysis including:
    - Keyword overview
    - Historical search volume trends
    - Keyword difficulty
    - Search intent
    - Keyword ideas (expansion)
    - Google Trends data

    Args:
        keywords: Keywords to analyze
        location_name: Target location
        include_historical: Include historical search volume
        include_trends: Include Google Trends data

    Returns:
        Dict with comprehensive keyword analysis

    Example:
        >>> result = full_keyword_analysis(["ai writing tools", "chatgpt alternatives"])
    """
    print(f"\n📊 Full keyword analysis: {keywords}")
    results = {}

    print("  → Getting keyword overview...")
    results["overview"] = get_keyword_overview(
        keywords=keywords,
        location_name=location_name,
        include_serp_info=True
    )

    print("  → Getting keyword difficulty...")
    results["difficulty"] = get_bulk_keyword_difficulty(
        keywords=keywords,
        location_name=location_name
    )

    print("  → Getting search intent...")
    results["search_intent"] = get_search_intent(
        keywords=keywords,
        location_name=location_name
    )

    print("  → Getting keyword ideas...")
    results["keyword_ideas"] = get_keyword_ideas(
        keywords=keywords,
        location_name=location_name,
        limit=100
    )

    if include_historical:
        print("  → Getting historical search volume...")
        results["historical"] = get_historical_search_volume(
            keywords=keywords,
            location_name=location_name
        )

    if include_trends:
        print("  → Getting Google Trends data...")
        results["trends"] = get_trends_explore(
            keywords=keywords[:5],
            location_name=location_name
        )

    print(f"✅ Full analysis complete\n")
    return results


def competitor_analysis(
    domain: str,
    keywords: List[str] = None,
    location_name: str = None
) -> Dict[str, Any]:
    """
    Analyze a competitor's keyword strategy.

    Args:
        domain: Competitor domain to analyze
        keywords: Optional keywords to find competitors for
        location_name: Target location

    Returns:
        Dict with competitor analysis data

    Example:
        >>> result = competitor_analysis("competitor.com")
    """
    print(f"\n🎯 Competitor analysis: {domain}")
    results = {}

    print("  → Getting domain keywords...")
    results["domain_keywords"] = get_domain_keywords(
        target_domain=domain,
        location_name=location_name,
        limit=100
    )

    print("  → Getting keywords from Google Ads data...")
    results["ads_keywords"] = get_keywords_for_site(
        target_domain=domain,
        location_name=location_name
    )

    if keywords:
        print("  → Finding other competitors...")
        results["other_competitors"] = get_competitors(
            keywords=keywords,
            location_name=location_name
        )

    print(f"✅ Competitor analysis complete\n")
    return results


def trending_topics(
    location_name: str = None
) -> Dict[str, Any]:
    """
    Get currently trending topics and searches.

    Args:
        location_name: Target location

    Returns:
        Dict with trending data

    Example:
        >>> result = trending_topics()
    """
    print("\n📈 Getting trending topics...")
    result = get_trending_now(location_name=location_name)
    print("✅ Trending topics retrieved\n")
    return result


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_recent_results(category: str = None, limit: int = 10) -> List[Path]:
    """
    Get recently saved results.

    Args:
        category: Filter by category (keywords_data, labs, serp, trends)
        limit: Maximum results to return

    Returns:
        List of result file paths
    """
    return list_results(category=category, limit=limit)


def load_latest(category: str, operation: str = None) -> Optional[Dict]:
    """
    Load the most recent result for a category/operation.

    Args:
        category: Result category
        operation: Specific operation (optional)

    Returns:
        The loaded result data or None
    """
    return get_latest_result(category=category, operation=operation)


# ============================================================================
# QUICK ACCESS - Direct API function exports
# ============================================================================

# For direct access to individual API functions, import from respective modules:
# from api.keywords_data import get_search_volume, get_keywords_for_site
# from api.labs import get_keyword_suggestions, get_bulk_keyword_difficulty
# from api.serp import get_google_serp, get_youtube_serp
# from api.trends import get_trends_explore, get_youtube_trends


if __name__ == "__main__":
    print("""
DataForSEO API Toolkit
======================

High-level functions:
  - keyword_research(keyword)
  - youtube_keyword_research(keyword)
  - landing_page_keyword_research(keywords, competitor_domain)
  - full_keyword_analysis(keywords)
  - competitor_analysis(domain)
  - trending_topics()

Usage:
  from main import *
  result = keyword_research("your keyword here")

All results are automatically saved to /results directory.
""")
