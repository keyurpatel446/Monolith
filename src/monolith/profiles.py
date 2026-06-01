"""Compression profiles.

A profile selects which canonical rules to emit and sets the overall tone
line. Intensity rises from `lite` -> `full` -> `ultra`.

`projected_output_reduction` is an ESTIMATE of how much agent OUTPUT shrinks
under the profile, expressed as a (low, high) fraction. The ranges are drawn
from the upstream benchmarks Monolith builds on (claude-token-efficient and
caveman, which report ~60-65% at their most aggressive settings). They are
projections, not guarantees, and `monolith stats` always labels them as such.
"""

from monolith.rules import RULES

PROFILES = {
    "lite": {
        "description": "Gentle: strip conversational filler only. Safe default for any task.",
        "tone": "Be concise and skip conversational filler.",
        "rule_ids": [
            "no_openers",
            "no_closers",
            "no_restate",
            "no_repeat_apology",
        ],
        "projected_output_reduction": (0.25, 0.35),
    },
    "full": {
        "description": "Default: filler removal plus dense formatting and no over-engineering.",
        "tone": "Answer directly and densely. Optimize for the fewest tokens that fully convey the answer.",
        "rule_ids": [
            "no_openers",
            "no_closers",
            "no_restate",
            "lead_with_answer",
            "no_unsolicited_summary",
            "dense_format",
            "no_code_narration",
            "minimal_comments",
            "no_overengineering",
            "no_sycophancy",
            "no_repeat_apology",
        ],
        "projected_output_reduction": (0.55, 0.65),
    },
    "ultra": {
        "description": "Aggressive: telegraphic, bullet-first output. Best for high-volume automation.",
        "tone": "Respond in the fewest tokens possible. Telegraphic style, bullets over prose, no restatement, no narration.",
        "rule_ids": list(RULES.keys()),  # every rule
        "projected_output_reduction": (0.60, 0.70),
    },
}

DEFAULT_PROFILE = "full"


def get_profile(name):
    """Return the profile dict for `name`, or None if unknown."""
    return PROFILES.get(name)


def profile_names():
    """Return profile names ordered from least to most aggressive."""
    return ["lite", "full", "ultra"]
