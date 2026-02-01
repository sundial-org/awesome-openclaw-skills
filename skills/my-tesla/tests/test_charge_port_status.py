import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class ChargePortStatusTests(unittest.TestCase):
    def test_charge_port_status_json_shape(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {
            "charge_state": {
                "charge_port_door_open": True,
                "charge_port_latch": "Engaged",
                "conn_charge_cable": "SAE",
                "charging_state": "Charging",
                # extra fields should be ignored
                "battery_level": 50,
            },
            # drive_state/location must not be pulled into the object
            "drive_state": {"latitude": 1.23, "longitude": 4.56},
        }

        out = tesla._charge_port_status_json(vehicle, data)
        self.assertEqual(out["display_name"], "Test Car")
        self.assertEqual(out["state"], "online")
        self.assertEqual(out["charge_port_door_open"], True)
        self.assertEqual(out["charge_port_latch"], "Engaged")
        self.assertEqual(out["conn_charge_cable"], "SAE")
        self.assertEqual(out["charging_state"], "Charging")
        self.assertNotIn("drive_state", out)
        self.assertNotIn("latitude", out)


if __name__ == "__main__":
    unittest.main()
