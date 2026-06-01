# Blog post (dev.to / Hashnode)

**Title**: One ruleset for Claude Code, Codex and Copilot — cutting AI output tokens ~60–80%

**Tags**: ai, productivity, opensource, python

---

## The problem

Modern dev teams rarely use just one AI coding assistant. You might use Claude
Code in the terminal, Codex in one editor, and GitHub Copilot in another. Each
one reads its project instructions from a *different* file:

- Claude Code → `CLAUDE.md`
- OpenAI Codex → `AGENTS.md`
- GitHub Copilot → `.github/copilot-instructions.md`

If you want all three to "stop greeting me, answer directly, don't over-engineer"
— rules that genuinely cut output tokens and cost — you end up maintaining the
same content in three places.

## The idea

[Monolith](https://github.com/keyurpatel446/Monolith) keeps **one** canonical
ruleset and compiles it into each agent's native file. Author once; every agent
obeys.

```bash
pipx install monolith-ai
monolith init               # detect agents, create .monolith/settings.json
monolith apply --agent all  # write all three config files
monolith doctor             # verify each picked it up
```

Writes are idempotent and non-destructive: the generated content lives between
`<!-- monolith:start -->` / `<!-- monolith:end -->` markers, so your own notes in
the same file are never touched.

## Tiers

Three intensity levels let you trade politeness for tokens:

| Tier | What it does |
|------|--------------|
| `lite` | strip greetings/closers/filler |
| `full` | + dense formatting, no over-engineering |
| `ultra` | telegraphic, bullet-first |

## Show me the numbers (honestly)

`monolith bench` measures real reduction on a built-in corpus of verbose/concise
response pairs (exact counts with `tiktoken` if installed, heuristic otherwise):

```
TOTAL  394 -> 77 tokens  (80%)
```

That 80% is on *the sample corpus*, not your prompts — and I'm careful not to
oversell it. `monolith compare` puts Monolith next to
[caveman](https://github.com/JuliusBrussee/caveman) and
[claude-token-efficient](https://github.com/drona23/claude-token-efficient),
clearly labelling which numbers are **measured** here vs each project's
**published** figure. The takeaway: they're all in the ~60–80% range. Monolith's
edge isn't a higher percentage — it's being one tool across three agents.

## Beyond rules

Because the same "one source, compile everywhere" idea is useful elsewhere,
Monolith also includes:

- `plan` — parse a PRD/Markdown file into a tracked task tree (`{#slug}` /
  `@after:` dependencies), emitting a `TASKS.md` your agents read.
- `hub` — browse and install curated, token-frugal agent commands/prompts.
- `shrink` — deterministically compress verbose tool output (logs, JSON) to save
  tokens, plus an experimental MCP server.

## Try it

It's MIT-licensed with a dependency-free core. Repo and docs:
**https://github.com/keyurpatel446/Monolith**

If you find a claim too strong or a rule that hurts more than it helps, open an
issue — honest feedback is the whole point.
