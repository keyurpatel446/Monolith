# X/Twitter + LinkedIn

## X / Twitter thread

**1/**
You use Claude Code, Codex, AND Copilot.
Each reads its rules from a different file.
You copy-paste "be concise" into all three and keep them in sync by hand. 😮‍💨

Meet Monolith: write the rules once, compile them everywhere. 🧱
🔗 github.com/keyurpatel446/Monolith

**2/**
```
pipx install monolith-ai
monolith init
monolith apply --agent all
```
→ writes CLAUDE.md, AGENTS.md, and .github/copilot-instructions.md.
Idempotent: it only edits between markers, so your own notes stay put.

**3/**
Three tiers — lite / full / ultra — control how hard it compresses output.
`monolith bench` measures the real reduction (~60–80%).
`monolith compare` shows it next to caveman & token-efficient, with provenance.

**4/**
It's not just rules:
• `plan` → turn a PRD into a tracked task tree (TASKS.md)
• `hub` → install curated agent commands
• `shrink` → compress verbose tool output deterministically

**5/**
Honest bit: compression is *comparable* to existing tools, not magically better.
The win is breadth — one cross-agent tool — not a bigger %.
Stdlib-only core. MIT. ⭐ if it's useful: github.com/keyurpatel446/Monolith

## LinkedIn

If your team uses more than one AI coding assistant, you're probably maintaining
the same "be concise, no filler" instructions in three different config files —
one each for Claude Code, OpenAI Codex, and GitHub Copilot.

I built **Monolith**, an open-source CLI that keeps a single ruleset and compiles
it into each agent's native format. One command and every agent follows the same
token-saving rules — cutting output tokens (and cost) by roughly 60–80%
depending on the tier.

It also does measured benchmarking, PRD-to-task planning, a resource hub, and
runtime output compression. Dependency-free core, MIT-licensed, and deliberately
honest about its numbers (it ships a `compare` command that labels measured vs
published figures).

Repo + docs: https://github.com/keyurpatel446/Monolith
Feedback and contributions welcome. #AI #DeveloperTools #OpenSource #LLM
