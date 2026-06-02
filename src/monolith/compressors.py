"""Command-aware (semantic) output compressors.

Generic ``shrink`` is content-agnostic, so it can't tell signal from noise — 196
distinct ``PASSED`` lines look like 196 unique lines to it. The big wins (rtk's
~90%) come from *understanding the command*: for a test run you keep only the
failures and the summary; for a linter you keep only the diagnostics; for
``git status`` you drop the "(use …)" hint chatter.

This module maps a command (its argv) to a specialised compressor. ``run`` uses
it; if no compressor matches, it falls back to generic ``shrink``. Because
``monolith run`` saves full output to a tee file on failure, these filters can
be aggressive without losing recoverability.

Each compressor is ``(argv, text) -> str``. Adding one is a matcher + a function
registered in ``_REGISTRY``.
"""

from __future__ import annotations

import os
import re
from collections import OrderedDict
from typing import Callable, List, Optional, Sequence, Tuple

from monolith.shrink import DEFAULT_LEVEL, shrink

Compressor = Callable[[Sequence[str], str], str]
Matcher = Callable[[Sequence[str]], bool]


def _dedupe(lines: List[str]) -> str:
    """Join lines, dropping exact duplicates while preserving order."""
    return "\n".join(OrderedDict.fromkeys(lines))


# --- test runners -------------------------------------------------------

_TEST_TOKENS = {"pytest", "py.test", "jest", "vitest", "rspec", "unittest", "mocha"}
_TEST_KEEP = re.compile(
    r"\b(FAIL|FAILED|FAILURES|ERROR|Error|Traceback|panic:)\b"
    r"|^\s*[E>]\s"
    r"|^_{3,}"
    r"|\b\d+\s+(failed|error|errors|passed|skipped)\b"
    r"|^(ok|FAIL)\b"
)


def _is_test(argv: Sequence[str]) -> bool:
    joined = " ".join(argv)
    if any(tok in _TEST_TOKENS for tok in argv):
        return True
    if re.search(r"\b(go|cargo)\s+test\b", joined):
        return True
    if re.search(r"\b(npm|yarn|pnpm)\s+(run\s+)?test\b", joined):
        return True
    if re.search(r"\bpython3?\s+-m\s+(pytest|unittest)\b", joined):
        return True
    return False


def _compress_test(argv: Sequence[str], text: str) -> str:
    lines = text.splitlines()
    kept = [ln for ln in lines if _TEST_KEEP.search(ln)]
    if not kept:
        kept = [ln for ln in lines if ln.strip()][-3:]  # all green -> tail summary
    return _dedupe(kept)


# --- linters / type-checkers -------------------------------------------

_LINT_TOKENS = {
    "eslint", "tsc", "ruff", "flake8", "pylint", "mypy", "golangci-lint",
    "stylelint", "biome",
}
_LINT_KEEP = re.compile(
    r"^\S+\.\w+$"                       # eslint per-file header (path on its own line)
    r"|^\s*\d+:\d+\b"                   # eslint "  12:5  error ..."
    r"|^\S+[:(]\d+([:,]\d+)?[):]"       # file:line[:col]: or file(line,col):
    r"|\berror\b|\bwarning\b"           # tsc/ruff messages
    r"|\b\d+\s+(error|warning|problem)s?\b"  # summary counts
)


def _is_lint(argv: Sequence[str]) -> bool:
    if any(tok in _LINT_TOKENS for tok in argv):
        return True
    return bool(re.search(r"\b(npm|yarn|pnpm)\s+(run\s+)?lint\b", " ".join(argv)))


def _compress_lint(argv: Sequence[str], text: str) -> str:
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()]
    kept = [ln for ln in lines if _LINT_KEEP.search(ln)]
    if not kept:
        kept = lines[-2:]  # e.g. "All files pass linting." / "0 problems"
    return _dedupe(kept)


# --- git status ---------------------------------------------------------

