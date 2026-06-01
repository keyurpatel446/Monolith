# Claude Code setup

Monolith writes its token-efficiency rules into `CLAUDE.md` at your project
root — the file Claude Code automatically loads as project memory.

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

## Notes

- Claude Code merges `CLAUDE.md` files from parent directories and `~/.claude/`.
  Monolith manages the project-root file; user-global rules still apply on top.
- To tighten output, switch profiles: `monolith profile ultra --apply`.
- User instructions in the conversation always override these rules — that line
  is part of every generated block.
