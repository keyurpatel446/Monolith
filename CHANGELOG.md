# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.1] - 2026-06-15

### Changed
- `monolith tasks-to-issues` is now idempotent: it skips tasks whose title
  already exists as an open issue, so re-running no longer creates duplicates.

### Internal (architecture / SOLID)
- Extracted the GitHub Issues HTTP client out of the console into
  `monolith/issues.py` (was inline argparse logic).
- Extracted cross-artifact analysis + checklist generation into
  `monolith/analysis.py`; `analyze_feature` now returns structured
  `Finding`/`Severity` values instead of severity-prefixed strings.
- `monolith shrink` levels are now a data-driven registry (`_LEVEL_SPECS`)
  rather than `if level in (...)` branches — adding a level is a table entry.
- The agent roster is single-sourced from the compiler registry: hub install
  paths derive from each compiler's `hub_path`, removing the duplicate table
  in `hub.py`.
- Deduplicated the four copies of the `reduction` formula into
  `tokens.safe_reduction`.
- Hardened JSON loading: corrupt settings fall back to defaults; a corrupt task
  store raises a clear error instead of silently clobbering data.
- Promoted `tasks._extract_tags` to the public `extract_tags` (no more
  cross-module private import from `scan.py`).
- Fixed a dead always-true filter in the grep/find output compressor.

## [1.0.0] - 2026-06-12

First stable release. The CLI surface (command names, flags, and the on-disk
layout under `.monolith/`) is now considered stable and follows semantic
versioning — breaking changes only in a future 2.0.

### Added
- Friendlier first-run guidance: running bare `monolith` now points new users
  at `monolith setup`, and `monolith doctor` on an unconfigured project tells
  you to run `monolith setup` instead of `apply`.

### Changed
- `scripts/demo.sh` now showcases the one-command `monolith setup` flow and
  `monolith hub install sdd`.
- Documented the supported install paths (`pipx`, `uv`, `pip`) and recorded
  Homebrew/conda-forge as planned distribution channels in the roadmap.

### Notes
- Builds on the onboarding work from 0.2.2 (`monolith setup`, hub bundles,
  settings-scoped `hub install`).

## [0.2.2] - 2026-06-12

### Added
- **`monolith setup [--agent <agent>|all] [--tier <tier>]`** — one-shot
  onboarding that replaces the `init` + `apply` + `doctor` chain with a single
  command. `monolith setup --agent claude` sets up Claude Code end-to-end.
- **Hub bundles**: `monolith hub install sdd` installs all six SDD workflow
  commands at once (previously six separate `hub install` invocations).
  `monolith hub list` now shows available bundles.
- `monolith init --agent <agent>|all` — scope settings to one agent at init time.
- `monolith doctor --agent <agent>|all|config` — narrow or widen the check.

### Changed
- `monolith hub install` now defaults to the agents in `.monolith/settings.json`
  (when present) instead of writing config directories for all 7 agents.
  Pass `--agent all` for the old behaviour.

### Fixed
- The documented Claude quickstart no longer ended in failure: `monolith init`
  in a repo with no agent files targeted all 7 agents, so
  `apply --agent claude && doctor` reported six `FAIL` lines and exited 1.
  `setup --agent claude` (or `init --agent claude`) keeps `doctor` green.

## [0.2.1] - 2026-06-02

### Added
- **4 new agent adapters**: Cursor (`.cursorrules`), Windsurf (`.windsurfrules`),
  Gemini CLI (`GEMINI.md`), Aider (`CONVENTIONS.md`). `monolith apply --agent all`
  now writes 7 agent files from one ruleset.
- **`monolith tasks-to-issues --repo owner/repo`**: push todo/doing tasks to
  GitHub Issues via the GitHub API. Stdlib-only (no new deps); requires
  `GITHUB_TOKEN`. Options: `--label`, `--done`, `--spec-link`.
- Hub install paths extended to cover Cursor (`.cursor/rules/*.mdc`), Windsurf
  (`.windsurf/rules/`), Gemini (`.gemini/commands/`), and Aider
  (`.aider/instructions/`).
- **SEO**: expanded `pyproject.toml` keywords and description; added
  `Changelog`, `Documentation`, and `Bug Tracker` URLs; README agent table and
  keyword footer updated to cover all 7 agents.

## [0.2.0] - 2026-06-02

### Added
- **Full Spec-Driven Development (SDD) pipeline** — `constitution → specify →
  clarify → plan → analyze → tasks → implement` — matching spec-kit's methodology,
  delivered offline with zero new dependencies.
- `monolith constitution` — scaffold `.monolith/memory/constitution.md` with
  mission, principles, and definition of done.
- `monolith specify <feature> [--plan] [--data-model] [--contracts]` — scaffold
  `specs/<feature>/` with `spec.md`, `plan.md`, `data-model.md`, and
  `contracts/README.md` from opinionated templates.
- `monolith analyze [feature]` — structural cross-artifact consistency check
  (spec ↔ plan ↔ tasks). Reports OK / WARN / ERROR / INFO per artifact; exits 1
  on any ERROR. Runs all features when no name is given.
- `monolith checklist <feature> [--write]` — generate a quality gate checklist
  pre-populated from the feature's existing artifacts. `--write` saves
  `specs/<feature>/checklist.md`.
- New `workflow.py` module: `scaffold_*` helpers, `analyze_feature`, and
  `generate_checklist` — all deterministic, offline, stdlib-only.
- **6 new hub resources** installable as slash commands across Claude Code,
  Codex, and Copilot:
  - `monolith.constitution` — agent-guided governance setup
  - `monolith.specify` — agent-guided requirements authoring
  - `monolith.clarify` — ambiguity resolution before planning
  - `monolith.analyze` — cross-artifact consistency review
  - `monolith.checklist` — quality gate before shipping
  - `monolith.implement` — dependency-ordered task execution

