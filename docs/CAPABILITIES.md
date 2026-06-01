# Capabilities

What Monolith does, at a glance. Run `monolith <command> --help` for details, or
see the [usage guide](USAGE.md).

| Capability | Monolith |
|---|---|
| Token-saving rules | ✅ one directive set, tiers `lite` / `full` / `ultra` |
| Cross-agent output | ✅ compiles to `CLAUDE.md`, `AGENTS.md`, `.github/copilot-instructions.md` |
| Idempotent, non-destructive | ✅ edits only between markers; your own notes are preserved |
| Measured savings | ✅ `bench` measures real reduction; `stats` shows projected + measured |
| Custom rules | ✅ `rules list / add / remove` |
| Task management | ✅ `plan` (PRD → task tree), `tasks`, `task` with `{#slug}` / `@after:` deps |
| Agent-readable task file | ✅ generated `TASKS.md` |
| Resource hub | ✅ `hub list / search / show / install` curated agent commands |
| Runtime output compression | ✅ `shrink` (lite/full/ultra) + experimental MCP server |
| Health check | ✅ `doctor` verifies each agent picked up the block |
| Dependencies | ✅ stdlib-only core (`tiktoken` optional via `[bench]`) |
| License | ✅ MIT |

## What makes Monolith different

- **One source of truth.** Author your rules once; Monolith compiles them into
  every agent's native config — no copy-paste, no drift.
- **Honest numbers.** Reductions are labelled projected vs measured; nothing is
  overstated.
- **Dependency-free core.** A small Python CLI that runs anywhere, no Node, no
  services.
- **More than rules.** Task planning, a resource hub, and runtime `shrink` in
  the same tool.
