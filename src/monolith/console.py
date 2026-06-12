"""Monolith command-line console.

Sub-commands
------------
    init            detect agents in the repo and create .monolith/settings.json
    setup           one-shot onboarding: init + apply + doctor
    apply           compile the directives into each agent's native config file
    tier            show or switch the active compression tier
    stats           show projected + last-measured token savings for the active tier
    bench           run the benchmark corpus and record measured token reduction
    rules           list / add / remove custom directives (extra_rules)
    scan            scan the repo for @monolith: tags and apply them
    constitution    scaffold .monolith/memory/constitution.md
    specify         scaffold specs/<feature>/ artifact files
    analyze         validate cross-artifact consistency for a feature
    checklist       generate a quality checklist for a feature
    plan            parse a PRD/Markdown file into a task tree (writes TASKS.md)
    tasks           list the task tree (optionally re-emit TASKS.md)
    task            update a single task's status
    tasks-to-issues push tasks to GitHub Issues via the API
    hub             browse and install curated agent resources
    shrink          compress verbose text/output deterministically
    run             run a command and compress its output (tee full output on failure)
    gain            show cumulative token savings from `run`
    mcp             run the experimental MCP server (shrink tool over stdio)
    doctor          verify each configured agent picked up the Monolith block

The module exposes :func:`main`, which is the ``monolith`` console-script entry
point declared in ``pyproject.toml``.
"""

from __future__ import annotations

import argparse
import json
import os
import signal
import subprocess
import sys
import urllib.error
import urllib.request
from typing import List, Sequence

from monolith import __version__
from monolith.adapters import all_keys, get_compiler
from monolith.benchmark import load_last_report, run_benchmark, save_report
from monolith.compression import DEFAULT_TIER, get_tier, tier_names
from monolith import hub as hub_module
from monolith.mcp_server import serve as mcp_serve
from monolith.runner import load_gain, run_command
from monolith.scan import apply_found, scan_repo
from monolith.shrink import DEFAULT_LEVEL, LEVELS, shrink
from monolith.settings import (
    default_settings,
    extra_rules,
    load_settings,
    save_settings,
    settings_exist,
)
from monolith import workflow as workflow_module
from monolith.tasks import (
    STATUSES,
    emit_tasks_md,
    load_tasks,
    parse_prd,
    render_tree_lines,
    save_tasks,
    set_status,
    tasks_exist,
)
from monolith.tokens import count_tokens


def estimate_tokens(text: str) -> int:
    """Return the token count for ``text`` (exact if tiktoken is installed)."""
    return count_tokens(text)


def _resolve_agents(requested: str | None, settings: dict) -> List[str]:
    """Translate an ``--agent`` value into a concrete list of agent keys.

    ``"all"`` -> every registered agent; ``"config"``/``None`` -> the agents
    saved in settings; anything else -> that single agent.
    """
    if requested in (None, "config"):
        return list(settings.get("agents", all_keys()))
    if requested == "all":
        return all_keys()
    return [requested]


# ---------------------------------------------------------------------------
# Command handlers. Each takes the parsed args and returns a process exit code.
# ---------------------------------------------------------------------------

def _seed_agents(root: str, requested: str | None) -> List[str]:
    """Pick the agent list for a fresh setup.

    Explicit ``--agent`` wins; otherwise use whichever agent files already
    exist, falling back to all agents so a fresh repo gets full coverage.
    """
    if requested == "all":
        return all_keys()
    if requested:
        return [requested]
    detected = [key for key in all_keys() if get_compiler(key).file_present(root)]
    return detected or all_keys()


def cmd_init(args: argparse.Namespace) -> int:
    """Create ``.monolith/settings.json``, pre-seeding any detected agents."""
    root = args.root
    if settings_exist(root) and not args.force:
        print(
            f"Settings already exist at {root}/.monolith/settings.json "
            "(use --force to overwrite)."
        )
        return 0

    agents = _seed_agents(root, args.agent)
    settings = default_settings(agents=agents)
    path = save_settings(settings, root)

    print("Initialized Monolith.")
    print(f"  settings: {path}")
    print(f"  tier:     {settings['tier']}")
    print(f"  agents:   {', '.join(agents)}")
    print("\nNext: `monolith apply` to write the rules into each agent's config.")
    print("(Or do everything in one go next time: `monolith setup`.)")
    return 0


def cmd_setup(args: argparse.Namespace) -> int:
    """One-shot onboarding: init + apply + doctor in a single command."""
    root = args.root
    settings = load_settings(root)
    if args.agent or not settings_exist(root):
        settings["agents"] = _seed_agents(root, args.agent)
    if args.tier:
        settings["tier"] = args.tier
    save_settings(settings, root)

    code = cmd_apply(argparse.Namespace(root=root, agent="config"))
    if code != 0:
        return code
    print()
    code = cmd_doctor(argparse.Namespace(root=root, agent="config"))
    if code == 0:
        print("\nNext steps (optional):")
        print("  monolith hub install sdd   # spec-driven development slash commands")
        print("  monolith stats             # projected savings + input cost")
    return code


def cmd_apply(args: argparse.Namespace) -> int:
    """Compile the active tier into the targeted agents' config files."""
    root = args.root
    settings = load_settings(root)
    tier_name = settings["tier"]

    if get_tier(tier_name) is None:
        print(f"error: unknown tier {tier_name!r} in settings", file=sys.stderr)
        return 1

    rules = extra_rules(settings)
    agents = _resolve_agents(args.agent, settings)
    print(f"Applying tier '{tier_name}' to: {', '.join(agents)}")
    for key in agents:
        compiler = get_compiler(key)
        if compiler is None:
            print(f"  ? unknown agent: {key}")
            continue
        outcome = compiler.apply(root, tier_name, rules)
        marker = "+" if outcome == "created" else "~"
        print(f"  {marker} {compiler.label:<14} -> {compiler.target_path}")
    return 0


def cmd_tier(args: argparse.Namespace) -> int:
    """Show the active tier, or switch to ``args.name`` when given."""
    root = args.root
    settings = load_settings(root)

    # No name -> list tiers, marking the active one.
    if args.name is None:
        print(f"Active tier: {settings['tier']}")
        print("\nAvailable tiers:")
        for name in tier_names():
            tier = get_tier(name)
            marker = "*" if name == settings["tier"] else " "
            print(f"  {marker} {name:<6} {tier.description}")
        return 0

    if get_tier(args.name) is None:
        print(
            f"error: unknown tier {args.name!r} "
            f"(choose from {', '.join(tier_names())})",
            file=sys.stderr,
        )
        return 1

    settings["tier"] = args.name
    save_settings(settings, root)
    print(f"Tier set to '{args.name}'.")
    if args.apply:
        # Re-apply to the configured agents immediately.
        return cmd_apply(argparse.Namespace(root=root, agent="config"))
    print("Run `monolith apply` to regenerate agent configs.")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    """Report projected output reduction and the block's fixed input cost."""
    root = args.root
    settings = load_settings(root)
    tier = get_tier(settings["tier"])
    if tier is None:
        print(f"error: unknown tier {settings['tier']!r} in settings", file=sys.stderr)
        return 1

    low, high = tier.reduction_percent()
    rules = extra_rules(settings)

    print("Monolith stats")
    print(f"  tier: {tier.name}  ({tier.description})")
    print(f"  projected OUTPUT reduction per response: {low}-{high}%  (estimate)")
    print("\n  one-time INPUT cost of the managed block per agent file:")
    for key in _resolve_agents("config", settings):
        compiler = get_compiler(key)
        if compiler is None:
            continue
        block = compiler.render(tier.name, rules)
        print(
            f"    {compiler.label:<14} ~{estimate_tokens(block)} tokens "
            f"({compiler.target_path})"
        )
    # Surface the most recent measured benchmark, if one has been run.
    last = load_last_report(root)
    if last:
        print(
            f"\n  last measured reduction: {last['reduction'] * 100:.0f}% "
            f"over {last['samples']} samples "
            f"({last['baseline_tokens']}->{last['optimized_tokens']} tokens, "
            f"{last['counter']})"
        )
    else:
        print("\n  (run `monolith bench` to record a measured reduction)")

    print("\n  Note: projections derive from upstream benchmarks; the measured")
    print("  figure is over Monolith's sample corpus. Savings accrue once output")
    print("  volume outweighs the small fixed input cost above.")
    return 0


def cmd_bench(args: argparse.Namespace) -> int:
    """Run the benchmark corpus, print results, and record them."""
    report = run_benchmark()
    print(f"Monolith benchmark ({report.counter})")
    for result in report.results:
        print(
            f"  {result.name:<16} {result.verbose_tokens:>4} -> "
            f"{result.concise_tokens:>4} tokens  ({result.reduction * 100:.0f}%)"
        )
    print(
        f"  {'TOTAL':<16} {report.baseline_tokens:>4} -> "
        f"{report.optimized_tokens:>4} tokens  ({report.reduction * 100:.0f}%)"
    )
    path = save_report(report, args.root)
    print(f"\nRecorded to {path}")
    return 0


def cmd_rules(args: argparse.Namespace) -> int:
    """List, add, or remove custom directives stored in settings."""
    root = args.root
    settings = load_settings(root)
    rules = extra_rules(settings)

    if args.action == "list":
        if not rules:
            print("No custom rules. Add one with `monolith rules add \"...\"`.")
            return 0
        print("Custom rules:")
        for index, rule in enumerate(rules, start=1):
            print(f"  {index}. {rule}")
        return 0

    if args.action == "add":
        if not args.value:
            print("error: `rules add` needs the rule text", file=sys.stderr)
            return 1
        rules.append(args.value)
        settings["extra_rules"] = rules
        save_settings(settings, root)
        print(f"Added rule #{len(rules)}. Run `monolith apply` to regenerate configs.")
        return 0

    # action == "remove": accept a 1-based index or an exact text match.
    if not args.value:
        print("error: `rules remove` needs an index or the exact rule text", file=sys.stderr)
        return 1
    removed = None
    if args.value.isdigit():
        idx = int(args.value)
        if 1 <= idx <= len(rules):
            removed = rules.pop(idx - 1)
    elif args.value in rules:
        rules.remove(args.value)
        removed = args.value
    if removed is None:
        print(f"error: no rule matching {args.value!r}", file=sys.stderr)
        return 1
    settings["extra_rules"] = rules
    save_settings(settings, root)
    print(f"Removed: {removed}. Run `monolith apply` to regenerate configs.")
    return 0


def cmd_scan(args: argparse.Namespace) -> int:
    """Scan the repo for @monolith: tags; report, and apply with --apply."""
    root = args.root
    found = scan_repo(root)

    print(f"Found {len(found.tasks)} task tag(s) and {len(found.rules)} rule tag(s).")
    for title in found.tasks:
        print(f"  task: {title}")
    for text in found.rules:
        print(f"  rule: {text}")

    if found.total() == 0:
        return 0
    if not args.apply:
        print("\n(dry run — pass --apply to add these to tasks/rules)")
        return 0

    added_tasks, added_rules = apply_found(found, root)
    print(
        f"\nApplied: {len(added_tasks)} new task(s), {len(added_rules)} new rule(s) "
        "(duplicates skipped)."
    )
    if added_rules:
        print("Run `monolith apply` to regenerate agent configs with the new rules.")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    """Parse a PRD/Markdown file into a task tree and emit TASKS.md."""
    root = args.root
    if tasks_exist(root) and not args.force:
        print("A task plan already exists (use --force to overwrite).")
        return 1
    try:
        with open(args.prd, "r", encoding="utf-8") as handle:
            text = handle.read()
    except OSError as exc:
        print(f"error: cannot read PRD: {exc}", file=sys.stderr)
        return 1

    tasks = parse_prd(text)
    if not tasks:
        print("No headings or list items found; nothing to plan.")
        return 1

    save_tasks(tasks, root)
    md_path = emit_tasks_md(tasks, root)
    print(f"Planned {len(tasks)} task(s).")
    print(f"  store: {root}/.monolith/tasks/tasks.json")
    print(f"  agents read: {md_path}")
    return 0


def cmd_tasks(args: argparse.Namespace) -> int:
    """List the current task tree; optionally re-emit TASKS.md."""
    root = args.root
    tasks = load_tasks(root)
    if not tasks:
        print("No tasks yet. Create some with `monolith plan <prd-file>`.")
        return 0
    done = sum(1 for t in tasks if t.status == "done")
    print(f"Tasks ({done}/{len(tasks)} done):")
    for line in render_tree_lines(tasks):
        print(f"  {line}")
    if args.emit:
        path = emit_tasks_md(tasks, root)
        print(f"\nRe-emitted {path}")
    return 0


def cmd_task(args: argparse.Namespace) -> int:
    """Update a single task's status, then re-emit TASKS.md."""
    root = args.root
    tasks = load_tasks(root)
    if not tasks:
        print("No tasks yet. Create some with `monolith plan <prd-file>`.")
        return 1

    changed, message = set_status(tasks, args.id, args.status)
    if not changed:
        print(f"error: {message}", file=sys.stderr)
        return 1

    save_tasks(tasks, root)
    emit_tasks_md(tasks, root)
    print(message)
    return 0


def cmd_hub(args: argparse.Namespace) -> int:
    """Browse and install curated agent resources."""
    if args.action == "list":
        print("Resource hub:")
        for resource in hub_module.CATALOG:
            print(f"  {resource.id:<16} [{resource.kind}] {resource.summary}")
        print("\nBundles (install several at once):")
        for name, ids in hub_module.BUNDLES.items():
            print(f"  {name:<16} [bundle] {', '.join(ids)}")
        return 0

    if args.action == "search":
        if not args.value:
            print("error: `hub search` needs a query", file=sys.stderr)
            return 1
        matches = hub_module.search(args.value)
        if not matches:
            print(f"No resources match {args.value!r}.")
            return 0
        for resource in matches:
            print(f"  {resource.id:<16} [{resource.kind}] {resource.summary}")
        return 0

    if args.action == "show":
        bundle = hub_module.BUNDLES.get(args.value or "")
        if bundle is not None:
            print(f"{args.value}  [bundle]")
            print("  installs:")
            for rid in bundle:
                print(f"    {rid}")
            return 0
        resource = hub_module.find(args.value or "")
        if resource is None:
            print(f"error: no resource with id {args.value!r}", file=sys.stderr)
            return 1
        print(f"{resource.id}  [{resource.kind}]")
        print(f"  {resource.summary}")
        print(f"  agents: {', '.join(resource.agents())}")
        print("\n--- body ---")
        print(resource.body)
        return 0

    # action == "install" — a single resource id or a bundle name.
    requested = args.value or ""
    ids = hub_module.BUNDLES.get(requested, [requested])
    resources = []
    for rid in ids:
        resource = hub_module.find(rid)
        if resource is None:
            print(f"error: no resource with id {rid!r}", file=sys.stderr)
            return 1
        resources.append(resource)

    # Agent scope: explicit flag > project settings > all the resource supports.
    if args.agent not in (None, "all", "config"):
        agents = [args.agent]
    elif args.agent == "config" or (args.agent is None and settings_exist(args.root)):
        agents = list(load_settings(args.root).get("agents", all_keys()))
    else:
        agents = None  # every agent each resource supports

    wrote_any = False
    for resource in resources:
        written = hub_module.install(
            resource, args.root, agents if agents is not None else resource.agents()
        )
        if not written:
            print(f"Nothing installed for '{resource.id}' (no target for: {args.agent}).")
            continue
        wrote_any = True
        print(f"Installed '{resource.id}':")
        for path in written:
            print(f"  + {path}")
    return 0 if wrote_any else 1


def cmd_shrink(args: argparse.Namespace) -> int:
    """Compress text from a file or stdin; write result to stdout, stats to stderr."""
    if args.path:
        try:
            with open(args.path, "r", encoding="utf-8") as handle:
                text = handle.read()
        except OSError as exc:
            print(f"error: cannot read {args.path}: {exc}", file=sys.stderr)
            return 1
    else:
        text = sys.stdin.read()

    result = shrink(text, args.level)
    sys.stdout.write(result.text)
    if result.text and not result.text.endswith("\n"):
        sys.stdout.write("\n")
    # Stats on stderr so the compressed text can be piped cleanly.
    print(
        f"shrink[{args.level}]: {result.before_tokens} -> {result.after_tokens} tokens "
        f"({result.reduction * 100:.0f}% reduction)",
        file=sys.stderr,
    )
    return 0


