import os
import stat
import tempfile
import unittest
from pathlib import Path

import scripts.tesla as tesla


class DefaultsPermissionsTests(unittest.TestCase):
    def test_save_defaults_sets_0600_permissions_best_effort(self):
        # On Windows this may not apply; but this repo targets macOS/Linux.
        if os.name != "posix":
            self.skipTest("POSIX-only permissions")

        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "defaults.json"

            # Patch the module-level DEFAULTS_FILE for this test.
            old = tesla.DEFAULTS_FILE
            try:
                tesla.DEFAULTS_FILE = p
                tesla.save_defaults({"default_car": "Test"})

                mode = stat.S_IMODE(p.stat().st_mode)
                self.assertEqual(mode, 0o600)
            finally:
                tesla.DEFAULTS_FILE = old


if __name__ == "__main__":
    unittest.main()
