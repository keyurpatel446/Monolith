# Usage Guide

Full reference for the Monolith CLI. For the big picture see the
[README](../README.md); for the plan see the [Roadmap](../ROADMAP.md).

## Install

Requires Python ≥ 3.9, no third-party dependencies.

```bash
pip install -e .                       # editable install -> `monolith` on PATH
# or, without installing:
PYTHONPATH=src python -m monolith ...  # run from a checkout
```

## Concepts

- **Directive** — one canonical token-saving rule (`src/monolith/directives.py`).
- **Tier** — which directives to emit and how aggressively
  (`lite`/`full`/`ultra`, in `src/monolith/compression.py`).
- **Compiler** — renders the directives into one agent's native file
  (`src/monolith/adapters/`). Compilers self-register, so adding an agent is
  one new file.
- **Settings** — `.monolith/settings.json` holds the active tier, target
  agents, and any extra (custom) rules.
- **Managed block** — the section between `<!-- monolith:start -->` and
  `<!-- monolith:end -->`. Monolith only ever edits inside these markers.
- **Feature** — a named folder under `specs/<feature>/` containing the SDD
  artifact set: `spec.md`, `plan.md`, `tasks.md`, `data-model.md`, `contracts/`.
- **Constitution** — `.monolith/memory/constitution.md`: project-wide principles
  and definition of done, read by every SDD command.

## Token-efficiency workflow

```bash
monolith setup                # init + apply + doctor in one command
```

Or step by step:

```bash
monolith init                 # 1. set up settings (detects existing agent files)
monolith apply --agent all    # 2. write the directives into every agent file
monolith doctor               # 3. verify the block landed everywhere
```

Iterate as you like:

```bash
monolith tier                # see current + available tiers
monolith tier ultra          # switch (run `apply` after, or use --apply)
monolith tier full --apply
monolith stats               # projected savings + input cost per file
```

## SDD workflow

```bash
monolith constitution                    # 1. scaffold .monolith/memory/constitution.md
monolith specify user-auth               # 2. scaffold specs/user-auth/spec.md
# fill in spec.md …
monolith analyze user-auth               # 3. check for gaps (re-run at each step)
monolith specify user-auth --plan        # 4. scaffold plan.md
# fill in plan.md …
monolith plan specs/user-auth/spec.md   # 5. parse spec into task tree
monolith analyze user-auth               # 6. confirm full coverage
monolith checklist user-auth             # 7. quality gate before shipping
```

Install the agent-facing slash commands once:

```bash
monolith hub install sdd     # bundle: all six monolith.* commands
```

Then use `/monolith.specify`, `/monolith.clarify`, etc. directly in any agent.

## Commands

### `monolith setup [--agent <agent>|all] [--tier <tier>]`
One-shot onboarding: writes settings (scoped to `--agent` if given, otherwise
detected agent files, otherwise all), applies the directives, and runs the
doctor. Safe to re-run; an explicit `--agent`/`--tier` updates existing
settings.

### `monolith init [--force] [--agent <agent>|all]`
Detects which agent files already exist in the project and writes
`.monolith/settings.json`. If none exist, all agents are targeted by
default; `--agent` scopes the settings to one agent. Use `--force` to
overwrite existing settings.

### `monolith apply [--agent {all,claude,codex,copilot,config}]`
Compiles the active tier into the target files. Default `config` uses the
agent list from your settings. The write is **idempotent** — re-running updates
only the managed block and leaves your own content untouched.

### `monolith tier [name] [--apply]`
With no `name`, prints the active tier and the available ones. With a
`name`, switches the active tier. Add `--apply` to regenerate configs
immediately.

### `monolith stats`
Prints the projected per-response output reduction for the active tier, the
one-time input-token cost of the managed block in each agent file, and — if you
have run `monolith bench` — the last *measured* reduction. Projections are
labeled separately from measurements.