def cmd_run(args: argparse.Namespace) -> int:
    """Run a command, print its compressed output, tee full output on failure.

    Exits with the wrapped command's own return code so the agent still sees
    pass/fail.
    """
    argv = list(args.cmd)
    if argv and argv[0] == "--":
        argv = argv[1:]
    if not argv:
        print("error: nothing to run (usage: monolith run -- <command>)", file=sys.stderr)
        return 2

    try:
        result = run_command(argv, root=args.root, level=args.level, timeout=args.timeout)
    except FileNotFoundError:
        print(f"error: command not found: {argv[0]}", file=sys.stderr)
        return 127
    except subprocess.TimeoutExpired:
        print(f"error: command timed out after {args.timeout}s", file=sys.stderr)
        return 124

    # Compressed output to stdout; on failure point to the full saved output.
    sys.stdout.write(result.output)
    if result.output and not result.output.endswith("\n"):
        sys.stdout.write("\n")
    if result.tee_path:
        sys.stdout.write(f"↳ full output: {result.tee_path}\n")
    # Savings to stderr so stdout stays clean for piping.
    print(
        f"run[{result.kind}] exit={result.returncode}: "
        f"{result.before_tokens} -> {result.after_tokens} tokens "
        f"({result.reduction * 100:.0f}% saved)",
        file=sys.stderr,
    )
    return result.returncode


def cmd_gain(args: argparse.Namespace) -> int:
    """Report cumulative token savings recorded by `monolith run`."""
    ledger = load_gain(args.root)
    if not ledger or ledger.get("runs", 0) == 0:
        print("No runs recorded yet. Use `monolith run -- <command>` first.")
        return 0
    before = ledger["before_tokens"]
    after = ledger["after_tokens"]
    saved = before - after
    pct = (saved / before * 100) if before else 0.0
    print("Monolith gain")
    print(f"  commands run:   {ledger['runs']}")
    print(f"  tokens in:      {before}")
    print(f"  tokens out:     {after}")
    print(f"  tokens saved:   {saved}  ({pct:.0f}%)")
    return 0


def cmd_constitution(args: argparse.Namespace) -> int:
    """Scaffold .monolith/memory/constitution.md if it does not exist."""
    created, path = workflow_module.scaffold_constitution(args.root)
    if created:
        print(f"Created {path}")
        print("Fill in your mission, principles, and definition of done.")
        print("Then install the /monolith.constitution command:")
        print("  monolith hub install monolith.constitution")
    else:
        print(f"Constitution already exists: {path}")
        print("Edit it directly, or use /monolith.constitution to update it with an agent.")
    return 0


def cmd_specify(args: argparse.Namespace) -> int:
    """Scaffold specs/<feature>/ with the requested artifact files."""
    root = args.root
    feature = args.feature
    created_any = False

    # Always scaffold spec.md
    created, path = workflow_module.scaffold_spec(root, feature)
    if created:
        print(f"  + {path}")
        created_any = True
    else:
        print(f"  ~ {path}  (already exists)")

    if args.plan:
        created, path = workflow_module.scaffold_plan(root, feature)
        if created:
            print(f"  + {path}")
            created_any = True
        else:
            print(f"  ~ {path}  (already exists)")

    if args.data_model:
        created, path = workflow_module.scaffold_data_model(root, feature)
        if created:
            print(f"  + {path}")
            created_any = True
        else:
            print(f"  ~ {path}  (already exists)")

    if args.contracts:
        created, path = workflow_module.scaffold_contracts(root, feature)
        if created:
            print(f"  + {path}")
            created_any = True
        else:
            print(f"  ~ {path}  (already exists)")

    if created_any:
        print(f"\nFeature scaffold ready at specs/{feature}/")
        print("Next: fill in spec.md, then run `monolith analyze " + feature + "`")
    else:
        print(f"\nAll artifacts already exist for '{feature}'.")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    """Report cross-artifact consistency for a feature."""
    root = args.root

    if args.feature:
        features = [args.feature]
    else:
        features = workflow_module.list_features(root)
        if not features:
            print("No features found under specs/. Run `monolith specify <feature>` first.")
            return 0

    errors = 0
    for feature in features:
        print(f"{'─' * 40}")
        print(f"Feature: {feature}")
        for finding in workflow_module.analyze_feature(root, feature):
            print(f"  {finding}")
            if finding.startswith("ERROR"):
                errors += 1
        print()

    if errors:
        print(f"{errors} error(s) found. Fix before implementing.")
        return 1
    return 0


