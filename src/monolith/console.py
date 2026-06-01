"""Monolith command-line console.

Sub-commands
------------
    init      detect agents in the repo and create .monolith/settings.json
    apply     compile the directives into each agent's native config file
    tier      show or switch the active compression tier
    stats     show projected token savings for the active tier
    doctor    verify each configured agent picked up the Monolith block

The module exposes :func:`main`, which is the ``monolith`` console-script entry
point declared in ``pyproject.toml``.
"""

from __future__ import annotations

import argparse
import sys
from typing import List, Sequence

from monolith import __version__
from monolith.adapters import all_keys, get_compiler
from monolith.compression import DEFAULT_TIER, get_tier, tier_names
from monolith.settings import (
    default_settings,
    extra_rules,
    load_settings,
    save_settings,
    settings_exist,
)

# Rough heuristic: English text averages ~4 characters per token. Good enough
# for reporting the fixed input cost of the managed block.
_CHARS_PER_TOKEN = 4


def estimate_tokens(text: str) -> int:
    """Return a coarse token estimate for ``text`` (never less than 1)."""
    return max(1, len(text) // _CHARS_PER_TOKEN)


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

def cmd_init(args: argparse.Namespace) -> int:
    """Create ``.monolith/settings.json``, pre-seeding any detected agents."""
    root = args.root
    if settings_exist(root) and not args.force:
        print(
            f"Settings already exist at {root}/.monolith/settings.json "
            "(use --force to overwrite)."
        )
        return 0

    # Seed the agent list from whichever agent files already exist; otherwise
    # target all of them so a fresh repo gets full coverage.
    detected = [key for key in all_keys() if get_compiler(key).file_present(root)]
    agents = detected or all_keys()

    settings = default_settings(agents=agents)
    path = save_settings(settings, root)

    print("Initialized Monolith.")
    print(f"  settings: {path}")
    print(f"  tier:     {settings['tier']}")
    if detected:
        print(f"  detected agents: {', '.join(detected)}")
    else:
        print(f"  no agent files found; targeting all: {', '.join(agents)}")
    print("\nNext: `monolith apply` to write the rules into each agent's config.")
    return 0


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
    print("\n  Note: reductions are projections derived from upstream benchmarks,")
    print("  not measurements. Savings accrue once output volume outweighs the")
    print("  small fixed input cost above.")
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    """Verify every configured agent has a healthy Monolith block."""
    root = args.root
    settings = load_settings(root)

    print(f"Monolith doctor (tier: {settings['tier']})")
    all_ok = True
    for key in _resolve_agents("config", settings):
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
    p_init.set_defaults(func=cmd_init)

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

    p_stats = sub.add_parser("stats", help="show projected token savings")
    p_stats.set_defaults(func=cmd_stats)

    p_doctor = sub.add_parser("doctor", help="verify agent configs are set up")
    p_doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Console-script entry point. Returns a process exit code."""
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