### `monolith bench`
Runs the built-in benchmark corpus (matched verbose/concise response pairs),
prints per-sample and aggregate measured reduction, and records the headline to
`.monolith/stats.json`. Uses [`tiktoken`](https://github.com/openai/tiktoken)
for exact counts when installed, otherwise a ~4-chars/token heuristic; the
active counter is shown in the output.

### `monolith rules list | add <text> | remove <index|text>`
Manages the `extra_rules` in your settings — custom directives appended to every
generated block. `add` appends a rule, `remove` takes a 1-based index or the
exact rule text, `list` prints them. Re-run `monolith apply` afterwards.

### `monolith plan <prd-file> [--force]`
Parses a PRD/Markdown file into a task tree (see *Task management* below), saves
it to `.monolith/tasks/tasks.json`, and writes a root `TASKS.md`. Refuses to
overwrite an existing plan unless `--force` is given.

### `monolith tasks [--emit]`
Lists the current task tree with status and dependencies. `--emit` re-writes
`TASKS.md` from the stored tasks.

### `monolith task <id> --status {todo,doing,done}`
Updates one task's status, re-saves the store, and re-emits `TASKS.md`. Warns
(without blocking) if you advance a task whose dependencies are not yet `done`.

### `monolith scan [--apply]`
Walks the repo for inline `@monolith:` tags and acts on them. `@monolith:task
<title>` (with optional `{#slug}` / `@after:slug`) adds a task; `@monolith:rule
<text>` adds a custom directive. Dry run by default — pass `--apply` to write.
Idempotent: tasks de-dupe by title, rules by text.

```python
# @monolith:task Add rate limiting {#ratelimit} @after:auth
# @monolith:rule Always validate request bodies
```

### `monolith hub list | search <q> | show <id> | install <id> [--agent]`
Browse and install curated, token-frugal agent resources (slash commands and
prompts) that ship inside Monolith. `install` writes the asset into each target
agent's conventional path (e.g. `.claude/commands/`, `.codex/prompts/`,
`.github/prompts/`). By default it targets the agents in your settings (or all
the resource supports when no settings exist); pass `--agent <key>` for one
agent or `--agent all` for everything. `install` also accepts a bundle name —
`monolith hub install sdd` installs all six SDD workflow commands at once.

### `monolith shrink [file] [--level lite|full|ultra]`
Compresses verbose text/output deterministically (no model). Reads a file or
stdin, writes the compressed text to **stdout** and the savings to **stderr**
(so it pipes cleanly). Levels: `lite` (whitespace), `full` (+ ANSI strip and
fold identical lines), `ultra` (+ clip very long output with a marker).

```bash
pytest -q 2>&1 | monolith shrink --level full > short.log
```

### `monolith run [--level lite|full|ultra] [--timeout N] -- <command>`
Runs `<command>`, prints its **compressed** combined output, and exits with the
command's own return code (so the agent still sees pass/fail). On failure the
**full** output is saved to `.monolith/tee/` and a pointer is appended, so the
agent can read details without re-running. Each run records token savings.

`run` is **command-aware** — it applies a semantic filter when it recognises the
command, and falls back to generic `--level` compression otherwise:

| Command | What it keeps |
|---------|---------------|
| test runners (pytest, jest, vitest, `go test`, `cargo test`, `unittest`, `npm test`) | failures + summary only (~90% on large runs) |
| linters/type-checkers (eslint, tsc, ruff, flake8, pylint, mypy, …) | diagnostics + counts |
| `git status` | branch + changed/untracked paths (drops "(use …)" hints) |
| grep / find / rg / fd | matches grouped by file, paths grouped by directory |

```bash
monolith run -- pytest -q          # failures + summary only; full log saved if it fails
monolith run -- git status
```

### `monolith gain`
Reports cumulative token savings recorded by `monolith run` (commands run,
tokens in/out, total saved).

### `monolith mcp`
Runs the **experimental** MCP server over stdio (newline-delimited JSON-RPC),
exposing a single `shrink` tool so an MCP-capable agent can compress tool output
at runtime. The request handlers are unit-tested; the live loop is experimental.

