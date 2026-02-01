"""
Utility functions for locating paths.
"""

import os
import warnings
from pathlib import Path
from typing import Optional


def find_git_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """
    Find the root of the git repository containing the given path.
    
    Args:
        start_path: Path to start searching from. Defaults to cwd.
    
    Returns:
        Path to git root, or None if not in a git repository.
    """
    if start_path is None:
        start_path = Path.cwd()
    
    current = start_path.resolve()
    
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    
    # Check root as well
    if (current / ".git").exists():
        return current
    
    return None


def get_default_store_path() -> Path:
    """
    Get the default store path.

    Priority:
    1. KEEP_STORE_PATH environment variable
    2. .keep/ directory at git repository root
    3. ~/.keep/ in user's home directory (if not in a repo)

    Returns:
        Path to the store directory (may not exist yet).
    """
    # Check environment variable first
    env_path = os.environ.get("KEEP_STORE_PATH")
    if env_path:
        return Path(env_path).resolve()
    
    # Try to find git root
    git_root = find_git_root()
    if git_root:
        return git_root / ".keep"

    # Fall back to home directory with warning
    home = Path.home()
    warnings.warn(
        f"Not in a git repository. Using {home / '.keep'} for storage. "
        f"Set KEEP_STORE_PATH to specify a different location.",
        stacklevel=2,
    )
    return home / ".keep"
