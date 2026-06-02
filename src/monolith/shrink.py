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
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List

from monolith.tokens import count_tokens

LEVELS = ("lite", "full", "ultra")
DEFAULT_LEVEL = "full"

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
_BLANK_RUN_RE = re.compile(r"\n{3,}")

# ultra: keep this many lines at the head and tail when clipping.
_ULTRA_HEAD = 40
_ULTRA_TAIL = 20
_ULTRA_TRIGGER = _ULTRA_HEAD + _ULTRA_TAIL + 10  # only clip clearly-long output


@dataclass
class ShrinkResult:
    """Compressed text plus before/after token counts."""

    text: str
    before_tokens: int
    after_tokens: int

    @property
    def reduction(self) -> float:
        """Fractional token reduction (0..1)."""
        if self.before_tokens == 0:
            return 0.0
        return 1.0 - (self.after_tokens / self.before_tokens)


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
    if level not in LEVELS:
        raise ValueError(f"unknown level: {level!r} (choose from {', '.join(LEVELS)})")

    before = count_tokens(text)
    out = text

    if level in ("full", "ultra"):
        out = _ANSI_RE.sub("", out)

    # Strip trailing whitespace on every line (all levels).
    lines = [line.rstrip() for line in out.split("\n")]

    if level in ("full", "ultra"):
        lines = _fold_identical_lines(lines)
    if level == "ultra":
        lines = _clip_middle(lines)

    out = "\n".join(lines)
    # Collapse runs of blank lines (all levels).
    out = _BLANK_RUN_RE.sub("\n\n", out).strip("\n")

    return ShrinkResult(text=out, before_tokens=before, after_tokens=count_tokens(out))
