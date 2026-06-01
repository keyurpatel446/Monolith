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

## Workflow

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

## Commands

### `monolith init [--force]`
Detects which agent files already exist in the project and writes
`.monolith/settings.json`. If none exist, all three agents are targeted by
default. Use `--force` to overwrite existing settings.

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

### `monolith compare`
Prints a provenance-tagged comparison of Monolith against caveman and
claude-token-efficient. **Input overhead** is measured here for every approach
with the same tokenizer (objective). **Output reduction** is labeled `measured`
for Monolith's corpus and `published` for the other projects' own figures — it
is not a single-model head-to-head, which is impossible offline.

### `monolith hub list | search <q> | show <id> | install <id> [--agent]`
Browse and install curated, token-frugal agent resources (slash commands and
prompts) that ship inside Monolith. `install` writes the asset into each target
agent's conventional path (e.g. `.claude/commands/`, `.codex/prompts/`,
`.github/prompts/`); pass `--agent <key>` to install for one agent only.

### `monolith shrink [file] [--level lite|full|ultra]`
Compresses verbose text/output deterministically (no model). Reads a file or
stdin, writes the compressed text to **stdout** and the savings to **stderr**
(so it pipes cleanly). Levels: `lite` (whitespace), `full` (+ ANSI strip and
fold identical lines), `ultra` (+ clip very long output with a marker).

```bash
pytest -q 2>&1 | monolith shrink --level full > short.log
```

### `monolith mcp`
Runs the **experimental** MCP server over stdio (newline-delimited JSON-RPC),
exposing a single `shrink` tool so an MCP-capable agent can compress tool output
at runtime. The request handlers are unit-tested; the live loop is experimental.

### `monolith doctor`
Checks each configured agent's file for a healthy Monolith block and reports
`ok`/`FAIL` per agent. Exit code is non-zero if any agent is missing the block.

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
