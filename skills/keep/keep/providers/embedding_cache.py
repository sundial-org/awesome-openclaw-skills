"""
Embedding cache using SQLite.

Wraps any EmbeddingProvider to cache embeddings by content hash,
avoiding redundant embedding calls for unchanged content.
"""

import hashlib
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .base import EmbeddingProvider


class EmbeddingCache:
    """
    SQLite-based embedding cache.
    
    Cache key is SHA256(model_name + content), so different models
    don't share cached embeddings.
    """
    
    def __init__(self, cache_path: Path, max_entries: int = 50000):
        """
        Args:
            cache_path: Path to SQLite database file
            max_entries: Maximum cache entries (LRU eviction when exceeded)
        """
        self._cache_path = cache_path
        self._max_entries = max_entries
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()
    
    def _init_db(self) -> None:
        """Initialize the SQLite database."""
        self._cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._cache_path), check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS embedding_cache (
                content_hash TEXT PRIMARY KEY,
                model_name TEXT NOT NULL,
                embedding BLOB NOT NULL,
                dimension INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                last_accessed TEXT NOT NULL
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_last_accessed 
            ON embedding_cache(last_accessed)
        """)
        self._conn.commit()
    
    def _hash_key(self, model_name: str, content: str) -> str:
        """Generate cache key from model name and content."""
        key_input = f"{model_name}:{content}"
        return hashlib.sha256(key_input.encode("utf-8")).hexdigest()
    
    def get(self, model_name: str, content: str) -> Optional[list[float]]:
        """
        Get cached embedding if it exists.
        
        Updates last_accessed timestamp on hit.
        """
        content_hash = self._hash_key(model_name, content)
        cursor = self._conn.execute(
            "SELECT embedding FROM embedding_cache WHERE content_hash = ?",
            (content_hash,)
        )
        row = cursor.fetchone()
        
        if row is not None:
            # Update last_accessed
            now = datetime.now(timezone.utc).isoformat()
            self._conn.execute(
                "UPDATE embedding_cache SET last_accessed = ? WHERE content_hash = ?",
                (now, content_hash)
            )
            self._conn.commit()
            
            # Deserialize embedding
            return json.loads(row[0])
        
        return None
    
    def put(
        self,
        model_name: str,
        content: str,
        embedding: list[float]
    ) -> None:
        """
        Cache an embedding.
        
        Evicts oldest entries if cache exceeds max_entries.
        """
        content_hash = self._hash_key(model_name, content)
        now = datetime.now(timezone.utc).isoformat()
        embedding_blob = json.dumps(embedding)
        
        self._conn.execute("""
            INSERT OR REPLACE INTO embedding_cache 
            (content_hash, model_name, embedding, dimension, created_at, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (content_hash, model_name, embedding_blob, len(embedding), now, now))
        self._conn.commit()
        
        # Evict old entries if needed
        self._maybe_evict()
    
    def _maybe_evict(self) -> None:
        """Evict oldest entries if cache exceeds max size."""
        cursor = self._conn.execute("SELECT COUNT(*) FROM embedding_cache")
        count = cursor.fetchone()[0]
        
        if count > self._max_entries:
            # Delete oldest 10% by last_accessed
            evict_count = max(1, count // 10)
            self._conn.execute("""
                DELETE FROM embedding_cache 
                WHERE content_hash IN (
                    SELECT content_hash FROM embedding_cache 
                    ORDER BY last_accessed ASC 
                    LIMIT ?
                )
            """, (evict_count,))
            self._conn.commit()
    
    def stats(self) -> dict:
        """Get cache statistics."""
        cursor = self._conn.execute("""
            SELECT COUNT(*), COUNT(DISTINCT model_name) 
            FROM embedding_cache
        """)
        count, models = cursor.fetchone()
        return {
            "entries": count,
            "models": models,
            "max_entries": self._max_entries,
            "cache_path": str(self._cache_path),
        }
    
    def clear(self) -> None:
        """Clear all cached embeddings."""
        self._conn.execute("DELETE FROM embedding_cache")
        self._conn.commit()

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __del__(self) -> None:
        """Ensure connection is closed on cleanup."""
        self.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - close connection."""
        self.close()
        return False


class CachingEmbeddingProvider:
    """
    Wrapper that adds caching to any EmbeddingProvider.
    
    Usage:
        base_provider = SentenceTransformerEmbedding()
        cached = CachingEmbeddingProvider(base_provider, cache_path)
    """
    
    def __init__(
        self,
        provider: EmbeddingProvider,
        cache_path: Path,
        max_entries: int = 50000
    ):
        self._provider = provider
        self._cache = EmbeddingCache(cache_path, max_entries)
        self._hits = 0
        self._misses = 0
    
    @property
    def model_name(self) -> str:
        """Get the underlying provider's model name."""
        return getattr(self._provider, "model_name", "unknown")
    
    @property
    def dimension(self) -> int:
        """Get embedding dimension from the wrapped provider."""
        return self._provider.dimension
    
    def embed(self, text: str) -> list[float]:
        """
        Get embedding, using cache when available.
        """
        # Check cache
        cached = self._cache.get(self.model_name, text)
        if cached is not None:
            self._hits += 1
            return cached
        
        # Cache miss - compute embedding
        self._misses += 1
        embedding = self._provider.embed(text)
        
        # Store in cache
        self._cache.put(self.model_name, text, embedding)
        
        return embedding
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """
        Get embeddings for batch, using cache where available.
        
        Only computes embeddings for cache misses.
        """
        results: list[Optional[list[float]]] = [None] * len(texts)
        to_embed: list[tuple[int, str]] = []
        
        # Check cache for each text
        for i, text in enumerate(texts):
            cached = self._cache.get(self.model_name, text)
            if cached is not None:
                self._hits += 1
                results[i] = cached
            else:
                self._misses += 1
                to_embed.append((i, text))
        
        # Batch embed cache misses
        if to_embed:
            indices, texts_to_embed = zip(*to_embed)
            embeddings = self._provider.embed_batch(list(texts_to_embed))
            
            for idx, text, embedding in zip(indices, texts_to_embed, embeddings):
                results[idx] = embedding
                self._cache.put(self.model_name, text, embedding)
        
        return results  # type: ignore
    
    def stats(self) -> dict:
        """Get cache and hit/miss statistics."""
        cache_stats = self._cache.stats()
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0
        return {
            **cache_stats,
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.1%}",
        }
