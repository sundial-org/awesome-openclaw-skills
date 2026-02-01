"""
Core API for associative memory.
"""

import re
from pathlib import Path
from typing import Any, Optional

from .config import load_or_create_config, StoreConfig
from .paths import get_default_store_path
from .providers import get_registry
from .providers.base import (
    DocumentProvider,
    EmbeddingProvider,
    SummarizationProvider,
    TaggingProvider,
)
from .types import Item


# Collection name validation: lowercase ASCII and underscores only
COLLECTION_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class AssociativeMemory:
    """
    Persistent associative memory with semantic search capabilities.
    
    The store is initialized automatically on construction. If the store
    does not exist at the given path, it will be created with default
    configuration.
    
    Args:
        store_path: Path to the store directory. If None, defaults to
                    .keep/ at the git repository root (or cwd if not
                    in a repo). Can be overridden with KEEP_STORE_PATH.
        collection: Default collection name for operations.
                    Must be lowercase ASCII and underscores only.
    
    Raises:
        RuntimeError: If store initialization fails.
    
    Example:
        # Uses .keep/ at repo root by default
        mem = AssociativeMemory()
        
        # Or specify explicitly
        mem = AssociativeMemory("/data/memory", collection="project_docs")
        mem.update("file:///path/to/readme.md")
        results = mem.find("installation instructions")
    """
    
    def __init__(
        self,
        store_path: Optional[str | Path] = None,
        collection: str = "default"
    ) -> None:
        """Initialize or open an existing associative memory store."""
        # Resolve store path (uses git root/.keep by default)
        if store_path is None:
            self._store_path = get_default_store_path()
        else:
            self._store_path = Path(store_path).resolve()
        
        # Validate collection name
        if not COLLECTION_NAME_PATTERN.match(collection):
            raise ValueError(
                f"Invalid collection name '{collection}'. "
                "Must be lowercase ASCII, starting with a letter, using only letters, numbers, and underscores."
            )
        self._default_collection = collection
        
        # Load or create configuration
        self._config: StoreConfig = load_or_create_config(self._store_path)
        
        # Initialize providers
        registry = get_registry()
        self._document_provider: DocumentProvider = registry.create_document(
            self._config.document.name,
            self._config.document.params,
        )
        self._embedding_provider: EmbeddingProvider = registry.create_embedding(
            self._config.embedding.name,
            self._config.embedding.params,
        )
        self._summarization_provider: SummarizationProvider = registry.create_summarization(
            self._config.summarization.name,
            self._config.summarization.params,
        )
        self._tagging_provider: TaggingProvider = registry.create_tagging(
            self._config.tagging.name,
            self._config.tagging.params,
        )
        
        # TODO: Initialize ChromaDb store
        # self._store = ChromaStore(self._store_path, self._embedding_provider.dimension)
    
    def _resolve_collection(self, collection: Optional[str]) -> str:
        """Resolve collection name, validating if provided."""
        if collection is None:
            return self._default_collection
        if not COLLECTION_NAME_PATTERN.match(collection):
            raise ValueError(f"Invalid collection name: {collection}")
        return collection
    
    # -------------------------------------------------------------------------
    # Write Operations
    # -------------------------------------------------------------------------
    
    def update(
        self,
        id: str,
        source_tags: Optional[dict[str, str]] = None,
        *,
        collection: Optional[str] = None
    ) -> Item:
        """
        Insert or update a document in the store.
        
        Fetches the document at the given URI, generates embeddings, summary,
        and tags, then stores/updates the item. Updates are serialized to
        avoid concurrency issues.
        
        Args:
            id: URI locating the original document (file://, https://, etc.)
            source_tags: Optional tags to store alongside generated tags
            collection: Override the default collection for this operation
        
        Returns:
            The created or updated Item.
        
        Raises:
            ValueError: If the URI is invalid or unsupported.
            IOError: If the document cannot be fetched.
            RuntimeError: If embedding/summarization/tagging fails.
        
        Example:
            item = mem.update(
                "file:///project/docs/api.md",
                source_tags={"category": "documentation", "version": "2.0"}
            )
        """
        raise NotImplementedError()
    
    def remember(
        self,
        content: str,
        *,
        id: Optional[str] = None,
        source_tags: Optional[dict[str, str]] = None,
        collection: Optional[str] = None
    ) -> Item:
        """
        Store inline content directly (without fetching from a URI).
        
        Use this for indexing conversation snippets, notes, or any content
        that doesn't have a persistent URI. The content is embedded, 
        summarized, and tagged just like URI-based documents.
        
        Args:
            content: The text content to remember
            id: Optional identifier. If not provided, generates one like
                "mem:2026-01-30T12:34:56". Use a meaningful ID for later
                retrieval, e.g., "conversation:2026-01-30:auth-discussion"
            source_tags: Optional tags to store alongside generated tags
            collection: Override the default collection for this operation
        
        Returns:
            The created or updated Item.
        
        Example:
            # Remember a conversation summary
            mem.remember(
                content="Discussed auth flow. Decided to use OAuth2 with PKCE.",
                id="conversation:2026-01-30:auth",
                source_tags={"session": "abc123", "topic": "authentication"}
            )
            
            # Remember a quick note
            mem.remember("User prefers dark mode themes")
        """
        raise NotImplementedError()
    
    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------
    
    def find(
        self,
        query: str,
        *,
        limit: int = 10,
        collection: Optional[str] = None
    ) -> list[Item]:
        """
        Find items using semantic similarity search.
        
        The query is embedded and compared against all items in the collection.
        Results are ordered by similarity score (highest first).
        
        Args:
            query: Natural language query text
            limit: Maximum number of results to return
            collection: Override the default collection for this operation
        
        Returns:
            List of Items with similarity scores, ordered by relevance.
        
        Example:
            results = mem.find("error handling patterns", limit=5)
            for item in results:
                print(f"{item.score:.2f} - {item.summary[:50]}")
        """
        raise NotImplementedError()
    
    def find_similar(
        self,
        id: str,
        *,
        limit: int = 10,
        include_self: bool = False,
        collection: Optional[str] = None
    ) -> list[Item]:
        """
        Find items similar to an existing item.
        
        Uses the embedding of the specified item to find nearest neighbors.
        
        Args:
            id: URI of an existing item in the store
            limit: Maximum number of results to return
            include_self: Whether to include the queried item in results
            collection: Override the default collection for this operation
        
        Returns:
            List of Items with similarity scores, ordered by relevance.
        
        Raises:
            KeyError: If the specified item does not exist.
        
        Example:
            similar = mem.find_similar("file:///docs/auth.md", limit=3)
        """
        raise NotImplementedError()
    
    def query_fulltext(
        self,
        query: str,
        *,
        limit: int = 10,
        collection: Optional[str] = None
    ) -> list[Item]:
        """
        Search item summaries using full-text search.
        
        Performs a text search on the generated summaries. Useful when you
        need exact keyword matching rather than semantic similarity.
        
        Args:
            query: Search terms (supports basic boolean operators)
            limit: Maximum number of results to return
            collection: Override the default collection for this operation
        
        Returns:
            List of matching Items (score may reflect text relevance).
        
        Example:
            results = mem.query_fulltext("authentication OAuth")
        """
        raise NotImplementedError()
    
    def query_tag(
        self,
        key: str,
        value: Optional[str] = None,
        *,
        limit: int = 100,
        collection: Optional[str] = None
    ) -> list[Item]:
        """
        Find items by tag.
        
        Args:
            key: Tag key to match
            value: Optional tag value to match. If None, matches any value.
            limit: Maximum number of results to return
            collection: Override the default collection for this operation
        
        Returns:
            List of matching Items (no particular order).
        
        Example:
            # All items with 'category' tag
            mem.query_tag("category")
            
            # Items where category is 'documentation'
            mem.query_tag("category", "documentation")
        """
        raise NotImplementedError()
    
    # -------------------------------------------------------------------------
    # Collection Management
    # -------------------------------------------------------------------------
    
    def list_collections(self) -> list[str]:
        """
        List all collections in the store.
        
        Returns:
            List of collection names.
        """
        raise NotImplementedError()
    
    # -------------------------------------------------------------------------
    # Utilities
    # -------------------------------------------------------------------------
    
    def get(self, id: str, *, collection: Optional[str] = None) -> Optional[Item]:
        """
        Retrieve a specific item by ID.
        
        Args:
            id: URI of the item
            collection: Override the default collection
        
        Returns:
            The Item if found, None otherwise.
        """
        raise NotImplementedError()
    
    def exists(self, id: str, *, collection: Optional[str] = None) -> bool:
        """
        Check if an item exists in the store.
        
        Args:
            id: URI of the item
            collection: Override the default collection
        
        Returns:
            True if the item exists, False otherwise.
        """
        raise NotImplementedError()
    
    # -------------------------------------------------------------------------
    # Context & Top-of-Mind
    # -------------------------------------------------------------------------
    
    def set_context(
        self,
        summary: str,
        *,
        active_items: Optional[list[str]] = None,
        topics: Optional[list[str]] = None,
        metadata: Optional[dict[str, Any]] = None,
    ) -> "WorkingContext":
        """
        Set the current working context.
        
        The working context is a high-level summary of what's being worked on.
        Any agent can read this to instantly understand current focus.
        This is the "Level 3" of the hierarchical context model.
        
        Args:
            summary: Natural language description of current focus
            active_items: IDs of items currently being worked with
            topics: Active topic/domain tags
            metadata: Additional context-specific data
        
        Returns:
            The updated WorkingContext.
        
        Example:
            mem.set_context(
                summary="Implementing OAuth2 PKCE flow. Reviewing token refresh.",
                active_items=["file:///src/auth.py"],
                topics=["authentication", "security"]
            )
        """
        raise NotImplementedError()
    
    def get_context(self) -> Optional["WorkingContext"]:
        """
        Get the current working context.
        
        Returns:
            The current WorkingContext, or None if not set.
        
        Example:
            ctx = mem.get_context()
            if ctx:
                print(f"Current focus: {ctx.summary}")
                print(f"Active topics: {ctx.topics}")
        """
        raise NotImplementedError()
    
    def top_of_mind(
        self,
        hint: Optional[str] = None,
        *,
        limit: int = 10,
        collection: Optional[str] = None,
    ) -> list[Item]:
        """
        Get items most relevant to current work.
        
        Combines multiple signals to surface what's most important right now:
        - Items updated in the current session
        - Items similar to the working context
        - Items with active topic tags
        - Recency (with decay)
        
        This is "associative top-of-mind" — not just recent items, but
        contextually relevant items weighted by current focus.
        
        Args:
            hint: Optional focus hint to bias results (e.g., "authentication")
            limit: Maximum number of results
            collection: Override the default collection
        
        Returns:
            List of Items ordered by relevance to current work.
        
        Example:
            # What's relevant right now?
            items = mem.top_of_mind()
            
            # What's relevant about auth specifically?
            items = mem.top_of_mind("authentication", limit=5)
        """
        raise NotImplementedError()
    
    def recent(
        self,
        *,
        limit: int = 20,
        since: Optional[str] = None,
        collection: Optional[str] = None,
    ) -> list[Item]:
        """
        Get recently updated items.
        
        Simple temporal retrieval, ordered by update time (newest first).
        
        Args:
            limit: Maximum number of results
            since: ISO timestamp or date string; only return items updated after
            collection: Override the default collection
        
        Returns:
            List of Items ordered by recency.
        
        Example:
            # Last 20 items
            items = mem.recent()
            
            # Items from today
            items = mem.recent(since="2026-01-30")
        """
        raise NotImplementedError()
    
    # -------------------------------------------------------------------------
    # Topic Management (Level 2)
    # -------------------------------------------------------------------------
    
    def list_topics(self, *, collection: Optional[str] = None) -> list[str]:
        """
        List all topics that have been identified in the collection.
        
        Topics are derived from the `_topic` system tag on items.
        
        Returns:
            List of topic names.
        """
        raise NotImplementedError()
    
    def get_topic_summary(
        self,
        topic: str,
        *,
        collection: Optional[str] = None,
    ) -> Optional["TopicSummary"]:
        """
        Get a summary of items within a topic.
        
        Topic summaries are "Level 2" in the hierarchy — they aggregate
        multiple items without requiring retrieval of all of them.
        
        Args:
            topic: Topic name to summarize
            collection: Override the default collection
        
        Returns:
            TopicSummary with overview and key items, or None if topic doesn't exist.
        
        Example:
            summary = mem.get_topic_summary("authentication")
            print(f"Auth topic: {summary.item_count} items")
            print(f"Summary: {summary.summary}")
        """
        raise NotImplementedError()
    
    def refresh_topic_summary(
        self,
        topic: str,
        *,
        collection: Optional[str] = None,
    ) -> "TopicSummary":
        """
        Regenerate the summary for a topic.
        
        Call this after significant changes to items in the topic.
        Uses the summarization provider to create an aggregate summary.
        
        Args:
            topic: Topic name to summarize
            collection: Override the default collection
        
        Returns:
            The regenerated TopicSummary.
        """
        raise NotImplementedError()

    # -------------------------------------------------------------------------
    # System Documents
    # -------------------------------------------------------------------------
    
    def get_routing(self) -> "RoutingContext":
        """
        Get the current routing configuration.
        
        Routing controls how items are directed to private vs shared stores.
        The routing document (`_system:routing`) is itself stored in the
        shared store and can be queried/updated like any other document.
        
        Returns:
            The current RoutingContext.
        
        Example:
            routing = mem.get_routing()
            print(f"Private patterns: {routing.private_patterns}")
        """
        raise NotImplementedError()
    
    def get_system_document(self, name: str) -> Optional[Item]:
        """
        Get a system document by name.
        
        System documents control the store's behavior. They are stored
        as regular items with IDs like `_system:{name}`.
        
        Well-known system documents:
        - `routing`: Private/shared routing patterns
        - `context`: Current working context
        - `guidance`: Local behavioral guidance
        
        Args:
            name: System document name (without `_system:` prefix)
        
        Returns:
            The system document as an Item, or None if not found.
        
        Example:
            guidance = mem.get_system_document("guidance:code_review")
        """
        return self.get(f"_system:{name}")
    
    def list_system_documents(self) -> list[Item]:
        """
        List all system documents in the store.
        
        Returns:
            List of system document Items.
        
        Example:
            for doc in mem.list_system_documents():
                print(f"{doc.id}: {doc.summary[:50]}")
        """
        return self.query_tag("_system", "true")


# Import at end to avoid circular import
from .context import WorkingContext, TopicSummary, RoutingContext
