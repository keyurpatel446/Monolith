"""Head-to-head comparison harness (Monolith vs caveman vs token-efficient).

Honesty first
-------------
Monolith cannot run a live model, and it certainly cannot run *another* tool's
model. So a fully controlled "same prompts through every tool" benchmark is out
of reach offline. What this harness reports is split into two clearly labelled
parts:

1. **Input overhead — objective, measured here.** Every approach injects some
   instruction text (rules) into the agent's context, which costs input tokens
   on every request. We count those tokens with the same tokenizer for all
   approaches, so this column is a true apples-to-apples measurement.

2. **Output reduction — mixed.** For Monolith we report the figure *measured*
   by :mod:`monolith.benchmark` on its sample corpus. For the other tools we
   report their own *published* figures, with a citation. These are not
   something Monolith measured, and the harness says so.

The point is to be defensible, not flattering: the numbers come with their
provenance attached.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from monolith.adapters import get_compiler
from monolith.benchmark import run_benchmark
from monolith.tokens import count_tokens, counter_name


@dataclass(frozen=True)
class Approach:
    """One tool/configuration being compared."""

    key: str
    label: str
    #: instruction text the approach injects (used for the objective overhead)
    instruction: str
    #: published output-reduction (low, high) fractions, or None if measured
    published_reduction: Optional[Tuple[float, float]]
    #: where the published figure comes from (empty for measured approaches)
    citation: str


# Representative instruction text for each competitor, paraphrased from their
# public documentation (not verbatim copies). Used only to estimate the input
# overhead each approach adds; phrasing differences of a few tokens do not
# change the conclusion.
_TOKEN_EFFICIENT_RULES = (
    "Skip greetings and closing pleasantries. Do not restate the question. "
    "Avoid unnecessary elaboration, rewrites, and sycophantic agreement. "
    "Answer directly and stop."
)
_CAVEMAN_RULES = (
    "Compress output aggressively. Use the fewest tokens that preserve meaning. "
    "Telegraphic style, no filler, no narration. why use many token when few "
    "token do trick."
)


def _approaches() -> List[Approach]:
    """Build the comparison set. Monolith's instruction is its real block."""
    monolith_block = get_compiler("claude").render("full")
    return [
        Approach(
            key="normal",
            label="Normal (no tool)",
            instruction="",
            published_reduction=(0.0, 0.0),
            citation="baseline",
        ),
        Approach(
            key="token-efficient",
            label="claude-token-efficient",
            instruction=_TOKEN_EFFICIENT_RULES,
            published_reduction=(0.60, 0.63),
            citation="project README (~63%)",
        ),
        Approach(
            key="caveman",
            label="caveman",
            instruction=_CAVEMAN_RULES,
            published_reduction=(0.60, 0.65),
            citation="project README (~65% avg, up to ~76%)",
        ),
        Approach(
            key="monolith",
            label="Monolith (full tier)",
            instruction=monolith_block,
            published_reduction=None,  # measured below
            citation="",
        ),
    ]


@dataclass
class ApproachResult:
    """Comparison numbers for one approach."""

    label: str
    input_overhead_tokens: int
    output_reduction: float  # fraction 0..1
    measured: bool           # True if we measured it, False if published
    citation: str


@dataclass
class ComparisonReport:
    results: List[ApproachResult]
    counter: str


def run_comparison() -> ComparisonReport:
    """Compute input overhead (measured) and output reduction (measured/cited)."""
    # Measure Monolith's output reduction on the shared corpus once.
    measured_reduction = run_benchmark().reduction

    results: List[ApproachResult] = []
    for approach in _approaches():
        overhead = count_tokens(approach.instruction) if approach.instruction else 0
        if approach.published_reduction is None:
            reduction, measured, citation = measured_reduction, True, "measured on corpus"
        else:
            low, high = approach.published_reduction
            reduction, measured, citation = (low + high) / 2, False, approach.citation
        results.append(
            ApproachResult(
                label=approach.label,
                input_overhead_tokens=overhead,
                output_reduction=reduction,
                measured=measured,
                citation=citation,
            )
        )
    return ComparisonReport(results=results, counter=counter_name())
