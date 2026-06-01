# Monolith

**One token-efficiency ruleset for every AI coding assistant.**

Monolith is a small, dependency-free CLI that writes proven token-saving rules
into the native config file each AI coding agent already reads — so you author
the rules **once** and every agent obeys them:

| Agent | File Monolith generates |
|-------|-------------------------|
| Claude Code | `CLAUDE.md` |
| OpenAI Codex | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |

It synthesizes the best ideas from a few popular projects into one tool:

- **Filler removal** — no greetings, closers, or restatement
  (inspired by [claude-token-efficient](https://github.com/drona23/claude-token-efficient)).
- **Dense, low-token output** with intensity profiles `lite` / `full` / `ultra`
  (inspired by [caveman](https://github.com/JuliusBrussee/caveman)).
- A roadmap toward **task management** and a **resource hub**
  (inspired by [claude-task-master](https://github.com/eyaltoledano/claude-task-master)
  and [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)).

> Projected output reduction is **55–65%** on the `full` profile, based on the
> upstream benchmarks Monolith builds on. These are projections, not
> guarantees — `monolith stats` always labels them as such.

## Why

Each agent reads instructions from a different file, so today you'd copy-paste
the same rules into three places and keep them in sync by hand. Monolith keeps
one canonical source and compiles it. Re-running is safe: managed content lives
between markers and never clobbers your own notes in the same file.

## Install

Requires Python ≥ 3.9. No third-party dependencies.

```bash
# from a clone of this repo
pip install -e .
# or run without installing
PYTHONPATH=src python -m monolith --help
```

## Quickstart

```bash
monolith init                 # detect agents, create .monolith/config.json
monolith apply --agent all    # write CLAUDE.md, AGENTS.md, copilot-instructions.md
monolith doctor               # verify each agent picked up the rules
```

Switch how aggressive the rules are at any time:

```bash
monolith profile ultra --apply   # most aggressive, re-applies immediately
monolith stats                   # projected savings + one-time input cost
```

## Commands

| Command | Description |
|---------|-------------|
| `monolith init` | Detect agent files and create `.monolith/config.json`. |
| `monolith apply [--agent all\|claude\|codex\|copilot\|config]` | Compile the ruleset into agent configs (idempotent). |
| `monolith profile [name] [--apply]` | Show or switch the active profile. |
| `monolith stats` | Show projected output reduction and the input cost of the block. |
| `monolith doctor` | Verify each configured agent has the Monolith block. |

Global flag `--root <dir>` runs against another project directory.

## Profiles

| Profile | Intensity | Projected output reduction* |
|---------|-----------|-----------------------------|
| `lite` | filler removal only | ~25–35% |
| `full` (default) | filler + dense formatting + no over-engineering | ~55–65% |
| `ultra` | telegraphic, bullet-first, every rule | ~60–70% |

\* Projections derived from upstream benchmarks, not per-project measurements.

## Documentation

- [Usage guide](docs/USAGE.md)
- Per-agent setup: [Claude Code](docs/agents/claude-code.md) ·
  [Codex](docs/agents/codex.md) · [Copilot](docs/agents/copilot.md)
- [Roadmap](ROADMAP.md)

## License

MIT © Keyur Patel
