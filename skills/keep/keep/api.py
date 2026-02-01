"""
Core API for associative memory.

This is the minimal working implementation focused on:
- update(): fetch → embed → summarize → store
- remember(): embed → summarize → store  
- find(): embed query → search
- get(): retrieve by ID
"""

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import os
import subprocess
import sys

from .config import load_or_create_config, StoreConfig
from .paths import get_default_store_path
from .pending_summaries import PendingSummaryQueue
from .providers import get_registry
from .providers.base import (
    DocumentProvider,
    EmbeddingProvider,
    SummarizationProvider,
)
from .providers.embedding_cache import CachingEmbeddingProvider
from .store import ChromaStore
from .types import Item, filter_non_system_tags


# Default max length for truncated placeholder summaries
TRUNCATE_LENGTH = 500

# Maximum attempts before giving up on a pending summary
MAX_SUMMARY_ATTEMPTS = 5


# Collection name validation: lowercase ASCII and underscores only
COLLECTION_NAME_PATTERN = re.compile(r"^[a-z][a-z0-9_]*$")


class Keeper:
    """
    Semantic memory keeper - persistent storage with similarity search.

    Example:
        kp = Keeper()
        kp.update("file:///path/to/readme.md")
        results = kp.find("installation instructions")
    """
    
    def __init__(
        self,
        store_path: Optional[str | Path] = None,
        collection: str = "default",
        decay_half_life_days: float = 30.0
    ) -> None:
        """
        Initialize or open an existing associative memory store.
        
        Args:
            store_path: Path to store directory. Uses default if not specified.
            collection: Default collection name.
            decay_half_life_days: Memory decay half-life in days (ACT-R model).
                After this many days, an item's effective relevance is halved.
                Set to 0 or negative to disable decay.
        """
        # Resolve store path
        if store_path is None:
            self._store_path = get_default_store_path()
        else:
            self._store_path = Path(store_path).resolve()
        
        # Validate collection name
        if not COLLECTION_NAME_PATTERN.match(collection):
            raise ValueError(
                f"Invalid collection name '{collection}'. "
                "Must be lowercase ASCII, starting with a letter."
            )
        self._default_collection = collection
        self._decay_half_life_days = decay_half_life_days
        
        # Load or create configuration
        self._config: StoreConfig = load_or_create_config(self._store_path)
        
        # Initialize providers
        registry = get_registry()
        
        self._document_provider: DocumentProvider = registry.create_document(
            self._config.document.name,
            self._config.document.params,
        )
        
        # Create embedding provider with caching
        base_embedding_provider = registry.create_embedding(
            self._config.embedding.name,
            self._config.embedding.params,
        )
        cache_path = self._store_path / "embedding_cache.db"
        self._embedding_provider: EmbeddingProvider = CachingEmbeddingProvider(
            base_embedding_provider,
            cache_path=cache_path,
        )
        
        self._summarization_provider: SummarizationProvider = registry.create_summarization(
            self._config.summarization.name,
            self._config.summarization.params,
        )

        # Initialize pending summary queue
        queue_path = self._store_path / "pending_summaries.db"
        self._pending_queue = PendingSummaryQueue(queue_path)

        # Initialize store
        self._store = ChromaStore(
            self._store_path,
            embedding_dimension=self._embedding_provider.dimension,
        )
    
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
        collection: Optional[str] = None,
        lazy: bool = False
    ) -> Item:
        """
        Insert or update a document in the store.

        Fetches the document, generates embeddings and summary, then stores it.

        **Update behavior:**
        - Summary: Always replaced with newly generated summary
        - Tags: Merged - existing source tags are preserved, new source_tags override
          on key collision. System tags (prefixed with _) are always managed by
          the system.

        Args:
            id: URI of document to fetch and index
            source_tags: User-provided tags to merge with existing tags
            collection: Target collection (uses default if None)
            lazy: If True, use truncated placeholder summary and queue for
                  background processing. Use `process_pending()` to generate
                  real summaries later.

        Returns:
            The stored Item with merged tags and new summary
        """
        coll = self._resolve_collection(collection)

        # Get existing item to preserve tags
        existing_tags = {}
        existing = self._store.get(coll, id)
        if existing:
            # Extract existing non-system tags
            existing_tags = filter_non_system_tags(existing.tags)

        # Fetch document
        doc = self._document_provider.fetch(id)

        # Generate embedding
        embedding = self._embedding_provider.embed(doc.content)

        # Generate summary (or queue for later if lazy)
        if lazy:
            # Truncated placeholder
            if len(doc.content) > TRUNCATE_LENGTH:
                summary = doc.content[:TRUNCATE_LENGTH] + "..."
            else:
                summary = doc.content
            # Queue for background processing
            self._pending_queue.enqueue(id, coll, doc.content)
        else:
            summary = self._summarization_provider.summarize(doc.content)

        # Build tags: existing + new (new overrides on collision)
        tags = {**existing_tags}

        # Merge in new source tags (filtered to prevent system tag override)
        if source_tags:
            tags.update(filter_non_system_tags(source_tags))

        # Add system tags
        tags["_source"] = "uri"
        if doc.content_type:
            tags["_content_type"] = doc.content_type

        # Store
        self._store.upsert(
            collection=coll,
            id=id,
            embedding=embedding,
            summary=summary,
            tags=tags,
        )

        # Spawn background processor if lazy
        if lazy:
            self._spawn_processor()

        # Return the stored item
        result = self._store.get(coll, id)
        return result.to_item()
    
    def remember(
        self,
        content: str,
        *,
        id: Optional[str] = None,
        source_tags: Optional[dict[str, str]] = None,
        collection: Optional[str] = None,
        lazy: bool = False
    ) -> Item:
        """
        Store inline content directly (without fetching from a URI).

        Use for conversation snippets, notes, insights.

        **Update behavior (when id already exists):**
        - Summary: Replaced with newly generated summary from content
        - Tags: Merged - existing source tags preserved, new source_tags override
          on key collision. System tags (prefixed with _) are always managed by
          the system.

        Args:
            content: Text to store and index
            id: Optional custom ID (auto-generated if None)
            source_tags: User-provided tags to merge with existing tags
            collection: Target collection (uses default if None)
            lazy: If True, use truncated placeholder summary and queue for
                  background processing. Use `process_pending()` to generate
                  real summaries later.

        Returns:
            The stored Item with merged tags and new summary
        """
        coll = self._resolve_collection(collection)

        # Generate ID if not provided
        if id is None:
            timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")
            id = f"mem:{timestamp}"

        # Get existing item to preserve tags
        existing_tags = {}
        existing = self._store.get(coll, id)
        if existing:
            # Extract existing non-system tags
            existing_tags = filter_non_system_tags(existing.tags)

        # Generate embedding
        embedding = self._embedding_provider.embed(content)

        # Generate summary (or queue for later if lazy)
        if lazy:
            # Truncated placeholder
            if len(content) > TRUNCATE_LENGTH:
                summary = content[:TRUNCATE_LENGTH] + "..."
            else:
                summary = content
            # Queue for background processing
            self._pending_queue.enqueue(id, coll, content)
        else:
            summary = self._summarization_provider.summarize(content)

        # Build tags: existing + new (new overrides on collision)
        tags = {**existing_tags}

        # Merge in new source tags (filtered)
        if source_tags:
            tags.update(filter_non_system_tags(source_tags))

        # Add system tags
        tags["_source"] = "inline"

        # Store
        self._store.upsert(
            collection=coll,
            id=id,
            embedding=embedding,
            summary=summary,
            tags=tags,
        )

        # Spawn background processor if lazy
        if lazy:
            self._spawn_processor()

        # Return the stored item
        result = self._store.get(coll, id)
        return result.to_item()

    # -------------------------------------------------------------------------
    # Query Operations
    # -------------------------------------------------------------------------
    
    def _apply_recency_decay(self, items: list[Item]) -> list[Item]:
        """
        Apply ACT-R style recency decay to search results.
        
        Multiplies each item's similarity score by a decay factor based on
        time since last update. Uses exponential decay with configurable half-life.
        
        Formula: effective_score = similarity × 0.5^(days_elapsed / half_life)
        """
        if self._decay_half_life_days <= 0:
            return items  # Decay disabled
        
        now = datetime.now(timezone.utc)
        decayed_items = []
        
        for item in items:
            # Get last update time from tags
            updated_str = item.tags.get("_updated")
            if updated_str and item.score is not None:
                try:
                    # Parse ISO timestamp
                    updated = datetime.fromisoformat(updated_str.replace("Z", "+00:00"))
                    days_elapsed = (now - updated).total_seconds() / 86400
                    
                    # Exponential decay: 0.5^(days/half_life)
                    decay_factor = 0.5 ** (days_elapsed / self._decay_half_life_days)
                    decayed_score = item.score * decay_factor
                    
                    # Create new Item with decayed score
                    decayed_items.append(Item(
                        id=item.id,
                        summary=item.summary,
                        tags=item.tags,
                        score=decayed_score
                    ))
                except (ValueError, TypeError):
                    # If timestamp parsing fails, keep original
                    decayed_items.append(item)
            else:
                decayed_items.append(item)
        
        # Re-sort by decayed score (highest first)
        decayed_items.sort(key=lambda x: x.score if x.score is not None else 0, reverse=True)
        
        return decayed_items
    
    def find(
        self,
        query: str,
        *,
        limit: int = 10,
        collection: Optional[str] = None
    ) -> list[Item]:
        """
        Find items using semantic similarity search.
        
        Scores are adjusted by recency decay (ACT-R model) - older items
        have reduced effective relevance unless recently accessed.
        """
        coll = self._resolve_collection(collection)
        
        # Embed query
        embedding = self._embedding_provider.embed(query)
        
        # Search (fetch extra to account for re-ranking)
        fetch_limit = limit * 2 if self._decay_half_life_days > 0 else limit
        results = self._store.query_embedding(coll, embedding, limit=fetch_limit)
        
        # Convert to Items and apply decay
        items = [r.to_item() for r in results]
        items = self._apply_recency_decay(items)
        
        return items[:limit]
    
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
        """
        coll = self._resolve_collection(collection)
        
        # Get the item to find its embedding
        item = self._store.get(coll, id)
        if item is None:
            raise KeyError(f"Item not found: {id}")
        
        # Search using the summary's embedding
        embedding = self._embedding_provider.embed(item.summary)
        actual_limit = limit + 1 if not include_self else limit
        results = self._store.query_embedding(coll, embedding, limit=actual_limit)
        
        # Filter self if needed
        if not include_self:
            results = [r for r in results if r.id != id]
        
        # Convert to Items and apply decay
        items = [r.to_item() for r in results]
        items = self._apply_recency_decay(items)
        
        return items[:limit]
    
    def query_fulltext(
        self,
        query: str,
        *,
        limit: int = 10,
        collection: Optional[str] = None
    ) -> list[Item]:
        """
        Search item summaries using full-text search.
        """
        coll = self._resolve_collection(collection)
        results = self._store.query_fulltext(coll, query, limit=limit)
        return [r.to_item() for r in results]
    
    def query_tag(
        self,
        key: Optional[str] = None,
        value: Optional[str] = None,
        *,
        limit: int = 100,
        collection: Optional[str] = None,
        **tags: str
    ) -> list[Item]:
        """
        Find items by tag(s).

        Usage:
            # Simple: single key-value pair
            query_tag("project", "myapp")
            query_tag("tradition", "buddhist")

            # Advanced: multiple tags via kwargs
            query_tag(tradition="buddhist", source="mn22")
        """
        coll = self._resolve_collection(collection)

        # Build tag filter from positional or keyword args
        tag_filter = {}

        if key is not None:
            if value is None:
                raise ValueError(f"Value required when querying by key '{key}'")
            tag_filter[key] = value

        if tags:
            tag_filter.update(tags)

        if not tag_filter:
            raise ValueError("At least one tag must be specified")

        # Build where clause
        where = {k: v for k, v in tag_filter.items()}

        results = self._store.query_metadata(coll, where, limit=limit)
        return [r.to_item() for r in results]
    
    # -------------------------------------------------------------------------
    # Direct Access
    # -------------------------------------------------------------------------
    
    def get(self, id: str, *, collection: Optional[str] = None) -> Optional[Item]:
        """
        Retrieve a specific item by ID.
        """
        coll = self._resolve_collection(collection)
        result = self._store.get(coll, id)
        if result is None:
            return None
        return result.to_item()
    
    def exists(self, id: str, *, collection: Optional[str] = None) -> bool:
        """
        Check if an item exists in the store.
        """
        coll = self._resolve_collection(collection)
        return self._store.exists(coll, id)
    
    def delete(self, id: str, *, collection: Optional[str] = None) -> bool:
        """
        Delete an item from the store.
        
        Returns True if item existed and was deleted.
        """
        coll = self._resolve_collection(collection)
        return self._store.delete(coll, id)
    
    # -------------------------------------------------------------------------
    # Collection Management
    # -------------------------------------------------------------------------
    
    def list_collections(self) -> list[str]:
        """
        List all collections in the store.
        """
        return self._store.list_collections()
    
    def count(self, *, collection: Optional[str] = None) -> int:
        """
        Count items in a collection.
        """
        coll = self._resolve_collection(collection)
        return self._store.count(coll)
    
    def embedding_cache_stats(self) -> dict:
        """
        Get embedding cache statistics.

        Returns dict with: entries, hits, misses, hit_rate, cache_path
        """
        if isinstance(self._embedding_provider, CachingEmbeddingProvider):
            return self._embedding_provider.stats()
        return {"enabled": False}

    # -------------------------------------------------------------------------
    # Pending Summaries
    # -------------------------------------------------------------------------

    def process_pending(self, limit: int = 10) -> int:
        """
        Process pending summaries queued by lazy update/remember.

        Generates real summaries for items that were indexed with
        truncated placeholders. Updates the stored items in place.

        Items that fail MAX_SUMMARY_ATTEMPTS times are removed from
        the queue (the truncated placeholder remains in the store).

        Args:
            limit: Maximum number of items to process in this batch

        Returns:
            Number of items successfully processed
        """
        items = self._pending_queue.dequeue(limit=limit)
        processed = 0

        for item in items:
            # Skip items that have failed too many times
            # (attempts was already incremented by dequeue, so check >= MAX)
            if item.attempts >= MAX_SUMMARY_ATTEMPTS:
                # Give up - remove from queue, keep truncated placeholder
                self._pending_queue.complete(item.id, item.collection)
                continue

            try:
                # Generate real summary
                summary = self._summarization_provider.summarize(item.content)

                # Update the stored item's summary
                self._store.update_summary(item.collection, item.id, summary)

                # Remove from queue
                self._pending_queue.complete(item.id, item.collection)
                processed += 1

            except Exception:
                # Leave in queue for retry (attempt counter already incremented)
                pass

        return processed

    def pending_count(self) -> int:
        """Get count of pending summaries awaiting processing."""
        return self._pending_queue.count()

    def pending_stats(self) -> dict:
        """
        Get pending summary queue statistics.

        Returns dict with: pending, collections, max_attempts, oldest, queue_path
        """
        return self._pending_queue.stats()

    @property
    def _processor_pid_path(self) -> Path:
        """Path to the processor PID file."""
        return self._store_path / "processor.pid"

    def _is_processor_running(self) -> bool:
        """Check if a processor is already running."""
        pid_path = self._processor_pid_path
        if not pid_path.exists():
            return False

        try:
            pid = int(pid_path.read_text().strip())
            # Check if process is alive by sending signal 0
            os.kill(pid, 0)
            return True
        except (ValueError, ProcessLookupError, PermissionError):
            # PID file invalid, process dead, or permission issue
            # Clean up stale PID file
            try:
                pid_path.unlink()
            except OSError:
                pass
            return False

    def _spawn_processor(self) -> bool:
        """
        Spawn a background processor if not already running.

        Returns True if a new processor was spawned, False if one was
        already running or spawn failed.
        """
        if self._is_processor_running():
            return False

        try:
            # Spawn detached process
            # Use sys.executable to ensure we use the same Python
            cmd = [
                sys.executable, "-m", "keep.cli",
                "process-pending",
                "--daemon",
                "--store", str(self._store_path),
            ]

            # Platform-specific detachment
            kwargs: dict = {
                "stdout": subprocess.DEVNULL,
                "stderr": subprocess.DEVNULL,
                "stdin": subprocess.DEVNULL,
            }

            if sys.platform != "win32":
                # Unix: start new session to fully detach
                kwargs["start_new_session"] = True
            else:
                # Windows: use CREATE_NEW_PROCESS_GROUP
                kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP

            subprocess.Popen(cmd, **kwargs)
            return True

        except Exception:
            # Spawn failed - not critical, queue will be processed later
            return False

    def close(self) -> None:
        """
        Close resources (embedding cache connection, pending queue, etc.).

        Good practice to call when done, though Python's GC will clean up eventually.
        """
        # Close embedding cache if it exists
        if hasattr(self._embedding_provider, '_cache'):
            cache = self._embedding_provider._cache
            if hasattr(cache, 'close'):
                cache.close()

        # Close pending summary queue
        if hasattr(self, '_pending_queue'):
            self._pending_queue.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close resources."""
        self.close()
        return False

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
