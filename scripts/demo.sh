#!/usr/bin/env bash
# Scripted Monolith demo — ideal for recording an asciinema cast or a GIF.
#
#   Record:   asciinema rec monolith-demo.cast -c "bash scripts/demo.sh"
#   To GIF:   agg monolith-demo.cast monolith-demo.gif   (https://github.com/asciinema/agg)
#
# Runs in a throwaway temp directory so it never touches your repo.
set -euo pipefail

step() { printf '\n\033[1;36m$ %s\033[0m\n' "$*"; "$@"; sleep 1; }

DEMO_DIR="$(mktemp -d)"
trap 'rm -rf "$DEMO_DIR"' EXIT
cd "$DEMO_DIR"

printf '\033[1;33m# Monolith: one ruleset for Claude Code, Codex & Copilot\033[0m\n'
sleep 1

step monolith init
step monolith apply --agent all
step monolith doctor
step monolith bench
step monolith tier ultra --apply

printf '\n\033[1;33m# Plan tasks from a PRD\033[0m\n'
printf '# Auth feature\n- Design schema {#schema}\n- Build API @after:schema\n' > prd.md
step monolith plan prd.md
step monolith tasks

printf '\n\033[1;32m# Done. https://github.com/keyurpatel446/Monolith\033[0m\n'
