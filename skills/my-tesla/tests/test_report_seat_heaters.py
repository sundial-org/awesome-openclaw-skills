import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class ReportSeatHeatersTests(unittest.TestCase):
    def test_report_includes_seat_heaters_when_available(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {
            "charge_state": {"battery_level": 50, "battery_range": 123.4},
            "climate_state": {"is_climate_on": True, "seat_heater_left": 3, "seat_heater_right": 1},
            "vehicle_state": {},
        }

        out = tesla._report(vehicle, data)
        self.assertIn("Seat heaters:", out)
        # Compact labels (D=driver, P=passenger)
        self.assertIn("D 3", out)
        self.assertIn("P 1", out)


if __name__ == "__main__":
    unittest.main()
