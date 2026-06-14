"""Runtime output compression — shrink verbose tool output safely.

Where the directives ask the *model* to be terse, this module compresses
already-produced text (logs, command output, JSON dumps) deterministically and
*without a model*. Every transformation is either lossless or marks what it
removed, so the result stays trustworthy:

* ``lite``  — strip trailing whitespace; collapse 3+ blank lines to one.
* ``full``  — also strip ANSI colour codes and fold runs of identical lines
              into ``<line>  (xN)``.
* ``ultra`` — also clip very long outputs to a head + tail with an explicit
              ``... (omitted N lines) ...`` marker in the middle.

It is deterministic and offline; Phase 5 wires it into an (experimental) MCP
server in ``mcp_server.py``.

Note: a shrink *level* (runtime text compression, here) is a different axis from
a compression *tier* (the directive set asked of the model, in
``compression.py``). They unfortunately share the names ``lite``/``full``/
``ultra`` for user familiarity — do not conflate them.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from monolith.tokens import count_tokens, safe_reduction

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_BLANK_RUN_RE = re.compile(r"\n{3,}")

# ultra: keep this many lines at the head and tail when clipping.
_ULTRA_HEAD = 40
_ULTRA_TAIL = 20
_ULTRA_TRIGGER = _ULTRA_HEAD + _ULTRA_TAIL + 10  # only clip clearly-long output


@dataclass(frozen=True)
class _LevelSpec:
    """Which transforms a level enables. Adding a level = add a row, not code."""

    strip_ansi: bool
    fold_identical: bool
    clip_middle: bool


# Registry of levels, ordered least -> most aggressive. ``shrink`` reads this
# table rather than branching on level names, so a new level is a new entry.
_LEVEL_SPECS: dict[str, _LevelSpec] = {
    "lite":  _LevelSpec(strip_ansi=False, fold_identical=False, clip_middle=False),
    "full":  _LevelSpec(strip_ansi=True,  fold_identical=True,  clip_middle=False),
    "ultra": _LevelSpec(strip_ansi=True,  fold_identical=True,  clip_middle=True),
}
LEVELS = tuple(_LEVEL_SPECS)
DEFAULT_LEVEL = "full"


@dataclass
class ShrinkResult:
    """Compressed text plus before/after token counts."""

    text: str
    before_tokens: int
    after_tokens: int

    @property
    def reduction(self) -> float:
        """Fractional token reduction (0..1)."""
        return safe_reduction(self.before_tokens, self.after_tokens)


def _fold_identical_lines(lines: List[str]) -> List[str]:
    """Collapse consecutive identical non-empty lines into ``line  (xN)``.

    Empty lines are passed through untouched so the blank-run collapser (not
    this fold) handles them — otherwise repeated blanks would turn into a
    meaningless ``(xN)`` marker.
    """
    folded: List[str] = []
    run_value: str | None = None
    run_count = 0

    def flush() -> None:
        if run_value is None:
            return
        folded.append(f"{run_value}  (x{run_count})" if run_count > 1 else run_value)

    for line in lines:
        if line == "":
            flush()
            run_value, run_count = None, 0
            folded.append(line)
            continue
        if line == run_value:
            run_count += 1
        else:
            flush()
            run_value, run_count = line, 1
    flush()
    return folded


def _clip_middle(lines: List[str]) -> List[str]:
    """Keep head + tail of a long list, marking the omitted middle."""
    if len(lines) <= _ULTRA_TRIGGER:
        return lines
    omitted = len(lines) - _ULTRA_HEAD - _ULTRA_TAIL
    return (
        lines[:_ULTRA_HEAD]
        + [f"... (omitted {omitted} lines) ..."]
        + lines[-_ULTRA_TAIL:]
    )


def shrink(text: str, level: str = DEFAULT_LEVEL) -> ShrinkResult:
    """Compress ``text`` at the given ``level`` and report token savings."""
    spec = _LEVEL_SPECS.get(level)
    if spec is None:
        raise ValueError(f"unknown level: {level!r} (choose from {', '.join(LEVELS)})")

    before = count_tokens(text)
    out = text

    if spec.strip_ansi:
        out = _ANSI_RE.sub("", out)

    # Strip trailing whitespace on every line (all levels).
    lines = [line.rstrip() for line in out.split("\n")]

    if spec.fold_identical:
        lines = _fold_identical_lines(lines)
    if spec.clip_middle:
        lines = _clip_middle(lines)

    out = "\n".join(lines)
    # Collapse runs of blank lines (all levels).
    out = _BLANK_RUN_RE.sub("\n\n", out).strip("\n")

    return ShrinkResult(text=out, before_tokens=before, after_tokens=count_tokens(out))
