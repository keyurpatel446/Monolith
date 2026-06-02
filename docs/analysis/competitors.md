# Competitor analysis

Where Monolith sits against the projects in the same space, and where to invest.

## Landscape

| Project | Core job | Lang | Stars (approx) | Overlap with Monolith |
|---------|----------|------|----------------|------------------------|
| **rtk** (Rust Token Killer) | Compress **command output** at runtime | Rust | growing | Direct — our `run`/`shrink` |
| **caveman** | Compress **agent output** (rules + MCP) | JS/Py | ~67k | Direct — our rules/tiers |
| **claude-token-efficient** | A drop-in token-saving `CLAUDE.md` | Markdown | small | Subset of our rules |
| **spec-kit** (GitHub) | Spec-driven dev workflow | Python | ~108k | Our `plan`/`tasks` (they're deeper) |

## Dimension-by-dimension

### Runtime output compression (vs rtk)
- **rtk leads on breadth**: ~100 command-specific compressors, transparent shell
  hooks, Rust speed.
- **Monolith now has the mechanism** (`run` + tee + `gain`) and semantic
  compressors for tests/lint/git/grep/find. Gaps: build-tool compressors,
  transparent hooks, and lint needs grouping (see benchmarks). Tests already
  match rtk (~90–98%).

### Agent-output rules (vs caveman / token-efficient)
- Comparable reduction (~60–80%). **Monolith's edge: cross-agent** (one ruleset →
  Claude Code + Codex + Copilot) and honest measured-vs-projected reporting.
- caveman leads on maturity, subagents, memory compression.

### Planning (vs spec-kit)
- spec-kit is a far deeper SDD workflow (constitution/specify/clarify/analyze).
- Monolith's `plan`/`tasks`/`scan` are lightweight and cross-agent; not trying to
  match spec-kit's depth.

## Honest positioning

Monolith is **the only one that unifies all three concerns** (rules + tasks +
runtime compression) in one dependency-free cross-agent CLI. It does **not** beat
any specialist in that specialist's lane:
- Not as broad as rtk at command compression.
- Not as mature as caveman at agent-output compression.
- Not as deep as spec-kit at planning.

**Where to invest (priority):**
1. Close the rtk gap on the *common* commands (lint grouping, build tools,
   shell-hooks) — highest user-visible value.
2. Strengthen measured evidence (benchmarks.md, real-world `gain` data).
3. Lean the marketing on *breadth + honesty + zero-deps cross-agent*, not on
   out-compressing any single tool.
