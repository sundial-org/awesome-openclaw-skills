"""
Data types for associative memory.
"""

from dataclasses import dataclass, field
from typing import Optional


# System tag prefix - tags starting with this are managed by the system
SYSTEM_TAG_PREFIX = "_"


def filter_non_system_tags(tags: dict[str, str]) -> dict[str, str]:
    """
    Filter out any system tags (those starting with '_').
    
    Use this to ensure source tags and derived tags cannot
    overwrite system-managed values.
    """
    return {k: v for k, v in tags.items() if not k.startswith(SYSTEM_TAG_PREFIX)}


@dataclass(frozen=True)
class Item:
    """
    An item retrieved from the associative memory store.
    
    This is a read-only snapshot. To modify an item, use api.update()
    which returns a new Item with updated values.
    
    Timestamps and other system metadata live in tags, not as explicit fields.
    This follows the "schema as data" principle.
    
    Attributes:
        id: URI or custom identifier for the item
        summary: Generated summary of the content
        tags: All tags (source, system, and generated combined)
        score: Similarity score (present only in search results)
    
    System tags (managed automatically, in tags dict):
        _created: ISO timestamp when first indexed
        _updated: ISO timestamp when last indexed  
        _updated_date: Date portion for easier queries
        _content_type: MIME type if known
        _source: How content was obtained (uri, inline)
        _session: Session that last touched this item
    """
    id: str
    summary: str
    tags: dict[str, str] = field(default_factory=dict)
    score: Optional[float] = None
    
    @property
    def created(self) -> str | None:
        """ISO timestamp when first indexed (from _created tag)."""
        return self.tags.get("_created")
    
    @property
    def updated(self) -> str | None:
        """ISO timestamp when last indexed (from _updated tag)."""
        return self.tags.get("_updated")
    
    def __str__(self) -> str:
        score_str = f" [{self.score:.3f}]" if self.score is not None else ""
        return f"{self.id}{score_str}: {self.summary[:60]}..."
