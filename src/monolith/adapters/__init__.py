"""Agent adapters: compile the canonical ruleset into native config files."""

from monolith.adapters.claude import ClaudeAdapter
from monolith.adapters.codex import CodexAdapter
from monolith.adapters.copilot import CopilotAdapter

# key -> adapter class. The key is what users pass to `--agent`.
ADAPTERS = {
    "claude": ClaudeAdapter,
    "codex": CodexAdapter,
    "copilot": CopilotAdapter,
}


def get_adapter(key):
    """Instantiate the adapter for `key`, or return None if unknown."""
    cls = ADAPTERS.get(key)
    return cls() if cls else None


def all_keys():
    return list(ADAPTERS.keys())
