"""Tests for the comparison harness."""

import unittest

from monolith.compare import run_comparison


class CompareTests(unittest.TestCase):
    def test_includes_all_approaches(self):
        labels = [r.label for r in run_comparison().results]
        self.assertIn("Normal (no tool)", labels)
        self.assertIn("caveman", labels)
        self.assertIn("claude-token-efficient", labels)
        self.assertTrue(any("Monolith" in label for label in labels))

    def test_normal_has_zero_overhead_and_reduction(self):
        normal = next(r for r in run_comparison().results if r.label == "Normal (no tool)")
        self.assertEqual(normal.input_overhead_tokens, 0)
        self.assertEqual(normal.output_reduction, 0.0)

    def test_monolith_is_measured_others_published(self):
        results = {r.label: r for r in run_comparison().results}
        self.assertTrue(results["Monolith (full tier)"].measured)
        self.assertFalse(results["caveman"].measured)
        # Monolith injects real rules, so its overhead is non-trivial.
        self.assertGreater(results["Monolith (full tier)"].input_overhead_tokens, 0)


if __name__ == "__main__":
    unittest.main()
