"""Task management — parse a PRD into a task tree, track it, emit TASKS.md.

Monolith stays deterministic and offline: PRD parsing is a structural Markdown
read, not an LLM call. The conventions are intentionally small:

* Markdown headings (``#`` .. ``######``) and list items (``-``, ``*``, ``+``,
  or ``1.``) each become a task. Nesting (heading depth + list indentation)
  defines parent/child relationships.
* Optional inline tags let you wire up dependencies by a stable name you
  control:
    - ``{#slug}``      names the task ``slug`` (so others can depend on it).
    - ``@after:a,b``   marks the task as depending on tasks named ``a`` and ``b``.

Tasks are stored as JSON under ``.monolith/tasks/tasks.json`` (committable, so
the plan is shared with the team) and rendered to a root ``TASKS.md`` that the
coding agents read as ordinary project context.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Sequence, Tuple

#: Allowed task states, ordered from not-started to finished.
STATUSES: Tuple[str, ...] = ("todo", "doing", "done")
DEFAULT_STATUS = "todo"

TASKS_DIR = os.path.join(".monolith", "tasks")
TASKS_FILE = "tasks.json"
TASKS_MARKDOWN = "TASKS.md"

# Markdown line patterns.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*\S)\s*$")
_LIST_RE = re.compile(r"^(\s*)(?:[-*+]|\d+\.)\s+(.*\S)\s*$")
# Inline tags, stripped from the displayed title once parsed.
_NAME_RE = re.compile(r"\{#([\w-]+)\}")
_AFTER_RE = re.compile(r"@after:([\w,-]+)")

# How many spaces of list indentation count as one nesting level.
_INDENT_UNIT = 2


@dataclass
class Task:
    """A single unit of work in the plan."""

    id: str
    title: str
    level: int  # 1 = top level; larger = deeper in the tree
    parent: str | None = None
    status: str = DEFAULT_STATUS
    deps: List[str] = field(default_factory=list)  # ids this task depends on

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        return cls(
            id=data["id"],
            title=data["title"],
            level=int(data.get("level", 1)),
            parent=data.get("parent"),
            status=data.get("status", DEFAULT_STATUS),
            deps=list(data.get("deps", [])),
        )


# -- PRD parsing ---------------------------------------------------------

def _extract_tags(text: str) -> Tuple[str, str | None, List[str]]:
    """Pull ``{#name}`` and ``@after:`` tags out of ``text``.

    Returns ``(clean_title, name_or_None, after_names)``.
    """
    name = None
    after: List[str] = []

    name_match = _NAME_RE.search(text)
    if name_match:
        name = name_match.group(1)

    after_match = _AFTER_RE.search(text)
    if after_match:
        after = [part for part in after_match.group(1).split(",") if part]

    clean = _AFTER_RE.sub("", _NAME_RE.sub("", text))
    # Collapse the whitespace the removed tags may have left behind.
    clean = re.sub(r"\s{2,}", " ", clean).strip()
    return clean, name, after


def parse_prd(text: str) -> List[Task]:
    """Parse PRD/Markdown ``text`` into an ordered list of :class:`Task`.

    Dependencies declared via ``@after:`` are resolved to task ids; references
    that match no named task are dropped (the caller may surface a warning by
    diffing requested vs resolved, but parsing itself stays lenient).
    """
    tasks: List[Task] = []
    # Stack of (level, task_id) used to find the parent of the current task.
    stack: List[Tuple[int, str]] = []
    # Map user-chosen name -> generated id, and pending dep names per task id.
    name_to_id: Dict[str, str] = {}
    pending_after: Dict[str, List[str]] = {}
    counter = 0
    # Depth of the most recent heading; list items nest beneath it. Tracked
    # separately from the stack so sibling list items stay at the same level.
    heading_level = 0

    for raw in text.splitlines():
        heading = _HEADING_RE.match(raw)
        item = None if heading else _LIST_RE.match(raw)
        if not heading and not item:
            continue

        if heading:
            level = len(heading.group(1))
            heading_level = level
            title_src = heading.group(2)
        else:
            indent = len(item.group(1))
            # List items sit one level below the current heading, plus their
            # own indentation depth.
            level = heading_level + 1 + (indent // _INDENT_UNIT)
            title_src = item.group(2)

        title, name, after = _extract_tags(title_src)
        counter += 1
        task_id = f"T{counter}"

        # Parent = nearest item on the stack with a strictly smaller level.
        while stack and stack[-1][0] >= level:
            stack.pop()
        parent = stack[-1][1] if stack else None
        stack.append((level, task_id))

        if name:
            name_to_id[name] = task_id
        if after:
            pending_after[task_id] = after

        tasks.append(Task(id=task_id, title=title, level=level, parent=parent))

    # Second pass: resolve dependency names to ids now that all names are known.
    by_id = {t.id: t for t in tasks}
    for task_id, names in pending_after.items():
        resolved = [name_to_id[n] for n in names if n in name_to_id]
        by_id[task_id].deps = resolved

    return tasks


# -- persistence ---------------------------------------------------------

def tasks_path(root: str = ".") -> str:
    return os.path.join(root, TASKS_DIR, TASKS_FILE)


def tasks_exist(root: str = ".") -> bool:
    return os.path.exists(tasks_path(root))


def save_tasks(tasks: Sequence[Task], root: str = ".") -> str:
    """Persist tasks to ``.monolith/tasks/tasks.json``."""
    os.makedirs(os.path.join(root, TASKS_DIR), exist_ok=True)
    path = tasks_path(root)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump([t.to_dict() for t in tasks], handle, indent=2)
        handle.write("\n")
    return path


def load_tasks(root: str = ".") -> List[Task]:
    """Load tasks from the store (empty list if none saved)."""
    path = tasks_path(root)
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as handle:
        return [Task.from_dict(d) for d in json.load(handle)]


# -- mutation ------------------------------------------------------------

def find_task(tasks: Sequence[Task], task_id: str) -> Task | None:
    """Return the task with ``task_id`` (case-insensitive), or ``None``."""
    target = task_id.upper()
    for task in tasks:
        if task.id.upper() == target:
            return task
    return None


def set_status(tasks: Sequence[Task], task_id: str, status: str) -> Tuple[bool, str]:
    """Set a task's status. Returns ``(changed, message)``.

    Validates the status value and warns (without blocking) when a task is
    advanced while its dependencies are not yet ``done`` — the warning is part
    of the returned message.
    """
    if status not in STATUSES:
        return False, f"unknown status {status!r} (choose from {', '.join(STATUSES)})"

    task = find_task(tasks, task_id)
    if task is None:
        return False, f"no such task: {task_id}"

    by_id = {t.id: t for t in tasks}
    unmet = [
        dep for dep in task.deps
        if dep in by_id and by_id[dep].status != "done"
    ]

    task.status = status
    message = f"{task.id} -> {status}"
    if status in ("doing", "done") and unmet:
        message += f"  (warning: depends on unfinished {', '.join(unmet)})"
    return True, message


# -- rendering -----------------------------------------------------------

_STATUS_BOX = {"todo": "[ ]", "doing": "[~]", "done": "[x]"}


def _line_for(task: Task, indent: int) -> str:
    box = _STATUS_BOX.get(task.status, "[ ]")
    suffix = f"  (after {', '.join(task.deps)})" if task.deps else ""
    return f"{'  ' * indent}- {box} {task.id}: {task.title}{suffix}"


def render_tree_lines(tasks: Sequence[Task]) -> List[str]:
    """Return display lines for the CLI, indented by task level."""
    base = min((t.level for t in tasks), default=1)
    return [_line_for(t, t.level - base) for t in tasks]


def render_tasks_md(tasks: Sequence[Task]) -> str:
    """Render the full ``TASKS.md`` document agents read."""
    done = sum(1 for t in tasks if t.status == "done")
    header = [
        "<!-- Generated by Monolith. Edit tasks via `monolith task`/`monolith plan`. -->",
        "# Tasks",
        "",
        f"Progress: {done}/{len(tasks)} done.",
        "",
        "Legend: `[ ]` todo · `[~]` doing · `[x]` done.",
        "",
    ]
    body = render_tree_lines(tasks) if tasks else ["_No tasks yet._"]
    return "\n".join(header + body) + "\n"


def emit_tasks_md(tasks: Sequence[Task], root: str = ".") -> str:
    """Write ``TASKS.md`` at the project root and return its path."""
    path = os.path.join(root, TASKS_MARKDOWN)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(render_tasks_md(tasks))
    return path
