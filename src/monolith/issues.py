"""GitHub Issues integration — push Monolith tasks to a repo's issue tracker.

Kept out of the console layer so the HTTP/client logic is a unit-testable,
reusable component rather than inline argparse handling. Uses only ``urllib``
(stdlib) to honour Monolith's dependency-free core.

The push is idempotent by default: titles that already exist as open issues are
skipped, so re-running ``monolith tasks-to-issues`` does not create duplicates.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from typing import List, Optional, Sequence, Set, Tuple

from monolith.tasks import Task

API_ROOT = "https://api.github.com"
_PER_PAGE = 100


@dataclass
class PushResult:
    """Outcome of a push: created issues, skipped duplicates, and errors."""

    created: List[str] = field(default_factory=list)  # "#12 T3: title  <url>"
    skipped: List[str] = field(default_factory=list)  # titles already open
    errors: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors


def split_repo(repo: str) -> Optional[Tuple[str, str]]:
    """Split ``owner/repo`` into ``(owner, repo)``; ``None`` if malformed."""
    owner, _, name = repo.partition("/")
    if not owner or not name:
        return None
    return owner, name


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }


def _request(url: str, token: str, data: Optional[bytes] = None, method: str = "GET"):
    req = urllib.request.Request(url, data=data, headers=_headers(token), method=method)
    with urllib.request.urlopen(req) as resp:  # noqa: S310 - fixed https API host
        return json.loads(resp.read())


def existing_open_titles(owner: str, repo: str, token: str) -> Set[str]:
    """Return the titles of currently-open issues (paginated, PRs excluded)."""
    titles: Set[str] = set()
    page = 1
    while True:
        url = (
            f"{API_ROOT}/repos/{owner}/{repo}/issues"
            f"?state=open&per_page={_PER_PAGE}&page={page}"
        )
        batch = _request(url, token)
        for issue in batch:
            # The issues endpoint also returns pull requests; skip those.
            if "pull_request" not in issue:
                titles.add(issue.get("title", ""))
        if len(batch) < _PER_PAGE:
            break
        page += 1
    return titles


def _issue_body(task: Task, spec_link: str) -> str:
    parts = [f"Task `{task.id}` from Monolith task tree."]
    if task.deps:
        parts.append(f"\nDepends on: {', '.join(task.deps)}")
    parts.append(f"\nStatus: `{task.status}`")
    if spec_link:
        parts.append(f"\nSpec: {spec_link}")
    return "\n".join(parts)


def push_tasks(
    tasks: Sequence[Task],
    repo: str,
    token: str,
    *,
    label: str = "",
    spec_link: str = "",
    include_done: bool = False,
    dedupe: bool = True,
) -> PushResult:
    """Create one GitHub issue per eligible task.

    Eligible = status ``todo``/``doing`` (plus ``done`` when ``include_done``).
    When ``dedupe`` is set, tasks whose title already matches an open issue are
    skipped instead of duplicated.
    """
    result = PushResult()
    split = split_repo(repo)
    if split is None:
        result.errors.append("--repo must be in owner/repo format")
        return result
    owner, name = split

    wanted = {"todo", "doing", "done"} if include_done else {"todo", "doing"}
    to_push = [t for t in tasks if t.status in wanted]

    seen: Set[str] = set()
    if dedupe:
        try:
            seen = existing_open_titles(owner, name, token)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            result.errors.append(f"could not list existing issues: HTTP {exc.code}: {detail}")
            return result

    for task in to_push:
        if task.title in seen:
            result.skipped.append(task.title)
            continue
        payload: dict = {"title": task.title, "body": _issue_body(task, spec_link)}
        if label:
            payload["labels"] = [label]
        try:
            created = _request(
                f"{API_ROOT}/repos/{owner}/{name}/issues",
                token,
                data=json.dumps(payload).encode(),
                method="POST",
            )
            result.created.append(
                f"#{created['number']} {task.id}: {task.title}  {created['html_url']}"
            )
            seen.add(task.title)  # guard against duplicate titles within this batch
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            result.errors.append(f"{task.id} — HTTP {exc.code}: {detail}")
    return result
