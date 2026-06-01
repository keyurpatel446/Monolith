# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/), and this project adheres to
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added
- `docs/CAPABILITIES.md` (Capability × Monolith table) and `docs/ABOUT.md`
  (suggested GitHub About / topics).
- Claude Code guide: install steps, installing hub commands as slash commands,
  and adding the `shrink` MCP server.

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

[Unreleased]: https://github.com/keyurpatel446/Monolith/compare/v0.1.2...HEAD
[0.1.2]: https://github.com/keyurpatel446/Monolith/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/keyurpatel446/Monolith/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/keyurpatel446/Monolith/releases/tag/v0.1.0
