"""Tests for the command-line console."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from monolith.console import main
from monolith.settings import load_settings, settings_exist


def run(argv):
    """Run the console capturing stdout; return ``(exit_code, output)``."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


class ConsoleTests(unittest.TestCase):
    def test_init_creates_settings(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "init"])
            self.assertEqual(code, 0)
            self.assertTrue(settings_exist(root))
            self.assertIn("Initialized Monolith", out)

    def test_apply_writes_all_three_agents(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, _ = run(["--root", root, "apply", "--agent", "all"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(root, "CLAUDE.md")))
            self.assertTrue(os.path.exists(os.path.join(root, "AGENTS.md")))
            self.assertTrue(
                os.path.exists(os.path.join(root, ".github", "copilot-instructions.md"))
            )

    def test_tier_switch_persists(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, _ = run(["--root", root, "tier", "ultra"])
            self.assertEqual(code, 0)
            self.assertEqual(load_settings(root)["tier"], "ultra")

    def test_tier_apply_flag_regenerates(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            run(["--root", root, "tier", "ultra", "--apply"])
            with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8") as fh:
                self.assertIn("tier: ultra", fh.read())

    def test_doctor_fails_before_apply_succeeds_after(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            self.assertEqual(run(["--root", root, "doctor"])[0], 1)
            run(["--root", root, "apply", "--agent", "all"])
            code, out = run(["--root", root, "doctor"])
            self.assertEqual(code, 0)
            self.assertIn("All configured agents", out)

    def test_stats_reports_projection(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, out = run(["--root", root, "stats"])
            self.assertEqual(code, 0)
            self.assertIn("projected OUTPUT reduction", out)


if __name__ == "__main__":
    unittest.main()