def cmd_checklist(args: argparse.Namespace) -> int:
    """Generate or write a quality checklist for a feature."""
    root = args.root
    feature = args.feature
    text = workflow_module.generate_checklist(root, feature)

    if args.write:
        out_path = workflow_module.artifact_path(root, feature, "checklist.md")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(text)
        print(f"Written to {out_path}")
    else:
        print(text)
    return 0


def cmd_tasks_to_issues(args: argparse.Namespace) -> int:
    """Push todo/doing tasks to GitHub Issues. Requires GITHUB_TOKEN env var."""
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        print("error: GITHUB_TOKEN environment variable not set", file=sys.stderr)
        print("  export GITHUB_TOKEN=<your-personal-access-token>", file=sys.stderr)
        return 1

    tasks = load_tasks(args.root)
    if not tasks:
        print("No tasks found. Run `monolith plan <prd>` first.")
        return 0

    target_statuses = {"todo", "doing"} if not args.done else {"todo", "doing", "done"}
    to_push = [t for t in tasks if t.status in target_statuses]
    if not to_push:
        print("No tasks with status todo/doing to push.")
        return 0

    owner, _, repo = args.repo.partition("/")
    if not owner or not repo:
        print("error: --repo must be in owner/repo format", file=sys.stderr)
        return 1

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Content-Type": "application/json",
    }

    created = 0
    errors = 0
    for task in to_push:
        body_parts = [f"Task `{task.id}` from Monolith task tree."]
        if task.deps:
            body_parts.append(f"\nDepends on: {', '.join(task.deps)}")
        body_parts.append(f"\nStatus: `{task.status}`")
        if args.spec_link:
            body_parts.append(f"\nSpec: {args.spec_link}")

        payload: dict = {
            "title": task.title,
            "body": "\n".join(body_parts),
        }
        if args.label:
            payload["labels"] = [args.label]

        data = json.dumps(payload).encode()
        req = urllib.request.Request(
            f"https://api.github.com/repos/{owner}/{repo}/issues",
            data=data,
            headers=headers,
            method="POST",
        )
        try:
            with urllib.request.urlopen(req) as resp:
                result = json.loads(resp.read())
            print(f"  + #{result['number']}  {task.id}: {task.title}")
            print(f"    {result['html_url']}")
            created += 1
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode(errors="replace")
            print(f"  error: {task.id} — HTTP {exc.code}: {detail}", file=sys.stderr)
            errors += 1

    print(f"\n{created} issue(s) created", end="")
    if errors:
        print(f", {errors} error(s)", end="")
    print(".")
    return 1 if errors else 0


def cmd_mcp(args: argparse.Namespace) -> int:
    """Run the experimental MCP server (shrink tool) over stdio."""
    return mcp_serve()


