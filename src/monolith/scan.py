"""Scan a repository for inline ``@monolith:`` tags and act on them.

You annotate your code or notes in context, and Monolith collects the tags and
folds them into its stores:

* ``@monolith:task <title> [{#slug}] [@after:slug,...]`` -> a task in the task
  tree (and ``TASKS.md``). Same ``{#slug}`` / ``@after:`` grammar as PRD parsing.
* ``@monolith:rule <text>`` -> a custom directive appended to ``extra_rules``.

The captured text runs to the end of the line; trailing comment closers
(``-->``, ``*/``) are trimmed. Scanning is a dry run unless ``--apply`` is given,
and applying is idempotent — tasks are de-duplicated by title, rules by text.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from typing import List, Tuple

from monolith.settings import extra_rules, load_settings, save_settings
from monolith.tasks import (
    Task,
    emit_tasks_md,
    extract_tags,
    load_tasks,
    save_tasks,
)

# The marker is assembled at runtime so this source file does not itself contain
# a literal tag that a scan of this repo would pick up as a real task/rule.
_MARK = "@" + "monolith:"
_TASK_RE = re.compile(re.escape(_MARK) + r"task\s+(.+)")
_RULE_RE = re.compile(re.escape(_MARK) + r"rule\s+(.+)")

# Directories never worth scanning.
_SKIP_DIRS = {
    ".git", ".monolith", ".hg", ".svn", "node_modules", ".venv", "venv", "env",
    "__pycache__", "dist", "build", ".idea", ".vscode", ".mypy_cache",
    ".pytest_cache", ".eggs",
}
# Skip files larger than this (likely binary/generated).
_MAX_BYTES = 1_000_000


def _clean(text: str) -> str:
    """Trim trailing comment closers and whitespace from captured tag text."""
    text = text.strip()
    for closer in ("-->", "*/", "#}", "}}"):
        if text.endswith(closer):
            text = text[: -len(closer)].strip()
    return text


@dataclass
class Found:
    """Raw tag text discovered during a scan."""

    tasks: List[str] = field(default_factory=list)  # task titles (with tags)
    rules: List[str] = field(default_factory=list)  # rule texts

    def total(self) -> int:
        return len(self.tasks) + len(self.rules)


def scan_text(text: str) -> Found:
    """Find ``@monolith:`` tags in a single string."""
    found = Found()
    for line in text.splitlines():
        task = _TASK_RE.search(line)
        if task:
            found.tasks.append(_clean(task.group(1)))
            continue
        rule = _RULE_RE.search(line)
        if rule:
            found.rules.append(_clean(rule.group(1)))
    return found


def scan_repo(root: str = ".") -> Found:
    """Walk ``root`` and collect tags from every readable text file."""
    found = Found()
    for dirpath, dirnames, filenames in os.walk(root):
        # Prune skip dirs in place so os.walk doesn't descend into them.
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            try:
                if os.path.getsize(path) > _MAX_BYTES:
                    continue
                with open(path, "r", encoding="utf-8") as handle:
                    text = handle.read()
            except (OSError, UnicodeDecodeError):
                continue  # unreadable or binary -> skip
            file_found = scan_text(text)
            found.tasks.extend(file_found.tasks)
            found.rules.extend(file_found.rules)
    return found


def apply_found(found: Found, root: str = ".") -> Tuple[List[str], List[str]]:
    """Merge discovered tags into the task store and settings.

    Returns ``(added_task_ids, added_rules)``. Idempotent: tasks already present
    (by title) and rules already present (by text) are skipped.
    """
    added_tasks: List[str] = []
    added_rules: List[str] = []

    # --- tasks ---
    if found.tasks:
        tasks = load_tasks(root)
        existing_titles = {t.title for t in tasks}
        # Continue numbering after the current highest T<n>.
        next_n = 1 + max(
            (int(t.id[1:]) for t in tasks if t.id[1:].isdigit()), default=0
        )
        # Resolve @after slugs declared within this scan batch.
        slug_to_id: dict[str, str] = {}
        pending: List[Tuple[str, List[str]]] = []  # (task_id, dep_slugs)

        for raw in found.tasks:
            title, slug, after = extract_tags(raw)
            if not title or title in existing_titles:
                continue
            task_id = f"T{next_n}"
            next_n += 1
            existing_titles.add(title)
            tasks.append(Task(id=task_id, title=title, level=1))
            added_tasks.append(task_id)
            if slug:
                slug_to_id[slug] = task_id
            if after:
                pending.append((task_id, after))

        by_id = {t.id: t for t in tasks}
        for task_id, dep_slugs in pending:
            by_id[task_id].deps = [slug_to_id[s] for s in dep_slugs if s in slug_to_id]

        if added_tasks:
            save_tasks(tasks, root)
            emit_tasks_md(tasks, root)

    # --- rules ---
    if found.rules:
        settings = load_settings(root)
        rules = extra_rules(settings)
        for text in found.rules:
            if text and text not in rules:
                rules.append(text)
                added_rules.append(text)
        if added_rules:
            settings["extra_rules"] = rules
            save_settings(settings, root)

    return added_tasks, added_rules
