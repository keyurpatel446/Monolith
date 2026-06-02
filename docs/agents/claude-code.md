# Using Monolith with Claude Code

This guide covers everything from first install to the full Spec-Driven Development
workflow inside Claude Code — CLI, desktop app, and web.

---

## How it works

Claude Code automatically reads `CLAUDE.md` at your project root on every
session. Monolith writes its token-efficiency rules into that file (between
markers it owns), so Claude Code obeys them without any further configuration
in the app.

```
your project/
├── CLAUDE.md          ← Monolith writes here; Claude Code reads this automatically
└── .claude/
    └── commands/      ← Monolith hub installs slash commands here
```

---

## Step 1 — Install Monolith

```bash
pipx install monolith-ai      # recommended: isolated, always on PATH
# or
pip install monolith-ai
```

Verify:

```bash
monolith --version
```

---

## Step 2 — Set up your project

Run these once in the root of any project you use with Claude Code:

```bash
monolith init                  # creates .monolith/settings.json
monolith apply --agent claude  # writes token rules into CLAUDE.md
monolith doctor                # confirms Claude Code picked it up
```

Expected `doctor` output:

```
[ok ] Claude Code     CLAUDE.md  (managed block present)
```

That's it. Open Claude Code in this project — the rules are active immediately.

> **All agents at once:** if you also use Copilot, Cursor, Codex, etc., run
> `monolith apply --agent all` instead to write all 7 config files in one go.

---

## Step 3 — Choose your tier

Three compression levels. Switch at any time:

```bash
monolith tier                  # show current tier and all options
monolith tier full --apply     # default — filler + dense format (~55–65% reduction)
monolith tier ultra --apply    # telegraphic, bullet-first (~60–70% reduction)
monolith tier lite --apply     # gentle — just remove filler words (~25–35%)
```

See your projected savings:

```bash
monolith stats
```

---

## Step 4 — Install slash commands

Monolith ships curated slash commands that install straight into
`.claude/commands/` — they appear as `/command-name` inside Claude Code.

### SDD workflow commands (recommended — install all at once)

```bash
monolith hub install monolith.constitution
monolith hub install monolith.specify
monolith hub install monolith.clarify
monolith hub install monolith.analyze
monolith hub install monolith.checklist
monolith hub install monolith.implement
```

Then in Claude Code:

| Type this | What it does |
|-----------|-------------|
| `/monolith.constitution` | Sets up project governance + principles |
| `/monolith.specify` | Writes `specs/<feature>/spec.md` (requirements + user stories) |
| `/monolith.clarify` | Surfaces every ambiguity in the spec before you plan |
| `/monolith.analyze` | Checks spec ↔ plan ↔ tasks for gaps |
| `/monolith.checklist` | Generates a quality gate before shipping |
| `/monolith.implement` | Reads spec + plan + tasks, implements in dependency order |

### Utility commands

```bash
monolith hub install concise-commit   # /concise-commit  — one-line Conventional Commit
monolith hub install terse-review     # /terse-review    — correctness-only diff review
monolith hub install explain-diff     # /explain-diff    — bullet summary of current diff
monolith hub install test-plan        # /test-plan       — list test cases for selected code
monolith hub install explain-terse    # /explain-terse   — explain code in ≤5 bullets
```

List everything available:

```bash
monolith hub list
```

---

## Step 5 — Add the MCP server (optional)

Expose Monolith's output compressor to Claude Code as an MCP tool so Claude
can shrink verbose command output at runtime without leaving the session:

```bash
claude mcp add monolith-shrink -- monolith mcp
```

This registers a stdio MCP server. Once added, Claude Code can call the
`shrink` tool directly on any long output.

Verify it registered:

```bash
claude mcp list
```

> The MCP server is experimental — the request handlers are unit-tested but the
> live stdio loop is still being validated across MCP clients.

---

## Full SDD workflow example

Here is the complete flow from idea to shipped feature, all inside Claude Code:

**1. Set up governance (once per project)**

```
/monolith.constitution
```

