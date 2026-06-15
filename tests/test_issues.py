"""Tests for the GitHub Issues client (monolith.issues)."""

import json
import unittest
from unittest import mock

from monolith import issues
from monolith.tasks import Task


def _fake_request(existing_titles):
    """Return a stand-in for ``issues._request`` plus a record of POSTed bodies.

    GET (list issues) yields one short page of ``existing_titles`` then stops;
    POST records the payload and returns a created-issue stub.
    """
    created = []

    def _req(url, token, data=None, method="GET"):
        if method == "GET":
            if "page=1" in url:
                return [{"title": t} for t in existing_titles]
            return []
        payload = json.loads(data.decode())
        created.append(payload)
        return {"number": len(created), "html_url": f"https://gh/{len(created)}"}

    return _req, created


def _tasks():
    return [
        Task(id="T1", title="Build API", level=1, status="todo"),
        Task(id="T2", title="Write docs", level=1, status="doing"),
        Task(id="T3", title="Ship", level=1, status="done"),
    ]


class PushTasksTests(unittest.TestCase):
    def test_creates_todo_and_doing_skips_done_by_default(self):
        req, created = _fake_request(existing_titles=[])
        with mock.patch.object(issues, "_request", req):
            result = issues.push_tasks(_tasks(), "acme/app", "tok")
        self.assertTrue(result.ok)
        self.assertEqual(len(result.created), 2)  # todo + doing, not done
        self.assertEqual({c["title"] for c in created}, {"Build API", "Write docs"})

    def test_include_done_pushes_done_too(self):
        req, created = _fake_request(existing_titles=[])
        with mock.patch.object(issues, "_request", req):
            result = issues.push_tasks(_tasks(), "acme/app", "tok", include_done=True)
        self.assertTrue(result.ok)
        self.assertEqual(len(created), 3)

    def test_idempotent_skips_already_open_titles(self):
        req, created = _fake_request(existing_titles=["Build API"])
        with mock.patch.object(issues, "_request", req):
            result = issues.push_tasks(_tasks(), "acme/app", "tok")
        self.assertEqual(result.skipped, ["Build API"])
        self.assertEqual([c["title"] for c in created], ["Write docs"])

    def test_label_attached_when_given(self):
        req, created = _fake_request(existing_titles=[])
        with mock.patch.object(issues, "_request", req):
            result = issues.push_tasks(_tasks(), "acme/app", "tok", label="task")
        self.assertTrue(result.ok)
        self.assertTrue(all(c["labels"] == ["task"] for c in created))

    def test_malformed_repo_is_an_error(self):
        result = issues.push_tasks(_tasks(), "not-a-repo", "tok")
        self.assertFalse(result.ok)
        self.assertEqual(result.created, [])

    def test_split_repo(self):
        self.assertEqual(issues.split_repo("a/b"), ("a", "b"))
        self.assertIsNone(issues.split_repo("nope"))


if __name__ == "__main__":
    unittest.main()
