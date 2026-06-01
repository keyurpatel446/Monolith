# Hacker News — Show HN

**Title**
> Show HN: Monolith – one token-saving ruleset for Claude Code, Codex and Copilot

**URL**
> https://github.com/keyurpatel446/Monolith

**First comment (post immediately after submitting)**

I kept copy-pasting the same "be concise, no filler" instructions into three
different files — `CLAUDE.md` for Claude Code, `AGENTS.md` for Codex, and
`.github/copilot-instructions.md` for Copilot — and keeping them in sync by hand.

Monolith is a small, dependency-free Python CLI that keeps one canonical ruleset
and compiles it into each agent's native file (idempotently — it only edits
between markers, so your own notes are safe). `monolith init && monolith apply
--agent all` and you're done.

It also grew a few things around that: `bench` measures real token reduction on
a sample corpus, `compare` puts it next to caveman / claude-token-efficient
(with provenance — see below), `plan` turns a PRD into a tracked task tree, and
`shrink` compresses verbose tool output deterministically.

Honesty notes, because HN will (rightly) ask:
- Output reduction is ~60–80% depending on tier. The 80% figure is measured on
  *my* sample corpus with a heuristic counter (or tiktoken if installed), not
  your prompts.
- I do **not** claim to beat caveman/token-efficient on compression — they're in
  the same ballpark. Monolith's only real edge is breadth: one tool across three
  agents, plus tasks/hub/shrink. `monolith compare` labels every number as
  measured vs published.

Core is stdlib-only. MIT. Feedback (especially "this claim is too strong")
very welcome.
