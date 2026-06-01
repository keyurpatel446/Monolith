"""GitHub Copilot adapter -> .github/copilot-instructions.md."""

import os

from monolith.adapters.base import Adapter


class CopilotAdapter(Adapter):
    key = "copilot"
    label = "GitHub Copilot"
    target_path = os.path.join(".github", "copilot-instructions.md")

    def intro(self):
        return (
            "GitHub Copilot: apply these custom instructions to keep responses "
            "concise and low-token across this repository."
        )