_GIT_HINT = re.compile(r"^\s*\(use ")


def _is_git_status(argv: Sequence[str]) -> bool:
    return "git" in argv and "status" in argv


def _compress_git_status(argv: Sequence[str], text: str) -> str:
    # Drop the "(use git add …)" hint lines and blank lines; keep branch info,
    # section headers, and the actual changed/untracked paths.
    kept = [
        ln.rstrip()
        for ln in text.splitlines()
        if ln.strip() and not _GIT_HINT.search(ln)
    ]
    return "\n".join(kept)


# --- grep / find --------------------------------------------------------

_GREP_CMDS = {"grep", "egrep", "fgrep", "rg", "ag"}
_FIND_CMDS = {"find", "fd"}


def _is_grepfind(argv: Sequence[str]) -> bool:
    return bool(argv) and os.path.basename(argv[0]) in (_GREP_CMDS | _FIND_CMDS)


def _compress_grepfind(argv: Sequence[str], text: str) -> str:
    """Group results to cut repeated prefixes.

    grep: group matches under each file (drop the repeated ``file:`` prefix).
    find/fd: group paths by directory. Never expands — if grouping wouldn't be
    smaller (e.g. single-file ``grep -n`` output, or tiny results), the original
    de-duplicated text is returned.
    """
    cmd = os.path.basename(argv[0])
    lines = [ln for ln in text.splitlines() if ln.strip()]
    passthrough = _dedupe(lines)
    groups: "OrderedDict[str, List[str]]" = OrderedDict()

    if cmd in _FIND_CMDS:
        for ln in lines:
            groups.setdefault(os.path.dirname(ln) or ".", []).append(os.path.basename(ln))
        grouped = "\n".join(
            f"{d}/ ({len(items)}): {', '.join(items)}" for d, items in groups.items()
        )
    else:
        # grep "file:rest" — but ignore a numeric prefix (single-file `-n` output
        # is "line:rest", which has no filename to group by).
        grouped_any = False
        for ln in lines:
            parts = ln.split(":", 1)
            if len(parts) == 2 and not parts[0].isdigit():
                groups.setdefault(parts[0], []).append(parts[1])
                grouped_any = True
            else:
                groups.setdefault("", []).append(ln)
        if not grouped_any:
            return passthrough
        out: List[str] = []
        for f, matches in groups.items():
            out.append(f"{f} ({len(matches)}):" if f else "")
            out.extend(f"  {m}" for m in matches)
        grouped = "\n".join(ln for ln in out if ln != "" or True)

    # Don't expand: only use the grouped form if it's actually smaller.
    return grouped if len(grouped) < len(passthrough) else passthrough


# --- registry -----------------------------------------------------------

# (name, matcher, compressor) — order matters; matchers are specific.
_REGISTRY: List[Tuple[str, Matcher, Compressor]] = [
    ("test", _is_test, _compress_test),
    ("lint", _is_lint, _compress_lint),
    ("git-status", _is_git_status, _compress_git_status),
    ("grep/find", _is_grepfind, _compress_grepfind),
]


def pick(argv: Sequence[str]) -> Optional[Tuple[str, Compressor]]:
    """Return ``(name, compressor)`` for ``argv``, or None if none match."""
    for name, matcher, compressor in _REGISTRY:
        if matcher(argv):
            return name, compressor
    return None


def compress_for(argv: Sequence[str], text: str, level: str = DEFAULT_LEVEL) -> Tuple[str, str]:
    """Compress ``text`` for ``argv``. Returns ``(compressed, kind)``.

    Uses a semantic compressor when one matches and yields non-empty output;
    otherwise falls back to generic ``shrink`` (kind ``"generic"``).
    """
    chosen = pick(argv)
    if chosen is not None:
        name, compressor = chosen
        out = compressor(argv, text).strip("\n")
        if out:
            return out, name
    return shrink(text, level).text, "generic"
