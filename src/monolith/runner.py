"""Run a command and compress its output (inspired by rtk).

This wraps an external command, captures its combined output, and compresses it
with :mod:`monolith.shrink` so far fewer tokens reach the agent's context. Two
features beyond plain ``shrink`` make it useful in real agent loops:

* **Failure recovery (tee).** When the command exits non-zero, the *full*,
  uncompressed output is written to ``.monolith/tee/`` and a pointer is appended,
  so the agent can read the details without re-running the command.
* **Savings ledger.** Each run records before/after token counts to
  ``.monolith/gain.json`` so ``monolith gain`` can report cumulative savings.

Security: the command is executed with ``shell=False`` (argument list, no shell
interpolation), so there is no shell-injection surface. It runs exactly the
command you pass after ``--``.
"""

from __future__ import annotations

import json
import os
import subprocess
import time
from dataclasses import dataclass
from typing import List, Sequence

from monolith.compressors import compress_for
from monolith.shrink import DEFAULT_LEVEL
from monolith.tokens import count_tokens

TEE_DIR = os.path.join(".monolith", "tee")
GAIN_FILE = os.path.join(".monolith", "gain.json")


@dataclass
class RunResult:
    """Outcome of a wrapped command run."""

    returncode: int
    output: str          # compressed combined stdout+stderr
    before_tokens: int
    after_tokens: int
    tee_path: str | None  # full output on failure, else None
    kind: str = "generic"  # which compressor was used (e.g. "test")

    @property
    def reduction(self) -> float:
        if self.before_tokens == 0:
            return 0.0
        return 1.0 - (self.after_tokens / self.before_tokens)


def _save_tee(raw: str, root: str, argv: Sequence[str]) -> str:
    """Write full output to a timestamped file under .monolith/tee/."""
    os.makedirs(os.path.join(root, TEE_DIR), exist_ok=True)
    slug = "-".join(argv)[:40].replace("/", "_").replace(" ", "_") or "cmd"
    name = f"{int(time.time())}-{slug}.log"
    path = os.path.join(root, TEE_DIR, name)
    with open(path, "w", encoding="utf-8") as handle:
        handle.write(raw)
    return path


def _record_gain(before: int, after: int, root: str) -> None:
    """Add this run's token counts to the cumulative ledger."""
    path = os.path.join(root, GAIN_FILE)
    ledger = {"runs": 0, "before_tokens": 0, "after_tokens": 0}
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                ledger.update(json.load(handle))
        except (json.JSONDecodeError, OSError):
            pass
    ledger["runs"] += 1
    ledger["before_tokens"] += before
    ledger["after_tokens"] += after
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(ledger, handle, indent=2)
        handle.write("\n")


def load_gain(root: str = ".") -> dict | None:
    """Return the cumulative savings ledger, or None if nothing recorded."""
    path = os.path.join(root, GAIN_FILE)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError):
        return None


def run_command(
    argv: Sequence[str],
    root: str = ".",
    level: str = DEFAULT_LEVEL,
    timeout: float | None = None,
) -> RunResult:
    """Execute ``argv``, compress its output, tee on failure, record savings."""
    proc = subprocess.run(  # noqa: S603 - shell=False, argv list; no injection
        list(argv),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    raw = proc.stdout
    if proc.stderr:
        raw = (raw + "\n" + proc.stderr) if raw else proc.stderr

    # Command-aware compression when we recognise the command; else generic.
    compressed, kind = compress_for(argv, raw, level)
    before_tokens = count_tokens(raw)
    after_tokens = count_tokens(compressed)

    tee_path = _save_tee(raw, root, argv) if proc.returncode != 0 else None
    _record_gain(before_tokens, after_tokens, root)

    return RunResult(
        returncode=proc.returncode,
        output=compressed,
        before_tokens=before_tokens,
        after_tokens=after_tokens,
        tee_path=tee_path,
        kind=kind,
    )
