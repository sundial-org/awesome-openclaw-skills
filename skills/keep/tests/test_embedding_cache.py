"""Tests for embedding cache."""

import pytest
from pathlib import Path

from keep.providers.embedding_cache import EmbeddingCache, CachingEmbeddingProvider


class MockEmbeddingProvider:
    """Mock embedding provider for testing cache behavior."""
    
    def __init__(self, dimension: int = 4):
        self.model_name = "mock-model"
        self._dimension = dimension
        self.embed_calls = 0
        self.batch_calls = 0
    
    @property
    def dimension(self) -> int:
        return self._dimension
    
    def embed(self, text: str) -> list[float]:
        self.embed_calls += 1
        # Simple deterministic "embedding" based on text length
        return [float(len(text) % (i + 1)) for i in range(self._dimension)]
    
    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        self.batch_calls += 1
        return [self.embed(t) for t in texts]


class TestEmbeddingCache:
    """Test the low-level EmbeddingCache."""
    
    @pytest.fixture
    def cache(self, tmp_path: Path) -> EmbeddingCache:
        return EmbeddingCache(tmp_path / "cache.db")
    
    def test_cache_miss_returns_none(self, cache: EmbeddingCache) -> None:
        """Cache miss returns None."""
        result = cache.get("model", "unknown content")
        assert result is None
    
    def test_put_and_get(self, cache: EmbeddingCache) -> None:
        """Can store and retrieve embeddings."""
        embedding = [0.1, 0.2, 0.3, 0.4]
        cache.put("model", "hello world", embedding)
        
        result = cache.get("model", "hello world")
        assert result == embedding
    
    def test_different_models_different_cache(self, cache: EmbeddingCache) -> None:
        """Same content with different models has different cache entries."""
        emb1 = [0.1, 0.2]
        emb2 = [0.9, 0.8]
        
        cache.put("model-a", "hello", emb1)
        cache.put("model-b", "hello", emb2)
        
        assert cache.get("model-a", "hello") == emb1
        assert cache.get("model-b", "hello") == emb2
    
    def test_overwrite_existing(self, cache: EmbeddingCache) -> None:
        """Writing same key overwrites."""
        cache.put("model", "text", [1.0])
        cache.put("model", "text", [2.0])
        
        assert cache.get("model", "text") == [2.0]
    
    def test_stats(self, cache: EmbeddingCache) -> None:
        """Stats reports entry count."""
        cache.put("model", "a", [1.0])
        cache.put("model", "b", [2.0])
        
        stats = cache.stats()
        assert stats["entries"] == 2
        assert stats["models"] == 1
    
    def test_clear(self, cache: EmbeddingCache) -> None:
        """Clear removes all entries."""
        cache.put("model", "text", [1.0])
        cache.clear()
        
        assert cache.get("model", "text") is None
        assert cache.stats()["entries"] == 0
    
    def test_eviction_when_max_exceeded(self, tmp_path: Path) -> None:
        """Old entries evicted when max exceeded."""
        cache = EmbeddingCache(tmp_path / "small_cache.db", max_entries=10)
        
        # Add 15 entries
        for i in range(15):
            cache.put("model", f"text-{i}", [float(i)])
        
        # Should have evicted some
        stats = cache.stats()
        assert stats["entries"] <= 10


class TestCachingEmbeddingProvider:
    """Test the caching wrapper."""
    
    @pytest.fixture
    def mock_provider(self) -> MockEmbeddingProvider:
        return MockEmbeddingProvider()
    
    @pytest.fixture
    def cached_provider(
        self, mock_provider: MockEmbeddingProvider, tmp_path: Path
    ) -> CachingEmbeddingProvider:
        return CachingEmbeddingProvider(
            mock_provider,
            cache_path=tmp_path / "cache.db"
        )
    
    def test_first_call_is_cache_miss(
        self, cached_provider: CachingEmbeddingProvider, mock_provider: MockEmbeddingProvider
    ) -> None:
        """First embed call goes to the provider."""
        cached_provider.embed("hello")
        
        assert mock_provider.embed_calls == 1
        assert cached_provider.stats()["misses"] == 1
    
    def test_second_call_is_cache_hit(
        self, cached_provider: CachingEmbeddingProvider, mock_provider: MockEmbeddingProvider
    ) -> None:
        """Second call with same text uses cache."""
        cached_provider.embed("hello")
        cached_provider.embed("hello")
        
        # Provider only called once
        assert mock_provider.embed_calls == 1
        
        stats = cached_provider.stats()
        assert stats["hits"] == 1
        assert stats["misses"] == 1
    
    def test_different_text_is_cache_miss(
        self, cached_provider: CachingEmbeddingProvider, mock_provider: MockEmbeddingProvider
    ) -> None:
        """Different text is a cache miss."""
        cached_provider.embed("hello")
        cached_provider.embed("world")
        
        assert mock_provider.embed_calls == 2
    
    def test_batch_uses_cache(
        self, cached_provider: CachingEmbeddingProvider, mock_provider: MockEmbeddingProvider
    ) -> None:
        """Batch embed uses cache for known texts."""
        # Pre-cache one text
        cached_provider.embed("hello")
        
        # Batch with mix of cached and uncached
        results = cached_provider.embed_batch(["hello", "world", "hello"])
        
        assert len(results) == 3
        # Only "world" should have caused additional embed
        # (batch_calls goes through embed() in our mock)
        assert mock_provider.batch_calls == 1
    
    def test_dimension_passthrough(
        self, cached_provider: CachingEmbeddingProvider, mock_provider: MockEmbeddingProvider
    ) -> None:
        """Dimension property passes through."""
        assert cached_provider.dimension == mock_provider.dimension
    
    def test_model_name_passthrough(
        self, cached_provider: CachingEmbeddingProvider, mock_provider: MockEmbeddingProvider
    ) -> None:
        """Model name property passes through."""
        assert cached_provider.model_name == mock_provider.model_name
    
    def test_hit_rate_in_stats(
        self, cached_provider: CachingEmbeddingProvider
    ) -> None:
        """Stats includes hit rate."""
        cached_provider.embed("a")
        cached_provider.embed("a")
        cached_provider.embed("a")
        
        stats = cached_provider.stats()
        assert stats["hit_rate"] == "66.7%"
