import unittest

from scripts.tesla import _round_coord


class TestLocationRounding(unittest.TestCase):
    def test_round_coord_basic(self):
        self.assertEqual(_round_coord(37.123456, 2), 37.12)
        self.assertEqual(_round_coord(-122.987654, 2), -122.99)

    def test_round_coord_digits_range(self):
        # Reject overly-precise / invalid digit counts.
        self.assertIsNone(_round_coord(1.2345, -1))
        self.assertIsNone(_round_coord(1.2345, 7))

        # Allow the full supported range.
        self.assertEqual(_round_coord(1.2345678, 0), 1.0)
        self.assertEqual(_round_coord(1.2345678, 6), 1.234568)

    def test_round_coord_invalid_inputs(self):
        self.assertIsNone(_round_coord(None, 2))
        self.assertIsNone(_round_coord("", 2))
        self.assertIsNone(_round_coord(1.23, "nope"))


if __name__ == "__main__":
    unittest.main()
