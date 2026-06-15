"""Tests for settings/tasks persistence robustness against corrupt JSON."""

import os
import tempfile
import unittest

from monolith.settings import (
    DEFAULT_TIER,
    default_settings,
    load_settings,
    save_settings,
    settings_path,
)
from monolith.tasks import Task, load_tasks, save_tasks, tasks_path


class SettingsTests(unittest.TestCase):
    def test_missing_keys_backfilled_from_defaults(self):
        with tempfile.TemporaryDirectory() as root:
            save_settings({"tier": "ultra"}, root)
            loaded = load_settings(root)
            self.assertEqual(loaded["tier"], "ultra")
            self.assertIn("agents", loaded)
            self.assertIn("extra_rules", loaded)

    def test_corrupt_settings_fall_back_to_defaults(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.dirname(settings_path(root)), exist_ok=True)
            with open(settings_path(root), "w", encoding="utf-8") as fh:
                fh.write("{ not valid json ]")
            loaded = load_settings(root)
            self.assertEqual(loaded["tier"], DEFAULT_TIER)
            self.assertEqual(loaded, default_settings())


class TasksRobustnessTests(unittest.TestCase):
    def test_corrupt_task_store_raises_not_clobbers(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.dirname(tasks_path(root)), exist_ok=True)
            with open(tasks_path(root), "w", encoding="utf-8") as fh:
                fh.write("{bad json")
            with self.assertRaises(ValueError):
                load_tasks(root)

    def test_round_trip(self):
        with tempfile.TemporaryDirectory() as root:
            save_tasks([Task(id="T1", title="a", level=1)], root)
            self.assertEqual(load_tasks(root)[0].title, "a")


if __name__ == "__main__":
    unittest.main()
