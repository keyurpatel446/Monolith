"""GitHub Copilot compiler -> ``.github/copilot-instructions.md``."""

from __future__ import annotations

import os

from monolith.adapters import register
from monolith.adapters.compiler import Compiler


@register
class GitHubCopilotCompiler(Compiler):
    key = "copilot"
    label = "GitHub Copilot"
    # os.path.join keeps the separator correct on every platform.
    target_path = os.path.join(".github", "copilot-instructions.md")

    def preamble(self) -> str:
        return (
            "GitHub Copilot: apply these custom instructions to keep responses "
            "concise and low-token across this repository."
        )
