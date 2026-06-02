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
- **As of v0.2.0 Monolith ships the full SDD pipeline**: `constitution →
  specify → clarify → plan → analyze → tasks → implement` — matching spec-kit's
  methodology.
- Monolith's approach: CLI commands + installable slash commands, structured
  `specs/<feature>/` artifacts, offline structural analysis. Zero new
  dependencies.
- spec-kit still leads on template maturity, extensions/presets ecosystem, and
  community resources. Monolith's edge: cross-agent compilation, token
  compression, and runtime `shrink` — none of which spec-kit offers.

## Honest positioning

Monolith is **the only tool that unifies all four concerns** (token efficiency +
SDD workflow + task management + runtime compression) in one dependency-free
cross-agent CLI.

Remaining gaps vs specialists:
- **vs rtk**: not as broad at command compression (build tools, transparent
  shell hooks still pending).
- **vs caveman**: not as mature at agent-output compression (subagents, memory
  compression).
- **vs spec-kit**: templates less battle-tested; no extensions/presets ecosystem.

**Where to invest next (priority):**
1. SDD template quality — battle-test the spec/plan/tasks templates with real
   projects; add more opinionated examples.
2. Close the rtk gap on build tools and transparent shell hooks.
3. Strengthen measured evidence (benchmarks, real-world `gain` data).
4. Lean the marketing on *breadth + SDD + honesty + zero-deps cross-agent*.
