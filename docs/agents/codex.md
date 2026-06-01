# OpenAI Codex setup

Monolith writes its token-efficiency rules into `AGENTS.md` at your project
root — the conventional instructions file the Codex agent reads.

## Apply

```bash
monolith init
monolith apply --agent codex
```

This creates or updates `AGENTS.md` with a managed block between
`<!-- monolith:start -->` and `<!-- monolith:end -->`. Existing content is
preserved.

## Verify

```bash
monolith doctor
```

You should see `OpenAI Codex  AGENTS.md  (managed block present)`.

## Notes

- `AGENTS.md` is the widely adopted convention for agent instructions and is
  read by Codex and several other agents, so this file does double duty.
- Switch intensity with `monolith tier <lite|full|ultra> --apply`.
- User instructions in the conversation always override these rules.
