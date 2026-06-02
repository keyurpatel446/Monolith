"""Agent compiler registry.

Compilers self-register via the :func:`register` decorator, so wiring up a new
agent is just "add a file + decorate the class" — no central list to edit. The
concrete compiler modules are imported at the bottom of this file to trigger
their registration on first import of the package.
"""

from __future__ import annotations

from typing import Dict, List, Type

from monolith.adapters.compiler import Compiler

# key -> compiler class. Populated by the @register decorator below.
_REGISTRY: Dict[str, Type[Compiler]] = {}


def register(cls: Type[Compiler]) -> Type[Compiler]:
    """Class decorator that records a compiler under its ``key``.

    Returns the class unchanged so it can be used as a normal decorator.
    """
    if not cls.key:
        raise ValueError(f"{cls.__name__} must define a non-empty `key`")
    _REGISTRY[cls.key] = cls
    return cls


def get_compiler(key: str) -> Compiler | None:
    """Instantiate the compiler registered under ``key`` (``None`` if unknown)."""
    cls = _REGISTRY.get(key)
    return cls() if cls else None


def all_keys() -> List[str]:
    """Return every registered agent key, in registration order."""
    return list(_REGISTRY)


# Import concrete compilers last so their @register decorators run. Listed
# explicitly (rather than auto-discovered) to keep import order deterministic.
from monolith.adapters import (  # noqa: E402,F401
    claude_code,
    openai_codex,
    github_copilot,
    cursor,
    windsurf,
    gemini,
    aider,
)
