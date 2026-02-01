"""Google Trends API - Trend data across Google Search, YouTube, News, Images, and Shopping."""
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataforseo_client.rest import ApiException

from core.client import get_client
from core.storage import save_result
from config.settings import settings


def get_trends_explore(
    keywords: List[str],
    location_name: str = None,
    search_type: str = "web",
    time_range: str = "past_12_months",
    date_from: str = None,
    date_to: str = None,
    category_code: int = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google Trends data for keywords.

    Args:
        keywords: List of keywords to compare (max 5)
        location_name: Target location (defaults to worldwide if not specified)
        search_type: Type of search - "web", "news", "youtube", "images", "froogle" (shopping)
        time_range: Preset time range - "past_hour", "past_4_hours", "past_day",
                    "past_7_days", "past_month", "past_3_months", "past_12_months",
                    "past_5_years"
        date_from: Custom start date (yyyy-mm-dd), overrides time_range
        date_to: Custom end date (yyyy-mm-dd)
        category_code: Google Trends category filter
        save: Whether to save results

    Returns:
        Dict containing trend graph data, regional interest, related topics and queries

    Example:
        >>> result = get_trends_explore(["python", "javascript"], search_type="youtube")
        >>> result = get_trends_explore(["ai video editing"], time_range="past_12_months")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME

    request_params = {
        "keywords": keywords[:5],  # API limit
        "location_name": location,
        "type": search_type
    }

    # Add time parameters
    if date_from and date_to:
        request_params["date_from"] = date_from
        request_params["date_to"] = date_to
    else:
        request_params["time_range"] = time_range

    if category_code:
        request_params["category_code"] = category_code

    try:
        response = client.keywords_data.google_trends_explore_live([request_params])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="trends",
                operation="explore",
                keyword="_vs_".join(keywords[:3]),
                extra_info=f"{search_type}_{time_range}"
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_youtube_trends(
    keywords: List[str],
    location_name: str = None,
    time_range: str = "past_12_months",
    save: bool = True
) -> Dict[str, Any]:
    """
    Get YouTube-specific trend data for keywords.

    Convenience wrapper for get_trends_explore with YouTube search type.

    Args:
        keywords: List of keywords to compare (max 5)
        location_name: Target location
        time_range: Time range for trend data
        save: Whether to save results

    Returns:
        Dict containing YouTube trend data

    Example:
        >>> result = get_youtube_trends(["shorts tutorial", "youtube shorts"])
    """
    return get_trends_explore(
        keywords=keywords,
        location_name=location_name,
        search_type="youtube",
        time_range=time_range,
        save=save
    )


def get_news_trends(
    keywords: List[str],
    location_name: str = None,
    time_range: str = "past_12_months",
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google News trend data for keywords.

    Args:
        keywords: List of keywords to compare (max 5)
        location_name: Target location
        time_range: Time range for trend data
        save: Whether to save results

    Returns:
        Dict containing news trend data

    Example:
        >>> result = get_news_trends(["artificial intelligence", "machine learning"])
    """
    return get_trends_explore(
        keywords=keywords,
        location_name=location_name,
        search_type="news",
        time_range=time_range,
        save=save
    )


def get_shopping_trends(
    keywords: List[str],
    location_name: str = None,
    time_range: str = "past_12_months",
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google Shopping trend data for keywords.

    Args:
        keywords: List of keywords to compare (max 5)
        location_name: Target location
        time_range: Time range for trend data
        save: Whether to save results

    Returns:
        Dict containing shopping/e-commerce trend data

    Example:
        >>> result = get_shopping_trends(["wireless earbuds", "bluetooth headphones"])
    """
    return get_trends_explore(
        keywords=keywords,
        location_name=location_name,
        search_type="froogle",  # Google Shopping
        time_range=time_range,
        save=save
    )


def compare_keyword_trends(
    keywords: List[str],
    location_name: str = None,
    search_types: List[str] = None,
    time_range: str = "past_12_months",
    save: bool = True
) -> Dict[str, Dict[str, Any]]:
    """
    Compare keyword trends across multiple search types.

    Args:
        keywords: Keywords to compare (max 5)
        location_name: Target location
        search_types: List of search types to compare (defaults to web, youtube)
        time_range: Time range
        save: Whether to save individual results

    Returns:
        Dict with search_type keys and trend data values

    Example:
        >>> result = compare_keyword_trends(
        ...     ["video editing tutorial"],
        ...     search_types=["web", "youtube", "images"]
        ... )
    """
    if search_types is None:
        search_types = ["web", "youtube"]

    results = {}
    for search_type in search_types:
        results[search_type] = get_trends_explore(
            keywords=keywords,
            location_name=location_name,
            search_type=search_type,
            time_range=time_range,
            save=save
        )

    return results


def get_trending_now(
    location_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get currently trending searches.

    Args:
        location_name: Target location
        save: Whether to save results

    Returns:
        Dict containing trending searches

    Example:
        >>> result = get_trending_now()
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME

    try:
        response = client.keywords_data.google_trends_trending_now_live([{
            "location_name": location
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="trends",
                operation="trending_now",
                keyword=location
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise
