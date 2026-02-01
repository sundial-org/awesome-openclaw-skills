import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class ReportOpeningsTests(unittest.TestCase):
    def test_report_includes_openings_when_fields_present(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {
            "charge_state": {"battery_level": 50, "battery_range": 123.4},
            "climate_state": {"inside_temp": 20, "outside_temp": 10, "is_climate_on": False},
            "vehicle_state": {
                "locked": True,
                "sentry_mode": False,
                "df": 1,  # open
                "rt": 0,  # closed
            },
        }

        out = tesla._report(vehicle, data)
        self.assertIn("Openings:", out)
        self.assertIn("Driver front door", out)

    def test_report_json_openings_omits_when_unknown(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {"vehicle_state": {"locked": True}}
        out = tesla._report_json(vehicle, data)
        self.assertNotIn("openings", out)

    def test_report_json_openings_all_closed(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {"vehicle_state": {"df": 0, "rt": 0}}
        out = tesla._report_json(vehicle, data)
        self.assertIn("openings", out)
        self.assertEqual(out["openings"]["open"], [])
        self.assertEqual(out["openings"]["all_closed"], True)


if __name__ == "__main__":
    unittest.main()
