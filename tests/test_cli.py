import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from monolith.cli import main
from monolith.config import load_config, config_exists


def run(argv):
    """Run the CLI capturing stdout; return (exit_code, output)."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


class CliTests(unittest.TestCase):
    def test_init_creates_config(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "init"])
            self.assertEqual(code, 0)
            self.assertTrue(config_exists(root))
            self.assertIn("Initialized Monolith", out)

    def test_apply_writes_all_three_agents(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, _ = run(["--root", root, "apply", "--agent", "all"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(root, "CLAUDE.md")))
            self.assertTrue(os.path.exists(os.path.join(root, "AGENTS.md")))
            self.assertTrue(os.path.exists(
                os.path.join(root, ".github", "copilot-instructions.md")))

    def test_profile_switch_persists(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, out = run(["--root", root, "profile", "ultra"])
            self.assertEqual(code, 0)
            self.assertEqual(load_config(root)["profile"], "ultra")

    def test_doctor_fails_before_apply_succeeds_after(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code_before, _ = run(["--root", root, "doctor"])
            self.assertEqual(code_before, 1)
            run(["--root", root, "apply", "--agent", "all"])
            code_after, out = run(["--root", root, "doctor"])
            self.assertEqual(code_after, 0)
            self.assertIn("All configured agents", out)

    def test_stats_reports_projection(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, out = run(["--root", root, "stats"])
            self.assertEqual(code, 0)
            self.assertIn("projected OUTPUT reduction", out)


if __name__ == "__main__":
    unittest.main()
