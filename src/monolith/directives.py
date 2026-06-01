"""Directive catalog — the single source of truth for token-saving rules.

A *directive* is one imperative instruction (e.g. "do not greet") that we ask
an agent to follow. Directives are defined here exactly once and are later
selected by compression tiers (see ``compression.py``) and rendered into each
agent's native config by the compilers (see ``adapters/``).

Design notes
------------
* Each directive carries a **stable id**. Tiers reference directives by id, so
  rewording a directive's text never breaks a tier definition.
* Directives are stored in an ``OrderedDict``-like plain ``dict`` (insertion
  order is guaranteed in Python 3.7+). The declaration order *is* the canonical
  emission order, so the generated config reads top-to-bottom as written here.
* Text is kept to a single sentence so the rendered block stays dense — which
  is, after all, the whole point of the tool.
"""

from __future__ import annotations

from typing import Dict, FrozenSet

# ---------------------------------------------------------------------------
# Canonical directives: id -> imperative instruction.
# Ordering here defines the order they appear in generated config files.
# ---------------------------------------------------------------------------
_DIRECTIVES: Dict[str, str] = {
    "no_openers": (
        "Do not open with greetings, acknowledgements, or filler such as "
        '"Sure!", "Great question!", or "Certainly".'
    ),
    "no_closers": (
        "Do not end with pleasantries or offers of further help such as "
        '"I hope this helps!" or "Let me know if you need anything else."'
    ),
    "no_restate": "Do not restate or paraphrase the request before answering.",
    "lead_with_answer": (
        "Lead with the answer or the result; put caveats and context after, "
        "and only if they matter."
    ),
    "no_unsolicited_summary": (
        "Do not append a summary of what you just did unless explicitly asked."
    ),
    "dense_format": (
        "Prefer dense formats — tables, lists, and code blocks — over prose "
        "when they convey the same information in fewer tokens."
    ),
    "no_code_narration": (
        "Do not narrate or re-explain code you just wrote unless asked; let "
        "the code and concise comments speak."
    ),
    "minimal_comments": (
        "Write only comments that add non-obvious information; skip comments "
        "that merely restate the code."
    ),
    "no_overengineering": (
        "Implement what was asked. Do not add speculative abstractions, "
        "options, or defensive code that was not requested."
    ),
    "no_sycophancy": (
        "Do not agree reflexively. If something is wrong or a better option "
        "exists, say so plainly and briefly."
    ),
    "no_repeat_apology": (
        "Correct mistakes in one short sentence; do not apologize repeatedly."
    ),
    "terse_prose": (
        "Keep prose telegraphic: short sentences, no emphatic adverbs, no "
        "marketing tone. Cut any word that does not change the meaning."
    ),
    "bullets_over_paragraphs": (
        "Default to bullet points over paragraphs; use at most one short "
        "paragraph per idea."
    ),
}

#: A line that must accompany every generated block so user intent is never
#: silently overridden by these rules.
OVERRIDE_NOTE = "User instructions in the conversation always override these rules."


def directive_text(directive_id: str) -> str | None:
    """Return the instruction text for ``directive_id`` (``None`` if unknown)."""
    return _DIRECTIVES.get(directive_id)


def all_directive_ids() -> FrozenSet[str]:
    """Return every known directive id as an immutable set.

    Frozen so callers cannot mutate the catalog by accident.
    """
    return frozenset(_DIRECTIVES)


def ordered_ids() -> tuple[str, ...]:
    """Return all directive ids in their canonical (declaration) order."""
    return tuple(_DIRECTIVES)
