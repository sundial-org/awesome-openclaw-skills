"""
Pending summaries queue using SQLite.

Stores content that needs summarization for later processing.
This enables fast indexing with lazy summarization.
"""

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class PendingSummary:
    """A queued item awaiting summarization."""
    id: str
    collection: str
    content: str
    queued_at: str
    attempts: int = 0


class PendingSummaryQueue:
    """
    SQLite-backed queue for pending summarizations.

    Items are added during fast indexing (with truncated placeholder summary)
    and processed later by `keep process-pending` or programmatically.
    """

    def __init__(self, queue_path: Path):
        """
        Args:
            queue_path: Path to SQLite database file
        """
        self._queue_path = queue_path
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self) -> None:
        """Initialize the SQLite database."""
        self._queue_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(self._queue_path), check_same_thread=False)
        self._conn.execute("""
            CREATE TABLE IF NOT EXISTS pending_summaries (
                id TEXT NOT NULL,
                collection TEXT NOT NULL,
                content TEXT NOT NULL,
                queued_at TEXT NOT NULL,
                attempts INTEGER DEFAULT 0,
                PRIMARY KEY (id, collection)
            )
        """)
        self._conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_queued_at
            ON pending_summaries(queued_at)
        """)
        self._conn.commit()

    def enqueue(self, id: str, collection: str, content: str) -> None:
        """
        Add an item to the pending queue.

        If the same id+collection already exists, replaces it (newer content wins).
        """
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute("""
            INSERT OR REPLACE INTO pending_summaries
            (id, collection, content, queued_at, attempts)
            VALUES (?, ?, ?, ?, 0)
        """, (id, collection, content, now))
        self._conn.commit()

    def dequeue(self, limit: int = 10) -> list[PendingSummary]:
        """
        Get the oldest pending items for processing.

        Items are returned but not removed - call `complete()` after successful processing.
        Increments attempt counter on each dequeue.
        """
        cursor = self._conn.execute("""
            SELECT id, collection, content, queued_at, attempts
            FROM pending_summaries
            ORDER BY queued_at ASC
            LIMIT ?
        """, (limit,))

        items = []
        for row in cursor.fetchall():
            items.append(PendingSummary(
                id=row[0],
                collection=row[1],
                content=row[2],
                queued_at=row[3],
                attempts=row[4],
            ))

        # Increment attempt counters
        if items:
            ids = [(item.id, item.collection) for item in items]
            self._conn.executemany("""
                UPDATE pending_summaries
                SET attempts = attempts + 1
                WHERE id = ? AND collection = ?
            """, ids)
            self._conn.commit()

        return items

    def complete(self, id: str, collection: str) -> None:
        """Remove an item from the queue after successful processing."""
        self._conn.execute("""
            DELETE FROM pending_summaries
            WHERE id = ? AND collection = ?
        """, (id, collection))
        self._conn.commit()

    def count(self) -> int:
        """Get count of pending items."""
        cursor = self._conn.execute("SELECT COUNT(*) FROM pending_summaries")
        return cursor.fetchone()[0]

    def stats(self) -> dict:
        """Get queue statistics."""
        cursor = self._conn.execute("""
            SELECT
                COUNT(*) as total,
                COUNT(DISTINCT collection) as collections,
                MAX(attempts) as max_attempts,
                MIN(queued_at) as oldest
            FROM pending_summaries
        """)
        row = cursor.fetchone()
        return {
            "pending": row[0],
            "collections": row[1],
            "max_attempts": row[2] or 0,
            "oldest": row[3],
            "queue_path": str(self._queue_path),
        }

    def clear(self) -> int:
        """Clear all pending items. Returns count of items cleared."""
        count = self.count()
        self._conn.execute("DELETE FROM pending_summaries")
        self._conn.commit()
        return count

    def close(self) -> None:
        """Close the database connection."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def __del__(self):
        """Ensure connection is closed on garbage collection."""
        self.close()
