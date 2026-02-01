"""DataForSEO Labs API - Keyword research, suggestions, difficulty, and competitive analysis."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataforseo_client.rest import ApiException

from core.client import get_client
from core.storage import save_result
from config.settings import settings


def get_keyword_overview(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    include_serp_info: bool = False,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get comprehensive keyword data including search volume, CPC, competition, and search intent.

    Args:
        keywords: List of keywords (max 700)
        location_name: Target location
        language_name: Target language
        include_serp_info: Include SERP features data
        save: Whether to save results

    Returns:
        Dict containing comprehensive keyword metrics

    Example:
        >>> result = get_keyword_overview(["best python courses", "python for beginners"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_keyword_overview_live([{
            "keywords": keywords[:700],
            "location_name": location,
            "language_name": language,
            "include_serp_info": include_serp_info
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="keyword_overview",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_keywords"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_keyword_suggestions(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    include_seed_keyword: bool = True,
    include_serp_info: bool = False,
    limit: int = 100,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get keyword suggestions based on a seed keyword.

    Suggestions match the seed with additional words before, after, or within the phrase.

    Args:
        keyword: Seed keyword (min 3 characters)
        location_name: Target location
        language_name: Target language
        include_seed_keyword: Include metrics for the seed keyword
        include_serp_info: Include SERP data for each keyword
        limit: Maximum results (max 1000)
        save: Whether to save results

    Returns:
        Dict containing keyword suggestions with metrics

    Example:
        >>> result = get_keyword_suggestions("python tutorial")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_keyword_suggestions_live([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "include_seed_keyword": include_seed_keyword,
            "include_serp_info": include_serp_info,
            "limit": min(limit, 1000)
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="keyword_suggestions",
                keyword=keyword,
                extra_info=f"limit_{limit}"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_keyword_ideas(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    include_serp_info: bool = False,
    closely_variants: bool = False,
    limit: int = 700,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get keyword ideas that fall into the same category as seed keywords.

    Goes beyond semantic similarity to suggest relevant keywords by mapping
    seed terms against category taxonomies.

    Args:
        keywords: Seed keywords (max 200)
        location_name: Target location
        language_name: Target language
        include_serp_info: Include SERP data
        closely_variants: Use phrase-match (True) vs broad-match (False)
        limit: Maximum results (max 1000)
        save: Whether to save results

    Returns:
        Dict containing keyword ideas with metrics

    Example:
        >>> result = get_keyword_ideas(["youtube marketing", "video seo"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_keyword_ideas_live([{
            "keywords": keywords[:200],
            "location_name": location,
            "language_name": language,
            "include_serp_info": include_serp_info,
            "closely_variants": closely_variants,
            "limit": min(limit, 1000)
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="keyword_ideas",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_seeds"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_related_keywords(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    depth: int = 2,
    include_seed_keyword: bool = True,
    include_serp_info: bool = False,
    limit: int = 100,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get related keywords from Google's "searches related to" feature.

    Uses depth-first search algorithm on SERP "related searches" element.

    Args:
        keyword: Seed keyword
        location_name: Target location
        language_name: Target language
        depth: Search depth 0-4 (0=seed only, 4=max ~4680 results)
        include_seed_keyword: Include seed keyword metrics
        include_serp_info: Include SERP data
        limit: Maximum results (max 1000)
        save: Whether to save results

    Returns:
        Dict containing related keywords with metrics

    Example:
        >>> result = get_related_keywords("video editing software", depth=2)
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_related_keywords_live([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": min(depth, 4),
            "include_seed_keyword": include_seed_keyword,
            "include_serp_info": include_serp_info,
            "limit": min(limit, 1000)
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="related_keywords",
                keyword=keyword,
                extra_info=f"depth_{depth}"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_bulk_keyword_difficulty(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get keyword difficulty scores for multiple keywords.

    Difficulty score (0-100) indicates how hard it is to rank in top-10 organic results.

    Args:
        keywords: List of keywords (max 1000)
        location_name: Target location
        language_name: Target language
        save: Whether to save results

    Returns:
        Dict containing keyword difficulty scores

    Example:
        >>> result = get_bulk_keyword_difficulty(["seo tools", "keyword research"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_bulk_keyword_difficulty_live([{
            "keywords": keywords[:1000],
            "location_name": location,
            "language_name": language
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="keyword_difficulty",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_keywords"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_historical_search_volume(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    include_serp_info: bool = False,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get historical search volume and trend data for keywords.

    Returns monthly search volume data since 2019.

    Args:
        keywords: List of keywords (max 700)
        location_name: Target location
        language_name: Target language
        include_serp_info: Include SERP features
        save: Whether to save results

    Returns:
        Dict containing historical search volume with monthly breakdowns

    Example:
        >>> result = get_historical_search_volume(["ai tools", "chatgpt"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_historical_search_volume_live([{
            "keywords": keywords[:700],
            "location_name": location,
            "language_name": language,
            "include_serp_info": include_serp_info
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="historical_search_volume",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_keywords"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_search_intent(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get search intent classification for keywords.

    Classifies keywords as informational, navigational, transactional, or commercial.

    Args:
        keywords: List of keywords (max 1000)
        location_name: Target location
        language_name: Target language
        save: Whether to save results

    Returns:
        Dict containing search intent classifications

    Example:
        >>> result = get_search_intent(["buy python course", "what is python"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_search_intent_live([{
            "keywords": keywords[:1000],
            "location_name": location,
            "language_name": language
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="search_intent",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_keywords"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_domain_keywords(
    target_domain: str,
    location_name: str = None,
    language_name: str = None,
    limit: int = 100,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get keywords that a domain ranks for in organic search.

    Args:
        target_domain: Domain to analyze (e.g., "example.com")
        location_name: Target location
        language_name: Target language
        limit: Maximum results
        save: Whether to save results

    Returns:
        Dict containing keywords the domain ranks for

    Example:
        >>> result = get_domain_keywords("competitor.com")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_ranked_keywords_live([{
            "target": target_domain,
            "location_name": location,
            "language_name": language,
            "limit": limit
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="domain_keywords",
                keyword=target_domain
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_competitors(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    limit: int = 20,
    save: bool = True
) -> Dict[str, Any]:
    """
    Find domains that compete for the same keywords.

    Args:
        keywords: Keywords to find competitors for
        location_name: Target location
        language_name: Target language
        limit: Maximum competitors to return
        save: Whether to save results

    Returns:
        Dict containing competitor domains and their metrics

    Example:
        >>> result = get_competitors(["video editing software", "best video editor"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.labs.google_competitors_domain_live([{
            "keywords": keywords,
            "location_name": location,
            "language_name": language,
            "limit": limit
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="labs",
                operation="competitors",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_keywords"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise
