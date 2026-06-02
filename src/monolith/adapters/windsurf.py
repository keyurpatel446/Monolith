"""Windsurf compiler -> ``.windsurfrules`` (project-level AI instructions)."""

from __future__ import annotations

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class WindsurfCompiler(Compiler):
    key = "windsurf"
    label = "Windsurf"
    target_path = ".windsurfrules"

    def preamble(self) -> str:
        return (
            "Windsurf: apply these rules to reduce token usage in every AI "
            "response in this project unless the user says otherwise."
        )
