# Monolith Roadmap

Monolith unifies four ideas — token efficiency, dense output, task management,
and resource discovery — into one cross-agent tool for Claude Code, OpenAI
Codex, and GitHub Copilot. This document is the living plan.

## Vision

> Author your AI-workflow rules and assets **once**; let Monolith deliver them
> in the native format every agent understands.

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
- Next (v0.2): build-tool compressors and transparent shell-hook wrapping.

## v0.2.0 (planned)

Post-1.0-readiness work, roughly in priority order:

- **Richer tasks** — cross-file/existing-task dependencies in `scan` (reference
  tasks by id, not just same-batch slugs); `task` subcommands to add/remove/edit
  and reorder; show blocked tasks in `tasks`.
- **More `scan` tag types** — `@monolith:ignore` (exclude a file from `shrink`),
  `@monolith:todo` aliasing `task`, and a `--strip` option to remove tags after
  applying.
- **Hub depth** — more curated resources, an `--update` flag to refresh
  installed assets, and an optional signed/remote manifest for community assets.
- **Measurement** — per-tier benchmark corpora so `bench`/`stats` report a
  measured number per tier, not just `full`.
- **MCP hardening** — validate the stdio server against real MCP clients; add an
  `apply`/`tasks` read tool alongside `shrink`.
- **More command-aware compression** — build-tool compressors
  (webpack/next/cargo build, docker) and transparent agent shell-hooks so
  commands are wrapped without typing `monolith run`. (Test/lint/git/grep/find
  compressors shipped in 0.1.6–0.1.7.)
- **Distribution & brand** — first PyPI release via Trusted Publishing (see
  `docs/PUBLISHING.md`), a recorded demo GIF in the README, and a
  social-preview image (1280×640: 🧱 logo + tagline + before/after numbers).
- **Docs site** — publish `docs/` via GitHub Pages and set it as the repo
  website.

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
