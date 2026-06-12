"""Tests for the command-line console."""

import io
import os
import tempfile
import unittest
from contextlib import redirect_stdout

from monolith.console import main
from monolith.settings import load_settings, settings_exist


def run(argv):
    """Run the console capturing stdout; return ``(exit_code, output)``."""
    buf = io.StringIO()
    with redirect_stdout(buf):
        code = main(argv)
    return code, buf.getvalue()


def write_prd(root):
    """Write a small PRD file under ``root`` and return its path."""
    path = os.path.join(root, "prd.md")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("# Feature\n- First {#first}\n- Second @after:first\n")
    return path


class ConsoleTests(unittest.TestCase):
    def test_init_creates_settings(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "init"])
            self.assertEqual(code, 0)
            self.assertTrue(settings_exist(root))
            self.assertIn("Initialized Monolith", out)

    def test_init_agent_flag_scopes_targets(self):
        with tempfile.TemporaryDirectory() as root:
            code, _ = run(["--root", root, "init", "--agent", "claude"])
            self.assertEqual(code, 0)
            self.assertEqual(load_settings(root)["agents"], ["claude"])

    def test_setup_single_agent_is_green_in_one_command(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "setup", "--agent", "claude"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(root, "CLAUDE.md")))
            self.assertEqual(load_settings(root)["agents"], ["claude"])
            self.assertIn("All configured agents", out)
            self.assertNotIn("FAIL", out)

    def test_setup_all_agents_and_tier(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "setup", "--agent", "all", "--tier", "ultra"])
            self.assertEqual(code, 0)
            self.assertEqual(load_settings(root)["tier"], "ultra")
            self.assertTrue(os.path.exists(os.path.join(root, "AGENTS.md")))
            self.assertIn("All configured agents", out)

    def test_apply_writes_all_three_agents(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, _ = run(["--root", root, "apply", "--agent", "all"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(root, "CLAUDE.md")))
            self.assertTrue(os.path.exists(os.path.join(root, "AGENTS.md")))
            self.assertTrue(
                os.path.exists(os.path.join(root, ".github", "copilot-instructions.md"))
            )

    def test_tier_switch_persists(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, _ = run(["--root", root, "tier", "ultra"])
            self.assertEqual(code, 0)
            self.assertEqual(load_settings(root)["tier"], "ultra")

    def test_tier_apply_flag_regenerates(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            run(["--root", root, "tier", "ultra", "--apply"])
            with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8") as fh:
                self.assertIn("tier: ultra", fh.read())

    def test_doctor_fails_before_apply_succeeds_after(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            self.assertEqual(run(["--root", root, "doctor"])[0], 1)
            run(["--root", root, "apply", "--agent", "all"])
            code, out = run(["--root", root, "doctor"])
            self.assertEqual(code, 0)
            self.assertIn("All configured agents", out)

    def test_doctor_unconfigured_suggests_setup(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "doctor"])
            self.assertEqual(code, 1)
            self.assertIn("monolith setup", out)

    def test_bare_invocation_hints_setup(self):
        code, out = run([])
        self.assertEqual(code, 0)
        self.assertIn("monolith setup", out)

    def test_stats_reports_projection(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, out = run(["--root", root, "stats"])
            self.assertEqual(code, 0)
            self.assertIn("projected OUTPUT reduction", out)


class Phase2Tests(unittest.TestCase):
    def test_bench_records_and_stats_reads_it(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            code, out = run(["--root", root, "bench"])
            self.assertEqual(code, 0)
            self.assertIn("TOTAL", out)
            # stats now reports the measured figure.
            _, stats_out = run(["--root", root, "stats"])
            self.assertIn("last measured reduction", stats_out)

    def test_rules_add_list_remove(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            run(["--root", root, "rules", "add", "Never touch vendor/."])
            self.assertEqual(load_settings(root)["extra_rules"], ["Never touch vendor/."])
            _, out = run(["--root", root, "rules", "list"])
            self.assertIn("Never touch vendor/.", out)
            run(["--root", root, "rules", "remove", "1"])
            self.assertEqual(load_settings(root)["extra_rules"], [])

    def test_custom_rule_appears_in_generated_block(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init"])
            run(["--root", root, "rules", "add", "Prefer pytest asserts."])
            run(["--root", root, "apply", "--agent", "claude"])
            with open(os.path.join(root, "CLAUDE.md"), encoding="utf-8") as fh:
                self.assertIn("Prefer pytest asserts.", fh.read())


class Phase3Tests(unittest.TestCase):
    def test_plan_creates_store_and_tasks_md(self):
        with tempfile.TemporaryDirectory() as root:
            prd = write_prd(root)
            code, out = run(["--root", root, "plan", prd])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(root, ".monolith", "tasks", "tasks.json")))
            self.assertTrue(os.path.exists(os.path.join(root, "TASKS.md")))

    def test_plan_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as root:
            prd = write_prd(root)
            run(["--root", root, "plan", prd])
            self.assertEqual(run(["--root", root, "plan", prd])[0], 1)
            self.assertEqual(run(["--root", root, "plan", prd, "--force"])[0], 0)

    def test_task_status_update_reflected_in_tasks_md(self):
        with tempfile.TemporaryDirectory() as root:
            prd = write_prd(root)
            run(["--root", root, "plan", prd])
            code, _ = run(["--root", root, "task", "T1", "--status", "done"])
            self.assertEqual(code, 0)
            with open(os.path.join(root, "TASKS.md"), encoding="utf-8") as fh:
                self.assertIn("[x] T1", fh.read())

    def test_tasks_list_shows_progress(self):
        with tempfile.TemporaryDirectory() as root:
            prd = write_prd(root)
            run(["--root", root, "plan", prd])
            code, out = run(["--root", root, "tasks"])
            self.assertEqual(code, 0)
            self.assertIn("done):", out)


class Phase45Tests(unittest.TestCase):
    def test_hub_list_and_install(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["hub", "list"])
            self.assertEqual(code, 0)
            self.assertIn("concise-commit", out)
            code, _ = run(["--root", root, "hub", "install", "concise-commit", "--agent", "claude"])
            self.assertEqual(code, 0)
            self.assertTrue(
                os.path.exists(os.path.join(root, ".claude", "commands", "concise-commit.md"))
            )

    def test_hub_install_unknown_resource_errors(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual(run(["--root", root, "hub", "install", "nope"])[0], 1)

    def test_hub_install_sdd_bundle(self):
        with tempfile.TemporaryDirectory() as root:
            code, out = run(["--root", root, "hub", "install", "sdd", "--agent", "claude"])
            self.assertEqual(code, 0)
            commands_dir = os.path.join(root, ".claude", "commands")
            for name in ("constitution", "specify", "clarify", "analyze",
                         "checklist", "implement"):
                self.assertTrue(
                    os.path.exists(os.path.join(commands_dir, f"monolith.{name}.md"))
                )

    def test_hub_install_respects_settings_agents(self):
        with tempfile.TemporaryDirectory() as root:
            run(["--root", root, "init", "--agent", "claude"])
            code, _ = run(["--root", root, "hub", "install", "concise-commit"])
            self.assertEqual(code, 0)
            self.assertTrue(
                os.path.exists(os.path.join(root, ".claude", "commands", "concise-commit.md"))
            )
            # Only the configured agent's directory is created.
            self.assertFalse(os.path.exists(os.path.join(root, ".codex")))

    def test_hub_list_shows_bundles(self):
        code, out = run(["hub", "list"])
        self.assertEqual(code, 0)
        self.assertIn("sdd", out)
        self.assertIn("bundle", out)

    def test_scan_dry_run_then_apply(self):
        marker = "@" + "monolith:"
        with tempfile.TemporaryDirectory() as root:
            with open(os.path.join(root, "x.py"), "w", encoding="utf-8") as fh:
                fh.write(f"# {marker}task Wire up CI\n# {marker}rule Keep PRs small\n")
            # Dry run reports but does not write a task store.
            code, out = run(["--root", root, "scan"])
            self.assertEqual(code, 0)
            self.assertIn("dry run", out)
            self.assertFalse(os.path.exists(os.path.join(root, "TASKS.md")))
            # Apply writes tasks + rules.
            code, out = run(["--root", root, "scan", "--apply"])
            self.assertEqual(code, 0)
            self.assertTrue(os.path.exists(os.path.join(root, "TASKS.md")))

    def test_shrink_file_reduces_tokens(self):
        with tempfile.TemporaryDirectory() as root:
            path = os.path.join(root, "log.txt")
            with open(path, "w", encoding="utf-8") as fh:
                fh.write("hit\n" * 10 + "\n\n\n\ndone\n")
            code, out = run(["shrink", path, "--level", "full"])
            self.assertEqual(code, 0)
            self.assertIn("(x10)", out)


if __name__ == "__main__":
    unittest.main()