Claude asks 3 questions (mission, principles, definition of done) and writes
`.monolith/memory/constitution.md`.

**2. Scaffold the feature spec**

```bash
monolith specify user-auth --plan --data-model
```

Or let Claude do it:

```
/monolith.specify
```

Claude asks for the feature name, then writes `specs/user-auth/spec.md` with
problem statement, user stories, functional requirements, and acceptance criteria.

**3. Resolve ambiguities**

```
/monolith.clarify
```

Claude reads the spec, lists every open question (`Q1: …`, `Q2: …`), waits for
your answers, then updates the spec.

**4. Generate the plan and tasks (CLI)**

```bash
monolith plan specs/user-auth/spec.md   # parses spec into TASKS.md
monolith tasks                          # review the task tree
```

**5. Check consistency**

```bash
monolith analyze user-auth
```

Or in the chat:

```
/monolith.analyze
```

Fix any ERROR findings before starting implementation.

**6. Implement**

```
/monolith.implement
```

Claude reads constitution + spec + plan + tasks, works through tasks in
dependency order, runs tests after each one, and marks tasks done.

**7. Quality gate**

```bash
monolith checklist user-auth
```

Or in the chat:

```
/monolith.checklist
```

Only ship when every box is checked.

**8. Push tasks to GitHub Issues (optional)**

```bash
export GITHUB_TOKEN=ghp_...
monolith tasks-to-issues --repo your-org/your-repo --label feature
```

---

## Compressing command output

Wrap any command with `monolith run` so Claude sees compressed output instead of
thousands of lines of test/lint/build noise:

```bash
monolith run -- pytest -q                 # keeps failures + summary only (~90%)
monolith run -- ruff check .              # keeps diagnostics + counts
monolith run -- git status                # drops "(use …)" hint lines
monolith run -- npm test                  # same as pytest for JS
```

On failure, the full output is saved to `.monolith/tee/` and Claude gets a
pointer — it can read details without re-running the command.

Check cumulative savings:

```bash
monolith gain
```

---

## Tips

| Tip | Command |
|-----|---------|
| Update rules after switching tier | `monolith apply --agent claude` |
| Add a project-specific rule | `monolith rules add "Never edit files under vendor/."` |
| Re-scan repo for inline task tags | `monolith scan --apply` |
| See what's in CLAUDE.md | Open `CLAUDE.md` — the managed block is between the markers |
| Reset to defaults | Delete the managed block and re-run `monolith apply` |

### Custom rules

Add rules specific to your project without editing `CLAUDE.md` directly:

```bash
monolith rules add "Prefer pytest-style asserts."
monolith rules add "Never modify files under vendor/."
monolith apply --agent claude              # regenerate with new rules
```

---

## Reference

| File | What it is |
|------|-----------|
| `CLAUDE.md` | Token rules — auto-loaded by Claude Code; managed by Monolith |
| `.claude/commands/*.md` | Slash commands installed by `monolith hub install` |
| `.monolith/settings.json` | Active tier, target agents, custom rules |
| `.monolith/memory/constitution.md` | Project governance (written by `/monolith.constitution`) |
| `specs/<feature>/` | SDD artifact folder (spec, plan, tasks, data-model, contracts) |
| `TASKS.md` | Agent-readable task tree (generated by `monolith plan`) |
| `.monolith/tee/` | Full command output saved on failure by `monolith run` |

---

## Troubleshooting

**`monolith doctor` shows FAIL**
Run `monolith apply --agent claude`. The block is missing or the file doesn't
exist yet.

**Slash commands don't appear in Claude Code**
Check that `monolith hub install <id>` wrote to `.claude/commands/`. The file
must end in `.md`. Restart Claude Code if it was open during install.

**MCP server not connecting**
Run `claude mcp list` to confirm it's registered. Try `monolith mcp` directly in
a terminal to check for errors. See the experimental caveat above.

**Rules not taking effect**
Open `CLAUDE.md` and confirm the managed block is present. If you have a
`~/.claude/CLAUDE.md`, project rules override user-global rules — both apply.
