"""Monolith — cross-agent token-efficiency layer for AI coding assistants.

One canonical ruleset, compiled into the native config each agent reads:
Claude Code (CLAUDE.md), OpenAI Codex (AGENTS.md), GitHub Copilot
(.github/copilot-instructions.md).
"""

from importlib import metadata as _metadata

# Single-source the version from the installed package metadata (pyproject.toml)
# so it can never drift. Fall back to a literal only when running from a source
# tree that isn't installed.
try:
    __version__ = _metadata.version("monolith-ai")
except _metadata.PackageNotFoundError:  # pragma: no cover - source-tree fallback
    __version__ = "1.0.1"
