import sqlite3
import unittest
from unittest.mock import patch

from scripts.tesla import mileage_fetch_points, resolve_since_ts


class TestMileageExportFilter(unittest.TestCase):
    def test_resolve_since_ts_prefers_explicit_ts(self):
        self.assertEqual(resolve_since_ts(since_ts=123, since_days=7), 123)

    def test_resolve_since_ts_since_days(self):
        with patch("scripts.tesla.time.time", return_value=1000):
            # 1 day = 86400 seconds
            self.assertEqual(resolve_since_ts(since_days=1), 1000 - 86400)

    def test_mileage_fetch_points_filters(self):
        conn = sqlite3.connect(":memory:")
        try:
            conn.execute(
                """
                CREATE TABLE mileage_points (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  ts_utc INTEGER NOT NULL,
                  vehicle_id TEXT,
                  vehicle_name TEXT,
                  odometer_mi REAL,
                  state TEXT,
                  source TEXT,
                  note TEXT
                );
                """
            )

            # Insert three points
            conn.execute(
                "INSERT INTO mileage_points(ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note) VALUES (?,?,?,?,?,?,?)",
                (10, "v1", "Car", 1.0, "online", "test", None),
            )
            conn.execute(
                "INSERT INTO mileage_points(ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note) VALUES (?,?,?,?,?,?,?)",
                (20, "v1", "Car", 2.0, "online", "test", None),
            )
            conn.execute(
                "INSERT INTO mileage_points(ts_utc, vehicle_id, vehicle_name, odometer_mi, state, source, note) VALUES (?,?,?,?,?,?,?)",
                (30, "v1", "Car", 3.0, "online", "test", None),
            )

            all_rows = mileage_fetch_points(conn)
            self.assertEqual([r[0] for r in all_rows], [10, 20, 30])

            filtered = mileage_fetch_points(conn, since_ts=21)
            self.assertEqual([r[0] for r in filtered], [30])
        finally:
            conn.close()


if __name__ == "__main__":
    unittest.main()
