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
- **Dense, low-token output** with intensity tiers `lite` / `full` / `ultra`
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
monolith init                 # detect agents, create .monolith/settings.json
monolith apply --agent all    # write CLAUDE.md, AGENTS.md, copilot-instructions.md
monolith doctor               # verify each agent picked up the rules
```

Switch how aggressive the rules are at any time:

```bash
monolith tier ultra --apply   # most aggressive, re-applies immediately
monolith stats                # projected savings + one-time input cost
```

## Commands

**Token efficiency**

| Command | Description |
|---------|-------------|
| `monolith init` | Detect agent files and create `.monolith/settings.json`. |
| `monolith apply [--agent all\|claude\|codex\|copilot\|config]` | Compile the directives into agent configs (idempotent). |
| `monolith tier [name] [--apply]` | Show or switch the active compression tier. |
| `monolith stats` | Show projected reduction, last measured reduction, and the input cost of the block. |
| `monolith bench` | Run the built-in benchmark corpus and record measured token reduction. |
| `monolith rules list\|add\|remove [value]` | Manage custom directives appended to every block. |
| `monolith doctor` | Verify each configured agent has the Monolith block. |

**Task management**

| Command | Description |
|---------|-------------|
| `monolith plan <prd-file> [--force]` | Parse a PRD/Markdown file into a task tree; writes `TASKS.md`. |
| `monolith tasks [--emit]` | List the task tree; `--emit` re-writes `TASKS.md`. |
| `monolith task <id> --status todo\|doing\|done` | Update a task's status (warns on unmet dependencies). |

Global flag `--root <dir>` runs against another project directory.

## Measuring savings

`monolith bench` measures the real token reduction between matched verbose/concise
response pairs (exact counts if [`tiktoken`](https://github.com/openai/tiktoken)
is installed, otherwise a heuristic), records it to `.monolith/stats.json`, and
`monolith stats` then shows that measured figure next to the projected range.

## Task management

Point `monolith plan` at a PRD or any structured Markdown file. Headings and
list items become tasks; nesting becomes parent/child. Wire up dependencies
with inline tags — `{#slug}` names a task and `@after:slug` depends on it:

```markdown
# Auth feature
- Design DB schema {#schema}
- Build API @after:schema
  - Add input validation
## Release @after:schema
```

`monolith plan prd.md` writes a shared task store under `.monolith/tasks/` and a
root `TASKS.md` your agents read as ordinary project context.

## Tiers

| Tier | Intensity | Projected output reduction* |
|------|-----------|-----------------------------|
| `lite` | filler removal only | ~25–35% |
| `full` (default) | filler + dense formatting + no over-engineering | ~55–65% |
| `ultra` | telegraphic, bullet-first, every directive | ~60–70% |

\* Projections derived from upstream benchmarks, not per-project measurements.

## Documentation

- [Usage guide](docs/USAGE.md)
- Per-agent setup: [Claude Code](docs/agents/claude-code.md) ·
  [Codex](docs/agents/codex.md) · [Copilot](docs/agents/copilot.md)
- [Roadmap](ROADMAP.md)

## License

MIT © Keyur Patel
