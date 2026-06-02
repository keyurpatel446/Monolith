# 🧱 Monolith

> **One ruleset. Every agent. Spec to ship.**

[![CI](https://github.com/keyurpatel446/Monolith/actions/workflows/ci.yml/badge.svg)](https://github.com/keyurpatel446/Monolith/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-development--branching)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-PayPal-00457C?logo=paypal&logoColor=white)](https://paypal.me/keyurpatel446)

**Monolith is a dependency-free CLI that unifies three concerns for AI-assisted
development:**

1. **Token efficiency** — compile one ruleset into Claude Code, OpenAI Codex,
   and GitHub Copilot's native config files. ~55–70% fewer output tokens.
2. **Spec-Driven Development** — a full `constitution → specify → clarify →
   plan → analyze → tasks → implement` pipeline with structured
   `specs/<feature>/` artifacts.
3. **Runtime compression** — wrap any command with `monolith run` to compress
   its output before the agent reads it.

| Agent | File Monolith manages |
|-------|-----------------------|
| Claude Code | `CLAUDE.md` |
| OpenAI Codex | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |

---

## ⚡ Before / After

**Without Monolith** — _84 tokens_
> Great question! I'd be happy to help you figure this out. So, the reason your
> function is returning `None` is actually because there's no explicit return
> statement at the end of the branch. What you'll want to do here is make sure
> you return the computed value. I hope this helps, and let me know if you have
> any other questions!

**With Monolith** — _19 tokens (−77%)_
> It returns `None` because that branch has no return. Return the computed value.

Same answer. ~⅕ the tokens. (Measured by `monolith bench`.)

---

## 📦 Install

Requires Python ≥ 3.9. Dependency-free core.

```bash
pipx install monolith-ai      # recommended (isolated)
# or
pip install monolith-ai
```

From source:

```bash
git clone https://github.com/keyurpatel446/Monolith && cd Monolith
pip install -e .              # or: pip install -e ".[bench]" for exact token counts
```

---

## 🚀 Quickstart

### Token efficiency (2 minutes)

```bash
monolith init                 # detect agents, create .monolith/settings.json
monolith apply --agent all    # write CLAUDE.md, AGENTS.md, copilot-instructions.md
monolith doctor               # verify each agent picked up the rules
monolith stats                # see projected savings + input cost
```

### Spec-Driven Development

```bash
monolith constitution                      # scaffold .monolith/memory/constitution.md
monolith specify user-auth                 # scaffold specs/user-auth/spec.md
monolith specify user-auth --plan \
  --data-model --contracts                 # scaffold all artifacts at once
monolith analyze user-auth                 # check spec ↔ plan ↔ tasks consistency
monolith checklist user-auth               # quality gate before shipping
```

Install the SDD slash commands so any agent can run the workflow:

```bash
monolith hub install monolith.constitution
monolith hub install monolith.specify
monolith hub install monolith.clarify
monolith hub install monolith.analyze
monolith hub install monolith.checklist
monolith hub install monolith.implement
```

---

## 🧰 What you get

### Token efficiency

| Command | Description |
|---------|-------------|
| `monolith init` | Detect agent files and create `.monolith/settings.json`. |
| `monolith apply [--agent all\|claude\|codex\|copilot\|config]` | Compile directives into agent configs (idempotent). |
| `monolith tier [name] [--apply]` | Show or switch the active compression tier. |
| `monolith stats` | Projected + measured reduction and input cost per file. |
| `monolith bench` | Run the benchmark corpus and record measured token reduction. |
| `monolith rules list\|add\|remove [value]` | Manage custom directives appended to every block. |
| `monolith doctor` | Verify each configured agent has the Monolith block. |

### Spec-Driven Development (SDD)

| Command | Description |
|---------|-------------|
| `monolith constitution` | Scaffold `.monolith/memory/constitution.md` — mission, principles, definition of done. |
| `monolith specify <feature> [--plan] [--data-model] [--contracts]` | Scaffold `specs/<feature>/` with templated artifact files. |
| `monolith analyze [feature]` | Structural cross-artifact check: spec ↔ plan ↔ tasks. Exits 1 on errors. |
| `monolith checklist <feature> [--write]` | Generate a quality gate checklist pre-checked against existing artifacts. |

### Task management

| Command | Description |
|---------|-------------|
| `monolith plan <prd-file> [--force]` | Parse a PRD/Markdown file into a task tree; writes `TASKS.md`. |
| `monolith tasks [--emit]` | List the task tree; `--emit` re-writes `TASKS.md`. |
| `monolith task <id> --status todo\|doing\|done` | Update a task's status (warns on unmet dependencies). |

### Resource hub & runtime

| Command | Description |
|---------|-------------|
| `monolith hub list\|search\|show\|install` | Browse and install curated agent resources (SDD commands + utilities). |
| `monolith shrink [file] [--level lite\|full\|ultra]` | Compress verbose output deterministically. |
| `monolith run -- <command>` | Run a command, compress its output, save full output on failure. |
| `monolith gain` | Show cumulative token savings from `run`. |
| `monolith mcp` | Experimental MCP server exposing `shrink` over stdio. |
| `monolith scan [--apply]` | Scan repo for `@monolith:` task/rule tags and apply them. |

Global flag `--root <dir>` runs against another project directory.

---

## 🗺️ SDD pipeline

Monolith ships a full Spec-Driven Development workflow as both CLI commands and
installable slash commands (cross-agent via the hub).

```
constitution → specify → clarify → plan → analyze → tasks → implement
```

Each feature gets a structured folder:

```
specs/
└── user-auth/
    ├── spec.md          # requirements + user stories + acceptance criteria
    ├── plan.md          # architecture + stack decisions + edge cases
    ├── tasks.md         # actionable task breakdown with @after: deps
    ├── data-model.md    # entity definitions + relationships
    ├── checklist.md     # quality gate (auto-generated)
    └── contracts/
        └── README.md    # API contract convention + per-endpoint files
```

Every slash command (e.g. `/monolith.specify`) installs into `.claude/commands/`,
`.codex/prompts/`, and `.github/prompts/` simultaneously — author once, run anywhere.

```bash
monolith hub list              # see all SDD commands + utilities
monolith hub show monolith.specify
```

---

## 🎚️ Tiers

| Tier | Intensity | Projected output reduction* |
|------|-----------|-----------------------------|
| `lite` | filler removal only | ~25–35% |
| `full` (default) | filler + dense formatting + no over-engineering | ~55–65% |
| `ultra` | telegraphic, bullet-first, every directive | ~60–70% |

\* Projections derived from upstream benchmarks. Run `monolith bench` for a
figure measured on the sample corpus.

---

## 🗂️ Task management

Point `monolith plan` at a PRD or any structured Markdown file. Headings and
list items become tasks; nesting becomes parent/child. Wire up dependencies with
inline tags — `{#slug}` names a task and `@after:slug` depends on it:

```markdown
# Auth feature
- Design DB schema {#schema}
- Build API @after:schema
  - Add input validation
## Release @after:schema
```

`monolith plan prd.md` writes a shared task store under `.monolith/tasks/` and
a root `TASKS.md` your agents read as ordinary project context.

For per-feature task tracking, put the PRD in `specs/<feature>/spec.md` and
use `monolith analyze <feature>` to check coverage.

---

## 📚 Documentation

- [Usage guide](docs/USAGE.md) · [Capabilities](docs/CAPABILITIES.md)
- Per-agent setup: [Claude Code](docs/agents/claude-code.md) ·
  [Codex](docs/agents/codex.md) · [Copilot](docs/agents/copilot.md)
- [Roadmap](ROADMAP.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md) · [Publishing](docs/PUBLISHING.md)
- [Analysis](docs/analysis/) — benchmarks, competitor & stability analysis
- Demo: run `bash scripts/demo.sh` (record with asciinema)

---

<sub>Keywords: reduce Claude Code token usage · Codex `AGENTS.md` token efficiency ·
GitHub Copilot instructions to save tokens · compress AI command/test output for
LLMs · cross-agent token optimization CLI · spec-driven development workflow ·
one config for Claude Code, Codex and Copilot.</sub>

## 🌱 Development & branching

| Branch | Purpose |
|--------|---------|
| `master` | Default / release branch. Merges here trigger CI to tag a release. |
| `develop` | Integration branch for completed features. |
| `feature/<name>` | Feature work. |
| `fix/<name>` | Bug fixes. |

CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs the test suite
on every push/PR to `master` and `develop`. When code is merged to `master`, it
reads the version from `pyproject.toml` and, if a matching tag does not yet
exist, creates the tag `vX.Y.Z` and a GitHub release. Bump `version` in
`pyproject.toml` to cut a new release.

```bash
python -m unittest discover -s tests -v   # run the tests locally
```

## ☕ Support

Monolith is free and MIT-licensed. If it saves you tokens (and money), consider
chipping in for a coffee — it genuinely helps keep the project moving. 🙏

[![Buy me a coffee via PayPal](https://img.shields.io/badge/☕%20Buy%20me%20a%20coffee-PayPal-00457C?logo=paypal&logoColor=white&style=for-the-badge)](https://paypal.me/keyurpatel446)

> 👉 **[paypal.me/keyurpatel446](https://paypal.me/keyurpatel446)**

## 📄 License

MIT © Keyur Patel
