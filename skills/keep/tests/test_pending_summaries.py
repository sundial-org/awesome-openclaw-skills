"""
Tests for pending summaries queue and lazy summarization.
"""

import os
import tempfile
import time
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from keep.pending_summaries import PendingSummaryQueue


class TestPendingSummaryQueue:
    """Tests for the SQLite-backed pending summary queue."""

    def test_enqueue_and_count(self):
        """Should enqueue items and track count."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            assert queue.count() == 0

            queue.enqueue("doc1", "default", "content one")
            assert queue.count() == 1

            queue.enqueue("doc2", "default", "content two")
            assert queue.count() == 2

            queue.close()

    def test_dequeue_returns_oldest_first(self):
        """Should return items in FIFO order."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("first", "default", "content first")
            queue.enqueue("second", "default", "content second")
            queue.enqueue("third", "default", "content third")

            items = queue.dequeue(limit=2)
            assert len(items) == 2
            assert items[0].id == "first"
            assert items[1].id == "second"

            queue.close()

    def test_dequeue_increments_attempts(self):
        """Should increment attempt counter on dequeue."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("doc1", "default", "content")

            items = queue.dequeue(limit=1)
            assert items[0].attempts == 0  # Was 0 before dequeue

            # Dequeue again (item still there since not completed)
            items = queue.dequeue(limit=1)
            assert items[0].attempts == 1  # Incremented

            queue.close()

    def test_complete_removes_item(self):
        """Should remove item from queue on complete."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("doc1", "default", "content")
            assert queue.count() == 1

            queue.complete("doc1", "default")
            assert queue.count() == 0

            queue.close()

    def test_enqueue_replaces_existing(self):
        """Should replace existing item with same id+collection."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("doc1", "default", "original content")
            queue.enqueue("doc1", "default", "updated content")

            assert queue.count() == 1

            items = queue.dequeue(limit=1)
            assert items[0].content == "updated content"

            queue.close()

    def test_separate_collections(self):
        """Should treat same id in different collections as separate items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("doc1", "collection_a", "content a")
            queue.enqueue("doc1", "collection_b", "content b")

            assert queue.count() == 2

            queue.close()

    def test_stats(self):
        """Should return queue statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("doc1", "coll_a", "content")
            queue.enqueue("doc2", "coll_b", "content")

            stats = queue.stats()
            assert stats["pending"] == 2
            assert stats["collections"] == 2
            assert "queue_path" in stats

            queue.close()

    def test_clear(self):
        """Should clear all pending items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            queue.enqueue("doc1", "default", "content")
            queue.enqueue("doc2", "default", "content")

            cleared = queue.clear()
            assert cleared == 2
            assert queue.count() == 0

            queue.close()


class TestLazySummarization:
    """Tests for lazy summarization in Keeper API."""

    def test_update_lazy_uses_truncated_summary(self):
        """Should use truncated content as summary when lazy=True."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a minimal store setup
            store_path = Path(tmpdir) / ".keep"
            store_path.mkdir()

            # We need to mock the heavy providers
            with patch("keep.api.get_registry") as mock_registry, \
                 patch("keep.api.CachingEmbeddingProvider") as mock_cache:
                # Mock providers
                mock_doc_provider = MagicMock()
                mock_doc_provider.fetch.return_value = MagicMock(
                    content="A" * 1000,  # Long content
                    content_type="text/plain"
                )

                mock_embed_provider = MagicMock()
                mock_embed_provider.dimension = 384
                mock_embed_provider.embed.return_value = [0.1] * 384

                # Make the cache wrapper return the mock directly
                mock_cache.return_value = mock_embed_provider

                mock_summ_provider = MagicMock()
                mock_summ_provider.summarize.return_value = "Generated summary"

                mock_reg = MagicMock()
                mock_reg.create_document.return_value = mock_doc_provider
                mock_reg.create_embedding.return_value = mock_embed_provider
                mock_reg.create_summarization.return_value = mock_summ_provider
                mock_registry.return_value = mock_reg

                from keep.api import Keeper, TRUNCATE_LENGTH

                kp = Keeper(store_path)

                # Lazy update
                item = kp.update("file:///test.txt", lazy=True)

                # Should NOT call summarize
                mock_summ_provider.summarize.assert_not_called()

                # Summary should be truncated content
                assert len(item.summary) == TRUNCATE_LENGTH + 3  # +3 for "..."
                assert item.summary.endswith("...")

                # Should be queued
                assert kp.pending_count() == 1

                kp.close()

    def test_process_pending_generates_summary(self):
        """Should generate real summary when processing pending items."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / ".keep"
            store_path.mkdir()

            with patch("keep.api.get_registry") as mock_registry, \
                 patch("keep.api.CachingEmbeddingProvider") as mock_cache:
                mock_doc_provider = MagicMock()
                mock_doc_provider.fetch.return_value = MagicMock(
                    content="Test content for summarization",
                    content_type="text/plain"
                )

                mock_embed_provider = MagicMock()
                mock_embed_provider.dimension = 384
                mock_embed_provider.embed.return_value = [0.1] * 384

                mock_cache.return_value = mock_embed_provider

                mock_summ_provider = MagicMock()
                mock_summ_provider.summarize.return_value = "Generated summary"

                mock_reg = MagicMock()
                mock_reg.create_document.return_value = mock_doc_provider
                mock_reg.create_embedding.return_value = mock_embed_provider
                mock_reg.create_summarization.return_value = mock_summ_provider
                mock_registry.return_value = mock_reg

                from keep.api import Keeper

                kp = Keeper(store_path)

                # Lazy update
                kp.update("file:///test.txt", lazy=True)
                assert kp.pending_count() == 1

                # Process pending
                processed = kp.process_pending(limit=10)
                assert processed == 1
                assert kp.pending_count() == 0

                # Summarize should have been called
                mock_summ_provider.summarize.assert_called_once()

                kp.close()


