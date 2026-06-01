"""Benchmark harness — measure real token reduction on a sample corpus.

Monolith cannot run a live model, so it cannot measure the savings on *your*
prompts directly. What it *can* do is measure the reduction between matched
pairs of agent responses — a verbose "before" and a concise "after" of the
same answer — using the real token counter. The built-in :data:`CORPUS` is a
small set of such pairs written in the style the ``full`` tier targets.

``monolith bench`` runs this corpus, prints per-sample and aggregate measured
reduction, and records the result to ``.monolith/stats.json`` so ``monolith
stats`` can show a measured figure alongside the projected range.
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
from typing import List, Sequence, Tuple

from monolith.tokens import count_tokens, counter_name

STATS_DIR = ".monolith"
STATS_FILE = "stats.json"


@dataclass(frozen=True)
class Sample:
    """A matched verbose/concise pair conveying the same information."""

    name: str
    verbose: str
    concise: str


# A compact, representative corpus. Each pair says the same thing; the concise
# side simply drops the filler the directives target (openers, closers,
# restatement, narration, hedging).
CORPUS: Tuple[Sample, ...] = (
    Sample(
        name="explain-fix",
        verbose=(
            "Great question! I'd be happy to help you figure this out. So, the "
            "reason your function is returning None is actually because there's "
            "no explicit return statement at the end of the branch. What you'll "
            "want to do here is make sure you return the computed value. I hope "
            "this helps, and please let me know if you have any other questions!"
        ),
        concise="It returns None because that branch has no return. Return the computed value.",
    ),
    Sample(
        name="code-change",
        verbose=(
            "Sure thing! Let me walk you through what I'm going to do. First I "
            "will open the file, then I'll locate the relevant function, and "
            "after that I'll add the missing guard clause. Here is the change I "
            "made:\n\n    if not items:\n        return []\n\nSo, as you can see, "
            "what this does is handle the empty case before the loop runs. Hope "
            "that makes sense!"
        ),
        concise=(
            "Added a guard for the empty case:\n\n    if not items:\n        return []"
        ),
    ),
    Sample(
        name="recommendation",
        verbose=(
            "That's a really interesting question and there are a lot of ways to "
            "think about it. Honestly, both options could work depending on your "
            "needs. If I had to pick, I would probably lean towards using a set "
            "here, mainly because membership checks are faster, but a list would "
            "also be fine in many cases. Let me know what you think!"
        ),
        concise="Use a set: membership checks are O(1) vs O(n) for a list.",
    ),
    Sample(
        name="status-summary",
        verbose=(
            "Absolutely! Here's a summary of everything I just did for you in "
            "this session. I went ahead and updated the configuration file, then "
            "I ran the tests to make sure nothing was broken, and finally I "
            "committed the changes with a descriptive message. Everything is "
            "looking good now. Thanks for your patience!"
        ),
        concise="Updated config, ran tests (passing), committed.",
    ),
    Sample(
        name="error-answer",
        verbose=(
            "Oh no, I'm so sorry about that error! Let me take another look. "
            "Okay, so it seems like the issue is that the module isn't installed "
            "in your environment. To fix this, what you'll want to do is run the "
            "install command. I really apologize for the confusion earlier!"
        ),
        concise="The module isn't installed. Run `pip install <module>`.",
    ),
)


@dataclass
class SampleResult:
    """Per-sample measurement."""

    name: str
    verbose_tokens: int
    concise_tokens: int

    @property
    def reduction(self) -> float:
        """Fractional token reduction for this sample (0..1)."""
        if self.verbose_tokens == 0:
            return 0.0
        return 1.0 - (self.concise_tokens / self.verbose_tokens)


@dataclass
class BenchmarkReport:
    """Aggregate result of a benchmark run."""

    results: List[SampleResult]
    counter: str
    timestamp: float

    @property
    def baseline_tokens(self) -> int:
        return sum(r.verbose_tokens for r in self.results)

    @property
    def optimized_tokens(self) -> int:
        return sum(r.concise_tokens for r in self.results)

    @property
    def reduction(self) -> float:
        """Corpus-wide fractional reduction (weighted by token volume)."""
        if self.baseline_tokens == 0:
            return 0.0
        return 1.0 - (self.optimized_tokens / self.baseline_tokens)

    def to_dict(self) -> dict:
        """Serialise the headline numbers for ``.monolith/stats.json``."""
        return {
            "timestamp": self.timestamp,
            "samples": len(self.results),
            "baseline_tokens": self.baseline_tokens,
            "optimized_tokens": self.optimized_tokens,
            "reduction": round(self.reduction, 4),
            "counter": self.counter,
        }


def run_benchmark(corpus: Sequence[Sample] = CORPUS) -> BenchmarkReport:
    """Measure token reduction across ``corpus`` and return a report."""
    results = [
        SampleResult(
            name=sample.name,
            verbose_tokens=count_tokens(sample.verbose),
            concise_tokens=count_tokens(sample.concise),
        )
        for sample in corpus
    ]
    return BenchmarkReport(results=results, counter=counter_name(), timestamp=time.time())


# -- persistence ---------------------------------------------------------

def stats_path(root: str = ".") -> str:
    return os.path.join(root, STATS_DIR, STATS_FILE)


def save_report(report: BenchmarkReport, root: str = ".") -> str:
    """Write the latest benchmark headline to ``.monolith/stats.json``."""
    os.makedirs(os.path.join(root, STATS_DIR), exist_ok=True)
    path = stats_path(root)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump({"last_benchmark": report.to_dict()}, handle, indent=2)
        handle.write("\n")
    return path


def load_last_report(root: str = ".") -> dict | None:
    """Return the recorded ``last_benchmark`` dict, or ``None`` if absent."""
    path = stats_path(root)
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as handle:
            return json.load(handle).get("last_benchmark")
    except (json.JSONDecodeError, OSError):
        return None