## [0.1.9] - 2026-06-02

### Fixed
- **Packaging**: use PEP 639 SPDX license metadata (`license = "MIT"` +
  `license-files`); the built sdist/wheel now pass `twine check` and are valid
  for PyPI.
- **Publishing actually triggers**: moved PyPI publish into the `release` job of
  `ci.yml`. A tag pushed by `GITHUB_TOKEN` does not trigger separate workflows,
  so the old `publish.yml` never ran; publishing now happens in the job that
  creates the tag. Removed `publish.yml`.

## [0.1.8] - 2026-06-01

### Changed
- Lint compressor now compacts diagnostics — keeps location + level + rule,
  drops the verbose human message and repeated file paths. Measured ~49–55%
  reduction (was ~1%); full detail still tee'd on failure.
- Removed "inspired by" attributions from the docs and code comments.

## [0.1.7] - 2026-06-01

### Added
- More command-aware compressors for `run`: linters/type-checkers
  (eslint/tsc/ruff/flake8/pylint/mypy/biome/stylelint), `git status` (drops the
  "(use …)" hint chatter), and grep/find (group matches by file, paths by
  directory; never expands).

## [0.1.6] - 2026-06-01

### Added
- `monolith run -- <command>` (`runner.py`): runs a command, prints its
  compressed output, propagates the exit code, and saves full output to
  `.monolith/tee/` on failure.
- Command-aware compression (`compressors.py`): `run` recognises test commands
  (pytest/jest/vitest/go test/cargo test/unittest/npm test) and keeps only
  failures + the summary (~90% reduction on large runs), falling back to generic
  `shrink` for unrecognised commands.
- `monolith gain`: cumulative token-savings ledger across `run` invocations.

## [0.1.5] - 2026-06-01

### Added
- `SECURITY.md` (disclosure policy + security model and considerations).
- `docs/PUBLISHING.md`; PyPI publish workflow switched to Trusted Publishing
  (OIDC) — no stored API token.
- More hub resources: `test-plan`, `tighten-prose`, `explain-diff`.
- v0.2.0 plan in `ROADMAP.md`.

## [0.1.4] - 2026-06-01

### Fixed
- CLI no longer prints a `BrokenPipeError` traceback when its output is piped
  into a consumer that closes early (e.g. `monolith shrink … | head`). (The fix
  missed the v0.1.3 tag due to a merge-ordering race; this release carries it.)

## [0.1.3] - 2026-06-01

### Added
- `monolith scan [--apply]`: scan the repo for inline `@monolith:task` and
  `@monolith:rule` tags and fold them into the task store / custom rules.
- `docs/CAPABILITIES.md` (Capability × Monolith table) and `docs/ABOUT.md`
  (suggested GitHub About / topics).
- Claude Code guide: install steps, installing hub commands as slash commands,
  and adding the `shrink` MCP server.

### Removed
- `monolith compare` command and the README competitor-comparison section.
  Monolith is now presented on its own capabilities; honest projected-vs-measured
  framing is kept.

## [0.1.2] - 2026-06-01

### Fixed
- `--version` now reads from installed package metadata (single-sourced), fixing
  a drift where it reported the previous version.

### Added
- Monolith now manages its own repository (dogfooding): generated `CLAUDE.md`,
  `AGENTS.md`, and `.github/copilot-instructions.md`.

## [0.1.1] - 2026-06-01

### Added
- PyPI publish workflow (`.github/workflows/publish.yml`) triggered on `v*` tags.
- Contributor docs: `CONTRIBUTING.md`, issue/PR templates, and a demo script
  (`scripts/demo.sh`).
- Launch copy pack under `docs/launch/`.

### Changed
- README install now leads with `pipx`/`pip` and links the changelog,
  contributing guide, and demo.

## [0.1.0] - 2026-06-01

### Added
- **Cross-agent token efficiency**: one directive set compiled into `CLAUDE.md`,
  `AGENTS.md`, and `.github/copilot-instructions.md`, with `lite`/`full`/`ultra`
  compression tiers. Commands: `init`, `apply`, `tier`, `doctor`.
- **Measurement**: `bench` (real reduction on a sample corpus), `stats`
  (projected + measured), and `compare` (provenance-tagged vs caveman /
  token-efficient). Optional `tiktoken` extra for exact counts.
- **Custom rules**: `rules list/add/remove`.
- **Task management**: `plan` (PRD/Markdown → task tree), `tasks`, and `task`
  with `{#slug}` / `@after:` dependencies and a generated `TASKS.md`.
- **Resource hub**: `hub list/search/show/install` of curated agent assets.
- **Runtime compression**: `shrink` (deterministic) and an experimental MCP
  server (`mcp`).
- CI with test matrix (Python 3.9/3.11/3.12) and auto-tagging on merge to
  `master`.

[Unreleased]: https://github.com/keyurpatel446/Monolith/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/keyurpatel446/Monolith/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/keyurpatel446/Monolith/compare/v0.1.9...v0.2.0
[0.1.9]: https://github.com/keyurpatel446/Monolith/compare/v0.1.8...v0.1.9
[0.1.8]: https://github.com/keyurpatel446/Monolith/compare/v0.1.7...v0.1.8
[0.1.7]: https://github.com/keyurpatel446/Monolith/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/keyurpatel446/Monolith/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/keyurpatel446/Monolith/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/keyurpatel446/Monolith/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/keyurpatel446/Monolith/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/keyurpatel446/Monolith/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/keyurpatel446/Monolith/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/keyurpatel446/Monolith/releases/tag/v0.1.0
