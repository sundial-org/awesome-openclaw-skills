"""SERP API - Google and YouTube search results data."""
import sys
from pathlib import Path
from typing import Dict, Any, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dataforseo_client.rest import ApiException

from core.client import get_client
from core.storage import save_result
from config.settings import settings


def get_google_serp(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    depth: int = 100,
    device: str = "desktop",
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google organic search results for a keyword.

    Args:
        keyword: Search query
        location_name: Target location
        language_name: Target language
        depth: Number of results (max 700)
        device: Device type ("desktop" or "mobile")
        save: Whether to save results

    Returns:
        Dict containing SERP data with rankings, URLs, titles, and SERP features

    Example:
        >>> result = get_google_serp("best video editing software")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.serp.google_organic_live_advanced([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": min(depth, 700),
            "device": device
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="serp",
                operation="google_organic",
                keyword=keyword,
                extra_info=device
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_youtube_serp(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    depth: int = 20,
    device: str = "desktop",
    save: bool = True
) -> Dict[str, Any]:
    """
    Get YouTube organic search results for a keyword.

    Args:
        keyword: Search query (max 700 characters)
        location_name: Target location
        language_name: Target language
        depth: Number of results (max 700, billed per 20)
        device: Device type ("desktop" or "mobile")
        save: Whether to save results

    Returns:
        Dict containing YouTube video rankings with titles, channels, views, etc.

    Example:
        >>> result = get_youtube_serp("python tutorial for beginners")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.serp.youtube_organic_live_advanced([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": min(depth, 700),
            "device": device
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="serp",
                operation="youtube_organic",
                keyword=keyword,
                extra_info=device
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_google_maps_serp(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    depth: int = 20,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google Maps/Local search results for a keyword.

    Args:
        keyword: Search query (e.g., "restaurants near me")
        location_name: Target location
        language_name: Target language
        depth: Number of results
        save: Whether to save results

    Returns:
        Dict containing local business listings

    Example:
        >>> result = get_google_maps_serp("coffee shops downtown")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.serp.google_maps_live_advanced([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": depth
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="serp",
                operation="google_maps",
                keyword=keyword
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_google_news_serp(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    depth: int = 100,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google News search results for a keyword.

    Args:
        keyword: Search query
        location_name: Target location
        language_name: Target language
        depth: Number of results
        save: Whether to save results

    Returns:
        Dict containing news articles and their rankings

    Example:
        >>> result = get_google_news_serp("artificial intelligence")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.serp.google_news_live_advanced([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": depth
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="serp",
                operation="google_news",
                keyword=keyword
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_google_images_serp(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    depth: int = 100,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google Images search results for a keyword.

    Args:
        keyword: Search query
        location_name: Target location
        language_name: Target language
        depth: Number of results
        save: Whether to save results

    Returns:
        Dict containing image results with URLs, titles, sources

    Example:
        >>> result = get_google_images_serp("python programming logo")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.serp.google_images_live_advanced([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": depth
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="serp",
                operation="google_images",
                keyword=keyword
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise


def get_featured_snippet(
    keyword: str,
    location_name: str = None,
    language_name: str = None,
    save: bool = True
) -> Dict[str, Any]:
    """
    Get Google SERP with focus on featured snippets and SERP features.

    Args:
        keyword: Search query (ideally a question)
        location_name: Target location
        language_name: Target language
        save: Whether to save results

    Returns:
        Dict containing SERP data with featured snippet details

    Example:
        >>> result = get_featured_snippet("how to edit videos")
    """
    client = get_client()
    location = location_name or settings.DEFAULT_LOCATION_NAME
    language = language_name or settings.DEFAULT_LANGUAGE_NAME

    try:
        response = client.serp.google_organic_live_advanced([{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "depth": 10,
            "device": "desktop"
        }])

        result = response.to_dict() if hasattr(response, 'to_dict') else response

        if save:
            save_result(
                result,
                category="serp",
                operation="featured_snippet",
                keyword=keyword
            )

        return result

    except ApiException as e:
        print(f"API Exception: {e}")
        raise
