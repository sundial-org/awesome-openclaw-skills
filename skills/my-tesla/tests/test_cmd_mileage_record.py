import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

import scripts.tesla as tesla


class CmdMileageRecordTests(unittest.TestCase):
    def test_record_skips_when_no_wake_and_asleep(self):
        with tempfile.TemporaryDirectory() as td:
            db = Path(td) / "mileage.sqlite"

            class FakeVehicle(dict):
                def get_vehicle_data(self):
                    raise AssertionError("should not be called when asleep + no-wake")

            v = FakeVehicle(display_name="Car", id_s="1", state="asleep")

            fake_tesla = SimpleNamespace(vehicle_list=lambda: [v])

            args = SimpleNamespace(
                action="record",
                db=str(db),
                no_wake=True,
                auto_wake_after_hours=24.0,
                json=True,
                email=None,
                car=None,
            )

            with mock.patch.object(tesla, "get_tesla", return_value=fake_tesla), \
                 mock.patch.object(tesla, "require_email", return_value="x@example.com"), \
                 mock.patch.object(tesla, "wake_vehicle", return_value=False):
                # Should not raise
                tesla.cmd_mileage(args)


if __name__ == "__main__":
    unittest.main()
