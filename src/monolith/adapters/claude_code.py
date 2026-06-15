"""Claude Code compiler -> ``CLAUDE.md`` (project memory)."""

from __future__ import annotations

import os

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class ClaudeCodeCompiler(Compiler):
    key = "claude"
    label = "Claude Code"
    target_path = "CLAUDE.md"
    command_dir = os.path.join(".claude", "commands")

    def preamble(self) -> str:
        return (
            "Claude Code: these project rules reduce token usage. Honour them "
            "in every response unless the user says otherwise."
        )
