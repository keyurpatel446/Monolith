# Contributing to Monolith

Thanks for your interest! Monolith aims to stay small, honest, and dependency-free.

## Development setup

```bash
git clone https://github.com/keyurpatel446/Monolith
cd Monolith
pip install -e .            # or: pip install -e ".[bench]" for exact token counts
python -m unittest discover -s tests -v
```

The core is **stdlib-only** by design; please don't add runtime dependencies
without discussion (`tiktoken` is an optional `[bench]` extra).

## Branching model

| Branch | Purpose |
|--------|---------|
| `master` | Default / release branch (merges trigger a tagged release). |
| `develop` | Integration branch. |
| `fetcher/<name>` | Feature work. |
| `fix/<name>` | Bug fixes. |

Open PRs against `develop`. Releases flow `develop → master`.

## Guidelines

- **Tests**: add/extend `unittest` tests under `tests/` for any behaviour change.
- **Comments**: match the surrounding style — module/function docstrings and
  rationale for non-obvious logic.
- **Honesty**: keep projected vs measured numbers clearly labelled; never
  overstate reductions.
- **Adding an agent**: subclass `Compiler` in `src/monolith/adapters/`, set
  `key`/`label`/`target_path`, override `preamble()`, decorate with `@register`,
  and add it to the import list in `adapters/__init__.py`.

## Releasing

Bump `version` in `pyproject.toml`, update `CHANGELOG.md`, and merge to `master`.
CI tags `vX.Y.Z`, creates a GitHub release, and publishes to PyPI.
