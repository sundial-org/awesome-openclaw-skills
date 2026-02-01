import io
import unittest
from contextlib import redirect_stdout
from unittest import mock

# Import the tesla script as a module
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class DummyVehicle:
    def __init__(self, display_name="Test Car", state="online", vehicle_data=None):
        self._display_name = display_name
        self._state = state
        self._vehicle_data = vehicle_data or {}
        self.command_calls = []

    def __getitem__(self, k):
        if k == "display_name":
            return self._display_name
        if k == "state":
            return self._state
        raise KeyError(k)

    def get(self, k, default=None):
        if k == "display_name":
            return self._display_name
        if k == "state":
            return self._state
        return default

    def get_vehicle_data(self):
        return self._vehicle_data

    def command(self, name, **kwargs):
        self.command_calls.append((name, kwargs))


class SeatsTests(unittest.TestCase):
    def test_parse_seat_heater_names(self):
        self.assertEqual(tesla._parse_seat_heater("driver"), 0)
        self.assertEqual(tesla._parse_seat_heater("passenger"), 1)
        self.assertEqual(tesla._parse_seat_heater("rear-left"), 2)
        self.assertEqual(tesla._parse_seat_heater("rear-center"), 3)
        self.assertEqual(tesla._parse_seat_heater("rear-right"), 4)
        self.assertEqual(tesla._parse_seat_heater("3rd-left"), 5)
        self.assertEqual(tesla._parse_seat_heater("3rd-right"), 6)
        self.assertEqual(tesla._parse_seat_heater("0"), 0)

        with self.assertRaises(ValueError):
            tesla._parse_seat_heater("nope")

    def test_seats_status_json_is_json_only(self):
        vehicle = DummyVehicle(vehicle_data={
            "climate_state": {
                "seat_heater_left": 3,
                "seat_heater_right": 1,
            }
        })

        args = mock.Mock()
        args.car = None
        args.action = "status"
        args.no_wake = True
        args.json = True

        with mock.patch.object(tesla, "get_tesla"), \
             mock.patch.object(tesla, "get_vehicle", return_value=vehicle), \
             mock.patch.object(tesla, "require_email", return_value="test@example.com"), \
             mock.patch.object(tesla, "_ensure_online_or_exit"):
            buf = io.StringIO()
            with redirect_stdout(buf):
                tesla.cmd_seats(args)

        out = buf.getvalue().strip()
        self.assertTrue(out.startswith("{"))
        self.assertIn('"seat_heater_left"', out)
        self.assertIn('"seat_heater_right"', out)

    def test_seats_set_calls_endpoint(self):
        vehicle = DummyVehicle()

        args = mock.Mock()
        args.car = None
        args.action = "set"
        args.seat = "driver"
        args.level = "2"
        args.yes = True

        with mock.patch.object(tesla, "get_tesla"), \
             mock.patch.object(tesla, "get_vehicle", return_value=vehicle), \
             mock.patch.object(tesla, "require_email", return_value="test@example.com"), \
             mock.patch.object(tesla, "wake_vehicle") as wake:
            tesla.cmd_seats(args)

        wake.assert_called_once()
        self.assertEqual(vehicle.command_calls, [("REMOTE_SEAT_HEATER_REQUEST", {"heater": 0, "level": 2})])


if __name__ == "__main__":
    unittest.main()
