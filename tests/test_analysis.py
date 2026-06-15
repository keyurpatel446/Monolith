"""Tests for cross-artifact analysis and checklist generation."""

import os
import tempfile
import unittest

from monolith import workflow
from monolith.analysis import Finding, Severity, analyze_feature, generate_checklist


class AnalyzeTests(unittest.TestCase):
    def test_findings_are_structured_values(self):
        with tempfile.TemporaryDirectory() as root:
            findings = analyze_feature(root, "feat")
            self.assertTrue(all(isinstance(f, Finding) for f in findings))
            self.assertTrue(all(isinstance(f.severity, Severity) for f in findings))

    def test_missing_pipeline_artifacts_are_errors(self):
        with tempfile.TemporaryDirectory() as root:
            findings = analyze_feature(root, "feat")
            errors = [f for f in findings if f.severity is Severity.ERROR]
            # spec.md, plan.md, tasks.md all missing.
            self.assertEqual(len(errors), 3)

    def test_root_tasks_md_satisfies_tasks_artifact(self):
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "TASKS.md"), "w", encoding="utf-8") as fh:
                fh.write("# Tasks\n- [ ] T1: do a thing\n- [ ] T2: do another\n")
            findings = analyze_feature(root, "feat")
            messages = [f.message for f in findings]
            self.assertFalse(any("tasks.md missing" in m for m in messages))

    def test_str_prefixes_severity(self):
        self.assertTrue(str(Finding(Severity.ERROR, "x")).startswith("ERROR"))
        self.assertTrue(str(Finding(Severity.OK, "x")).startswith("OK"))


class ChecklistTests(unittest.TestCase):
    def test_box_checked_for_existing_artifact(self):
        with tempfile.TemporaryDirectory() as root:
            workflow.scaffold_spec(root, "feat")
            text = generate_checklist(root, "feat")
            self.assertIn("[x] `spec.md`", text)
            self.assertIn("[ ] `plan.md`", text)


if __name__ == "__main__":
    unittest.main()
