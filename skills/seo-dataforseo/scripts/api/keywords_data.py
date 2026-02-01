"""Keywords Data API - Search volume, CPC, and keyword data from Google Ads."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataforseo_client.rest import ApiException

from core.client import get_client
from core.storage import save_result
from config.settings import settings


def get_search_volume(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get search volume, CPC, and competition data for keywords.

    Args:
        keywords: List of keywords to analyze (max 700)
        location_name: Target location (default: United States)
        language_name: Target language (default: English)
        save: Whether to save results to JSON file

    Returns:
        Dict containing search volume data for each keyword

    Example:
        >>> result = get_search_volume(["python tutorial", "learn python"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.keywords_data.google_ads_search_volume_live([{
            "keywords": keywords[:700],
            "location_name": location,
            "language_name": language
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            keyword_preview = keywords[0] if keywords else "bulk"
            save_result(
                result,
                category="keywords_data",
                operation="search_volume",
                keyword=keyword_preview,
                extra_info=f"{len(keywords)}_keywords"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_keywords_for_site(
    target_domain: str,
    location_name: str = None,
    language_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get keywords associated with a specific domain.

    Args:
        target_domain: Domain to analyze (e.g., "example.com")
        location_name: Target location
        language_name: Target language
        save: Whether to save results

    Returns:
        Dict containing keywords relevant to the domain

    Example:
        >>> result = get_keywords_for_site("competitor.com")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.keywords_data.google_ads_keywords_for_site_live([{
            "target": target_domain,
            "location_name": location,
            "language_name": language
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="keywords_data",
                operation="keywords_for_site",
                keyword=target_domain
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_ad_traffic_by_keywords(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    bid: float = 2.0,
    save: bool = True
) -> Dict[str, Any]:
    """
    Estimate advertising traffic potential for keywords.

    Args:
        keywords: List of keywords to analyze
        location_name: Target location
        language_name: Target language
        bid: Maximum CPC bid for estimation
        save: Whether to save results

    Returns:
        Dict containing traffic estimates

    Example:
        >>> result = get_ad_traffic_by_keywords(["buy shoes online", "best running shoes"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.keywords_data.google_ads_ad_traffic_by_keywords_live([{
            "keywords": keywords,
            "location_name": location,
            "language_name": language,
            "bid": bid
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="keywords_data",
                operation="ad_traffic",
                keyword=keywords[0] if keywords else "bulk"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_keywords_for_keywords(
    keywords: List[str],
    location_name: str = None,
    language_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get keyword expansion ideas from Google Ads Keyword Planner.

    Args:
        keywords: Seed keywords to expand (max 20)
        location_name: Target location
        language_name: Target language
        save: Whether to save results

    Returns:
        Dict containing expanded keyword ideas

    Example:
        >>> result = get_keywords_for_keywords(["video editing", "video software"])
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.keywords_data.google_ads_keywords_for_keywords_live([{
            "keywords": keywords[:20],
            "location_name": location,
            "language_name": language
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="keywords_data",
                operation="keywords_for_keywords",
                keyword=keywords[0] if keywords else "bulk",
                extra_info=f"{len(keywords)}_seeds"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise
