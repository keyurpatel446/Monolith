# Security Policy

## Reporting a vulnerability

Please report security issues privately via GitHub Security Advisories
("Report a vulnerability" on the repo's **Security** tab), or by email to
keyurpatel446@gmail.com. We aim to acknowledge reports within a few days.
Please do not open a public issue for undisclosed vulnerabilities.

## Supported versions

Monolith is pre-1.0; only the latest released version receives fixes.

## Security model

Monolith is a local, offline CLI with a deliberately small attack surface:

- **No code execution.** The codebase contains no `eval`, `exec`, `subprocess`,
  `os.system`, `pickle`, or dynamic import of untrusted input. Parsing (PRD,
  tags, JSON-RPC) is pure data handling.
- **No network in the core.** The only optional network dependency is
  `tiktoken` (the `[bench]` extra); if its encoding can't be fetched, Monolith
  falls back to a heuristic counter.
- **Scoped, non-destructive writes.** Generated content in `CLAUDE.md`,
  `AGENTS.md`, and `.github/copilot-instructions.md` lives between
  `<!-- monolith:start -->` / `<!-- monolith:end -->` markers; only that block is
  rewritten. Files are written to fixed paths under `--root` (no path traversal
  from user input). `TASKS.md` is fully generated and overwritten.
- **Filesystem scanning is read-only and bounded.** `monolith scan` walks the
  project with `os.walk` (symlinks are **not** followed), skips VCS/build dirs,
  and ignores files over ~1 MB or that aren't valid UTF-8.

## Things to be aware of

- **`monolith scan --apply` ingests repository content into agent context.**
  `@monolith:rule` tags become directives written into your agents' config, and
  `@monolith:task` tags become tasks. Treat this like any other code you run:
  **do not run `scan --apply` on a repository you don't trust**, since a
  malicious `@monolith:rule` could inject instructions into your agents. The
  default `monolith scan` is a dry run that only reports.
- **The MCP server (`monolith mcp`) is a local stdio process.** It exposes only
  a `shrink` text-compression tool and performs no file or network access. Run
  it only from agents you control.
- Generated agent files and `TASKS.md` are produced from your inputs; review
  them before committing, as with any generated artifact.
