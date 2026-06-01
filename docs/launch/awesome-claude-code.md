# awesome-claude-code submission

Target: https://github.com/hesreallyhim/awesome-claude-code

> Note: that repo is being reorganised — check its current `CONTRIBUTING` and
> category structure before submitting, and match the existing entry format.

## Suggested entry (Markdown)

```markdown
- [Monolith](https://github.com/keyurpatel446/Monolith) — Author your
  token-efficiency rules once and compile them into `CLAUDE.md`, plus Codex
  `AGENTS.md` and Copilot instructions. Dependency-free CLI with compression
  tiers, measured benchmarking, PRD→task planning, a resource hub, and runtime
  output `shrink`. MIT.
```

## Suggested PR title

> Add Monolith — cross-agent token-efficiency CLI (rules, bench, tasks, hub, shrink)

## Suggested PR body

```
Adding Monolith, a dependency-free CLI that compiles one token-efficiency
ruleset into Claude Code (CLAUDE.md), OpenAI Codex (AGENTS.md), and GitHub
Copilot config. It also includes measured benchmarking (`bench`/`compare`),
PRD→task planning (`plan`), a curated resource hub (`hub`), and deterministic
runtime output compression (`shrink`) with an experimental MCP server.

- Repo: https://github.com/keyurpatel446/Monolith
- License: MIT
- Core is stdlib-only; tiktoken is an optional extra.

I've tried to keep the docs honest — the README and a `compare` command label
measured vs published reduction figures rather than claiming a head-to-head win.
```

## How to submit

The GitHub tooling in this project is scoped to `keyurpatel446/Monolith`, so the
PR to `hesreallyhim/awesome-claude-code` has to be opened from your account:

1. Fork `hesreallyhim/awesome-claude-code`.
2. Add the entry above to the right category (follow their `CONTRIBUTING`).
3. Open the PR using the title/body above.

Other catalogs worth submitting to: awesome-ai-coding, awesome-cli-apps,
and any Codex/Copilot resource lists.
