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


class LintCompressorTests(unittest.TestCase):
    ESLINT = "\n".join([
        "/src/app.js",
        "  12:5  error    'x' is assigned a value but never used  no-unused-vars",
        "  40:1  warning  Unexpected console statement              no-console",
        "",
        "/src/util.js",
        "  3:10  error    Missing semicolon                         semi",
        "",
        "✖ 3 problems (2 errors, 1 warning)",
    ])

    def test_detects_lint_commands(self):
        self.assertIsNotNone(pick(["eslint", "."]))
        self.assertIsNotNone(pick(["tsc", "--noEmit"]))
        self.assertIsNotNone(pick(["npm", "run", "lint"]))

    def test_keeps_diagnostics_and_summary(self):
        out, kind = compress_for(["eslint", "."], self.ESLINT)
        self.assertEqual(kind, "lint")
        self.assertIn("no-unused-vars", out)
        self.assertIn("3 problems", out)
        self.assertNotIn("\n\n", out)  # blank lines dropped

    def test_compacts_diagnostics_for_real_savings(self):
        # Many files/diagnostics: compacting (drop prose, keep loc+rule) should
        # save a meaningful fraction, not ~0%.
        big = []
        for f in range(40):
            big.append(f"/src/components/widget{f}.jsx")
            big.append(f"  {f+1}:5  error    '{f}' is assigned but never used   no-unused-vars")
            big.append("")
        big.append("✖ 40 problems (40 errors, 0 warnings)")
        text = "\n".join(big)
        out, _ = compress_for(["eslint", "."], text)
        reduction = 1 - count_tokens(out) / count_tokens(text)
        self.assertGreater(reduction, 0.30)
        self.assertIn("no-unused-vars", out)  # still actionable


class GitStatusCompressorTests(unittest.TestCase):
    STATUS = "\n".join([
        "On branch main",
        "Your branch is up to date with 'origin/main'.",
        "",
        "Changes not staged for commit:",
        '  (use "git add <file>..." to update what will be committed)',
        '  (use "git restore <file>..." to discard changes in working directory)',
        "\tmodified:   src/app.py",
        "",
        "Untracked files:",
        '  (use "git add <file>..." to include in what will be committed)',
        "\tnotes.md",
    ])

    def test_drops_hint_and_blank_lines(self):
        out, kind = compress_for(["git", "status"], self.STATUS)
        self.assertEqual(kind, "git-status")
        self.assertIn("modified:   src/app.py", out)
        self.assertIn("On branch main", out)
        self.assertNotIn("(use ", out)
        self.assertNotIn("\n\n", out)


class GrepFindCompressorTests(unittest.TestCase):
    def test_grep_groups_by_file_and_shrinks(self):
        # Many matches in one file -> grouping drops the repeated path prefix.
        grep = "\n".join(
            f"src/very/long/path/app.py:{i}:import something_{i}" for i in range(12)
        )
        out, kind = compress_for(["grep", "-rn", "import", "."], grep)
        self.assertEqual(kind, "grep/find")
        self.assertIn("src/very/long/path/app.py (12):", out)
        self.assertLess(len(out), len(grep))

    def test_find_groups_by_directory_and_shrinks(self):
        find = "\n".join(f"src/pkg/module_{i}.py" for i in range(10))
        out, kind = compress_for(["find", ".", "-name", "*.py"], find)
        self.assertEqual(kind, "grep/find")
        self.assertIn("src/pkg/ (10)", out)
        self.assertLess(len(out), len(find))

    def test_grep_single_file_numeric_prefix_passes_through(self):
        # `grep -n` on one file yields "line:text" with no filename to group by.
        grep = "1:import os\n5:import sys"
        out, kind = compress_for(["grep", "-n", "import", "f.py"], grep)
        self.assertEqual(kind, "grep/find")
        self.assertNotIn("(", out)  # not mis-grouped by line number


if __name__ == "__main__":
    unittest.main()
