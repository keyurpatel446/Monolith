"""Project-local settings stored at ``.monolith/settings.json``.

The settings file records the user's choices for a project:

* ``tier``          — the active compression tier (``lite``/``full``/``ultra``).
* ``agents``        — which agents to target by default.
* ``extra_rules``   — custom directives appended verbatim to every block.

The on-disk format is forward-compatible: :func:`load_settings` overlays the
file onto a fresh default, so settings written by an older version that lack a
newer key keep working.
"""

from __future__ import annotations

import json
import os
from typing import List, Mapping, Sequence

from monolith.compression import DEFAULT_TIER

SETTINGS_DIR = ".monolith"
SETTINGS_FILE = "settings.json"


def settings_path(root: str = ".") -> str:
    """Return the absolute-ish path to the settings file under ``root``."""
    return os.path.join(root, SETTINGS_DIR, SETTINGS_FILE)


def default_settings(agents: Sequence[str] | None = None) -> dict:
    """Return a fresh settings dict, optionally pre-seeding the agent list."""
    return {
        "tier": DEFAULT_TIER,
        "agents": list(agents) if agents is not None else ["claude", "codex", "copilot"],
        "extra_rules": [],
    }


def settings_exist(root: str = ".") -> bool:
    """Return whether a settings file already exists under ``root``."""
    return os.path.exists(settings_path(root))


def load_settings(root: str = ".") -> dict:
    """Load settings from ``root``; fall back to defaults when absent.

    Missing keys are backfilled from :func:`default_settings` so callers can
    rely on every key being present.
    """
    path = settings_path(root)
    if not os.path.exists(path):
        return default_settings()
    with open(path, "r", encoding="utf-8") as handle:
        stored: Mapping = json.load(handle)
    merged = default_settings()
    merged.update(stored)
    return merged


def save_settings(settings: Mapping, root: str = ".") -> str:
    """Persist ``settings`` under ``root/.monolith/settings.json``.

    Returns the path written. Creates the ``.monolith`` directory if needed.
    """
    os.makedirs(os.path.join(root, SETTINGS_DIR), exist_ok=True)
    path = settings_path(root)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(settings, handle, indent=2)
        handle.write("\n")
    return path


def extra_rules(settings: Mapping) -> List[str]:
    """Return the custom directives from ``settings`` (always a list)."""
    return list(settings.get("extra_rules", []))
