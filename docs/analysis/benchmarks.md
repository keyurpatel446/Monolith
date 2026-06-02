# Benchmark analysis

Measured token reduction per command compressor, with a reproducible method.
**Honest framing:** these are measured on *representative synthetic outputs*
(described below), with the heuristic counter (`~4 chars/token`). They show the
shape of the savings, not a guarantee for your exact output. Install the
`[bench]` extra for exact `tiktoken` counts.

## Method

For each case we build a realistic command output, run it through the matching
`compress_for(argv, text)` compressor (or `shrink` for the generic case), and
compute `1 - out_tokens / in_tokens`. The generator is in the repo history; to
re-run, adapt the snippet in `docs/analysis/` or call `compress_for` directly.

## Results (measured)

| Case | in (tok) | out (tok) | saved |
|------|---------:|----------:|------:|
| pytest — 200 tests, 1 failure | 2173 | 44 | **98%** |
| generic log — repeated lines + blanks (`shrink full`) | 202 | 14 | **93%** |
| `git status` — dirty tree, hints | 154 | 103 | 33% |
| grep — 40 matches across 4 files | 565 | 384 | 32% |
| find — 80 files across 6 dirs | 437 | 300 | 31% |
| eslint — 50 files, 100 problems | 1588 | 1576 | **1% ⚠️** |

## Findings

- **Test runners are the headline win (~90–98%).** Discarding passing lines is
  hugely effective and safe (failures + summary retained; full log tee'd on
  failure). This is where Monolith already matches rtk.
- **Generic `shrink` is strong on repetitive output (~90%+)** — logs with many
  identical lines, blank runs, ANSI. Weak on output that is already unique/dense
  (it can only fold *identical* lines).
- **git/grep/find land ~30%.** Useful but modest: git drops hint chatter; grep
  drops repeated path prefixes; find groups by directory. Savings scale with the
  amount of repetition (more matches per file / files per dir → more savings).
- **lint is currently weak (~1%).** ⚠️ eslint's default output is *already*
  mostly diagnostics, so line-filtering barely helps. Real savings require
  **grouping** (e.g. `file: 2 errors, 1 warning [no-unused-vars, no-console]`),
  which we don't do yet. **This is a v0.2 fix and a 1.0 blocker for the lint
  claim.**

## Implications for claims

- Safe to claim: ~90% on test output; ~60–80% on verbose/dense agent *responses*
  (the rules side, separate corpus); strong savings on repetitive logs.
- Do **not** claim big savings for lint until grouping lands.
- Headline "~60–90% depending on command" is defensible; per-command numbers are
  in this table.
