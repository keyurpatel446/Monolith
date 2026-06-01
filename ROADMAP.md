# Monolith Roadmap

Monolith unifies four ideas — token efficiency, dense output, task management,
and resource discovery — into one cross-agent tool for Claude Code, OpenAI
Codex, and GitHub Copilot. This document is the living plan.

## Vision

> Author your AI-workflow rules and assets **once**; let Monolith deliver them
> in the native format every agent understands.

## Source projects and what we take from each

| Source | What Monolith adopts | Phase |
|--------|----------------------|-------|
| [claude-token-efficient](https://github.com/drona23/claude-token-efficient) | Filler-removal instruction rules | 1 (done) |
| [caveman](https://github.com/JuliusBrussee/caveman) | Compression profiles, stats, MCP output shrinking | 1–2, 5 |
| [claude-task-master](https://github.com/eyaltoledano/claude-task-master) | PRD → task breakdown, dependency tracking | 3 |
| [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) | Curated, installable resource catalog | 4 |

## Phases

### Phase 0 — Scaffold ✅
- Python package layout, CLI entry point, license, `.gitignore`.
- README, this roadmap, per-agent docs.

### Phase 1 — Token efficiency (MVP) ✅
- Canonical directive catalog (`directives.py`) + `lite`/`full`/`ultra`
  compression tiers (`compression.py`).
- Self-registering compilers emitting `CLAUDE.md`, `AGENTS.md`,
  `.github/copilot-instructions.md`.
- Idempotent, marker-bounded writes (single-pass regex) that preserve user
  content.
- Commands: `init`, `apply`, `tier`, `stats`, `doctor`.
- Unit tests for the compilers and the console.

### Phase 2 — Stats & benchmarks
- Real before/after token measurement, not just projections.
- A benchmark harness with sample prompts to validate per-profile reduction.
- `monolith stats` reads recorded runs from `.monolith/stats.json`.
- Custom rule management from the CLI (`monolith rules add/remove/list`).

### Phase 3 — Task management
- `monolith plan <prd-file>`: parse a requirements doc into a task tree.
- Dependency tracking and status (`todo` / `doing` / `done`).
- Emit tasks into each agent's conventions (e.g. a `TASKS.md` the agent reads).
- Agent-agnostic task store under `.monolith/tasks/`.

### Phase 4 — Resource hub
- Curated catalog of skills, slash-commands, hooks, and prompts.
- `monolith hub search/install <name>` placing assets in the right agent path.
- Versioned, signed manifest so installs are reproducible.

### Phase 5 — Runtime compression (MCP)
- Optional middleware that shrinks tool-call outputs at runtime (caveman-style),
  for agents that support MCP.
- Opt-in per project; measured against the stats harness.

## Design principles

1. **Author once, compile everywhere.** One source of truth per concern.
2. **Idempotent & non-destructive.** Never clobber user-authored content.
3. **Honest numbers.** Label projections vs. measurements.
4. **Few dependencies.** Phase 1 is stdlib-only; add deps only when they earn it.
5. **Agent-agnostic core, thin adapters.** New agents = a new small adapter.

## Adding a new agent

Create a `Compiler` subclass in `src/monolith/adapters/`, set `key`, `label`,
`target_path`, and override `preamble()`, then decorate it with `@register`.
Add the module to the import list at the bottom of `adapters/__init__.py`. The
base `Compiler` handles idempotent rendering and writes — no other wiring.
