"""Tests for PRD parsing, the task store, status updates, and rendering."""

import tempfile
import unittest

from monolith.tasks import (
    emit_tasks_md,
    load_tasks,
    parse_prd,
    render_tasks_md,
    save_tasks,
    set_status,
)

PRD = """\
# Build login
- Design schema {#schema}
- Implement API @after:schema
  - Add validation

## Ship it @after:schema
"""


class ParseTests(unittest.TestCase):
    def test_headings_and_items_become_tasks(self):
        tasks = parse_prd(PRD)
        titles = [t.title for t in tasks]
        self.assertIn("Build login", titles)
        self.assertIn("Design schema", titles)
        self.assertIn("Implement API", titles)
        self.assertIn("Add validation", titles)
        self.assertIn("Ship it", titles)

    def test_nesting_sets_parent(self):
        tasks = parse_prd(PRD)
        by_title = {t.title: t for t in tasks}
        # "Add validation" is indented under "Implement API".
        self.assertEqual(by_title["Add validation"].parent, by_title["Implement API"].id)
        # Top-level heading has no parent.
        self.assertIsNone(by_title["Build login"].parent)

    def test_dependencies_resolve_by_name(self):
        tasks = parse_prd(PRD)
        by_title = {t.title: t for t in tasks}
        schema_id = by_title["Design schema"].id
        self.assertEqual(by_title["Implement API"].deps, [schema_id])
        self.assertEqual(by_title["Ship it"].deps, [schema_id])

    def test_tags_are_stripped_from_titles(self):
        tasks = parse_prd(PRD)
        for task in tasks:
            self.assertNotIn("{#", task.title)
            self.assertNotIn("@after", task.title)

    def test_empty_prd_yields_no_tasks(self):
        self.assertEqual(parse_prd("just prose, no structure"), [])


class StatusTests(unittest.TestCase):
    def test_set_status_changes_and_validates_deps(self):
        tasks = parse_prd(PRD)
        by_title = {t.title: t for t in tasks}
        api = by_title["Implement API"]

        # Advancing before the dependency is done yields a warning in the message.
        changed, message = set_status(tasks, api.id, "doing")
        self.assertTrue(changed)
        self.assertIn("warning", message)

        # Finish the dependency, then advancing is clean.
        set_status(tasks, by_title["Design schema"].id, "done")
        changed, message = set_status(tasks, api.id, "done")
        self.assertTrue(changed)
        self.assertNotIn("warning", message)

    def test_unknown_task_and_status_are_rejected(self):
        tasks = parse_prd(PRD)
        self.assertFalse(set_status(tasks, "T999", "done")[0])
        self.assertFalse(set_status(tasks, tasks[0].id, "bogus")[0])


class StoreAndRenderTests(unittest.TestCase):
    def test_save_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as root:
            tasks = parse_prd(PRD)
            save_tasks(tasks, root)
            loaded = load_tasks(root)
            self.assertEqual([t.id for t in loaded], [t.id for t in tasks])
            self.assertEqual(loaded[0].title, tasks[0].title)

    def test_render_and_emit(self):
        with tempfile.TemporaryDirectory() as root:
            tasks = parse_prd(PRD)
            md = render_tasks_md(tasks)
            self.assertIn("# Tasks", md)
            self.assertIn("[ ]", md)
            path = emit_tasks_md(tasks, root)
            self.assertTrue(path.endswith("TASKS.md"))


if __name__ == "__main__":
    unittest.main()
