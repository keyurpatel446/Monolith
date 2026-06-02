# Capabilities

What Monolith does, at a glance. Run `monolith <command> --help` for details, or
see the [usage guide](USAGE.md).

| Capability | Monolith |
|---|---|
| Token-saving rules | ✅ one directive set, tiers `lite` / `full` / `ultra` |
| Cross-agent output | ✅ 7 agents: Claude Code, Codex, Copilot, Cursor, Windsurf, Gemini CLI, Aider |
| Idempotent, non-destructive | ✅ edits only between markers; your own notes are preserved |
| Measured savings | ✅ `bench` measures real reduction; `stats` shows projected + measured |
| Custom rules | ✅ `rules list / add / remove` |
| Task management | ✅ `plan` (PRD → task tree), `tasks`, `task` with `{#slug}` / `@after:` deps |
| Agent-readable task file | ✅ generated `TASKS.md` |
| Resource hub | ✅ `hub list / search / show / install` curated agent commands |
| Runtime output compression | ✅ `shrink` (lite/full/ultra) + experimental MCP server |
| Health check | ✅ `doctor` verifies each agent picked up the block |
| **SDD pipeline** | ✅ `constitution`, `specify`, `analyze`, `checklist` + 6 slash commands |
| **Structured specs folder** | ✅ `specs/<feature>/` with spec.md, plan.md, tasks.md, data-model.md, contracts/ |
| Dependencies | ✅ stdlib-only core (`tiktoken` optional via `[bench]`) |
| License | ✅ MIT |

## Spec-Driven Development (SDD) pipeline

Monolith now ships a full SDD workflow matching spec-kit's methodology, delivered
as CLI commands and installable slash commands for every supported agent.

```
constitution → specify → clarify → plan → analyze → tasks → implement
```

| Step | CLI | Slash command |
|---|---|---|
| Governance | `monolith constitution` | `/monolith.constitution` |
| Requirements | `monolith specify <feature>` | `/monolith.specify` |
| Ambiguity | _(agent-guided)_ | `/monolith.clarify` |
| Architecture | `monolith plan <prd>` | _(use CLI)_ |
| Consistency | `monolith analyze <feature>` | `/monolith.analyze` |
| Tasks | `monolith tasks` | _(use CLI)_ |
| Ship gate | `monolith checklist <feature>` | `/monolith.checklist` |
| Execute | _(agent-guided)_ | `/monolith.implement` |

Install all SDD slash commands in one step:

```
monolith hub install monolith.constitution
monolith hub install monolith.specify
monolith hub install monolith.clarify
monolith hub install monolith.analyze
monolith hub install monolith.checklist
monolith hub install monolith.implement
```

## What makes Monolith different

- **One source of truth.** Author your rules once; Monolith compiles them into
  every agent's native config — no copy-paste, no drift.
- **Honest numbers.** Reductions are labelled projected vs measured; nothing is
  overstated.
- **Dependency-free core.** A small Python CLI that runs anywhere, no Node, no
  services.
- **Full SDD pipeline.** constitution → specify → clarify → plan → analyze →
  tasks → implement, plus structured `specs/<feature>/` artifacts — all offline,
  no new dependencies.
- **More than rules.** Task planning, SDD workflow, a resource hub, and runtime
  `shrink` in the same tool.
