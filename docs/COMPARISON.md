# Comparison

How Monolith relates to the projects that inspired it. **Honest framing:** on raw
output compression, Monolith is *comparable* to caveman and token-efficient
(~60–80%), not dramatically better. Its distinguishing trait is **breadth** —
one cross-agent tool that also does tasks, a resource hub, and runtime
compression. Run `monolith compare` for a provenance-tagged, live version of the
overlap.

## Feature matrix

| Capability | **Monolith** | [caveman](https://github.com/JuliusBrussee/caveman) | [claude-token-efficient](https://github.com/drona23/claude-token-efficient) | [claude-task-master](https://github.com/eyaltoledano/claude-task-master) | [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code) |
|---|---|---|---|---|---|
| Token-saving rules | ✅ | ✅ | ✅ | ❌ | ❌ |
| Cross-agent (Claude Code + Codex + Copilot) | ✅ one source → 3 files | ➖ Claude-first (broad agent compat) | ➖ a `CLAUDE.md` | ➖ MCP/editors | n/a |
| Compression tiers | ✅ lite/full/ultra | ✅ lite/full/ultra/wenyan | ➖ profiles | ❌ | ❌ |
| Measured benchmark | ✅ `bench` (+ honest `compare`) | ✅ published benchmarks | ✅ published benchmark | ❌ | ❌ |
| Task management (PRD → tasks) | ✅ `plan`/`tasks`/`task` | ❌ | ❌ | ✅ (its focus) | ❌ |
| Resource hub / catalog | ✅ `hub` | ➖ ecosystem tools | ❌ | ❌ | ✅ (its focus, curated list) |
| Runtime output compression | ✅ `shrink` + experimental MCP | ✅ `caveman-shrink` (MCP) | ❌ | ❌ | ❌ |
| Custom rules from CLI | ✅ `rules` | ✅ | ➖ edit file | n/a | n/a |
| Dependencies | stdlib-only (tiktoken optional) | Node ≥18 | none (a file) | Node/npm | n/a |
| Language | Python | JS/Python/Shell | Markdown | JS/TS | Markdown |
| License | MIT | MIT | MIT | MIT w/ commons clause* | — |

➖ = partial / different scope. \*Check each project's current license terms.

## Output reduction (provenance matters)

| Approach | Output reduction | Source |
|----------|------------------|--------|
| Normal (no tool) | 0% | baseline |
| claude-token-efficient | ~63% | their published benchmark |
| caveman | ~65% avg (up to ~76%) | their published benchmark |
| **Monolith** (full tier) | **80% measured** on its sample corpus | `monolith bench` |

This is **not** a single-model head-to-head (impossible offline). Treat the
three rule-based tools as comparable; the Monolith number is measured on its own
corpus, the others are each project's published figure.

## When to pick what

- **Want one config that works across Claude Code, Codex, and Copilot, plus
  tasks/hub/shrink in a dependency-free CLI** → Monolith.
- **All-in on Claude Code and want the most mature output-compression ecosystem
  (subagents, MCP shrink, memory compression)** → caveman.
- **Just want a drop-in `CLAUDE.md` and nothing else** → claude-token-efficient.
- **Heavy, multi-model task/PRD management as the primary job** →
  claude-task-master (deeper than Monolith's task module today).
- **Browsing for skills/commands/hooks to install** → awesome-claude-code
  (Monolith's `hub` is a small curated subset, not a catalog of the ecosystem).

Monolith borrows the best idea from each and unifies them; it does not try to be
deeper than each specialist in that specialist's lane.
