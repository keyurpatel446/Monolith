"""Tests for the command wrapper (`monolith run`) and the gain ledger."""

import os
import sys
import tempfile
import unittest

from monolith.runner import load_gain, run_command


class RunnerTests(unittest.TestCase):
    def test_compresses_output_and_records_gain(self):
        with tempfile.TemporaryDirectory() as root:
            # A command that prints many repeated lines (compressible).
            code = "print('hit\\n' * 20)"
            result = run_command([sys.executable, "-c", code], root=root)
            self.assertEqual(result.returncode, 0)
            self.assertLess(result.after_tokens, result.before_tokens)
            self.assertIsNone(result.tee_path)  # success -> no tee
            # Gain ledger recorded one run.
            ledger = load_gain(root)
            self.assertEqual(ledger["runs"], 1)
            self.assertEqual(ledger["before_tokens"], result.before_tokens)

    def test_propagates_returncode_and_tees_on_failure(self):
        with tempfile.TemporaryDirectory() as root:
            code = "import sys; print('boom'); sys.exit(3)"
            result = run_command([sys.executable, "-c", code], root=root)
            self.assertEqual(result.returncode, 3)
            # Failure -> full output saved to a tee file.
            self.assertIsNotNone(result.tee_path)
            self.assertTrue(os.path.exists(result.tee_path))
            with open(result.tee_path, encoding="utf-8") as fh:
                self.assertIn("boom", fh.read())

    def test_gain_accumulates_across_runs(self):
        with tempfile.TemporaryDirectory() as root:
            run_command([sys.executable, "-c", "print('a')"], root=root)
            run_command([sys.executable, "-c", "print('b')"], root=root)
            self.assertEqual(load_gain(root)["runs"], 2)

    def test_load_gain_empty(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertIsNone(load_gain(root))


if __name__ == "__main__":
    unittest.main()
