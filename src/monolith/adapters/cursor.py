"""Cursor compiler -> ``.cursorrules`` (project-level AI instructions)."""

from __future__ import annotations

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class CursorCompiler(Compiler):
    key = "cursor"
    label = "Cursor"
    target_path = ".cursorrules"

    def preamble(self) -> str:
        return (
            "Cursor: apply these rules to reduce token usage in every AI "
            "response in this project unless the user says otherwise."
        )
