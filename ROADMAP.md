# Monolith Roadmap

Monolith unifies five ideas — token efficiency, dense output, spec-driven
development, task management, and resource discovery — into one cross-agent tool
for Claude Code, OpenAI Codex, and GitHub Copilot. This document is the living
plan.

## Vision

> Author your rules and specs **once**; let Monolith compile them into every
> agent's native format and guide the full path from idea to shipped code.

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

### Phase 2 — Stats & benchmarks ✅
- Real before/after token measurement via a benchmark corpus (`benchmark.py`).
- Token counter (`tokens.py`) using `tiktoken` when present, heuristic otherwise.
- `monolith bench` records measured reduction to `.monolith/stats.json`;
  `monolith stats` shows it next to the projected range.
- Custom rule management from the CLI: `monolith rules list/add/remove`.
- Unit tests for the harness, token counter, and rule commands.

### Phase 3 — Task management ✅
- `monolith plan <prd-file>`: parse a PRD/Markdown file into a task tree
  (`tasks.py`).
- Dependency tracking via `{#slug}` / `@after:slug` tags; status
  `todo`/`doing`/`done` with unmet-dependency warnings.
- Emits a root `TASKS.md` the agents read; agent-agnostic store under
  `.monolith/tasks/tasks.json`.
- `monolith tasks` (list) and `monolith task <id> --status` (update).
- Unit tests for parsing, nesting, dependencies, status, and rendering.

### Phase 3.5 — Inline tags ✅
- `monolith scan` (`scan.py`): walk the repo for `@monolith:task` and
  `@monolith:rule` tags and fold them into the task store / custom rules.
- Dry run by default; idempotent on `--apply`.

### Phase 4 — Resource hub ✅
- Curated, in-package catalog of cross-agent commands/prompts (`hub.py`).
- `monolith hub list/search/show/install`, placing assets in each agent's path
  (`.claude/commands/`, `.codex/prompts/`, `.github/prompts/`).
- Reproducible (assets ship with the package; no network needed).
- Future: signed/remote manifests for community-contributed assets.

### Phase 5 — Runtime compression (MCP) ✅ (experimental)
- `shrink.py`: deterministic, offline output compressor with lite/full/ultra
  levels (whitespace, ANSI strip, identical-line folding, long-output clipping).
- `monolith shrink` (file/stdin) and an experimental MCP server
  (`mcp_server.py`, `monolith mcp`) exposing `shrink` over stdio JSON-RPC.
- Handlers are unit-tested; the live stdio loop is marked experimental pending
  validation against more MCP clients.

### Phase 5.5 — Command wrapper ✅
- `monolith run -- <cmd>` (`runner.py`): run a command, compress its output,
  propagate its exit code, and on failure save full output to `.monolith/tee/`
  so the agent needn't re-run it.
- Command-aware compression (`compressors.py`): semantic compressors for test
  runners (~90%), linters/type-checkers, `git status`, and grep/find; generic
  fallback otherwise.
- `monolith gain`: cumulative token-savings ledger across `run` invocations.

### Phase 6 — Spec-Driven Development pipeline ✅ (v0.2.0)
- Full SDD workflow: `constitution → specify → clarify → plan → analyze →
  tasks → implement`, matching spec-kit's methodology offline with zero new
  dependencies.
- `workflow.py`: scaffolds `specs/<feature>/` with `spec.md`, `plan.md`,
  `data-model.md`, `contracts/`; `analyze_feature` (structural consistency
  check, OK/WARN/ERROR/INFO); `generate_checklist` (auto-checks existing
  artifacts).
- 4 new CLI commands: `constitution`, `specify`, `analyze`, `checklist`.
- 6 new hub resources installable as slash commands across all agents:
  `monolith.constitution`, `monolith.specify`, `monolith.clarify`,
  `monolith.analyze`, `monolith.checklist`, `monolith.implement`.
- All 74 existing tests pass unchanged.

### Phase 7 — Onboarding & 1.0 ✅ (v1.0.0)
- One-command setup: `monolith setup [--agent <agent>|all] [--tier]` runs
  `init` + `apply` + `doctor` in a single step.
- Hub bundles: `monolith hub install sdd` installs the whole SDD command set;
  `hub install` now defaults to the agents in `.monolith/settings.json`.
- `--agent` scoping on `init`/`doctor`; friendlier first-run guidance (bare
  `monolith` and a failing `doctor` on an unconfigured project both point at
  `monolith setup`).
- Fixed the documented Claude quickstart that previously ended in six `doctor`
  failures.
- **1.0.0 stability commitment**: the CLI surface (command names, flags, and
  on-disk layout under `.monolith/`) is now considered stable and will follow
  semantic versioning — breaking changes only in a future 2.0.

## Distribution

- **PyPI via Trusted Publishing** ✅ — every merge to `master` that bumps the
  version tags a release and publishes the wheel + sdist (OIDC, no stored
  token).
- **Demo GIF** — `scripts/demo.sh` drives the full flow; record with
  `asciinema rec -c "bash scripts/demo.sh"` then convert with `agg`.
- **Homebrew tap** (planned) — Monolith is dependency-free, so a
  `Language::Python::Virtualenv` formula is trivial; it needs a companion
  `homebrew-tap` repository to host `brew install keyurpatel446/tap/monolith`.
- **conda-forge** (planned) — submit a feedstock so `conda install monolith-ai`
  works for non-pip users.

## v0.3.0 (planned)

- **SDD depth** — battle-test spec/plan/tasks templates with real projects;
  add `monolith specify --all` shorthand; improve `analyze` with semantic
  heading-level coverage matching between spec and tasks.
- **Richer tasks** — cross-file/existing-task dependencies in `scan`; `task`
  subcommands to add/remove/edit; show blocked tasks in `tasks`.
- **More `scan` tag types** — `@monolith:ignore`, `@monolith:todo`, `--strip`.
- **Hub depth** — `--update` flag, optional signed/remote manifest for
  community assets.
- **MCP hardening** — validate the stdio server against real clients; add
  `apply`/`tasks` read tools alongside `shrink`.
- **More command-aware compression** — build-tool compressors (webpack/next/
  cargo build, docker) and transparent shell hooks.
- **Measurement** — per-tier benchmark corpora so `bench`/`stats` report a
  measured number for every tier.
- **Distribution & brand** — first PyPI release via Trusted Publishing, a
  recorded demo GIF in the README, and a social-preview image.
- **Docs site** — publish `docs/` via GitHub Pages.

## Design principles

1. **Author once, compile everywhere.** One source of truth per concern.
2. **Idempotent & non-destructive.** Never clobber user-authored content.
3. **Honest numbers.** Label projections vs. measurements.
4. **Few dependencies.** The core is stdlib-only; `tiktoken` is an optional
   extra (`[bench]`) that only sharpens measurement. Add deps only when earned.
5. **Agent-agnostic core, thin adapters.** New agents = a new small adapter.

## Adding a new agent

Create a `Compiler` subclass in `src/monolith/adapters/`, set `key`, `label`,
`target_path`, and override `preamble()`, then decorate it with `@register`.
Add the module to the import list at the bottom of `adapters/__init__.py`. The
base `Compiler` handles idempotent rendering and writes — no other wiring.
