"""Result storage utilities for persisting API responses."""
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings


def get_timestamp() -> str:
    """Generate timestamp for filenames."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def sanitize_filename(name: str) -> str:
    """Sanitize string for use as filename."""
    for char in ['/', '\\', ':', '*', '?', '"', '<', '>', '|', ' ']:
        name = name.replace(char, '_')
    return name[:100]  # Limit length


def save_result(
    data: Any,
    category: str,
    operation: str,
    keyword: Optional[str] = None,
    extra_info: Optional[str] = None
) -> Path:
    """
    Save API result to JSON file.

    Args:
        data: The API response data to save
        category: Result category (keywords_data, labs, serp, trends)
        operation: Specific operation name (e.g., search_volume, keyword_suggestions)
        keyword: Primary keyword(s) used in the request
        extra_info: Additional info for filename

    Returns:
        Path to the saved file
    """
    # Ensure results directory exists
    category_dir = settings.RESULTS_DIR / category
    category_dir.mkdir(parents=True, exist_ok=True)

    # Build filename
    timestamp = get_timestamp()
    parts = [timestamp, operation]

    if keyword:
        parts.append(sanitize_filename(keyword))
    if extra_info:
        parts.append(sanitize_filename(extra_info))

    filename = "__".join(parts) + ".json"
    filepath = category_dir / filename

    # Prepare data for JSON serialization
    if hasattr(data, 'to_dict'):
        data = data.to_dict()

    # Save with metadata wrapper
    result_wrapper = {
        "metadata": {
            "saved_at": datetime.now().isoformat(),
            "category": category,
            "operation": operation,
            "keyword": keyword,
            "extra_info": extra_info
        },
        "data": data
    }

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(result_wrapper, f, indent=2, ensure_ascii=False, default=str)

    print(f"Results saved to: {filepath}")
    return filepath


def load_result(filepath: Path) -> Dict[str, Any]:
    """Load a previously saved result."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def list_results(
    category: Optional[str] = None,
    operation: Optional[str] = None,
    limit: int = 50
) -> List[Path]:
    """
    List saved result files, optionally filtered by category/operation.

    Args:
        category: Filter by category (keywords_data, labs, serp, trends)
        operation: Filter by operation name
        limit: Maximum files to return

    Returns:
        List of file paths, sorted by most recent first
    """
    base_dir = settings.RESULTS_DIR

    if category:
        base_dir = base_dir / category

    if not base_dir.exists():
        return []

    pattern = f"*{operation}*" if operation else "*"
    files = sorted(base_dir.glob(f"**/{pattern}.json"), reverse=True)
    return files[:limit]


def get_latest_result(category: str, operation: Optional[str] = None) -> Optional[Dict]:
    """
    Get the most recent result for a category/operation.

    Args:
        category: Result category
        operation: Specific operation (optional)

    Returns:
        The loaded result data or None
    """
    files = list_results(category=category, operation=operation, limit=1)
    if files:
        return load_result(files[0])
    return None
