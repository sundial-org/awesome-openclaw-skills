import unittest
from unittest import mock

# Import the tesla script as a module
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import tesla  # noqa: E402


class DummyVehicle:
    def __init__(self, display_name="Test Car", state="online"):
        self._display_name = display_name
        self._state = state
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

    def command(self, name, **kwargs):
        self.command_calls.append((name, kwargs))


class CmdClimateDefrostTests(unittest.TestCase):
    def test_climate_defrost_on_calls_endpoint(self):
        vehicle = DummyVehicle()
        args = mock.Mock()
        args.car = None
        args.action = "defrost"
        args.value = "on"
        args.no_wake = False
        args.json = False
        args.celsius = False
        args.fahrenheit = False

        with mock.patch.object(tesla, "get_tesla"), \
             mock.patch.object(tesla, "get_vehicle", return_value=vehicle), \
             mock.patch.object(tesla, "require_email", return_value="test@example.com"), \
             mock.patch.object(tesla, "wake_vehicle") as wake:
            tesla.cmd_climate(args)

        wake.assert_called_once()
        self.assertEqual(vehicle.command_calls, [("SET_PRECONDITIONING_MAX", {"on": True})])

    def test_climate_defrost_off_calls_endpoint(self):
        vehicle = DummyVehicle()
        args = mock.Mock()
        args.car = None
        args.action = "defrost"
        args.value = "off"
        args.no_wake = False
        args.json = False
        args.celsius = False
        args.fahrenheit = False

        with mock.patch.object(tesla, "get_tesla"), \
             mock.patch.object(tesla, "get_vehicle", return_value=vehicle), \
             mock.patch.object(tesla, "require_email", return_value="test@example.com"), \
             mock.patch.object(tesla, "wake_vehicle") as wake:
            tesla.cmd_climate(args)

        wake.assert_called_once()
        self.assertEqual(vehicle.command_calls, [("SET_PRECONDITIONING_MAX", {"on": False})])

    def test_climate_defrost_requires_value(self):
        vehicle = DummyVehicle()
        args = mock.Mock()
        args.car = None
        args.action = "defrost"
        args.value = None
        args.no_wake = False
        args.json = False
        args.celsius = False
        args.fahrenheit = False

        with mock.patch.object(tesla, "get_tesla"), \
             mock.patch.object(tesla, "get_vehicle", return_value=vehicle), \
             mock.patch.object(tesla, "require_email", return_value="test@example.com"), \
             mock.patch.object(tesla, "wake_vehicle"):
            with self.assertRaises(ValueError):
                tesla.cmd_climate(args)


if __name__ == "__main__":
    unittest.main()
