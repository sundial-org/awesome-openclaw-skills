import os
import tempfile
import unittest
from pathlib import Path

import scripts.tesla as tesla


class MileageDbTests(unittest.TestCase):
    def test_init_and_insert(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "mileage.sqlite"
            tesla.mileage_init_db(db)

            conn = tesla._db_connect(db)
            try:
                tesla.mileage_insert_point(
                    conn,
                    ts_utc=1700000000,
                    vehicle_id="123",
                    vehicle_name="Car",
                    odometer_mi=100.0,
                    state="online",
                    source="test",
                    note=None,
                )
                conn.commit()

                last = tesla.mileage_last_success_ts(conn, "123")
                self.assertEqual(last, 1700000000)
            finally:
                conn.close()

    def test_resolve_db_path_env(self):
        with tempfile.TemporaryDirectory() as td:
            p = str(Path(td) / "x.sqlite")
            os.environ["MY_TESLA_MILEAGE_DB"] = p
            try:
                out = tesla.resolve_mileage_db_path(None)
                self.assertEqual(str(out), p)
            finally:
                os.environ.pop("MY_TESLA_MILEAGE_DB", None)


if __name__ == "__main__":
    unittest.main()
