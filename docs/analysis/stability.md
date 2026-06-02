# Stability & 1.0 readiness

A candid audit of whether Monolith is ready to declare a stable `1.0.0` (which
commits us to API/CLI stability under SemVer). **Recommendation: not yet** —
finish the items below first. Stay on `0.1.x`.

## Snapshot

- ~2,640 lines across 18 modules; **73 tests passing** on Python 3.9/3.11/3.12.
- No `eval`/`exec`/`os.system`/`pickle`; `run` uses `subprocess` with
  `shell=False` (see `SECURITY.md`).
- No bare `except:`, no `TODO`/`FIXME`/`XXX` in `src/`.
- 16 commands; CI tags + releases on merge to `master`.

## What's solid

- Core compile path (`init`/`apply`/`tier`/`doctor`) — idempotent, well-tested.
- Test-runner compression and generic `shrink` — strong, measured (benchmarks).
- Release pipeline, docs, security policy, contributor docs.

## 1.0 blockers / gaps

| # | Item | Why it blocks 1.0 |
|---|------|-------------------|
| 1 | **Lint compressor ~1% effective** | Claimed feature that barely works; needs grouping (benchmarks.md). |
| 2 | **MCP server is experimental** | Live stdio loop unvalidated against real clients; mark clearly or stabilize. |
| 3 | **No direct tests** for `tokens`, `settings`, `compression`, `directives`, `mcp_server` | Coverage gaps on the stable surface. (Indirectly exercised, but no unit tests.) |
| 4 | **No real-world usage data** | Savings are measured on synthetic/sample outputs, not aggregated real sessions. |
| 5 | **CLI surface not frozen** | `tier` vs `profile`, flag names, output formats may still change — fine in 0.x, must settle for 1.0. |
| 6 | **PyPI not yet published** | A stable release should be installable as `pip install monolith-ai`. |
| 7 | **Windows behaviour unverified** | SIGPIPE/paths guarded but untested on Windows. |

## Proposed path to 1.0

1. Fix the lint compressor (grouping) and re-measure.
2. Add unit tests for the five untested modules; target a coverage number.
3. Decide MCP: stabilize or label it `experimental` in `--help` and docs.
4. Collect real-world `gain` data across a battery of commands (see
   `benchmarks.md`); publish a methodology + numbers.
5. Freeze the CLI surface; document any renames; add a deprecation policy.
6. Publish to PyPI (Trusted Publishing already configured in the workflow).
7. Smoke-test on Windows (or document the support matrix).

When 1–6 are done, cut **1.0.0** and start honoring SemVer for the CLI.
