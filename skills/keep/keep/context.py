"""
Working context and top-of-mind retrieval.

This module provides hierarchical context management for efficient
"what are we working on?" queries with O(log(log(N))) retrieval.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Optional


@dataclass
class WorkingContext:
    """
    The current working context — a high-level summary of active work.
    
    This is the "Level 3" summary that any agent can read to instantly
    understand what's being worked on.
    
    Attributes:
        summary: Natural language description of current focus
        active_items: IDs of items currently being worked with
        topics: Active topic/domain tags
        updated: When context was last updated
        session_id: Current session identifier
        metadata: Additional context-specific data (arbitrary structure)
    """
    summary: str
    active_items: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    session_id: Optional[str] = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass  
class TopicSummary:
    """
    A summary of items within a topic cluster (Level 2).
    
    Topics aggregate related items and provide a mid-level
    overview without retrieving all underlying items.
    
    Attributes:
        topic: Topic identifier (tag value)
        summary: Generated summary of topic contents
        item_count: Number of items in this topic
        key_items: IDs of the most important items in the topic
        subtopics: Child topics if hierarchical
        updated: When topic summary was last regenerated
    """
    topic: str
    summary: str
    item_count: int
    key_items: list[str] = field(default_factory=list)
    subtopics: list[str] = field(default_factory=list)
    updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())


@dataclass
class RoutingContext:
    """
    Describes how items are routed between private and shared stores.
    
    This document lives at a well-known location in the shared store.
    The facade reads it to make routing decisions. The private store
    is physically separate and invisible from the shared store.
    
    Attributes:
        summary: Natural language description of the privacy model
        private_patterns: Tag patterns that route to private store (each pattern is dict[str, str])
        private_store_path: Location of the private store (if local)
        updated: When routing was last modified
        metadata: Additional routing configuration
    """
    summary: str = "Items tagged for private/draft visibility route to a separate store."
    private_patterns: list[dict[str, str]] = field(default_factory=lambda: [
        {"_visibility": "draft"},
        {"_visibility": "private"},
        {"_for": "self"},
    ])
    private_store_path: Optional[str] = None  # Resolved at init; None = default location
    updated: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    metadata: dict[str, Any] = field(default_factory=dict)


# Well-known item ID for the routing context document
ROUTING_CONTEXT_ID = "_system:routing"


# Reserved system tags for context management (stored with items)
CONTEXT_TAGS = {
    "_session": "Session that last touched this item",
    "_topic": "Primary topic classification",
    "_level": "Hierarchy level (0=source, 1=cluster, 2=topic, 3=context)",
    "_summarizes": "IDs of items this item summarizes (for hierarchy)",
}

# Relevance scoring is computed at query time, NOT stored.
# This preserves agility between broad exploration and focused work.
# Score factors:
#   - semantic similarity to query/hint
#   - recency (time decay)
#   - topic overlap with current WorkingContext.topics
#   - session affinity (same session = boost)
# The weighting of these factors can vary by retrieval mode.


def generate_session_id() -> str:
    """Generate a unique session identifier."""
    import uuid
    date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    short_uuid = uuid.uuid4().hex[:8]
    return f"{date}:{short_uuid}"


def matches_private_pattern(tags: dict[str, str], patterns: list[dict[str, str]]) -> bool:
    """
    Check if an item's tags match any private routing pattern.
    
    A pattern matches if ALL its key-value pairs are present in tags.
    """
    for pattern in patterns:
        if all(tags.get(k) == v for k, v in pattern.items()):
            return True
    return False
