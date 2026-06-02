# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `monolith run -- <command>` (`runner.py`): runs a command, prints its
  compressed output, propagates the exit code, and saves full output to
  `.monolith/tee/` on failure (inspired by rtk).
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

[Unreleased]: https://github.com/keyurpatel446/Monolith/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/keyurpatel446/Monolith/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/keyurpatel446/Monolith/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/keyurpatel446/Monolith/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/keyurpatel446/Monolith/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/keyurpatel446/Monolith/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/keyurpatel446/Monolith/releases/tag/v0.1.0
