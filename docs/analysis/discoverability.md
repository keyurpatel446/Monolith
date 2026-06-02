# Discoverability analysis (why it's not on Google, and the fix)

## Diagnosis

A brand-new repo named **Monolith** is hard to find for structural reasons, not
a single bug:

1. **Indexing lag** — Google takes days–weeks to crawl a new repo. Unavoidable.
2. **Name collision (the ceiling)** — "monolith" collides with the `monolith`
   web-archiver, monorepo tooling, and the architecture term. You will **not**
   rank for "monolith". This caps everything else.
3. **No backlinks** — nothing links in, so crawlers rarely visit and ranking
   signals are ~0. PyPI, awesome-lists, Show HN, a blog post are what fix this.
4. **Metadata unset** — GitHub About description/topics drive GitHub's *own*
   search and rich snippets; set them (see `docs/ABOUT.md`).
5. **No package / site** — `pypi.org/project/monolith-ai` and a GitHub Pages site
   are independently indexable and rank fast.

## What moves the needle (priority)

| Lever | Owner | Impact | Status |
|-------|-------|--------|--------|
| Publish to PyPI | you | high (fast index + backlink) | pending Trusted Publisher |
| Set GitHub topics + About | you | high (GitHub search) | pending |
| Target *phrases*, not "monolith" | both | high | this doc + README SEO |
| Backlinks (awesome-list PR, Show HN, blog) | you post / me draft | high over weeks | drafts in `docs/launch/` |
| GitHub Pages site w/ good titles | me/you | medium-high | proposed |
| Social preview image | you | medium (CTR on shares) | pending |

## Rebrand-for-search: analysis + recommendation

**The honest trade-off:** the repo name is the single biggest SEO limiter, but
renaming costs stars/history/links and is disruptive.

Two viable paths:

- **A. Keep "Monolith", win on phrases (recommended for now).** Don't rename.
  Brand consistently as **"Monolith AI"**, lean on the unique package name
  `monolith-ai`, and optimize all copy for the *search phrases* below. Cheap,
  non-disruptive, and good enough once PyPI + backlinks exist.
- **B. Coin a unique name (only if SEO is a top priority).** A distinctive,
  low-collision name ranks far better. Candidates to vet for availability on
  GitHub + PyPI: `tokenkeep`, `leanrules`, `agentcompress`, `tokensmith`,
  `fewtoken`. Cost: rename repo (GitHub redirects old URLs), republish, rebuild
  links. Recommend only if you're committed to chasing organic search.

> Recommendation: **Path A now**, revisit Path B before 1.0 if organic traffic
> matters. I can check name availability for Path B candidates on request.

## Target search phrases (use these in README, Pages, posts)

People don't search "monolith". They search:
- "reduce Claude Code token usage"
- "Codex AGENTS.md token efficiency"
- "GitHub Copilot instructions to save tokens"
- "compress AI command output / test output for LLM"
- "cross-agent token optimization CLI"
- "claude code codex copilot one config"

Each should appear naturally in the README, the Pages site `<title>`/headings,
and post titles.

## Backlink targets

- `hesreallyhim/awesome-claude-code` (PR text in `docs/launch/awesome-claude-code.md`)
- awesome-ai-coding, awesome-cli-apps, awesome-llmops
- Show HN + r/ClaudeAI + dev.to (drafts in `docs/launch/`)
- PyPI page (auto once published) and a GitHub Pages site

## Your checklist (only you can do these)

1. **PyPI**: configure the Trusted Publisher (`docs/PUBLISHING.md`) so a release
   publishes; this is the highest-leverage single action.
2. **GitHub → About**: paste the description + the topics from `docs/ABOUT.md`.
3. **Settings → default branch → `master`**; delete `claude/fervent-pascal-AZ8u2`.
4. **Settings → Social preview**: upload a 1280×640 image (logo + tagline +
   before/after numbers).
5. **Enable GitHub Pages** (Settings → Pages → from `/docs` or a Pages workflow)
   once the site lands.
6. Post the `docs/launch/` content (space them out) and open the awesome-list PR
   from your account.
