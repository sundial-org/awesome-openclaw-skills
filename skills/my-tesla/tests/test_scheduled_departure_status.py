import unittest

from scripts.tesla import _scheduled_departure_status_json


class TestScheduledDepartureStatus(unittest.TestCase):
    def test_scheduled_departure_status_json(self):
        charge = {
            'scheduled_departure_enabled': True,
            'scheduled_departure_time': 7 * 60 + 30,
            'preconditioning_enabled': False,
            'off_peak_charging_enabled': True,
        }
        out = _scheduled_departure_status_json(charge)
        self.assertEqual(out['scheduled_departure_enabled'], True)
        self.assertEqual(out['scheduled_departure_time'], 450)
        self.assertEqual(out['scheduled_departure_time_hhmm'], '07:30')
        self.assertEqual(out['preconditioning_enabled'], False)
        self.assertEqual(out['off_peak_charging_enabled'], True)

    def test_scheduled_departure_status_json_missing(self):
        out = _scheduled_departure_status_json({})
        # Ensure keys exist with None values for stable JSON schemas.
        self.assertIn('scheduled_departure_enabled', out)
        self.assertIn('scheduled_departure_time', out)
        self.assertIn('scheduled_departure_time_hhmm', out)


if __name__ == '__main__':
    unittest.main()
