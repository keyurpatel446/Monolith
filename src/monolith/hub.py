"""Resource hub — a curated, installable catalog of agent assets.

This is Monolith's take on the "awesome-claude-code" idea, made cross-agent and
installable. The catalog ships *inside* the package (no network needed, fully
reproducible). Each :class:`Resource` carries its file body and a per-agent
install path, so ``monolith hub install <id>`` drops the asset into the right
place for Claude Code, Codex, and/or Copilot.

The built-in assets are deliberately small, token-frugal prompts/commands that
fit Monolith's philosophy. Adding more is just appending to :data:`CATALOG`.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Dict, List, Sequence


@dataclass(frozen=True)
class Resource:
    """One installable asset."""

    id: str
    kind: str          # "command" | "prompt" | "hook"
    summary: str
    #: agent key -> install path (relative to project root)
    targets: Dict[str, str] = field(default_factory=dict)
    #: the file contents written on install
    body: str = ""

    def agents(self) -> List[str]:
        return list(self.targets)


# Per-agent path conventions reused by the catalog below.
def _paths(name: str, ext: str = "md") -> Dict[str, str]:
    """Standard cross-agent install paths for a named asset."""
    return {
        "claude": os.path.join(".claude", "commands", f"{name}.{ext}"),
        "codex": os.path.join(".codex", "prompts", f"{name}.{ext}"),
        "copilot": os.path.join(".github", "prompts", f"{name}.prompt.{ext}"),
    }


CATALOG: List[Resource] = [
    Resource(
        id="concise-commit",
        kind="command",
        summary="Write a one-line Conventional Commit message for staged changes.",
        targets=_paths("concise-commit"),
        body=(
            "# concise-commit\n\n"
            "Generate a single-line Conventional Commit message for the staged "
            "diff.\n\n"
            "Rules:\n"
            "- Format: `type(scope): summary` (<= 72 chars).\n"
            "- No body, no bullet list, no trailing notes.\n"
            "- Imperative mood; describe the change, not the process.\n"
        ),
    ),
    Resource(
        id="terse-review",
        kind="command",
        summary="Review a diff for correctness only, one finding per line.",
        targets=_paths("terse-review"),
        body=(
            "# terse-review\n\n"
            "Review the current diff for correctness bugs only.\n\n"
            "Output:\n"
            "- One finding per line: `file:line - issue`.\n"
            "- No praise, no summary, no style nitpicks unless they cause bugs.\n"
            "- If nothing is wrong, reply exactly: `No correctness issues found.`\n"
        ),
    ),
    Resource(
        id="explain-terse",
        kind="prompt",
        summary="Explain a piece of code in at most five bullet points.",
        targets=_paths("explain-terse"),
        body=(
            "# explain-terse\n\n"
            "Explain the selected code in at most five bullets.\n\n"
            "- Lead with what it does in one line.\n"
            "- Then only the non-obvious parts (edge cases, gotchas).\n"
            "- No restatement of the code line by line.\n"
        ),
    ),
    Resource(
        id="test-plan",
        kind="prompt",
        summary="List the test cases worth writing for the selected code.",
        targets=_paths("test-plan"),
        body=(
            "# test-plan\n\n"
            "List the test cases worth writing for the selected code.\n\n"
            "- One line per case: input/condition -> expected result.\n"
            "- Cover happy path, boundaries, and error cases.\n"
            "- Flag anything currently untestable and why. No test code yet.\n"
        ),
    ),
    Resource(
        id="tighten-prose",
        kind="prompt",
        summary="Rewrite the selected text to be shorter without losing meaning.",
        targets=_paths("tighten-prose"),
        body=(
            "# tighten-prose\n\n"
            "Rewrite the selected text to use fewer tokens while preserving all\n"
            "information.\n\n"
            "- Cut filler, hedging, and repetition; keep technical accuracy.\n"
            "- Preserve code, names, and numbers exactly.\n"
            "- Return only the rewrite.\n"
        ),
    ),
    Resource(
        id="explain-diff",
        kind="command",
        summary="Summarize what the current diff changes, one bullet per change.",
        targets=_paths("explain-diff"),
        body=(
            "# explain-diff\n\n"
            "Summarize what the current diff changes.\n\n"
            "- One bullet per logical change: `path — what changed and why`.\n"
            "- Call out behaviour changes and anything risky.\n"
            "- No restating unchanged code; no praise.\n"
        ),
    ),
]


def find(resource_id: str) -> Resource | None:
    """Return the catalog resource with ``resource_id`` (``None`` if absent)."""
    for resource in CATALOG:
        if resource.id == resource_id:
            return resource
    return None


def search(query: str) -> List[Resource]:
    """Return catalog resources whose id/summary/kind matches ``query``."""
    q = query.lower()
    return [
        r for r in CATALOG
        if q in r.id.lower() or q in r.summary.lower() or q in r.kind.lower()
    ]


def install(resource: Resource, root: str, agents: Sequence[str]) -> List[str]:
    """Write ``resource`` into the chosen agents' paths. Returns paths written.

    Agents without a defined target for this resource are skipped.
    """
    written: List[str] = []
    for agent in agents:
        rel = resource.targets.get(agent)
        if rel is None:
            continue
        path = os.path.join(root, rel)
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write(resource.body)
        written.append(path)
    return written
