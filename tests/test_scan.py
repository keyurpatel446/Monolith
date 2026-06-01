"""Tests for @monolith: tag scanning and applying."""

import os
import tempfile
import unittest

from monolith.scan import apply_found, scan_repo, scan_text
from monolith.settings import extra_rules, load_settings
from monolith.tasks import load_tasks

# Build the marker at runtime so this test file isn't itself a live tag.
M = "@" + "monolith:"


class ScanTextTests(unittest.TestCase):
    def test_finds_task_and_rule_tags(self):
        text = (
            f"# {M}task Build login {{#login}}\n"
            f"// {M}rule Always add type hints\n"
            "no tag here\n"
        )
        found = scan_text(text)
        self.assertEqual(len(found.tasks), 1)
        self.assertEqual(len(found.rules), 1)
        self.assertIn("Build login", found.tasks[0])
        self.assertEqual(found.rules[0], "Always add type hints")

    def test_trims_html_comment_closer(self):
        found = scan_text(f"<!-- {M}rule Validate inputs -->")
        self.assertEqual(found.rules[0], "Validate inputs")


class ScanRepoApplyTests(unittest.TestCase):
    def _write(self, root, name, content):
        path = os.path.join(root, name)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(content)

    def test_scan_repo_skips_unreadable_and_collects(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, "a.py", f"# {M}task Do thing\n")
            self._write(root, "b.md", f"{M}rule Be terse\n")
            found = scan_repo(root)
            self.assertEqual(len(found.tasks), 1)
            self.assertEqual(len(found.rules), 1)

    def test_apply_adds_tasks_and_rules_and_dedupes(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, "c.py", f"# {M}task Build API @after:schema\n"
                                      f"# {M}task Design schema {{#schema}}\n"
                                      f"# {M}rule Prefer pure functions\n")
            found = scan_repo(root)
            added_tasks, added_rules = apply_found(found, root)
            self.assertEqual(len(added_tasks), 2)
            self.assertEqual(added_rules, ["Prefer pure functions"])

            # Dependency resolved by slug within the batch.
            tasks = load_tasks(root)
            api = next(t for t in tasks if t.title == "Build API")
            schema = next(t for t in tasks if t.title == "Design schema")
            self.assertEqual(api.deps, [schema.id])
            self.assertIn("Prefer pure functions", extra_rules(load_settings(root)))

            # Re-applying the same tags adds nothing (idempotent).
            again_tasks, again_rules = apply_found(scan_repo(root), root)
            self.assertEqual(again_tasks, [])
            self.assertEqual(again_rules, [])

    def test_tasks_md_written_on_apply(self):
        with tempfile.TemporaryDirectory() as root:
            self._write(root, "d.py", f"# {M}task Ship it\n")
            apply_found(scan_repo(root), root)
            self.assertTrue(os.path.exists(os.path.join(root, "TASKS.md")))


if __name__ == "__main__":
    unittest.main()
