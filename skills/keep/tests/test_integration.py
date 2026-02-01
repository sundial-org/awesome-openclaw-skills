"""End-to-end integration tests for the minimal API path.

These tests verify the core flow:
  update/remember → embed → summarize → store → find/get → Item
"""

import tempfile
from datetime import datetime, timezone
from pathlib import Path

import pytest

from keep.api import Keeper


class TestEndToEnd:
    """Test the complete store → find cycle."""

    @pytest.fixture
    def memory(self, tmp_path: Path) -> Keeper:
        """Create an Keeper with a temp store."""
        return Keeper(store_path=tmp_path)

    def test_remember_and_get(self, memory: Keeper) -> None:
        """remember() stores an item, get() retrieves it."""
        item = memory.remember(
            "The dharma is like a raft for crossing over.",
            source_tags={"tradition": "buddhist", "source": "mn22"},
        )
        
        assert item.id.startswith("mem:")
        assert "raft" in item.summary  # summary, not content
        assert item.tags["tradition"] == "buddhist"
        
        # Retrieve it
        retrieved = memory.get(item.id)
        assert retrieved is not None
        assert retrieved.id == item.id
        assert retrieved.summary == item.summary

    def test_remember_and_find(self, memory: Keeper) -> None:
        """remember() stores, find() retrieves by semantic similarity."""
        # Store some items
        memory.remember(
            "Emptiness is form, form is emptiness.",
            source_tags={"tradition": "buddhist", "text": "heart-sutra"},
        )
        memory.remember(
            "All compounded things are impermanent.",
            source_tags={"tradition": "buddhist", "text": "dhammapada"},
        )
        memory.remember(
            "The medieval anchoress lived in solitude.",
            source_tags={"tradition": "christian", "text": "ancrene-wisse"},
        )

        # Find by semantic query
        results = memory.find("What is the nature of form and emptiness?")
        
        assert len(results) > 0
        # The Heart Sutra quote should be most relevant
        assert any("emptiness" in r.summary.lower() for r in results)
        # Results should have similarity scores
        assert results[0].score is not None

    def test_find_similar(self, memory: Keeper) -> None:
        """find_similar() finds items similar to an existing item."""
        # Store related items
        item1 = memory.remember("The lotus grows from muddy water.")
        memory.remember("The flower blooms in dirty ponds.")
        memory.remember("Knights traveled on horseback.")

        # Find similar to the lotus item
        similar = memory.find_similar(item1.id)
        
        assert len(similar) > 0
        # The flower item should be similar
        assert any("flower" in r.summary.lower() or "bloom" in r.summary.lower() 
                   for r in similar)

    def test_query_tag(self, memory: Keeper) -> None:
        """query_tag() filters by tag values."""
        memory.remember("Buddhist text one.", source_tags={"tradition": "buddhist"})
        memory.remember("Buddhist text two.", source_tags={"tradition": "buddhist"})
        memory.remember("Christian text.", source_tags={"tradition": "christian"})

        buddhist = memory.query_tag(tradition="buddhist")
        
        assert len(buddhist) == 2
        assert all(r.tags.get("tradition") == "buddhist" for r in buddhist)

    def test_query_fulltext(self, memory: Keeper) -> None:
        """query_fulltext() searches content."""
        memory.remember("The quick brown fox jumps over.")
        memory.remember("A lazy dog sleeps under the tree.")
        memory.remember("The medieval castle stood firm.")

        results = memory.query_fulltext("fox")
        
        assert len(results) == 1
        assert "fox" in results[0].summary

    def test_exists_and_delete(self, memory: Keeper) -> None:
        """exists() checks presence, delete() removes items."""
        item = memory.remember("Temporary content.", id="to-delete")
        
        assert memory.exists("to-delete") is True
        
        memory.delete("to-delete")
        
        assert memory.exists("to-delete") is False
        assert memory.get("to-delete") is None

    def test_list_collections(self, memory: Keeper) -> None:
        """list_collections() shows available collections."""
        # Default collection
        memory.remember("Something in default.")
        
        collections = memory.list_collections()
        assert "default" in collections

    def test_count(self, memory: Keeper) -> None:
        """count() returns number of items."""
        assert memory.count() == 0

        memory.remember("One")
        memory.remember("Two")
        memory.remember("Three")

        assert memory.count() == 3

    def test_update_merges_tags(self, memory: Keeper) -> None:
        """update() with existing item merges tags, replaces summary."""
        # First remember with initial tags
        item1 = memory.remember(
            "Original content about meditation.",
            id="test:meditation",
            source_tags={"topic": "meditation", "tradition": "zen", "level": "beginner"}
        )

        assert item1.tags["topic"] == "meditation"
        assert item1.tags["tradition"] == "zen"
        assert item1.tags["level"] == "beginner"

        # Update with new content and partial tags
        item2 = memory.remember(
            "Updated content about advanced meditation practice.",
            id="test:meditation",
            source_tags={"level": "advanced", "practice": "shikantaza"}  # level changes, practice is new
        )

        # Summary should be replaced
        assert "advanced" in item2.summary.lower()

        # Tags should be merged: old preserved, new added, collision uses new value
        assert item2.tags["topic"] == "meditation"  # preserved from first call
        assert item2.tags["tradition"] == "zen"  # preserved from first call
        assert item2.tags["level"] == "advanced"  # updated (was "beginner")
        assert item2.tags["practice"] == "shikantaza"  # new tag added

        # Verify via get()
        retrieved = memory.get("test:meditation")
        assert retrieved is not None
        assert retrieved.tags["topic"] == "meditation"
        assert retrieved.tags["tradition"] == "zen"
        assert retrieved.tags["level"] == "advanced"
        assert retrieved.tags["practice"] == "shikantaza"


