# Claude Code setup

Monolith writes its token-efficiency rules into `CLAUDE.md` at your project
root — the file Claude Code automatically loads as project memory.

## 0. Install Monolith

```bash
pipx install monolith-ai     # recommended
# or
pip install monolith-ai
```

(Until the first PyPI release, install from source: `pip install -e .` in a
clone of the repo.)

## Apply

```bash
monolith init
monolith apply --agent claude
```

This creates or updates `CLAUDE.md`, inserting a managed block between
`<!-- monolith:start -->` and `<!-- monolith:end -->`. Any existing content in
`CLAUDE.md` is preserved.

## Verify

```bash
monolith doctor
```

You should see `Claude Code  CLAUDE.md  (managed block present)`. Inside Claude
Code you can also run `/memory` to confirm `CLAUDE.md` is loaded.

## Optional: install hub commands as slash commands

Monolith's curated resources install straight into Claude Code's slash-command
directory (`.claude/commands/`):

```bash
monolith hub install concise-commit --agent claude
# then in Claude Code:  /concise-commit
```

## Optional: add the `shrink` MCP server

Expose Monolith's deterministic output compressor to Claude Code as an MCP tool,
so the agent can shrink verbose command/log output at runtime:

```bash
claude mcp add monolith-shrink -- monolith mcp
```

This registers a stdio MCP server (see `monolith mcp`). It's experimental — the
request handlers are tested, the live loop is still being validated.

## Notes

- Claude Code merges `CLAUDE.md` files from parent directories and `~/.claude/`.
  Monolith manages the project-root file; user-global rules still apply on top.
- To tighten output, switch tiers: `monolith tier ultra --apply`.
- User instructions in the conversation always override these rules — that line
  is part of every generated block.
