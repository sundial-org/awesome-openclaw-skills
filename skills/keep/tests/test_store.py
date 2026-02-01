"""
Tests for ChromaDb store wrapper.

These tests use a temporary directory for each test to ensure isolation.
"""

import tempfile
from pathlib import Path

import pytest

# Skip all tests if chromadb not installed
chromadb = pytest.importorskip("chromadb")

from keep.store import ChromaStore, StoreResult


# -----------------------------------------------------------------------------
# Fixtures
# -----------------------------------------------------------------------------

@pytest.fixture
def store_path():
    """Provide a temporary directory for store tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def store(store_path):
    """Create a ChromaStore instance for testing."""
    return ChromaStore(store_path, embedding_dimension=4)


@pytest.fixture
def sample_embedding():
    """A simple 4-dimensional embedding for testing."""
    return [0.1, 0.2, 0.3, 0.4]


# -----------------------------------------------------------------------------
# Basic Operations
# -----------------------------------------------------------------------------

class TestBasicOperations:
    """Tests for upsert, get, exists, delete."""
    
    def test_upsert_and_get(self, store, sample_embedding):
        """Can store and retrieve an item."""
        store.upsert(
            collection="test",
            id="doc:1",
            embedding=sample_embedding,
            summary="Test document",
            tags={"project": "myapp", "type": "readme"},
        )
        
        result = store.get("test", "doc:1")
        
        assert result is not None
        assert result.id == "doc:1"
        assert result.summary == "Test document"
        assert result.tags["project"] == "myapp"
        assert result.tags["type"] == "readme"
    
    def test_get_not_found(self, store):
        """Get returns None for missing items."""
        result = store.get("test", "nonexistent")
        assert result is None
    
    def test_exists(self, store, sample_embedding):
        """Exists correctly reports item presence."""
        assert not store.exists("test", "doc:1")
        
        store.upsert("test", "doc:1", sample_embedding, "Test", {})
        
        assert store.exists("test", "doc:1")
    
    def test_delete(self, store, sample_embedding):
        """Delete removes items."""
        store.upsert("test", "doc:1", sample_embedding, "Test", {})
        assert store.exists("test", "doc:1")
        
        deleted = store.delete("test", "doc:1")
        
        assert deleted is True
        assert not store.exists("test", "doc:1")
    
    def test_delete_not_found(self, store):
        """Delete returns False for missing items."""
        deleted = store.delete("test", "nonexistent")
        assert deleted is False
    
    def test_upsert_updates_existing(self, store, sample_embedding):
        """Upsert updates existing items."""
        store.upsert("test", "doc:1", sample_embedding, "Original", {"v": "1"})
        store.upsert("test", "doc:1", sample_embedding, "Updated", {"v": "2"})
        
        result = store.get("test", "doc:1")
        
        assert result.summary == "Updated"
        assert result.tags["v"] == "2"


# -----------------------------------------------------------------------------
# System Tags
# -----------------------------------------------------------------------------

class TestSystemTags:
    """Tests for automatic system tag handling."""
    
    def test_created_timestamp_added(self, store, sample_embedding):
        """_created is automatically added on first insert."""
        store.upsert("test", "doc:1", sample_embedding, "Test", {})
        
        result = store.get("test", "doc:1")
        
        assert "_created" in result.tags
        assert result.tags["_created"].startswith("20")  # ISO timestamp
    
    def test_updated_timestamp_added(self, store, sample_embedding):
        """_updated is automatically added."""
        store.upsert("test", "doc:1", sample_embedding, "Test", {})
        
        result = store.get("test", "doc:1")
        
        assert "_updated" in result.tags
        assert "_updated_date" in result.tags
    
    def test_created_preserved_on_update(self, store, sample_embedding):
        """_created is preserved when updating an item."""
        store.upsert("test", "doc:1", sample_embedding, "Original", {})
        original = store.get("test", "doc:1")
        original_created = original.tags["_created"]
        
        store.upsert("test", "doc:1", sample_embedding, "Updated", {})
        updated = store.get("test", "doc:1")
        
        assert updated.tags["_created"] == original_created


# -----------------------------------------------------------------------------
# Embedding Queries
# -----------------------------------------------------------------------------

class TestEmbeddingQueries:
    """Tests for semantic similarity search."""
    
    def test_query_embedding_returns_similar(self, store):
        """Query returns items by embedding similarity."""
        store.upsert("test", "doc:1", [1.0, 0.0, 0.0, 0.0], "First", {})
        store.upsert("test", "doc:2", [0.9, 0.1, 0.0, 0.0], "Second", {})  # Similar to first
        store.upsert("test", "doc:3", [0.0, 0.0, 1.0, 0.0], "Third", {})   # Different
        
        results = store.query_embedding("test", [1.0, 0.0, 0.0, 0.0], limit=2)
        
        assert len(results) == 2
        assert results[0].id == "doc:1"  # Most similar
        assert results[1].id == "doc:2"  # Second most similar
    
    def test_query_embedding_with_limit(self, store):
        """Query respects limit parameter."""
        for i in range(5):
            store.upsert("test", f"doc:{i}", [float(i), 0.0, 0.0, 0.0], f"Doc {i}", {})
        
        results = store.query_embedding("test", [0.0, 0.0, 0.0, 0.0], limit=3)
        
        assert len(results) == 3
    
    def test_query_embedding_returns_score(self, store, sample_embedding):
        """Query results include similarity scores."""
        store.upsert("test", "doc:1", sample_embedding, "Test", {})
        
        results = store.query_embedding("test", sample_embedding, limit=1)
        
        assert results[0].distance is not None
        item = results[0].to_item()
        assert item.score is not None
        assert item.score > 0.9  # Should be very similar (nearly 1.0)


# -----------------------------------------------------------------------------
# Metadata Queries
# -----------------------------------------------------------------------------

class TestMetadataQueries:
    """Tests for tag-based filtering."""
    
    def test_query_metadata_exact_match(self, store, sample_embedding):
        """Query by exact tag value."""
        store.upsert("test", "doc:1", sample_embedding, "Alpha", {"project": "alpha"})
        store.upsert("test", "doc:2", sample_embedding, "Beta", {"project": "beta"})
        
        results = store.query_metadata("test", {"project": "alpha"})
        
        assert len(results) == 1
        assert results[0].id == "doc:1"
    
    def test_query_metadata_multiple_conditions(self, store, sample_embedding):
        """Query with multiple tag conditions (AND)."""
        store.upsert("test", "doc:1", sample_embedding, "A", {"type": "doc", "lang": "en"})
        store.upsert("test", "doc:2", sample_embedding, "B", {"type": "doc", "lang": "es"})
        store.upsert("test", "doc:3", sample_embedding, "C", {"type": "code", "lang": "en"})
        
        results = store.query_metadata("test", {
            "$and": [
                {"type": "doc"},
                {"lang": "en"},
            ]
        })
        
        assert len(results) == 1
        assert results[0].id == "doc:1"


# -----------------------------------------------------------------------------
# Fulltext Queries
# -----------------------------------------------------------------------------

class TestFulltextQueries:
    """Tests for full-text search on summaries."""
    
    def test_query_fulltext_substring(self, store, sample_embedding):
        """Fulltext search finds substring matches."""
        store.upsert("test", "doc:1", sample_embedding, "Installation guide for Python", {})
        store.upsert("test", "doc:2", sample_embedding, "API reference documentation", {})
        
        results = store.query_fulltext("test", "Python")
        
        assert len(results) == 1
        assert results[0].id == "doc:1"
    
    def test_query_fulltext_no_match(self, store, sample_embedding):
        """Fulltext search returns empty for no matches."""
        store.upsert("test", "doc:1", sample_embedding, "Hello world", {})
        
        results = store.query_fulltext("test", "nonexistent")
        
        assert len(results) == 0


# -----------------------------------------------------------------------------
# Collection Management
# -----------------------------------------------------------------------------

class TestCollectionManagement:
    """Tests for collection-level operations."""
    
    def test_list_collections_empty(self, store):
        """List collections on empty store."""
        # Accessing a collection creates it
        collections = store.list_collections()
        assert collections == []
    
    def test_list_collections(self, store, sample_embedding):
        """List collections after creating some."""
        store.upsert("alpha", "doc:1", sample_embedding, "A", {})
        store.upsert("beta", "doc:1", sample_embedding, "B", {})
        
        collections = store.list_collections()
        
        assert set(collections) == {"alpha", "beta"}
    
    def test_count(self, store, sample_embedding):
        """Count items in a collection."""
        assert store.count("test") == 0
        
        store.upsert("test", "doc:1", sample_embedding, "A", {})
        store.upsert("test", "doc:2", sample_embedding, "B", {})
        
        assert store.count("test") == 2
    
    def test_delete_collection(self, store, sample_embedding):
        """Delete an entire collection."""
        store.upsert("test", "doc:1", sample_embedding, "A", {})
        assert store.count("test") == 1
        
        deleted = store.delete_collection("test")
        
        assert deleted is True
        assert "test" not in store.list_collections()


# -----------------------------------------------------------------------------
# StoreResult Conversion
# -----------------------------------------------------------------------------

class TestStoreResult:
    """Tests for StoreResult to Item conversion."""
    
    def test_to_item_without_distance(self):
        """Convert result without distance (no score)."""
        result = StoreResult(id="doc:1", summary="Test", tags={"k": "v"})
        item = result.to_item()
        
        assert item.id == "doc:1"
        assert item.summary == "Test"
        assert item.tags == {"k": "v"}
        assert item.score is None
    
    def test_to_item_with_distance(self):
        """Convert result with distance to similarity score."""
        result = StoreResult(id="doc:1", summary="Test", tags={}, distance=0.0)
        item = result.to_item()
        
        # Distance 0 should give score 1.0 (identical)
        assert item.score == 1.0
    
    def test_to_item_distance_to_score(self):
        """Distance conversion: higher distance = lower score."""
        close = StoreResult(id="a", summary="", tags={}, distance=0.1)
        far = StoreResult(id="b", summary="", tags={}, distance=10.0)
        
        assert close.to_item().score > far.to_item().score


# -----------------------------------------------------------------------------
# Persistence
# -----------------------------------------------------------------------------

class TestPersistence:
    """Tests for data persistence across store instances."""
    
    def test_data_persists(self, store_path, sample_embedding):
        """Data survives store close and reopen."""
        # First instance
        store1 = ChromaStore(store_path, embedding_dimension=4)
        store1.upsert("test", "doc:1", sample_embedding, "Persistent", {"key": "value"})
        
        # New instance at same path
        store2 = ChromaStore(store_path, embedding_dimension=4)
        result = store2.get("test", "doc:1")
        
        assert result is not None
        assert result.summary == "Persistent"
        assert result.tags["key"] == "value"
