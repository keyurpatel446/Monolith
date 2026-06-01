"""Compression tiers — how aggressively to compress agent output.

A *tier* bundles three things:

1. ``directive_ids`` — which directives from :mod:`monolith.directives` to emit.
2. ``tone`` — a one-line stylistic instruction placed above the bullet list.
3. ``projected_reduction`` — an *estimated* (low, high) fraction by which agent
   OUTPUT shrinks under this tier.

The reduction ranges are projections taken from the published benchmarks of the
projects Monolith draws on (which report ~60-65% at their most aggressive
settings). They are deliberately surfaced as ranges and always labelled as
estimates by ``monolith stats`` so nothing here is mistaken for a measurement.

Tiers are immutable dataclasses, looked up through a small frozen registry, so
callers cannot accidentally mutate shared state.
"""

from __future__ import annotations

from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping, Tuple

from monolith.directives import ordered_ids


@dataclass(frozen=True)
class Tier:
    """An immutable description of one compression level."""

    name: str
    description: str
    tone: str
    #: directive ids to emit, in the order given
    directive_ids: Tuple[str, ...]
    #: estimated (low, high) fractional reduction of OUTPUT tokens
    projected_reduction: Tuple[float, float]

    def reduction_percent(self) -> Tuple[int, int]:
        """Return the projected reduction as integer percentages ``(low, high)``."""
        low, high = self.projected_reduction
        return int(low * 100), int(high * 100)


# ``full`` reuses ``lite``'s directives plus a few more; ``ultra`` emits every
# directive in catalog order. Building the tuples by composition keeps the
# definitions DRY and guarantees a sensible, stable emission order.
_LITE_IDS: Tuple[str, ...] = (
    "no_openers",
    "no_closers",
    "no_restate",
    "no_repeat_apology",
)
_FULL_IDS: Tuple[str, ...] = _LITE_IDS + (
    "lead_with_answer",
    "no_unsolicited_summary",
    "dense_format",
    "no_code_narration",
    "minimal_comments",
    "no_overengineering",
    "no_sycophancy",
)

# Registry of tiers, ordered least -> most aggressive. Wrapped in a read-only
# MappingProxyType so the public table cannot be mutated by callers.
_TIERS: Mapping[str, Tier] = MappingProxyType(
    {
        "lite": Tier(
            name="lite",
            description="Gentle: strip conversational filler only. Safe for any task.",
            tone="Be concise and skip conversational filler.",
            directive_ids=_LITE_IDS,
            projected_reduction=(0.25, 0.35),
        ),
        "full": Tier(
            name="full",
            description="Default: filler removal plus dense formatting and no over-engineering.",
            tone="Answer directly and densely. Use the fewest tokens that fully convey the answer.",
            directive_ids=_FULL_IDS,
            projected_reduction=(0.55, 0.65),
        ),
        "ultra": Tier(
            name="ultra",
            description="Aggressive: telegraphic, bullet-first output for high-volume automation.",
            tone="Respond in the fewest tokens possible: telegraphic, bullets over prose, no narration.",
            directive_ids=ordered_ids(),  # every directive, in catalog order
            projected_reduction=(0.60, 0.70),
        ),
    }
)

DEFAULT_TIER = "full"


def get_tier(name: str) -> Tier | None:
    """Return the :class:`Tier` named ``name`` (``None`` if unknown)."""
    return _TIERS.get(name)


def tier_names() -> Tuple[str, ...]:
    """Return tier names ordered from least to most aggressive."""
    return tuple(_TIERS)
