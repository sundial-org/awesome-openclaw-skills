"""
Keep - Semantic Memory

A persistent semantic memory with similarity search, full-text search,
and tag-based retrieval. Remember everything, find by meaning.

Quick Start:
    from keep import Keeper

    kp = Keeper()  # uses .keep/ at git repo root
    kp.update("file:///path/to/document.md", source_tags={"project": "myproject"})
    results = kp.find("something similar to this query")

CLI Usage:
    keep find "query text"
    keep update file:///path/to/doc.md -t category=docs
    keep collections --json

Default Store:
    .keep/ at the git repository root (created automatically).
    Override with KEEP_STORE_PATH or explicit path argument.

Environment Variables:
    KEEP_STORE_PATH      - Override default store location
    KEEP_OPENAI_API_KEY  - API key for OpenAI providers

The store is initialized automatically on first use. Configuration is persisted
in a TOML file within the store directory.
"""

# Configure quiet mode early (before any library imports)
import os
if not os.environ.get("KEEP_VERBOSE"):
    os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
    os.environ.setdefault("TRANSFORMERS_VERBOSITY", "error")
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    os.environ.setdefault("HF_HUB_DISABLE_TELEMETRY", "1")
    os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

from .api import Keeper
from .types import Item, filter_non_system_tags, SYSTEM_TAG_PREFIX
from .context import WorkingContext, TopicSummary, RoutingContext

__version__ = "0.1.0"
__all__ = [
    "Keeper",
    "Item",
    "WorkingContext",
    "TopicSummary",
    "RoutingContext",
    "filter_non_system_tags",
    "SYSTEM_TAG_PREFIX",
]
