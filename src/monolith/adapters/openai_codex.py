"""OpenAI Codex compiler -> ``AGENTS.md`` (the shared agent-instructions file)."""

from __future__ import annotations

import os

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class OpenAICodexCompiler(Compiler):
    key = "codex"
    label = "OpenAI Codex"
    target_path = "AGENTS.md"
    command_dir = os.path.join(".codex", "prompts")

    def preamble(self) -> str:
        return (
            "Codex agent: follow these token-efficiency rules for all output "
            "in this repository unless instructed otherwise."
        )
