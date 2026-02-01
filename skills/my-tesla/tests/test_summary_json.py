import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class SummaryJsonTests(unittest.TestCase):
    def test_summary_json_is_sanitized(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {
            "charge_state": {
                "battery_level": 63,
                "battery_range": 199.9,
                "usable_battery_level": 61,
                "charging_state": "Disconnected",
            },
            "climate_state": {
                "inside_temp": 20,
                "is_climate_on": False,
            },
            "vehicle_state": {"locked": True},
            # Present in raw vehicle_data, must not show up in summary JSON.
            "drive_state": {"latitude": 37.1234, "longitude": -122.5678},
        }

        out = tesla._summary_json(vehicle, data)

        self.assertIn("vehicle", out)
        self.assertEqual(out["vehicle"]["display_name"], "Test Car")

        # Must not include raw drive_state/location
        self.assertNotIn("drive_state", out)
        self.assertNotIn("location", out)
        self.assertNotIn("latitude", str(out))
        self.assertNotIn("longitude", str(out))

        # Expected useful bits
        self.assertEqual(out["battery"]["level_percent"], 63)
        self.assertEqual(out["battery"]["range_mi"], 199.9)
        self.assertEqual(out["battery"]["usable_level_percent"], 61)
        self.assertEqual(out["charging"]["charging_state"], "Disconnected")
        self.assertEqual(out["security"]["locked"], True)
        self.assertIn("summary", out)
        self.assertIsInstance(out["summary"], str)


if __name__ == "__main__":
    unittest.main()
