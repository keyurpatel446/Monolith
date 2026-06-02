# Analysis

Pre-1.0 analysis backing the decision of when to declare a stable release.

- [benchmarks.md](benchmarks.md) — measured per-command token reduction + method.
- [competitors.md](competitors.md) — vs rtk, caveman, token-efficient, spec-kit.
- [stability.md](stability.md) — code audit + 1.0 readiness checklist (blockers).
- [discoverability.md](discoverability.md) — why we're not on Google + the plan.

**Headline conclusions**
- Strongest, proven wins: test output (~98%) and repetitive logs (~93%).
- Known weak spot: the lint compressor (~1%) needs grouping — a 1.0 blocker.
- We are **not** 1.0-ready yet; see `stability.md` for the path.
- Discoverability is capped by the generic name "monolith"; win on *phrases* +
  PyPI + backlinks (see `discoverability.md`).
