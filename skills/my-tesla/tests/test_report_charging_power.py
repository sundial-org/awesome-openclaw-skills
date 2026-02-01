import unittest
import sys
from pathlib import Path

# Allow importing scripts/tesla.py as a module
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class ReportChargingPowerTests(unittest.TestCase):
    def test_report_includes_charging_power_details_when_present(self):
        vehicle = {"display_name": "Test Car", "state": "online"}
        data = {
            "charge_state": {
                "battery_level": 50,
                "battery_range": 123.4,
                "charging_state": "Charging",
                "charger_power": 7,
                "charger_voltage": 240,
                "charger_actual_current": 30,
            },
            "climate_state": {},
            "vehicle_state": {},
        }

        out = tesla._report(vehicle, data)
        self.assertIn("Charging: Charging", out)
        self.assertIn("Charging power:", out)
        self.assertIn("7 kW", out)
        self.assertIn("240V", out)
        self.assertIn("30A", out)


if __name__ == "__main__":
    unittest.main()
