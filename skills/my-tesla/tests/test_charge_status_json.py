import unittest

from scripts.tesla import _charge_status_json


class TestChargeStatusJson(unittest.TestCase):
    def test_charge_status_json_includes_useful_fields(self):
        charge = {
            'battery_level': 55,
            'battery_range': 123.4,
            'usable_battery_level': 52,
            'charging_state': 'Charging',
            'charge_limit_soc': 80,
            'time_to_full_charge': 1.5,
            'charge_rate': 22,
            'charger_power': 7,
            'charger_voltage': 240,
            'charger_actual_current': 29,
            'scheduled_charging_start_time': 60,
            'scheduled_charging_mode': 'DepartBy',
            'scheduled_charging_pending': True,
            'charge_port_door_open': True,
            'conn_charge_cable': 'SAEJ1772',
        }

        out = _charge_status_json(charge)

        # Sanity checks: key presence and values pass through.
        self.assertEqual(out.get('battery_level'), 55)
        self.assertEqual(out.get('usable_battery_level'), 52)
        self.assertEqual(out.get('charger_power'), 7)
        self.assertEqual(out.get('charger_voltage'), 240)
        self.assertEqual(out.get('charger_actual_current'), 29)
        self.assertEqual(out.get('charge_port_door_open'), True)
        self.assertEqual(out.get('conn_charge_cable'), 'SAEJ1772')

    def test_charge_status_json_handles_none(self):
        out = _charge_status_json(None)
        self.assertIsInstance(out, dict)
        self.assertIsNone(out.get('battery_level'))


if __name__ == '__main__':
    unittest.main()
