"""Tests for the agent compilers and the registry."""

import os
import tempfile
import unittest

from monolith.adapters import all_keys, get_compiler
from monolith.adapters.compiler import START, END


class CompilerTests(unittest.TestCase):
    def test_registry_has_all_three_agents(self):
        self.assertEqual(set(all_keys()), {"claude", "codex", "copilot"})

    def test_render_contains_markers_and_override(self):
        block = get_compiler("claude").render("full")
        self.assertIn(START, block)
        self.assertIn(END, block)
        self.assertIn("override", block.lower())
        self.assertIn("tier: full", block)

    def test_unknown_tier_raises(self):
        with self.assertRaises(ValueError):
            get_compiler("claude").render("nope")

    def test_extra_rules_are_appended(self):
        block = get_compiler("codex").render("lite", ["Never touch vendor/."])
        self.assertIn("Never touch vendor/.", block)

    def test_apply_creates_then_updates_idempotently(self):
        with tempfile.TemporaryDirectory() as root:
            compiler = get_compiler("codex")
            self.assertEqual(compiler.apply(root, "full"), "created")

            path = os.path.join(root, "AGENTS.md")
            self.assertEqual(compiler.apply(root, "ultra"), "updated")
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            # Exactly one block survives re-apply.
            self.assertEqual(content.count(START), 1)
            self.assertEqual(content.count(END), 1)
            self.assertIn("tier: ultra", content)

    def test_apply_preserves_user_content(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "CLAUDE.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("# My project notes\nKeep me.\n")
            get_compiler("claude").apply(root, "lite")
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("Keep me.", content)
            self.assertIn(START, content)

    def test_copilot_targets_github_dir(self):
        with tempfile.TemporaryDirectory() as root:
            get_compiler("copilot").apply(root, "full")
            self.assertTrue(
                os.path.exists(os.path.join(root, ".github", "copilot-instructions.md"))
            )


if __name__ == "__main__":
    unittest.main()
