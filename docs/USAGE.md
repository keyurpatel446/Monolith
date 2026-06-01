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

- **Ruleset** — the canonical token-saving directives (`src/monolith/rules.py`).
- **Profile** — which rules to emit and how aggressively (`lite`/`full`/`ultra`).
- **Adapter** — compiles the ruleset into one agent's native file.
- **Config** — `.monolith/config.json` holds the active profile, target agents,
  and any custom rules.
- **Managed block** — the section between `<!-- monolith:start -->` and
  `<!-- monolith:end -->`. Monolith only ever edits inside these markers.

## Workflow

```bash
monolith init                 # 1. set up config (detects existing agent files)
monolith apply --agent all    # 2. write the rules into every agent file
monolith doctor               # 3. verify the block landed everywhere
```

Iterate as you like:

```bash
monolith profile             # see current + available profiles
monolith profile ultra       # switch (run `apply` after, or use --apply)
monolith profile full --apply
monolith stats               # projected savings + input cost per file
```

## Commands

### `monolith init [--force]`
Detects which agent files already exist in the project and writes
`.monolith/config.json`. If none exist, all three agents are targeted by
default. Use `--force` to overwrite an existing config.

### `monolith apply [--agent {all,claude,codex,copilot,config}]`
Compiles the active profile into the target files. Default `config` uses the
agent list from your config. The write is **idempotent** — re-running updates
only the managed block and leaves your own content untouched.

### `monolith profile [name] [--apply]`
With no `name`, prints the active profile and the available ones. With a
`name`, switches the active profile. Add `--apply` to regenerate configs
immediately.

### `monolith stats`
Prints the projected per-response output reduction for the active profile and
the one-time input-token cost of the managed block in each agent file. All
reduction figures are labeled as projections, not measurements.

### `monolith doctor`
Checks each configured agent's file for a healthy Monolith block and reports
`ok`/`FAIL` per agent. Exit code is non-zero if any agent is missing the block.

## Global flags

| Flag | Effect |
|------|--------|
| `--root <dir>` | Operate on another project directory. |
| `--version` | Print the Monolith version. |

## Custom rules

Add project-specific directives by editing the `custom_rules` array in
`.monolith/config.json`, then re-run `monolith apply`. They are appended to the
generated block for every agent.

```json
{
  "profile": "full",
  "agents": ["claude", "codex", "copilot"],
  "custom_rules": [
    "Prefer pytest-style asserts in test files.",
    "Never edit files under vendor/."
  ]
}
```

## Tests

```bash
PYTHONPATH=src python -m unittest discover -s tests -v
```
