"""Cursor compiler -> ``.cursorrules`` (project-level AI instructions)."""

from __future__ import annotations

import os

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class CursorCompiler(Compiler):
    key = "cursor"
    label = "Cursor"
    target_path = ".cursorrules"
    command_dir = os.path.join(".cursor", "rules")
    command_ext = "mdc"

    def preamble(self) -> str:
        return (
            "Cursor: apply these rules to reduce token usage in every AI "
            "response in this project unless the user says otherwise."
        )