def cmd_doctor(args: argparse.Namespace) -> int:
    """Verify every configured agent has a healthy Monolith block."""
    root = args.root
    settings = load_settings(root)

    print(f"Monolith doctor (tier: {settings['tier']})")
    all_ok = True
    for key in _resolve_agents(getattr(args, "agent", "config"), settings):
        compiler = get_compiler(key)
        if compiler is None:
            print(f"  ? unknown agent in settings: {key}")
            all_ok = False
            continue
        report = compiler.status(root)
        all_ok = all_ok and report["ok"]
        mark = "ok " if report["ok"] else "FAIL"
        print(f"  [{mark}] {compiler.label:<14} {report['path']}  ({report['reason']})")

    if not all_ok:
        print("\nSome agents are not set up. Run `monolith apply`.")
        return 1
    print("\nAll configured agents have the Monolith block.")
    return 0


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    """Construct the top-level argument parser and its sub-commands."""
    parser = argparse.ArgumentParser(
        prog="monolith",
        description="Cross-agent token-efficiency layer for AI coding assistants.",
    )
    parser.add_argument("--version", action="version", version=f"monolith {__version__}")
    parser.add_argument(
        "--root", default=".", help="project root to operate in (default: current dir)"
    )

    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="create .monolith/settings.json")
    p_init.add_argument("--force", action="store_true", help="overwrite existing settings")
    p_init.add_argument(
        "--agent",
        choices=all_keys() + ["all"],
        default=None,
        help="target only this agent (default: detect existing files, else all)",
    )
    p_init.set_defaults(func=cmd_init)

    p_setup = sub.add_parser(
        "setup", help="one-shot onboarding: init + apply + doctor"
    )
    p_setup.add_argument(
        "--agent",
        choices=all_keys() + ["all"],
        default=None,
        help="target only this agent (default: detect existing files, else all)",
    )
    p_setup.add_argument(
        "--tier", choices=tier_names(), default=None,
        help=f"compression tier (default: {DEFAULT_TIER})",
    )
    p_setup.set_defaults(func=cmd_setup)

    p_apply = sub.add_parser("apply", help="write the directives into agent configs")
    p_apply.add_argument(
        "--agent",
        choices=all_keys() + ["all", "config"],
        default="config",
        help="which agent(s) to target (default: those in settings)",
    )
    p_apply.set_defaults(func=cmd_apply)

    p_tier = sub.add_parser("tier", help="show or switch the active compression tier")
    p_tier.add_argument(
        "name", nargs="?", choices=tier_names(), help="tier to switch to; omit to show current"
    )
    p_tier.add_argument("--apply", action="store_true", help="re-apply configs after switching")
    p_tier.set_defaults(func=cmd_tier)

    p_stats = sub.add_parser("stats", help="show projected + measured token savings")
    p_stats.set_defaults(func=cmd_stats)

    p_bench = sub.add_parser("bench", help="run the benchmark corpus, record results")
    p_bench.set_defaults(func=cmd_bench)

    p_rules = sub.add_parser("rules", help="list/add/remove custom directives")
    p_rules.add_argument("action", choices=["list", "add", "remove"])
    p_rules.add_argument(
        "value", nargs="?", help="rule text (add) or index/text (remove)"
    )
    p_rules.set_defaults(func=cmd_rules)

    p_scan = sub.add_parser("scan", help="scan the repo for @monolith: tags")
    p_scan.add_argument("--apply", action="store_true", help="apply found tags (default: dry run)")
    p_scan.set_defaults(func=cmd_scan)

    p_constitution = sub.add_parser(
        "constitution", help="scaffold .monolith/memory/constitution.md"
    )
    p_constitution.set_defaults(func=cmd_constitution)

    p_specify = sub.add_parser(
        "specify", help="scaffold specs/<feature>/ artifact files"
    )
    p_specify.add_argument("feature", help="feature name, e.g. user-auth")
    p_specify.add_argument(
        "--plan", action="store_true", help="also scaffold plan.md"
    )
    p_specify.add_argument(
        "--data-model", dest="data_model", action="store_true",
        help="also scaffold data-model.md",
    )
    p_specify.add_argument(
        "--contracts", action="store_true", help="also scaffold contracts/README.md"
    )
    p_specify.set_defaults(func=cmd_specify)

    p_analyze = sub.add_parser(
        "analyze", help="validate cross-artifact consistency for a feature"
    )
    p_analyze.add_argument(
        "feature", nargs="?",
        help="feature name (default: all features under specs/)",
    )
    p_analyze.set_defaults(func=cmd_analyze)

    p_checklist = sub.add_parser(
        "checklist", help="generate a quality checklist for a feature"
    )
    p_checklist.add_argument("feature", help="feature name")
    p_checklist.add_argument(
        "--write", action="store_true",
        help="write checklist.md into specs/<feature>/ instead of printing",
    )
    p_checklist.set_defaults(func=cmd_checklist)

    p_plan = sub.add_parser("plan", help="parse a PRD/Markdown file into a task tree")
    p_plan.add_argument("prd", help="path to the PRD / Markdown file")
    p_plan.add_argument("--force", action="store_true", help="overwrite an existing plan")
    p_plan.set_defaults(func=cmd_plan)

    p_tasks = sub.add_parser("tasks", help="list the task tree")
    p_tasks.add_argument("--emit", action="store_true", help="re-write TASKS.md")
    p_tasks.set_defaults(func=cmd_tasks)

    p_task = sub.add_parser("task", help="update a single task's status")
    p_task.add_argument("id", help="task id, e.g. T3")
    p_task.add_argument("--status", required=True, choices=STATUSES, help="new status")
    p_task.set_defaults(func=cmd_task)

    p_t2i = sub.add_parser(
        "tasks-to-issues", help="push tasks to GitHub Issues (requires GITHUB_TOKEN)"
    )
    p_t2i.add_argument(
        "--repo", required=True, metavar="OWNER/REPO",
        help="target repository, e.g. acme/my-project",
    )
    p_t2i.add_argument(
        "--label", default="", metavar="LABEL",
        help="label to attach to every created issue (must already exist in the repo)",
    )
    p_t2i.add_argument(
        "--done", action="store_true",
        help="also push tasks with status 'done' (default: only todo and doing)",
    )
    p_t2i.add_argument(
        "--spec-link", dest="spec_link", default="", metavar="URL",
        help="URL to append to every issue body (e.g. link to the spec file)",
    )
    p_t2i.set_defaults(func=cmd_tasks_to_issues)

    p_hub = sub.add_parser("hub", help="browse and install curated agent resources")
    p_hub.add_argument("action", choices=["list", "search", "show", "install"])
    p_hub.add_argument("value", nargs="?", help="query (search) or resource id (show/install)")
    p_hub.add_argument(
        "--agent",
        choices=all_keys() + ["all", "config"],
        default=None,
        help="target agent for install (default: agents from settings, "
             "else all the resource supports)",
    )
    p_hub.set_defaults(func=cmd_hub)

    p_shrink = sub.add_parser("shrink", help="compress verbose text/output")
    p_shrink.add_argument("path", nargs="?", help="file to compress (default: stdin)")
    p_shrink.add_argument(
        "--level", choices=LEVELS, default=DEFAULT_LEVEL, help="compression level"
    )
    p_shrink.set_defaults(func=cmd_shrink)

    p_run = sub.add_parser("run", help="run a command and compress its output")
    p_run.add_argument(
        "--level", choices=LEVELS, default=DEFAULT_LEVEL, help="compression level"
    )
    p_run.add_argument("--timeout", type=float, default=None, help="seconds before aborting")
    p_run.add_argument(
        "cmd",
        nargs=argparse.REMAINDER,
        help="the command to run, e.g. `monolith run -- pytest -q`",
    )
    p_run.set_defaults(func=cmd_run)

    p_gain = sub.add_parser("gain", help="show cumulative token savings from run")
    p_gain.set_defaults(func=cmd_gain)

    p_mcp = sub.add_parser("mcp", help="run the experimental MCP server (stdio)")
    p_mcp.set_defaults(func=cmd_mcp)

    p_doctor = sub.add_parser("doctor", help="verify agent configs are set up")
    p_doctor.add_argument(
        "--agent",
        choices=all_keys() + ["all", "config"],
        default="config",
        help="which agent(s) to check (default: those in settings)",
    )
    p_doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point. Returns a process exit code."""
    # Behave like a normal Unix tool when piped into a consumer that closes
    # early (e.g. `monolith shrink … | head`): terminate quietly on SIGPIPE
    # instead of dumping a BrokenPipeError traceback. Guarded for platforms
    # (Windows) and contexts (non-main thread) where SIGPIPE isn't settable.
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    except (AttributeError, ValueError):
        pass

    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except BrokenPipeError:
        # The reader went away. Send any buffered output to devnull so the
        # final flush at interpreter shutdown doesn't re-raise, then exit 0.
        try:
            devnull = os.open(os.devnull, os.O_WRONLY)
            os.dup2(devnull, sys.stdout.fileno())
        except OSError:
            pass
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
