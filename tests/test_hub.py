"""Tests for the resource hub catalog and installer."""

import os
import tempfile
import unittest

from monolith.hub import BUNDLES, CATALOG, find, install, search


class HubTests(unittest.TestCase):
    def test_catalog_ids_are_unique(self):
        ids = [r.id for r in CATALOG]
        self.assertEqual(len(ids), len(set(ids)))

    def test_catalog_has_expected_resources(self):
        ids = {r.id for r in CATALOG}
        for expected in ("concise-commit", "terse-review", "test-plan", "explain-diff"):
            self.assertIn(expected, ids)
        # Every resource ships a non-empty body and at least one install target.
        for resource in CATALOG:
            self.assertTrue(resource.body.strip())
            self.assertTrue(resource.targets)

    def test_bundles_reference_real_resources(self):
        ids = {r.id for r in CATALOG}
        for bundle, members in BUNDLES.items():
            self.assertTrue(members)
            for member in members:
                self.assertIn(member, ids)
            # A bundle name must not shadow a resource id.
            self.assertNotIn(bundle, ids)

    def test_find_and_search(self):
        self.assertIsNotNone(find("concise-commit"))
        self.assertIsNone(find("does-not-exist"))
        self.assertTrue(search("commit"))
        self.assertEqual(search("zzzz-nope"), [])

    def test_install_writes_targeted_files(self):
        with tempfile.TemporaryDirectory() as root:
            resource = find("concise-commit")
            written = install(resource, root, ["claude", "copilot"])
            self.assertEqual(len(written), 2)
            for path in written:
                self.assertTrue(os.path.exists(path))
            # Claude path convention.
            self.assertTrue(
                os.path.exists(os.path.join(root, ".claude", "commands", "concise-commit.md"))
            )

    def test_install_skips_agents_without_target(self):
        with tempfile.TemporaryDirectory() as root:
            resource = find("concise-commit")
            written = install(resource, root, ["nonexistent-agent"])
            self.assertEqual(written, [])


if __name__ == "__main__":
    unittest.main()
