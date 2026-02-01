"""
Vector store implementation using ChromaDb.

This is the first concrete store implementation. The interface is designed
to be extractable to a Protocol when additional backends are needed.

For now, ChromaDb is the only implementation — and that's fine.
"""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from .types import Item, SYSTEM_TAG_PREFIX


@dataclass
class StoreResult:
    """Result from a store query with raw data before Item conversion."""
    id: str
    summary: str
    tags: dict[str, str]
    distance: float | None = None  # Lower is more similar in Chroma
    
    def to_item(self) -> Item:
        """Convert to Item, transforming distance to similarity score."""
        # Chroma uses L2 distance by default; convert to 0-1 similarity
        # score = 1 / (1 + distance) gives us 1.0 for identical, approaching 0 for distant
        score = None
        if self.distance is not None:
            score = 1.0 / (1.0 + self.distance)
        return Item(id=self.id, summary=self.summary, tags=self.tags, score=score)


class ChromaStore:
    """
    Persistent vector store using ChromaDb.
    
    Each collection maps to a ChromaDb collection. Items are stored with:
    - id: The item's URI or custom identifier
    - embedding: Vector representation for similarity search
    - document: The item's summary (stored for retrieval, searchable)
    - metadata: All tags (flattened to strings for Chroma compatibility)
    
    The store is initialized at a specific path and persists across sessions.
    
    Future: This class's public interface could become a Protocol for
    pluggable backends (SQLite+faiss, Postgres+pgvector, etc.)
    """
    
    def __init__(self, store_path: Path, embedding_dimension: int):
        """
        Initialize or open a ChromaDb store.
        
        Args:
            store_path: Directory for persistent storage
            embedding_dimension: Expected dimension of embeddings (for validation)
        """
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise RuntimeError(
                "ChromaStore requires 'chromadb' library. "
                "Install with: pip install chromadb"
            )
        
        self._store_path = store_path
        self._embedding_dimension = embedding_dimension
        
        # Ensure store directory exists
        store_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize persistent client
        self._client = chromadb.PersistentClient(
            path=str(store_path / "chroma"),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # Cache of collection handles
        self._collections: dict[str, Any] = {}
    
    def _get_collection(self, name: str) -> Any:
        """Get or create a collection by name."""
        if name not in self._collections:
            # get_or_create handles both cases
            self._collections[name] = self._client.get_or_create_collection(
                name=name,
                metadata={"hnsw:space": "l2"},  # L2 distance for similarity
            )
        return self._collections[name]
    
    def _tags_to_metadata(self, tags: dict[str, str]) -> dict[str, Any]:
        """
        Convert tags to Chroma metadata format.
        
        Chroma metadata values must be str, int, float, or bool.
        We store everything as strings for consistency.
        """
        return {k: str(v) for k, v in tags.items()}
    
    def _metadata_to_tags(self, metadata: dict[str, Any] | None) -> dict[str, str]:
        """Convert Chroma metadata back to tags."""
        if metadata is None:
            return {}
        return {k: str(v) for k, v in metadata.items()}
    
    # -------------------------------------------------------------------------
    # Write Operations
    # -------------------------------------------------------------------------
    
    def upsert(
        self,
        collection: str,
        id: str,
        embedding: list[float],
        summary: str,
        tags: dict[str, str],
    ) -> None:
        """
        Insert or update an item in the store.
        
        Args:
            collection: Collection name
            id: Item identifier (URI or custom)
            embedding: Vector embedding
            summary: Human-readable summary (stored as document)
            tags: All tags (source + system + generated)
        """
        if len(embedding) != self._embedding_dimension:
            raise ValueError(
                f"Embedding dimension mismatch: expected {self._embedding_dimension}, "
                f"got {len(embedding)}"
            )
        
        coll = self._get_collection(collection)
        
        # Add timestamp if not present
        now = datetime.now(timezone.utc).isoformat()
        if "_updated" not in tags:
            tags = {**tags, "_updated": now}
        if "_created" not in tags:
            # Check if item exists to preserve original created time
            existing = coll.get(ids=[id], include=["metadatas"])
            if existing["ids"]:
                old_created = existing["metadatas"][0].get("_created")
                if old_created:
                    tags = {**tags, "_created": old_created}
                else:
                    tags = {**tags, "_created": now}
            else:
                tags = {**tags, "_created": now}
        
        # Add date portion for easier date queries
        tags = {**tags, "_updated_date": now[:10]}
        
        coll.upsert(
            ids=[id],
            embeddings=[embedding],
            documents=[summary],
            metadatas=[self._tags_to_metadata(tags)],
        )
    
    def delete(self, collection: str, id: str) -> bool:
        """
        Delete an item from the store.
        
        Args:
            collection: Collection name
            id: Item identifier
            
        Returns:
            True if item existed and was deleted, False if not found
        """
        coll = self._get_collection(collection)
        
        # Check existence first
        existing = coll.get(ids=[id])
        if not existing["ids"]:
            return False
        
        coll.delete(ids=[id])
        return True

    def update_summary(self, collection: str, id: str, summary: str) -> bool:
        """
        Update just the summary of an existing item.

        Used by lazy summarization to replace placeholder summaries
        with real generated summaries.

        Args:
            collection: Collection name
            id: Item identifier
            summary: New summary text

        Returns:
            True if item was updated, False if not found
        """
        coll = self._get_collection(collection)

        # Get existing item
        existing = coll.get(ids=[id], include=["metadatas"])
        if not existing["ids"]:
            return False

        # Update metadata with new timestamp
        metadata = existing["metadatas"][0] or {}
        now = datetime.now(timezone.utc).isoformat()
        metadata["_updated"] = now
        metadata["_updated_date"] = now[:10]

        # Update just the document (summary) and metadata
        coll.update(
            ids=[id],
            documents=[summary],
            metadatas=[metadata],
        )
        return True

    # -------------------------------------------------------------------------
    # Read Operations
    # -------------------------------------------------------------------------
    
    def get(self, collection: str, id: str) -> StoreResult | None:
        """
        Retrieve a specific item by ID.
        
        Args:
            collection: Collection name
            id: Item identifier
            
        Returns:
            StoreResult if found, None otherwise
        """
        coll = self._get_collection(collection)
        result = coll.get(
            ids=[id],
            include=["documents", "metadatas"],
        )
        
        if not result["ids"]:
            return None
        
        return StoreResult(
            id=result["ids"][0],
            summary=result["documents"][0] or "",
            tags=self._metadata_to_tags(result["metadatas"][0]),
        )
    
    def exists(self, collection: str, id: str) -> bool:
        """Check if an item exists in the store."""
        coll = self._get_collection(collection)
        result = coll.get(ids=[id], include=[])
        return bool(result["ids"])
    
    def query_embedding(
        self,
        collection: str,
        embedding: list[float],
        limit: int = 10,
        where: dict[str, Any] | None = None,
    ) -> list[StoreResult]:
        """
        Query by embedding similarity.
        
        Args:
            collection: Collection name
            embedding: Query embedding vector
            limit: Maximum results to return
            where: Optional metadata filter (Chroma where clause)
            
        Returns:
            List of results ordered by similarity (most similar first)
        """
        coll = self._get_collection(collection)
        
        query_params = {
            "query_embeddings": [embedding],
            "n_results": limit,
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            query_params["where"] = where
        
        result = coll.query(**query_params)
        
        results = []
        for i, id in enumerate(result["ids"][0]):
            results.append(StoreResult(
                id=id,
                summary=result["documents"][0][i] or "",
                tags=self._metadata_to_tags(result["metadatas"][0][i]),
                distance=result["distances"][0][i] if result["distances"] else None,
            ))
        
        return results
    
    def query_metadata(
        self,
        collection: str,
        where: dict[str, Any],
        limit: int = 100,
    ) -> list[StoreResult]:
        """
        Query by metadata filter (tag query).
        
        Args:
            collection: Collection name
            where: Chroma where clause for metadata filtering
            limit: Maximum results to return
            
        Returns:
            List of matching results (no particular order)
        """
        coll = self._get_collection(collection)
        
        result = coll.get(
            where=where,
            limit=limit,
            include=["documents", "metadatas"],
        )
        
        results = []
        for i, id in enumerate(result["ids"]):
            results.append(StoreResult(
                id=id,
                summary=result["documents"][i] or "",
                tags=self._metadata_to_tags(result["metadatas"][i]),
            ))
        
        return results
    
    def query_fulltext(
        self,
        collection: str,
        query: str,
        limit: int = 10,
    ) -> list[StoreResult]:
        """
        Query by full-text search on document content (summaries).
        
        Args:
            collection: Collection name
            query: Text to search for
            limit: Maximum results to return
            
        Returns:
            List of matching results
        """
        coll = self._get_collection(collection)
        
        # Chroma's where_document does substring matching
        result = coll.get(
            where_document={"$contains": query},
            limit=limit,
            include=["documents", "metadatas"],
        )
        
        results = []
        for i, id in enumerate(result["ids"]):
            results.append(StoreResult(
                id=id,
                summary=result["documents"][i] or "",
                tags=self._metadata_to_tags(result["metadatas"][i]),
            ))
        
        return results
    
    # -------------------------------------------------------------------------
    # Collection Management
    # -------------------------------------------------------------------------
    
    def list_collections(self) -> list[str]:
        """List all collection names in the store."""
        collections = self._client.list_collections()
        return [c.name for c in collections]
    
    def delete_collection(self, name: str) -> bool:
        """
        Delete an entire collection.
        
        Args:
            name: Collection name
            
        Returns:
            True if collection existed and was deleted
        """
        try:
            self._client.delete_collection(name)
            self._collections.pop(name, None)
            return True
        except ValueError:
            return False
    
    def count(self, collection: str) -> int:
        """Return the number of items in a collection."""
        coll = self._get_collection(collection)
        return coll.count()
