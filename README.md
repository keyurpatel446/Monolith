# 🧱 Monolith

> **One ruleset. Every agent. Fewer tokens.**

[![CI](https://github.com/keyurpatel446/Monolith/actions/workflows/ci.yml/badge.svg)](https://github.com/keyurpatel446/Monolith/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](pyproject.toml)
[![PRs welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](#-development--branching)
[![Buy me a coffee](https://img.shields.io/badge/Buy%20me%20a%20coffee-PayPal-00457C?logo=paypal&logoColor=white)](https://paypal.me/keyurpatel446)

Monolith is a small, dependency-free CLI that writes proven token-saving rules
into the native config file each AI coding agent already reads — so you author
the rules **once** and every agent obeys them:

| Agent | File Monolith generates |
|-------|-------------------------|
| Claude Code | `CLAUDE.md` |
| OpenAI Codex | `AGENTS.md` |
| GitHub Copilot | `.github/copilot-instructions.md` |

It also does **task management** (PRD → tracked tasks), ships a **resource hub**
of installable agent commands, and can **`shrink`** verbose tool output at
runtime — all from one tool.

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

Same answer. ~⅕ the tokens. (Measured by `monolith bench`; see [Comparison](#-how-does-it-compare-to-caveman--token-efficient).)

---

## 🪄 Why

Each agent reads instructions from a different file, so today you'd copy-paste
the same rules into three places and keep them in sync by hand. Monolith keeps
one canonical source and compiles it. Re-running is safe: managed content lives
between markers and never clobbers your own notes in the same file.

It synthesizes the best ideas from popular projects into one cross-agent tool:
filler removal (inspired by
[claude-token-efficient](https://github.com/drona23/claude-token-efficient)),
dense-output tiers (inspired by
[caveman](https://github.com/JuliusBrussee/caveman)), task management (inspired
by [claude-task-master](https://github.com/eyaltoledano/claude-task-master)),
and a resource hub (inspired by
[awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)).

## 📦 Install

Requires Python ≥ 3.9. Dependency-free core.

```bash
pipx install monolith-ai      # recommended (isolated)
# or
pip install monolith-ai
```

From source (current default until the first PyPI release is published):

```bash
git clone https://github.com/keyurpatel446/Monolith && cd Monolith
pip install -e .              # or: pip install -e ".[bench]" for exact token counts
```

## 🚀 Quickstart

```bash
monolith init                 # detect agents, create .monolith/settings.json
monolith apply --agent all    # write CLAUDE.md, AGENTS.md, copilot-instructions.md
monolith doctor               # verify each agent picked up the rules
monolith tier ultra --apply   # crank up compression
monolith bench                # measure real token reduction on the sample corpus
```

## 🧰 What you get

**Token efficiency**

| Command | Description |
|---------|-------------|
| `monolith init` | Detect agent files and create `.monolith/settings.json`. |
| `monolith apply [--agent all\|claude\|codex\|copilot\|config]` | Compile the directives into agent configs (idempotent). |
| `monolith tier [name] [--apply]` | Show or switch the active compression tier. |
| `monolith stats` | Show projected reduction, last measured reduction, and the input cost of the block. |
| `monolith bench` | Run the built-in benchmark corpus and record measured token reduction. |
| `monolith rules list\|add\|remove [value]` | Manage custom directives appended to every block. |
| `monolith doctor` | Verify each configured agent has the Monolith block. |

**Task management**

| Command | Description |
|---------|-------------|
| `monolith plan <prd-file> [--force]` | Parse a PRD/Markdown file into a task tree; writes `TASKS.md`. |
| `monolith tasks [--emit]` | List the task tree; `--emit` re-writes `TASKS.md`. |
| `monolith task <id> --status todo\|doing\|done` | Update a task's status (warns on unmet dependencies). |

**Resource hub & runtime**

| Command | Description |
|---------|-------------|
| `monolith hub list\|search <q>\|show <id>\|install <id> [--agent]` | Browse and install curated agent resources. |
| `monolith shrink [file] [--level lite\|full\|ultra]` | Compress verbose output (stdin or file) deterministically. |
| `monolith mcp` | Run the experimental MCP server exposing `shrink` over stdio. |
| `monolith compare` | Compare Monolith vs caveman / token-efficient (with provenance). |

Global flag `--root <dir>` runs against another project directory.

## 🎚️ Tiers

| Tier | Intensity | Projected output reduction* |
|------|-----------|-----------------------------|
| `lite` | filler removal only | ~25–35% |
| `full` (default) | filler + dense formatting + no over-engineering | ~55–65% |
| `ultra` | telegraphic, bullet-first, every directive | ~60–70% |

\* Projections derived from upstream benchmarks, not per-project measurements.
Run `monolith bench` for a figure measured on the sample corpus.

## 📊 How does it compare to caveman / token-efficient?

Run `monolith compare` for a provenance-tagged table. Honest summary:

| Approach | Input overhead* | Output reduction |
|----------|-----------------|------------------|
| Normal (no tool) | 0 | 0% (baseline) |
| claude-token-efficient | low | ~63% (their published figure) |
| caveman | low | ~65% avg (their published figure) |
| **Monolith** (full tier) | higher (more rules) | **80% measured** on its corpus |

\* Input overhead is measured here for every approach with the same tokenizer.
Output reduction marked "measured" is Monolith's own corpus; the others are each
project's **published** number. This is **not** a single-model head-to-head
(impossible offline), so treat the three as comparable (~60–80%) rather than
ranking them by a few points. Monolith's edge is breadth — one cross-agent tool
that also does tasks, a resource hub, and runtime `shrink`.

## 🗂️ Task management

Point `monolith plan` at a PRD or any structured Markdown file. Headings and
list items become tasks; nesting becomes parent/child. Wire up dependencies
with inline tags — `{#slug}` names a task and `@after:slug` depends on it:

```markdown
# Auth feature
- Design DB schema {#schema}
- Build API @after:schema
  - Add input validation
## Release @after:schema
```

`monolith plan prd.md` writes a shared task store under `.monolith/tasks/` and a
root `TASKS.md` your agents read as ordinary project context.

## 📚 Documentation

- [Usage guide](docs/USAGE.md)
- Per-agent setup: [Claude Code](docs/agents/claude-code.md) ·
  [Codex](docs/agents/codex.md) · [Copilot](docs/agents/copilot.md)
- [Roadmap](ROADMAP.md) · [Changelog](CHANGELOG.md) · [Contributing](CONTRIBUTING.md)
- Demo: run `bash scripts/demo.sh` (record with asciinema)

## 🌱 Development & branching

| Branch | Purpose |
|--------|---------|
| `master` | Default / release branch. Merges here trigger CI to tag a release. |
| `develop` | Integration branch for completed features. |
| `fetcher/<name>` | Feature work. |
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
