"""OpenAI Codex adapter -> AGENTS.md."""

from monolith.adapters.base import Adapter


class CodexAdapter(Adapter):
    key = "codex"
    label = "OpenAI Codex"
    target_path = "AGENTS.md"

    def intro(self):
        return (
            "Codex agent: follow these token-efficiency rules for all output "
            "in this repository unless instructed otherwise."
        )
