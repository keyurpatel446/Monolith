# GitHub Copilot setup

Monolith writes its token-efficiency rules into
`.github/copilot-instructions.md` — the custom-instructions file GitHub Copilot
reads for repository-wide guidance.

## Apply

```bash
monolith init
monolith apply --agent copilot
```

This creates the `.github/` directory if needed and writes
`copilot-instructions.md` with a managed block between
`<!-- monolith:start -->` and `<!-- monolith:end -->`. Existing content is
preserved.

## Verify

```bash
monolith doctor
```

You should see
`GitHub Copilot  .github/copilot-instructions.md  (managed block present)`.

## Notes

- Copilot applies these instructions to chat and edit suggestions across the
  repository. Effects are strongest in Copilot Chat / agent modes.
- Commit `.github/copilot-instructions.md` so the whole team benefits.
- Switch intensity with `monolith profile <lite|full|ultra> --apply`.
- User instructions always override these rules.
