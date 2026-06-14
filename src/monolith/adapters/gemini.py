"""Gemini CLI compiler -> ``GEMINI.md`` (project memory file)."""

from __future__ import annotations

import os

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class GeminiCompiler(Compiler):
    key = "gemini"
    label = "Gemini CLI"
    target_path = "GEMINI.md"
    command_dir = os.path.join(".gemini", "commands")

    def preamble(self) -> str:
        return (
            "Gemini: apply these token-efficiency rules to every response "
            "in this project unless the user instructs otherwise."
        )