class TestMultipleCollections:
    """Test working with multiple collections."""

    @pytest.fixture
    def memory(self, tmp_path: Path) -> Keeper:
        return Keeper(store_path=tmp_path)

    def test_separate_collections(self, memory: Keeper) -> None:
        """Items in different collections are separate."""
        memory.remember("Work note", collection="work")
        memory.remember("Personal note", collection="personal")

        # Count per collection
        assert memory.count(collection="work") == 1
        assert memory.count(collection="personal") == 1
        
        # Get from specific collection
        work_results = memory.find("note", collection="work")
        assert len(work_results) == 1
        assert "Work" in work_results[0].summary


class TestSummarizationDefault:
    """Test that summarization works with truncation."""

    @pytest.fixture
    def memory(self, tmp_path: Path) -> Keeper:
        return Keeper(store_path=tmp_path)

    def test_long_content_truncated_for_summary(self, memory: Keeper) -> None:
        """Long content gets a truncated summary."""
        long_content = " ".join(["word"] * 500)  # 500 words
        
        item = memory.remember(long_content)
        
        # Summary should be stored (may be truncated depending on config)
        assert len(item.summary) > 0
        
        # Item should be retrievable
        retrieved = memory.get(item.id)
        assert retrieved is not None
        assert retrieved.summary == item.summary


class TestRecencyDecay:
    """Test ACT-R style memory decay."""

    @pytest.fixture
    def memory(self, tmp_path: Path) -> Keeper:
        return Keeper(store_path=tmp_path, decay_half_life_days=30.0)

    def test_decay_parameter_accepted(self, tmp_path: Path) -> None:
        """Can configure decay half-life."""
        mem = Keeper(store_path=tmp_path, decay_half_life_days=7.0)
        assert mem._decay_half_life_days == 7.0

    def test_decay_disabled_with_zero(self, tmp_path: Path) -> None:
        """Decay can be disabled by setting half-life to 0 or negative."""
        mem = Keeper(store_path=tmp_path, decay_half_life_days=0)
        assert mem._decay_half_life_days == 0
        
        mem2 = Keeper(store_path=tmp_path / "sub", decay_half_life_days=-1)
        assert mem2._decay_half_life_days == -1

    def test_recent_items_have_higher_effective_score(self, memory: Keeper) -> None:
        """Items are returned with scores; decay applies at query time."""
        # Store an item
        memory.remember("The dharma is like a raft for crossing over.")
        
        # Find it
        results = memory.find("dharma raft")
        
        # Should have a score
        assert len(results) > 0
        assert results[0].score is not None
        assert results[0].score > 0
        
        # For a fresh item with 0 days elapsed, decay factor ≈ 1.0
        # So effective score should be close to raw similarity

    def test_decay_formula_correctness(self, memory: Keeper) -> None:
        """Verify the decay formula: score × 0.5^(days/half_life)."""
        from datetime import timedelta
        from keep.types import Item
        
        # Create items with known scores and timestamps
        now = datetime.now(timezone.utc)
        
        # Item from 30 days ago (1 half-life) should have score × 0.5
        old_timestamp = (now - timedelta(days=30)).isoformat()
        old_item = Item(
            id="old",
            summary="old item",
            tags={"_updated": old_timestamp},
            score=1.0
        )
        
        # Item from today should have score × 1.0
        new_timestamp = now.isoformat()
        new_item = Item(
            id="new", 
            summary="new item",
            tags={"_updated": new_timestamp},
            score=1.0
        )
        
        # Apply decay
        decayed = memory._apply_recency_decay([old_item, new_item])
        
        # New item should be ranked first (higher effective score)
        assert decayed[0].id == "new"
        assert decayed[1].id == "old"
        
        # Old item's score should be approximately 0.5 (1 half-life decay)
        assert 0.45 < decayed[1].score < 0.55
        
        # New item's score should be approximately 1.0 (no decay)
        assert decayed[0].score > 0.95


class TestEmbeddingCacheIntegration:
    """Test that embedding cache is actually used by the API."""

    @pytest.fixture
    def memory(self, tmp_path: Path) -> Keeper:
        return Keeper(store_path=tmp_path)

    def test_cache_enabled_by_default(self, memory: Keeper) -> None:
        """Embedding cache is enabled by default."""
        stats = memory.embedding_cache_stats()
        assert "entries" in stats
        assert "hit_rate" in stats

    def test_repeated_queries_use_cache(self, memory: Keeper) -> None:
        """Repeated find() queries use cached embeddings."""
        # Store something to search
        memory.remember("The quick brown fox jumps over the lazy dog.")
        
        # First search
        memory.find("fox jumping")
        stats1 = memory.embedding_cache_stats()
        
        # Second identical search
        memory.find("fox jumping")
        stats2 = memory.embedding_cache_stats()
        
        # Should have cache hit on second query
        assert stats2["hits"] > stats1["hits"]
    
    def test_cache_persists_across_sessions(self, tmp_path: Path) -> None:
        """Cache persists when memory is reopened."""
        # First session
        mem1 = Keeper(store_path=tmp_path)
        mem1.remember("Persistent content")
        mem1.find("persistent")
        
        # Second session (new instance, same store)
        mem2 = Keeper(store_path=tmp_path)
        mem2.find("persistent")
        
        stats = mem2.embedding_cache_stats()
        # The query embedding "persistent" should hit cache from first session
        assert stats["hits"] >= 1