### `monolith doctor [--agent <agent>|all|config]`
Checks each configured agent's file for a healthy Monolith block and reports
`ok`/`FAIL` per agent. Exit code is non-zero if any agent is missing the block.
Defaults to the agents in your settings; `--agent` narrows or widens the check.

---

## SDD commands

### `monolith constitution`
Scaffolds `.monolith/memory/constitution.md` with a template for mission,
engineering principles, and definition of done. Does nothing if the file already
exists. Edit the file directly, or use the `/monolith.constitution` hub command
to let an agent fill it in interactively.

### `monolith specify <feature> [--plan] [--data-model] [--contracts]`
Scaffolds `specs/<feature>/` with:
- `spec.md` — requirements, user stories, acceptance criteria (always created)
- `plan.md` — architecture, stack decisions (with `--plan`)
- `data-model.md` — entity definitions, relationships (with `--data-model`)
- `contracts/README.md` — API contract convention (with `--contracts`)

Files that already exist are not overwritten. Run again with additional flags to
add optional artifacts later.

```bash
monolith specify payments            # spec.md only
monolith specify payments --plan --data-model --contracts   # full scaffold
```

### `monolith analyze [feature]`
Performs a structural cross-artifact consistency check for a feature:
- Checks that the constitution exists.
- Verifies each pipeline artifact (`spec.md`, `plan.md`, `tasks.md`) exists and
  is not still an unfilled template.
- Reports optional artifacts (`data-model.md`, `contracts/`) as INFO.

Findings are prefixed `OK`, `WARN`, `ERROR`, or `INFO`. Exits with code 1 if
any ERROR is found. Omit `feature` to analyze all features under `specs/`.

```bash
monolith analyze user-auth     # single feature
monolith analyze               # all features
```

### `monolith checklist <feature> [--write]`
Generates a quality checklist with four sections:
- **Spec and Planning** — artifact existence, open questions, non-goals
- **Implementation** — acceptance criteria, edge cases, no TODOs
- **Quality Gates** — tests, lint, doctor, analyze
- **Review** — PR description, reviewer sign-off, CHANGELOG

Checkboxes for `spec.md`, `plan.md`, and `tasks.md` are pre-checked when those
files already exist. Use `--write` to save the checklist to
`specs/<feature>/checklist.md` instead of printing.

```bash
monolith checklist user-auth           # print
monolith checklist user-auth --write   # save to specs/user-auth/checklist.md
```

---

## Global flags

| Flag | Effect |
|------|--------|
| `--root <dir>` | Operate on another project directory. |
| `--version` | Print the Monolith version. |

## Custom rules

Add project-specific directives by editing the `extra_rules` array in
`.monolith/settings.json`, then re-run `monolith apply`. They are appended to
the generated block for every agent.

```json
{
  "tier": "full",
  "agents": ["claude", "codex", "copilot"],
  "extra_rules": [
    "Prefer pytest-style asserts in test files.",
    "Never edit files under vendor/."
  ]
}
```

Or manage them from the CLI without editing JSON:

```bash
monolith rules add "Never edit files under vendor/."
monolith rules list
monolith rules remove 1
```

## Task management

`monolith plan <file>` turns a PRD or any structured Markdown into a tracked
task tree. The parsing conventions are intentionally small:

- **Headings** (`#`..`######`) and **list items** (`-`, `*`, `+`, `1.`) each
  become a task; nesting (heading depth + list indentation) sets parent/child.
- **`{#slug}`** names a task so others can depend on it.
- **`@after:slug1,slug2`** declares dependencies on named tasks.

```markdown
# Auth feature
- Design DB schema {#schema}
- Build API @after:schema
  - Add input validation
## Release @after:schema
```

```bash
monolith plan prd.md           # parse -> .monolith/tasks/tasks.json + TASKS.md
monolith tasks                 # show the tree with status + deps
monolith task T3 --status doing
monolith task T2 --status done
```

`tasks.json` and `settings.json` are meant to be committed (shared with the
team); `stats.json` is local and git-ignored. `TASKS.md` is fully generated —
edit tasks through the commands, not the file.

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
