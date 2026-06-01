"""Tests for the benchmark harness and token counting."""

import tempfile
import unittest

from monolith.benchmark import CORPUS, load_last_report, run_benchmark, save_report
from monolith.tokens import count_tokens, counter_name


class TokenTests(unittest.TestCase):
    def test_count_is_nonnegative_and_monotonic(self):
        self.assertGreaterEqual(count_tokens(""), 0)
        self.assertLess(count_tokens("a short line"), count_tokens("a much longer line of text here"))

    def test_counter_name_is_labelled(self):
        self.assertTrue(counter_name().startswith(("tiktoken:", "heuristic:")))


class BenchmarkTests(unittest.TestCase):
    def test_run_reports_positive_reduction(self):
        report = run_benchmark()
        self.assertEqual(len(report.results), len(CORPUS))
        # Every concise sample should be smaller than its verbose counterpart.
        for result in report.results:
            self.assertLess(result.concise_tokens, result.verbose_tokens)
        self.assertGreater(report.reduction, 0.0)
        self.assertLess(report.reduction, 1.0)

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertIsNone(load_last_report(root))
            report = run_benchmark()
            save_report(report, root)
            loaded = load_last_report(root)
            self.assertIsNotNone(loaded)
            self.assertEqual(loaded["samples"], len(CORPUS))
            self.assertAlmostEqual(loaded["reduction"], round(report.reduction, 4))


if __name__ == "__main__":
    unittest.main()