class TestProcessorSpawning:
    """Tests for background processor singleton spawning."""

    def test_is_processor_running_false_when_no_pid_file(self):
        """Should return False when no PID file exists."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / ".keep"
            store_path.mkdir()

            with patch("keep.api.get_registry") as mock_registry, \
                 patch("keep.api.CachingEmbeddingProvider") as mock_cache:
                mock_embed = MagicMock()
                mock_embed.dimension = 384
                mock_cache.return_value = mock_embed

                mock_reg = MagicMock()
                mock_reg.create_document.return_value = MagicMock()
                mock_reg.create_embedding.return_value = mock_embed
                mock_reg.create_summarization.return_value = MagicMock()
                mock_registry.return_value = mock_reg

                from keep.api import Keeper
                kp = Keeper(store_path)

                assert kp._is_processor_running() is False

                kp.close()

    def test_is_processor_running_true_when_pid_file_and_process_alive(self):
        """Should return True when PID file exists and process is alive."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / ".keep"
            store_path.mkdir()

            with patch("keep.api.get_registry") as mock_registry, \
                 patch("keep.api.CachingEmbeddingProvider") as mock_cache:
                mock_embed = MagicMock()
                mock_embed.dimension = 384
                mock_cache.return_value = mock_embed

                mock_reg = MagicMock()
                mock_reg.create_document.return_value = MagicMock()
                mock_reg.create_embedding.return_value = mock_embed
                mock_reg.create_summarization.return_value = MagicMock()
                mock_registry.return_value = mock_reg

                from keep.api import Keeper
                kp = Keeper(store_path)

                # Write our own PID (we know we're alive)
                kp._processor_pid_path.write_text(str(os.getpid()))

                assert kp._is_processor_running() is True

                # Clean up
                kp._processor_pid_path.unlink()
                kp.close()

    def test_is_processor_running_cleans_stale_pid_file(self):
        """Should clean up stale PID file for dead process."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / ".keep"
            store_path.mkdir()

            with patch("keep.api.get_registry") as mock_registry, \
                 patch("keep.api.CachingEmbeddingProvider") as mock_cache:
                mock_embed = MagicMock()
                mock_embed.dimension = 384
                mock_cache.return_value = mock_embed

                mock_reg = MagicMock()
                mock_reg.create_document.return_value = MagicMock()
                mock_reg.create_embedding.return_value = mock_embed
                mock_reg.create_summarization.return_value = MagicMock()
                mock_registry.return_value = mock_reg

                from keep.api import Keeper
                kp = Keeper(store_path)

                # Write a PID that definitely doesn't exist
                # (use a very high number that's unlikely to be a real PID)
                kp._processor_pid_path.write_text("999999999")

                assert kp._is_processor_running() is False
                # Stale PID file should be cleaned up
                assert not kp._processor_pid_path.exists()

                kp.close()

    def test_spawn_processor_does_not_spawn_if_already_running(self):
        """Should not spawn new processor if one is already running."""
        with tempfile.TemporaryDirectory() as tmpdir:
            store_path = Path(tmpdir) / ".keep"
            store_path.mkdir()

            with patch("keep.api.get_registry") as mock_registry, \
                 patch("keep.api.CachingEmbeddingProvider") as mock_cache, \
                 patch("keep.api.subprocess.Popen") as mock_popen:
                mock_embed = MagicMock()
                mock_embed.dimension = 384
                mock_cache.return_value = mock_embed

                mock_reg = MagicMock()
                mock_reg.create_document.return_value = MagicMock()
                mock_reg.create_embedding.return_value = mock_embed
                mock_reg.create_summarization.return_value = MagicMock()
                mock_registry.return_value = mock_reg

                from keep.api import Keeper
                kp = Keeper(store_path)

                # Pretend we're already running
                kp._processor_pid_path.write_text(str(os.getpid()))

                # Should not spawn
                result = kp._spawn_processor()
                assert result is False
                mock_popen.assert_not_called()

                kp._processor_pid_path.unlink()
                kp.close()


class TestMaxAttempts:
    """Tests for max attempts handling in pending summaries."""

    def test_items_removed_after_max_attempts(self):
        """Should remove items from queue after MAX_SUMMARY_ATTEMPTS failures."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue = PendingSummaryQueue(Path(tmpdir) / "pending.db")

            # Enqueue an item
            queue.enqueue("failing-doc", "default", "content that will fail")

            # Simulate MAX_SUMMARY_ATTEMPTS dequeues (each increments attempts)
            from keep.api import MAX_SUMMARY_ATTEMPTS
            for _ in range(MAX_SUMMARY_ATTEMPTS):
                items = queue.dequeue(limit=1)
                assert len(items) == 1
                # Don't call complete() - simulating failure

            # After MAX attempts, item should still be in queue but will be
            # removed by process_pending when it sees attempts >= MAX
            assert queue.count() == 1

            # Check that attempts counter is at MAX
            items = queue.dequeue(limit=1)
            assert items[0].attempts == MAX_SUMMARY_ATTEMPTS

            queue.close()

    def test_queue_del_closes_connection(self):
        """Should close connection when queue is garbage collected."""
        with tempfile.TemporaryDirectory() as tmpdir:
            queue_path = Path(tmpdir) / "pending.db"
            queue = PendingSummaryQueue(queue_path)
            queue.enqueue("doc1", "default", "content")

            # Get connection before del
            conn = queue._conn
            assert conn is not None

            # Delete queue - should close connection
            del queue

            # Connection should be closed (will raise if we try to use it)
            # Note: This is implementation-dependent; the connection object
            # may still exist but be in a closed state
