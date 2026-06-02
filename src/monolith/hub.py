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
    """Standard cross-agent install paths for a named asset (all 7 agents)."""
    return {
        "claude":   os.path.join(".claude",   "commands",        f"{name}.{ext}"),
        "codex":    os.path.join(".codex",    "prompts",         f"{name}.{ext}"),
        "copilot":  os.path.join(".github",   "prompts",         f"{name}.prompt.{ext}"),
        "cursor":   os.path.join(".cursor",   "rules",           f"{name}.mdc"),
        "windsurf": os.path.join(".windsurf", "rules",           f"{name}.{ext}"),
        "gemini":   os.path.join(".gemini",   "commands",        f"{name}.{ext}"),
        "aider":    os.path.join(".aider",    "instructions",    f"{name}.{ext}"),
    }


CATALOG: List[Resource] = [
    # -- SDD workflow commands -----------------------------------------------
    Resource(
        id="monolith.constitution",
        kind="command",
        summary="Establish project governance principles and definition of done.",
        targets=_paths("monolith.constitution"),
        body=(
            "# monolith.constitution\n\n"
            "Create or update the project constitution at `.monolith/memory/constitution.md`.\n\n"
            "Steps:\n"
            "1. Read the existing constitution if one exists.\n"
            "2. Ask the user three questions:\n"
            "   - What problem does this project solve and for whom?\n"
            "   - What are the 3–7 non-negotiable engineering principles?\n"
            "   - What is the definition of done for a task?\n"
            "3. Write or update `.monolith/memory/constitution.md` with their answers.\n"
            "4. Keep it under one page — this file is read on every task.\n\n"
            "Stop after writing. Do NOT start any implementation.\n"
        ),
    ),
    Resource(
        id="monolith.specify",
        kind="command",
        summary="Define functional requirements and user stories for a feature.",
        targets=_paths("monolith.specify"),
        body=(
            "# monolith.specify\n\n"
            "Create `specs/<feature>/spec.md` for the feature the user names.\n\n"
            "Steps:\n"
            "1. Ask: what is the feature name? (or infer from context)\n"
            "2. Read `.monolith/memory/constitution.md` if it exists.\n"
            "3. Read any existing `specs/<feature>/spec.md`.\n"
            "4. Fill in or update the spec with all of:\n"
            "   - Problem Statement (one paragraph)\n"
            "   - Goals (bullet list — what must be true when done)\n"
            "   - Non-Goals (what we are NOT building)\n"
            "   - User Stories (As a <role>, I want <action> so that <outcome>)\n"
            "   - Functional Requirements (numbered, specific, testable)\n"
            "   - Acceptance Criteria (checkbox list)\n"
            "   - Open Questions (anything unresolved)\n"
            "5. Stop. Do NOT plan or implement.\n"
        ),
    ),
    Resource(
        id="monolith.clarify",
        kind="command",
        summary="Surface and resolve ambiguities in a spec before planning.",
        targets=_paths("monolith.clarify"),
        body=(
            "# monolith.clarify\n\n"
            "Read the feature spec and surface every ambiguity that would block a correct plan.\n\n"
            "Steps:\n"
            "1. Ask: which feature? (or infer from context)\n"
            "2. Read `specs/<feature>/spec.md`.\n"
            "3. List every open question, ambiguity, or underspecified requirement.\n"
            "   Format: `Q1: <question>` — one per line, no filler.\n"
            "4. Wait for the user to answer each question.\n"
            "5. Update `specs/<feature>/spec.md` with the resolved answers.\n"
            "6. Confirm: 'Spec updated. Ready to plan.'\n\n"
            "Do NOT start planning until all blockers are resolved.\n"
        ),
    ),
    Resource(
        id="monolith.analyze",
        kind="command",
        summary="Validate cross-artifact consistency: spec ↔ plan ↔ tasks.",
        targets=_paths("monolith.analyze"),
        body=(
            "# monolith.analyze\n\n"
            "Check that spec, plan, and tasks are internally consistent for a feature.\n\n"
            "Steps:\n"
            "1. Ask: which feature? (or infer from context)\n"
            "2. Read `specs/<feature>/spec.md`, `plan.md`, `tasks.md`.\n"
            "3. For each requirement in spec.md — is it addressed in plan.md?\n"
            "4. For each plan component — does a task exist for it?\n"
            "5. For each acceptance criterion — is there a task that satisfies it?\n"
            "6. Report findings in three groups:\n"
            "   COVERED:  requirement → plan section → task id\n"
            "   GAP:      requirement with no plan or task coverage\n"
            "   ORPHAN:   tasks or plan sections with no spec backing\n"
            "7. If gaps exist, ask the user whether to fix spec, plan, or tasks.\n"
        ),
    ),
    Resource(
        id="monolith.checklist",
        kind="command",
        summary="Generate a quality gate checklist before shipping a feature.",
        targets=_paths("monolith.checklist"),
        body=(
            "# monolith.checklist\n\n"
            "Generate a quality checklist and confirm the feature is ready to ship.\n\n"
            "Steps:\n"
            "1. Ask: which feature? (or infer from context)\n"
            "2. Read `specs/<feature>/spec.md` and `plan.md`.\n"
            "3. Generate a checklist with four sections:\n"
            "   Spec compliance   — one checkbox per acceptance criterion from spec.md.\n"
            "   Implementation    — tests, lint, type-check, no TODOs.\n"
            "   Cross-artifact    — spec ↔ plan ↔ tasks consistent.\n"
            "   Review            — PR description, reviewer sign-off, CHANGELOG.\n"
            "4. Print the checklist. Work through each unchecked item with the user.\n"
            "5. Only declare 'Ready to ship' when every box is checked.\n"
        ),
    ),
    Resource(
        id="monolith.implement",
        kind="command",
        summary="Execute tasks from the spec in dependency order.",
        targets=_paths("monolith.implement"),
        body=(
            "# monolith.implement\n\n"
            "Implement the feature by executing its tasks in dependency order.\n\n"
            "Pre-flight (read ALL of these before writing any code):\n"
            "- `specs/<feature>/spec.md` — requirements and acceptance criteria.\n"
            "- `specs/<feature>/plan.md` — architecture and component design.\n"
            "- `specs/<feature>/tasks.md` or `TASKS.md` — ordered task list.\n"
            "- `.monolith/memory/constitution.md` — non-negotiable principles.\n\n"
            "Execution rules:\n"
            "- Work tasks in dependency order (`@after:` deps must be done first).\n"
            "- Mark each task `doing` before starting, `done` when tests pass.\n"
            "- Run `monolith run -- <test-cmd>` after each task to catch regressions.\n"
            "- If a task is blocked or unclear, stop and ask — do not guess.\n"
            "- After all tasks: run `monolith analyze <feature>` to confirm alignment.\n"
        ),
    ),
    # -- Utility commands ----------------------------------------------------
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
