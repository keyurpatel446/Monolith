import os
import tempfile
import unittest

from monolith.adapters import all_keys, get_adapter
from monolith.adapters.base import START, END


class AdapterTests(unittest.TestCase):
    def test_all_adapters_register(self):
        self.assertEqual(set(all_keys()), {"claude", "codex", "copilot"})

    def test_render_contains_markers_and_override(self):
        adapter = get_adapter("claude")
        block = adapter.render_block("full")
        self.assertIn(START, block)
        self.assertIn(END, block)
        self.assertIn("override", block.lower())
        self.assertIn("profile: full", block)

    def test_unknown_profile_raises(self):
        with self.assertRaises(ValueError):
            get_adapter("claude").render_block("nope")

    def test_apply_creates_then_updates_idempotently(self):
        with tempfile.TemporaryDirectory() as root:
            adapter = get_adapter("codex")
            self.assertEqual(adapter.apply(root, "full"), "created")
            path = os.path.join(root, "AGENTS.md")
            self.assertTrue(os.path.exists(path))

            # Re-apply must not duplicate the block.
            self.assertEqual(adapter.apply(root, "ultra"), "updated")
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertEqual(content.count(START), 1)
            self.assertEqual(content.count(END), 1)
            self.assertIn("profile: ultra", content)

    def test_apply_preserves_user_content(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "CLAUDE.md")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("# My project notes\nKeep me.\n")
            get_adapter("claude").apply(root, "lite")
            with open(path, encoding="utf-8") as fh:
                content = fh.read()
            self.assertIn("Keep me.", content)
            self.assertIn(START, content)

    def test_copilot_writes_under_github_dir(self):
        with tempfile.TemporaryDirectory() as root:
            get_adapter("copilot").apply(root, "full")
            self.assertTrue(
                os.path.exists(os.path.join(root, ".github", "copilot-instructions.md"))
            )


if __name__ == "__main__":
    unittest.main()
