"""Project-local Monolith configuration (`.monolith/config.json`).

The config records which profile is active, which agents to target, and any
user-authored custom rules to append to every generated block.
"""

import json
import os

from monolith.profiles import DEFAULT_PROFILE

CONFIG_DIR = ".monolith"
CONFIG_FILE = "config.json"


def config_path(root="."):
    return os.path.join(root, CONFIG_DIR, CONFIG_FILE)


def default_config(agents=None):
    return {
        "profile": DEFAULT_PROFILE,
        "agents": agents if agents is not None else ["claude", "codex", "copilot"],
        "custom_rules": [],
    }


def load_config(root="."):
    """Load config from `root`, or return defaults if none exists."""
    path = config_path(root)
    if not os.path.exists(path):
        return default_config()
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    # Fill any missing keys so older config files keep working.
    base = default_config()
    base.update(data)
    return base


def save_config(config, root="."):
    """Persist config under `root/.monolith/config.json`."""
    os.makedirs(os.path.join(root, CONFIG_DIR), exist_ok=True)
    path = config_path(root)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(config, fh, indent=2)
        fh.write("\n")
    return path


def config_exists(root="."):
    return os.path.exists(config_path(root))
