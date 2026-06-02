"""Command-aware (semantic) output compressors.

Generic ``shrink`` is content-agnostic, so it can't tell signal from noise — 196
distinct ``PASSED`` lines look like 196 unique lines to it. The big wins (rtk's
~90%) come from *understanding the command*: for a test run you keep only the
failures and the summary and discard everything green.

This module maps a command (its argv) to a specialised compressor. ``run`` uses
it; if no compressor matches, it falls back to generic ``shrink``. Because
``monolith run`` saves the full output to a tee file on failure, these filters
can be aggressive without losing recoverability.

More compressors (linters, builds, grep/find, git) are planned; each is just a
matcher + a filter function registered below.
"""

from __future__ import annotations

import re
from typing import Callable, List, Optional, Sequence, Tuple

from monolith.shrink import DEFAULT_LEVEL, shrink

# --- test runners -------------------------------------------------------

_TEST_TOKENS = {"pytest", "py.test", "jest", "vitest", "rspec", "unittest", "mocha"}

# Lines worth keeping from a test run: failures, errors, tracebacks, assertion
# detail, failure banners, and count summaries.
_TEST_KEEP = re.compile(
    r"\b(FAIL|FAILED|FAILURES|ERROR|Error|Traceback|panic:)\b"
    r"|^\s*[E>]\s"                       # pytest assertion / error detail lines
    r"|^_{3,}"                           # pytest failure banner "____ test ____"
    r"|\b\d+\s+(failed|error|errors|passed|skipped)\b"  # summary counts
    r"|^(ok|FAIL)\b"                     # go test verdicts
)


def _is_test(argv: Sequence[str]) -> bool:
    joined = " ".join(argv)
    if any(tok in _TEST_TOKENS for tok in argv):
        return True
    # `go test`, `cargo test`, `npm/yarn/pnpm test`, `python -m pytest/unittest`
    if re.search(r"\b(go|cargo)\s+test\b", joined):
        return True
    if re.search(r"\b(npm|yarn|pnpm)\s+(run\s+)?test\b", joined):
        return True
    if re.search(r"\bpython3?\s+-m\s+(pytest|unittest)\b", joined):
        return True
    return False


def _compress_test(text: str) -> str:
    """Keep only failure detail and summary lines from a test run."""
    lines = text.splitlines()
    kept = [ln for ln in lines if _TEST_KEEP.search(ln)]
    if not kept:
        # All green: keep just the tail summary so the agent sees the result.
        tail = [ln for ln in lines if ln.strip()][-3:]
        kept = tail
    # Collapse exact duplicates while preserving order.
    return "\n".join(dict.fromkeys(kept))


# --- registry -----------------------------------------------------------

# (name, matcher, compressor)
_REGISTRY: List[Tuple[str, Callable[[Sequence[str]], bool], Callable[[str], str]]] = [
    ("test", _is_test, _compress_test),
]


def pick(argv: Sequence[str]) -> Optional[Tuple[str, Callable[[str], str]]]:
    """Return ``(name, compressor)`` for ``argv``, or None if none match."""
    for name, matcher, compressor in _REGISTRY:
        if matcher(argv):
            return name, compressor
    return None


def compress_for(argv: Sequence[str], text: str, level: str = DEFAULT_LEVEL) -> Tuple[str, str]:
    """Compress ``text`` for ``argv``. Returns ``(compressed, kind)``.

    Uses a semantic compressor when one matches and yields non-empty output;
    otherwise falls back to generic ``shrink`` at ``level`` (kind ``"generic"``).
    """
    chosen = pick(argv)
    if chosen is not None:
        name, compressor = chosen
        out = compressor(text).strip("\n")
        if out:
            return out, name
    return shrink(text, level).text, "generic"
