"""Tests for command-aware (semantic) output compressors."""

import unittest

from monolith.compressors import compress_for, pick
from monolith.tokens import count_tokens

# A realistic pytest run: many passing lines, one failure, a summary.
PYTEST_OUTPUT = "\n".join(
    ["============================= test session starts ============================="]
    + [f"tests/test_mod.py::test_case_{i} PASSED      [{i}%]" for i in range(120)]
    + [
        "tests/test_auth.py::test_login FAILED        [99%]",
        "=================================== FAILURES ===================================",
        "_________________________________ test_login __________________________________",
        ">       assert auth.login('u', 'bad') is True",
        "E       AssertionError: assert None is True",
        "tests/test_auth.py:42: AssertionError",
        "FAILED tests/test_auth.py::test_login - AssertionError: assert None is True",
        "======================== 1 failed, 120 passed in 3.21s =========================",
    ]
)


class CompressorTests(unittest.TestCase):
    def test_detects_test_commands(self):
        self.assertIsNotNone(pick(["pytest", "-q"]))
        self.assertIsNotNone(pick(["python", "-m", "pytest"]))
        self.assertIsNotNone(pick(["go", "test", "./..."]))
        self.assertIsNotNone(pick(["npm", "test"]))
        self.assertIsNone(pick(["ls", "-la"]))

    def test_test_compressor_keeps_failures_drops_passes(self):
        out, kind = compress_for(["pytest"], PYTEST_OUTPUT)
        self.assertEqual(kind, "test")
        self.assertIn("test_login", out)
        self.assertIn("AssertionError", out)
        self.assertIn("1 failed, 120 passed", out)
        self.assertNotIn("PASSED", out)  # green lines dropped

    def test_test_compressor_hits_high_reduction(self):
        out, _ = compress_for(["pytest"], PYTEST_OUTPUT)
        reduction = 1 - count_tokens(out) / count_tokens(PYTEST_OUTPUT)
        # Semantic filtering should far exceed generic compression here.
        self.assertGreater(reduction, 0.85)

    def test_all_green_keeps_summary(self):
        green = "\n".join(
            [f"test_{i} PASSED" for i in range(10)] + ["10 passed in 0.1s"]
        )
        out, kind = compress_for(["pytest"], green)
        self.assertEqual(kind, "test")
        self.assertIn("passed", out)

    def test_unknown_command_falls_back_to_generic(self):
        out, kind = compress_for(["ls"], "a\n\n\n\nb")
        self.assertEqual(kind, "generic")
        self.assertEqual(out, "a\n\nb")


if __name__ == "__main__":
    unittest.main()
