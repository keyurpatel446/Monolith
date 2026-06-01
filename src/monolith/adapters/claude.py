"""Claude Code adapter -> CLAUDE.md."""

from monolith.adapters.base import Adapter


class ClaudeAdapter(Adapter):
    key = "claude"
    label = "Claude Code"
    target_path = "CLAUDE.md"

    def intro(self):
        return (
            "Claude Code: these project rules reduce token usage. Honour them "
            "in every response unless the user says otherwise."
        )
