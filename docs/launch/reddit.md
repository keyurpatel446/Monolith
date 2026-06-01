# Reddit

Lead with the problem, not the self-promo. Read each sub's self-promotion rules
first. Good fits: r/ClaudeAI, r/ChatGPTCoding, r/LocalLLaMA, r/commandline.

**Title**
> I got tired of maintaining 3 different "be concise" config files for Claude Code, Codex and Copilot — so I made one tool that compiles them

**Body**

If you use more than one AI coding agent, you've probably noticed each reads its
instructions from a different file: `CLAUDE.md`, `AGENTS.md`,
`.github/copilot-instructions.md`. Keeping the same token-saving rules in sync
across them is annoying.

Monolith is a tiny Python CLI that keeps one ruleset and compiles it into all
three (idempotent, never clobbers your own notes):

```
pipx install monolith-ai
monolith init
monolith apply --agent all
```

Tiers (`lite`/`full`/`ultra`) control how aggressive the "no filler, answer
directly, dense formatting" rules are. `monolith bench` shows measured token
reduction; `monolith compare` puts it next to caveman and token-efficient.

Honest take: compression is comparable to those tools (~60–80%); the point isn't
a higher percentage, it's not maintaining three files. It also does PRD→task
planning and runtime output `shrink` if you want them.

MIT, stdlib-only core. Repo: https://github.com/keyurpatel446/Monolith — would
love feedback on the rules themselves.
