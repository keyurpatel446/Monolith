"""Monolith command-line interface.

Commands:
    init      detect agents in the repo and create .monolith/config.json
    apply     compile the ruleset into each agent's native config file
    profile   show or switch the active compression profile
    stats     show projected token savings for the active profile
    doctor    verify each configured agent picked up the Monolith block
"""

import argparse
import sys

from monolith import __version__
from monolith.adapters import all_keys, get_adapter
from monolith.config import load_config, save_config, config_exists, default_config
from monolith.profiles import get_profile, profile_names


def estimate_tokens(text):
    """Rough token estimate (~4 chars/token), good enough for reporting."""
    return max(1, len(text) // 4)


def _resolve_agents(requested, config):
    """Map an --agent value to a concrete list of adapter keys."""
    if requested in (None, "config"):
        return list(config.get("agents", all_keys()))
    if requested == "all":
        return all_keys()
    return [requested]


# -- commands ------------------------------------------------------------

def cmd_init(args):
    root = args.root
    if config_exists(root) and not args.force:
        print("Config already exists at %s/.monolith/config.json (use --force to overwrite)."
              % root)
        return 0

    # Detect which agent files already live in the repo.
    detected = [key for key in all_keys() if get_adapter(key).file_present(root)]
    agents = detected if detected else all_keys()

    config = default_config(agents=agents)
    path = save_config(config, root)

    print("Initialized Monolith.")
    print("  config:  %s" % path)
    print("  profile: %s" % config["profile"])
    if detected:
        print("  detected agents: %s" % ", ".join(detected))
    else:
        print("  no agent files found; targeting all: %s" % ", ".join(agents))
    print("\nNext: `monolith apply` to write the rules into each agent's config.")
    return 0


def cmd_apply(args):
    root = args.root
    config = load_config(root)
    profile_name = config["profile"]
    custom_rules = config.get("custom_rules", [])

    if get_profile(profile_name) is None:
        print("error: unknown profile %r in config" % profile_name, file=sys.stderr)
        return 1

    agents = _resolve_agents(args.agent, config)
    print("Applying profile '%s' to: %s" % (profile_name, ", ".join(agents)))
    for key in agents:
        adapter = get_adapter(key)
        if adapter is None:
            print("  ? unknown agent: %s" % key)
            continue
        outcome = adapter.apply(root, profile_name, custom_rules)
        print("  %s %-14s -> %s" % ("+" if outcome == "created" else "~",
                                    adapter.label, adapter.target_path))
    return 0


def cmd_profile(args):
    root = args.root
    config = load_config(root)

    if args.name is None:
        print("Active profile: %s" % config["profile"])
        print("\nAvailable profiles:")
        for name in profile_names():
            p = get_profile(name)
            marker = "*" if name == config["profile"] else " "
            print("  %s %-6s %s" % (marker, name, p["description"]))
        return 0

    if get_profile(args.name) is None:
        print("error: unknown profile %r (choose from %s)"
              % (args.name, ", ".join(profile_names())), file=sys.stderr)
        return 1

    config["profile"] = args.name
    save_config(config, root)
    print("Profile set to '%s'." % args.name)
    if args.apply:
        return cmd_apply(argparse.Namespace(root=root, agent="config"))
    print("Run `monolith apply` to regenerate agent configs.")
    return 0


def cmd_stats(args):
    root = args.root
    config = load_config(root)
    profile_name = config["profile"]
    profile = get_profile(profile_name)
    if profile is None:
        print("error: unknown profile %r in config" % profile_name, file=sys.stderr)
        return 1

    low, high = profile["projected_output_reduction"]
    custom_rules = config.get("custom_rules", [])
    agents = _resolve_agents("config", config)

    print("Monolith stats")
    print("  profile: %s  (%s)" % (profile_name, profile["description"]))
    print("  projected OUTPUT reduction per response: %d-%d%%  (estimate)"
          % (int(low * 100), int(high * 100)))
    print("\n  one-time INPUT cost of the managed block per agent file:")
    for key in agents:
        adapter = get_adapter(key)
        if adapter is None:
            continue
        block = adapter.render_block(profile_name, custom_rules)
        print("    %-14s ~%d tokens (%s)"
              % (adapter.label, estimate_tokens(block), adapter.target_path))
    print("\n  Note: reductions are projections derived from upstream benchmarks,")
    print("  not measurements. Savings accrue once output volume outweighs the")
    print("  small fixed input cost above.")
    return 0


def cmd_doctor(args):
    root = args.root
    config = load_config(root)
    agents = _resolve_agents("config", config)

    print("Monolith doctor (profile: %s)" % config["profile"])
    all_ok = True
    for key in agents:
        adapter = get_adapter(key)
        if adapter is None:
            print("  ? unknown agent in config: %s" % key)
            all_ok = False
            continue
        st = adapter.status(root)
        mark = "ok " if st["ok"] else "FAIL"
        all_ok = all_ok and st["ok"]
        print("  [%s] %-14s %s  (%s)" % (mark, adapter.label, st["path"], st["reason"]))
    if not all_ok:
        print("\nSome agents are not set up. Run `monolith apply`.")
        return 1
    print("\nAll configured agents have the Monolith block.")
    return 0


# -- parser --------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="monolith",
        description="Cross-agent token-efficiency layer for AI coding assistants.",
    )
    parser.add_argument("--version", action="version",
                        version="monolith %s" % __version__)
    parser.add_argument("--root", default=".",
                        help="project root to operate in (default: current dir)")

    sub = parser.add_subparsers(dest="command")

    p_init = sub.add_parser("init", help="create .monolith/config.json")
    p_init.add_argument("--force", action="store_true",
                        help="overwrite an existing config")
    p_init.set_defaults(func=cmd_init)

    p_apply = sub.add_parser("apply", help="write the ruleset into agent configs")
    p_apply.add_argument("--agent", choices=all_keys() + ["all", "config"],
                         default="config",
                         help="which agent(s) to target (default: those in config)")
    p_apply.set_defaults(func=cmd_apply)

    p_profile = sub.add_parser("profile", help="show or switch the active profile")
    p_profile.add_argument("name", nargs="?", choices=profile_names(),
                           help="profile to switch to; omit to show current")
    p_profile.add_argument("--apply", action="store_true",
                           help="re-apply configs after switching")
    p_profile.set_defaults(func=cmd_profile)

    p_stats = sub.add_parser("stats", help="show projected token savings")
    p_stats.set_defaults(func=cmd_stats)

    p_doctor = sub.add_parser("doctor", help="verify agent configs are set up")
    p_doctor.set_defaults(func=cmd_doctor)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "command", None):
        parser.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
