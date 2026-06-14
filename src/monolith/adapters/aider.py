"""Aider compiler -> ``CONVENTIONS.md`` (project conventions file).

Aider reads ``CONVENTIONS.md`` as project context when it is present.
Users can also pin it with ``--read CONVENTIONS.md`` in ``.aider.conf.yml``
for guaranteed inclusion on every session.
"""

from __future__ import annotations

import os

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class AiderCompiler(Compiler):
    key = "aider"
    label = "Aider"
    target_path = "CONVENTIONS.md"
    command_dir = os.path.join(".aider", "instructions")

    def preamble(self) -> str:
        return (
            "Aider: follow these project conventions to reduce token usage "
            "in every response unless the user says otherwise."
        )
