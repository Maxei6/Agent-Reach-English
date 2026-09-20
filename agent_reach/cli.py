# -*- coding: utf-8 -*-
"""
Agent Reach CLI — installer, doctor, and configuration tool.

Usage:
    agent-reach install --env=auto
    agent-reach doctor
    agent-reach configure twitter-cookies
    agent-reach setup
"""

import argparse
import json
import os
import sys
import time

from agent_reach import __version__

# Pinned to the 0.4.2 state — PyPI still only has 0.4.1 (upstream issue #10).
_RDT_GIT_SOURCE = "git+https://github.com/public-clis/rdt-cli.git@5e4fb3720d5c174e976cd425ccc3b879d52cac66"
_MAX_CONFIGURE_VALUE_CHARS = 1024 * 1024
_SENSITIVE_CONFIG_KEYS = {
    "proxy",
    "github-token",
    "groq-key",
    "openai-key",
    "twitter-cookies",
}


def _ensure_utf8_console():
    """Best-effort Windows console UTF-8 setup for CLI runtime only."""
    if sys.platform != "win32":
        return
    # Avoid interfering with pytest/captured streams.
    if os.environ.get("PYTEST_CURRENT_TEST"):
        return
    try:
        import io
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        if hasattr(sys.stderr, "buffer"):
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        # Do not crash CLI just because encoding patch failed.
        pass


def _configure_logging(verbose: bool = False):
    """Suppress loguru output unless --verbose is set."""
    from loguru import logger
    logger.remove()  # Remove default stderr handler
    if verbose:
        logger.add(sys.stderr, level="INFO")


def main():
    _ensure_utf8_console()

    parser = argparse.ArgumentParser(
        prog="agent-reach",
        description="Give your AI Agent eyes to see the entire internet",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Show debug logs")
    parser.add_argument("--version", action="version", version=f"Agent Reach v{__version__}")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── setup ──
    sub.add_parser("setup", help="Interactive configuration wizard")

    # ── install ──
    p_install = sub.add_parser("install", help="One-shot installer with flags")
    p_install.add_argument("--env", choices=["local", "server", "auto"], default="auto",
                           help="Environment: local, server, or auto-detect")
    p_install.add_argument("--proxy", default="",
                           help="Network proxy saved for agents to export as HTTP(S)_PROXY "
                                "in restricted networks (http://user:pass@ip:port)")
    install_mode = p_install.add_mutually_exclusive_group()
    install_mode.add_argument(
        "--system",
        action="store_true",
        help="Explicitly allow system dependency, global tool, config, and skill installation",
    )
    install_mode.add_argument(
        "--safe",
        action="store_true",
        help="Safe check-only mode (default; retained for compatibility)",
    )
    p_install.add_argument("--dry-run", action="store_true",
                           help="Show what would be done without making any changes")
    p_install.add_argument("--channels", default="",
                           help="Comma-separated optional channels to install "
                                 "(twitter,reddit,facebook,instagram,linkedin,opencli,all)")

    # ── configure ──
    p_conf = sub.add_parser("configure", help="Set an Agent Reach configuration value")
    p_conf.add_argument("key", nargs="?", default=None,
                        choices=["proxy", "github-token", "groq-key", "openai-key",
                                  "twitter-cookies", "youtube-cookies"],
                        help="What to configure (omit if using --from-browser)")
    p_conf.add_argument("value", nargs="*", help="The value(s) to set")
    p_conf.add_argument(
        "--stdin",
        dest="read_stdin",
        action="store_true",
        help="Read the value from stdin instead of exposing it in process arguments",
    )
    p_conf.add_argument(
        "--sync-legacy-twitter",
        action="store_true",
        help="With twitter-cookies, also write legacy xfetch/bird credential files",
    )

    # ── doctor ──
    p_doctor = sub.add_parser("doctor", help="Check platform availability")
    p_doctor.add_argument("--json", action="store_true",
                          help="Output machine-readable JSON instead of the text report")

    # ── uninstall ──
    p_uninstall = sub.add_parser("uninstall", help="Remove all Agent Reach config, tokens, and skill files")
    p_uninstall.add_argument("--dry-run", action="store_true",
                             help="Show what would be removed without making any changes")
    p_uninstall.add_argument("--keep-config", action="store_true",
                             help="Remove skill files only, keep ~/.agent-reach/ config and tokens")

    # ── skill ──
    p_skill = sub.add_parser("skill", help="Manage agent skill registration")
    p_skill_group = p_skill.add_mutually_exclusive_group(required=True)
    p_skill_group.add_argument("--install", action="store_true",
                               help="Install SKILL.md to agent skill directories")
    p_skill_group.add_argument("--uninstall", action="store_true",
                               help="Remove SKILL.md from agent skill directories")

    # ── check-update ──
    # ── transcribe ──
    p_tr = sub.add_parser("transcribe", help="Transcribe a URL or local audio file (Whisper via Groq/OpenAI)")
    p_tr.add_argument("source", help="Audio/video URL or local file path")
    p_tr.add_argument("--provider", choices=["auto", "groq", "openai"], default="auto",
                      help="Transcription provider (default: first configured provider)")
    p_tr.add_argument(
        "--allow-provider-fallback",
        action="store_true",
        help=(
            "With --provider auto, allow sending audio to the next "
            "configured provider after a failure"
        ),
    )
    p_tr.add_argument("-o", "--output", default=None,
                      help="Write transcript to a file instead of stdout")

    sub.add_parser("check-update", help="Check for new versions and changes")

    # ── watch ──
    sub.add_parser("watch", help="Quick health check + update check (for scheduled tasks)")

    # ── version ──
    sub.add_parser("version", help="Show version")

    args = parser.parse_args()

    if args.command == "configure":
        if args.read_stdin and args.value:
            p_conf.error("--stdin cannot be combined with a positional value")
        if args.read_stdin and not args.key:
            p_conf.error("--stdin requires a configure key")
        if args.sync_legacy_twitter and args.key != "twitter-cookies":
            p_conf.error("--sync-legacy-twitter is only valid with twitter-cookies")

    if (
        args.command == "transcribe"
        and args.allow_provider_fallback
        and args.provider != "auto"
    ):
        p_tr.error("--allow-provider-fallback requires --provider auto")

    # Suppress loguru noise unless --verbose
    _configure_logging(getattr(args, "verbose", False))

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "version":
        print(f"Agent Reach v{__version__}")
        sys.exit(0)

    if args.command == "doctor":
        _cmd_doctor(args)
    elif args.command == "check-update":
        _cmd_check_update()
    elif args.command == "watch":
        _cmd_watch()
    elif args.command == "setup":
        _cmd_setup()
    elif args.command == "install":
        _cmd_install(args)
    elif args.command == "configure":
        _cmd_configure(args)
    elif args.command == "uninstall":
        _cmd_uninstall(args)
    elif args.command == "skill":
        _cmd_skill(args)
    elif args.command == "transcribe":
        _cmd_transcribe(args)


# ── Command handlers ────────────────────────────────


def _cmd_install(args):
    """One-shot deterministic installer."""
    import os

    from agent_reach.config import Config
    from agent_reach.doctor import check_all, format_report

    safe_mode = getattr(args, "safe", False) or not getattr(args, "system", False)
    dry_run = args.dry_run

    # Validate channel names before constructing config or changing the system.
    CHANNEL_INSTALLERS = {
        "twitter":     _install_twitter_deps,
        "reddit":      _install_reddit_deps,
        "facebook":    _install_opencli_deps,
        "instagram":   _install_opencli_deps,
        "opencli":     _install_opencli_deps,  # cross-channel backend, desktop only
        # linkedin: manual setup, no auto-install
    }
    supported_channels = set(CHANNEL_INSTALLERS) | {"linkedin"}
    raw_channels = [
        channel.strip().lower()
        for channel in args.channels.split(",")
        if channel.strip()
    ]
    unknown_channels = set(raw_channels) - supported_channels - {"all"}
    if unknown_channels:
        supported = ", ".join(sorted(supported_channels | {"all"}))
        unknown = ", ".join(sorted(unknown_channels))
        print(
            f"agent-reach install: error: unknown channel(s): {unknown}. "
            f"Supported: {supported}",
            file=sys.stderr,
        )
        raise SystemExit(2)

    if "all" in raw_channels:
        requested_channels = supported_channels
    else:
        requested_channels = set(raw_channels)

    config = Config(read_only=dry_run or safe_mode)
    print()
    print("Agent Reach Installer")
    print("=" * 40)

    if dry_run:
        print("DRY RUN — showing what would be done (no changes)")
        print()
    if safe_mode:
        print("SAFE MODE — skipping automatic system changes")
        print()

    # Only a real installation may create persistent directories.
    if not dry_run and not safe_mode:
        tools_dir = os.path.expanduser("~/.agent-reach/tools")
        os.makedirs(tools_dir, exist_ok=True)

    DESKTOP_ONLY_CHANNELS = {"opencli", "facebook", "instagram"}
    COOKIE_CHANNELS = {"twitter"}

    # Auto-detect environment
    env = args.env
    if env == "auto":
        env = _detect_environment()

    if env == "server":
        print("Environment: Server/VPS (auto-detected)")
    else:
        print("Environment: Local computer (auto-detected)")

    server_skipped_desktop_channels = set()
    if env == "server" and requested_channels:
        # Browser-session channels require a real desktop Chrome.
        server_skipped_desktop_channels = requested_channels & DESKTOP_ONLY_CHANNELS
        requested_channels -= server_skipped_desktop_channels

    # Apply explicit flags
    if args.proxy:
        if dry_run or safe_mode:
            mode = "dry-run" if dry_run else "safe"
            print(f"[{mode}] Would save network proxy")
        else:
            config.set("proxy", args.proxy)
            print("✅ Proxy saved for Agent Reach network access")

    # ── Install core system dependencies (lightweight, always) ──
    print()
    core_install_ok = True
    if dry_run:
        _install_system_deps_dryrun()
    elif safe_mode:
        _install_system_deps_safe()
    else:
        core_install_ok = _install_system_deps() is not False

    # ── mcporter (for Exa search) ──
    print()
    if dry_run:
        print("[dry-run] Would install mcporter and configure Exa search")
    elif safe_mode:
        _install_mcporter_safe()
    else:
        core_install_ok = (_install_mcporter() is not False) and core_install_ok

    if server_skipped_desktop_channels:
        print()
        print("  -- These channels require a desktop environment + Chrome and were skipped on the server: "
              f"{', '.join(sorted(server_skipped_desktop_channels))}")

    # ── Install optional channels (only if --channels specified) ──
    if requested_channels and not dry_run and not safe_mode:
        print()
        print("Installing optional channels...")
        ran_installers = set()
        optional_install_ok = True
        for ch_name in sorted(requested_channels):
            installer = CHANNEL_INSTALLERS.get(ch_name)
            if installer and installer not in ran_installers:
                optional_install_ok = (
                    installer() is not False
                ) and optional_install_ok
                ran_installers.add(installer)
    else:
        optional_install_ok = True

    if requested_channels and dry_run:
        print()
        print(f"[dry-run] Would install optional channels: {', '.join(sorted(requested_channels))}")

    # ── Cookie setup (explicit only — install never reads browser credentials) ──
    needs_cookies = bool(requested_channels & COOKIE_CHANNELS)
    if env == "local" and needs_cookies and not dry_run:
        print()
        print("Cookie login is never read automatically.")
        print("Run only the platform command you intend to authorize:")
        for channel in sorted(requested_channels & COOKIE_CHANNELS):
            if channel == "twitter":
                print("  agent-reach configure twitter-cookies")
    elif env == "local" and needs_cookies and dry_run:
        print()
        print("[dry-run] Cookie import remains explicit; install will not read a browser")

    # Environment-specific advice
    if env == "server":
        print()
        print("Tip: some platforms may restrict datacenter/server IPs.")
        print("   Reddit requires an authenticated route; see Doctor for the active backend and setup guidance.")
        print("   Save an explicit proxy for Agent Reach with: agent-reach configure proxy")
        print("   Cheap option: https://www.webshare.io ($1/month)")

    # Test channels
    if not dry_run:
        print()
        print("Testing channels...")
        results = check_all(config)
        ok = sum(1 for r in results.values() if r["status"] == "ok")
        total = len(results)

        # Final status
        print()
        print(format_report(results))
        print()

        if safe_mode:
            print(
                "Safe mode check complete. No changes were made. "
                f"{ok}/{total} channels active."
            )
        else:
            # ── Install agent skill ──
            skill_install_ok = _install_skill() is not False
            install_ok = (
                core_install_ok and optional_install_ok and skill_install_ok
            )

            if install_ok:
                print(f"Installation complete. {ok}/{total} channels active.")
            else:
                print(
                    "Installation incomplete: one or more requested "
                    f"steps failed. {ok}/{total} channels active."
                )

            if not requested_channels:
                # First install — hint about optional channels
                print()
                print("More channels available! Use --channels to install:")
                print("   agent-reach install --system --channels=twitter,reddit,facebook,instagram,linkedin,opencli")
                print("   agent-reach install --system --channels=all  (install everything)")

            # Star reminder
            print()
            print("If Agent Reach helps you, consider starring this fork:")
            print("   https://github.com/Maxei6/Agent-Reach-English")
            print("   It helps keep the fork discoverable. Thank you.")
            if not install_ok:
                raise SystemExit(1)
    else:
        print()
        print("Dry run complete. No changes were made.")


def _install_skill(force: bool = True):
    """Install Agent Reach as an agent skill for supported agent clients."""
    import importlib.resources
    import os
    import shutil

    def _read_skill_markdown(skill_pkg):
        return skill_pkg.joinpath("SKILL.md").read_text(encoding="utf-8")

    def _copy_skill_dir(target: str) -> str | None:
        """Copy entire skill directory (locale-specific SKILL.md + references/)."""
        try:
            if not force and os.path.exists(os.path.join(target, "SKILL.md")):
                return "preserved"

            # Clear existing installation. A symlinked skill dir (dotfiles
            # setups) breaks shutil.rmtree — unlink the link itself instead.
            if os.path.islink(target):
                os.unlink(target)
            elif os.path.exists(target):
                shutil.rmtree(target)
            os.makedirs(target, exist_ok=True)

            # Get skill directory from package (with fallback for editable installs)
            try:
                skill_pkg = importlib.resources.files("agent_reach").joinpath("skill")
                skill_md = _read_skill_markdown(skill_pkg)
            except Exception:
                from pathlib import Path
                skill_pkg = Path(__file__).resolve().parent / "skill"
                skill_md = _read_skill_markdown(skill_pkg)

            # Copy SKILL.md using the selected locale file
            with open(os.path.join(target, "SKILL.md"), "w", encoding="utf-8") as f:
                f.write(skill_md)

            # Copy references/ directory
            refs_pkg = skill_pkg.joinpath("references")
            refs_target = os.path.join(target, "references")
            os.makedirs(refs_target, exist_ok=True)

            for ref_file in refs_pkg.iterdir():
                name = ref_file.name if hasattr(ref_file, 'name') else str(ref_file).split('/')[-1]
                if name.endswith(".md"):
                    content = ref_file.read_text(encoding="utf-8") if hasattr(ref_file, 'read_text') else ref_file.read_text()
                    with open(os.path.join(refs_target, name), "w", encoding="utf-8") as f:
                        f.write(content)

            return "installed"
        except Exception as e:
            print(f"  Warning: Could not install skill: {e}")
            return None

    # Install into every known skill root that already exists.
    skill_dirs = [
        (os.path.expanduser("~/.agents/skills"), "Agent"),
        (os.path.expanduser("~/.config/opencode/skills"), "OpenCode"),
        (os.path.expanduser("~/.openclaw/skills"), "OpenClaw"),
        (os.path.expanduser("~/.claude/skills"), "Claude Code"),
    ]

    # Insert OPENCLAW_HOME path at the beginning if environment variable is set
    openclaw_home = os.environ.get("OPENCLAW_HOME")
    if openclaw_home:
        skill_dirs.insert(
            0,
            (os.path.join(openclaw_home, ".openclaw", "skills"), "OpenClaw"),
        )

    installed = False
    for skill_dir, platform_name in skill_dirs:
        if os.path.isdir(skill_dir):
            target = os.path.join(skill_dir, "agent-reach")
            status = _copy_skill_dir(target)
            if status:
                if status == "preserved":
                    print(f"Skill already installed for {platform_name}, preserving existing files: {target}")
                else:
                    print(f"Skill installed for {platform_name}: {target}")
                installed = True

    if not installed:
        # No known skill directory found — create for .agents by default
        target = os.path.expanduser("~/.agents/skills/agent-reach")
        os.makedirs(os.path.dirname(target), exist_ok=True)
        status = _copy_skill_dir(target)
        if status == "preserved":
            print(f"Skill already installed, preserving existing files: {target}")
        elif status == "installed":
            print(f"Skill installed: {target}")
            installed = True
        else:
            print("  -- Could not install agent skill (optional)")
            print(
                "  -- Tip: install OpenCode, OpenClaw, Claude Code, "
                "or create ~/.agents/skills/ manually"
            )
    return installed


def _uninstall_skill():
    """Remove SKILL.md from all known agent skill directories."""
    import shutil

    skill_dirs = [
        ("~/.config/opencode/skills/agent-reach", "OpenCode"),
        ("~/.openclaw/skills/agent-reach", "OpenClaw"),
        ("~/.claude/skills/agent-reach", "Claude Code"),
        ("~/.agents/skills/agent-reach", "Agent"),
    ]

    # Also check OPENCLAW_HOME
    openclaw_home = os.environ.get("OPENCLAW_HOME")
    if openclaw_home:
        skill_dirs.insert(
            0,
            (os.path.join(openclaw_home, ".openclaw", "skills", "agent-reach"), "OpenClaw"),
        )

    removed = False
    for skill_path_template, platform_name in skill_dirs:
        skill_path = os.path.expanduser(skill_path_template)
        if os.path.isdir(skill_path):
            try:
                if os.path.islink(skill_path):
                    os.unlink(skill_path)
                else:
                    shutil.rmtree(skill_path)
                print(f"  Removed {platform_name} skill: {skill_path}")
                removed = True
            except Exception as e:
                print(f"  Could not remove {skill_path}: {e}")

    if not removed:
        print("  No skill installations found.")


def _cmd_skill(args):
    """Manage agent skill registration."""
    if args.install:
        if not _install_skill():
            raise SystemExit(1)
    elif args.uninstall:
        _uninstall_skill()



def _install_system_deps():
    """Install system dependencies through an existing OS package manager."""
    import platform
    import shutil
    import subprocess

    print("Checking system dependencies...")

    gh_installed = bool(shutil.which("gh"))
    node_installed = bool(shutil.which("node") and shutil.which("npm"))

    if gh_installed:
        print("  ✅ gh CLI already installed")
    if node_installed:
        print("  ✅ Node.js already installed")

    missing_labels = []
    if not gh_installed:
        missing_labels.append("gh CLI")
    if not node_installed:
        missing_labels.append("Node.js")
    system_install_ok = not missing_labels

    os_type = platform.system().lower()
    if missing_labels and os_type == "linux":
        apt_get = shutil.which("apt-get")
        if not apt_get:
            system_install_ok = False
            print(
                "  [!]  Missing system dependencies: "
                f"{', '.join(missing_labels)}. apt-get is not available; "
                "install them manually."
            )
        else:
            packages = []
            if not gh_installed:
                packages.append("gh")
            if not node_installed:
                packages.extend(("nodejs", "npm"))
            print(f"  Installing {', '.join(missing_labels)} with apt-get...")
            try:
                update_result = subprocess.run(
                    [apt_get, "update", "-qq"],
                    capture_output=True,
                    timeout=120,
                )
                if update_result.returncode != 0:
                    system_install_ok = False
                    print(
                        "  [!]  apt-get update failed; no packages were installed."
                    )
                else:
                    install_result = subprocess.run(
                        [apt_get, "install", "-y", "-qq", *packages],
                        capture_output=True,
                        timeout=180,
                    )
                    if install_result.returncode == 0:
                        system_install_ok = True
                        print(
                            "  ✅ Installed with apt-get: "
                            f"{', '.join(missing_labels)}"
                        )
                    else:
                        system_install_ok = False
                        print(
                            "  [!]  apt-get install failed for: "
                            f"{', '.join(missing_labels)}"
                        )
            except (OSError, subprocess.TimeoutExpired):
                system_install_ok = False
                print(
                    "  [!]  apt-get failed for: "
                    f"{', '.join(missing_labels)}"
                )
    elif missing_labels and os_type == "darwin":
        brew = shutil.which("brew")
        if not brew:
            system_install_ok = False
            print(
                "  [!]  Missing system dependencies: "
                f"{', '.join(missing_labels)}. Homebrew is not available; "
                "install them manually."
            )
        else:
            system_install_ok = True
            brew_packages = []
            if not gh_installed:
                brew_packages.append(("gh", "gh CLI"))
            if not node_installed:
                brew_packages.append(("node", "Node.js"))
            for package, label in brew_packages:
                print(f"  Installing {label} with Homebrew...")
                try:
                    undici_result = subprocess.run(
                        [brew, "install", package],
                        capture_output=True,
                        timeout=180,
                    )
                    if undici_result.returncode == 0:
                        print(f"  ✅ {label} installed")
                    else:
                        system_install_ok = False
                        print(f"  [!]  {label} install failed")
                except (OSError, subprocess.TimeoutExpired):
                    system_install_ok = False
                    print(f"  [!]  {label} install failed")
    elif missing_labels:
        system_install_ok = False
        print(
            "  [!]  Missing system dependencies: "
            f"{', '.join(missing_labels)}. Install them manually."
        )

    # ── undici (proxy support for Node.js fetch) ──
    npm_cmd = shutil.which("npm")
    if npm_cmd:
        try:
            npm_root_result = subprocess.run(
                [npm_cmd, "root", "-g"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            npm_root_result = None

        if npm_root_result is None or npm_root_result.returncode != 0:
            print(
                "  -- Could not inspect global npm packages; "
                "skipping optional undici install"
            )
        else:
            npm_root = npm_root_result.stdout.strip()
            undici_path = (
                os.path.join(npm_root, "undici", "index.js")
                if npm_root
                else ""
            )
            if os.path.exists(undici_path):
                print("  ✅ undici already installed (Node.js proxy support)")
            else:
                try:
                    result = subprocess.run(
                        [npm_cmd, "install", "-g", "undici"],
                        capture_output=True,
                        encoding="utf-8",
                        errors="replace",
                        timeout=60,
                    )
                    if result.returncode == 0:
                        print("  ✅ undici installed (Node.js proxy support)")
                    else:
                        print(
                            "  -- undici install failed "
                            "(optional — may not work behind proxies)"
                        )
                except (OSError, subprocess.TimeoutExpired):
                    print(
                        "  -- undici install failed "
                        "(optional — may not work behind proxies)"
                    )

    # ── yt-dlp JS runtime config (YouTube requires external JS runtime) ──
    if shutil.which("deno"):
        print("  ✅ yt-dlp can use the installed Deno JS runtime")
    elif shutil.which("node"):
        from agent_reach.channels.youtube import (
            _JS_RUNTIMES_SUPPORTED_FROM,
            _parse_ytdlp_version,
        )
        from agent_reach.utils.paths import (
            PrivatePathError,
            atomic_write_private_text,
            get_ytdlp_config_path,
            read_small_text_no_follow,
        )

        ytdlp_cmd = shutil.which("yt-dlp")
        installed_version = None
        if ytdlp_cmd:
            try:
                version_result = subprocess.run(
                    [ytdlp_cmd, "--version"],
                    capture_output=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=10,
                )
                if version_result.returncode == 0:
                    installed_version = _parse_ytdlp_version(
                        version_result.stdout.strip()
                    )
            except (OSError, subprocess.TimeoutExpired):
                installed_version = None

        if (
            installed_version is None
            or installed_version < _JS_RUNTIMES_SUPPORTED_FROM
        ):
            print(
                "  -- yt-dlp JS runtime config was not written because yt-dlp is missing, too old, or "
                "its version could not be confirmed. Upgrade first: python -m pip install -U "
                '"yt-dlp[default]"'
            )
        else:
            ytdlp_config = get_ytdlp_config_path()
            try:
                existing_config = read_small_text_no_follow(
                    ytdlp_config,
                    max_bytes=1024 * 1024,
                )
                if (
                    existing_config is not None
                    and "--js-runtimes" in existing_config
                ):
                    print("  ✅ yt-dlp JS runtime already configured")
                else:
                    existing_config = existing_config or ""
                    separator = (
                        ""
                        if not existing_config
                        or existing_config.endswith(("\n", "\r"))
                        else "\n"
                    )
                    atomic_write_private_text(
                        ytdlp_config,
                        existing_config
                        + separator
                        + "--js-runtimes node\n",
                    )
                    print(
                        "  ✅ yt-dlp configured to use Node.js as JS runtime "
                        "(YouTube)"
                    )
            except (OSError, UnicodeError, ValueError, PrivatePathError):
                print(
                    "  -- Could not configure yt-dlp JS runtime "
                    "(YouTube may not work)"
                )

    # Platform-specific CLIs are optional and installed via --channels.
    # They are installed via --channels flag, not here.
    # See CHANNEL_INSTALLERS in _cmd_install().
    return system_install_ok



def _install_twitter_deps():
    """Install twitter-cli for Twitter search + timeline."""
    import shutil
    import subprocess

    print("Setting up Twitter (twitter-cli)...")
    if shutil.which("twitter"):
        print("  ✅ twitter-cli already installed")
        return True
    for tool, args in [
        ("pipx", ["install", "twitter-cli"]),
        ("uv", ["tool", "install", "twitter-cli"]),
    ]:
        tool_cmd = shutil.which(tool)
        if tool_cmd:
            try:
                result = subprocess.run(
                    [tool_cmd, *args], capture_output=True, encoding="utf-8",
                    errors="replace", timeout=120,
                )
                if result.returncode == 0 and shutil.which("twitter"):
                    print("  ✅ twitter-cli installed")
                    return True
            except (OSError, subprocess.TimeoutExpired):
                pass
    print("  [!]  twitter-cli install failed. Run: pipx install twitter-cli")
    return False



def _install_opencli_deps():
    """Install OpenCLI — cross-platform backend riding the user's Chrome session.

    Desktop-only. The npm package installs automatically; the Chrome
    extension CANNOT be installed programmatically (Chrome security model),
    so we print a one-click guide instead.
    """
    import shutil
    import subprocess

    from agent_reach.backends import (
        OPENCLI_EXTENSION_URL,
        OPENCLI_PACKAGE,
        opencli_status,
        opencli_summary,
    )

    print("Setting up OpenCLI (browser-session backend, desktop only)...")
    st = opencli_status()
    if st.installed and not st.broken:
        print(f"  ✅ {opencli_summary(st)}")
        if not st.ready:
            print(f"  {st.hint}")
        return True

    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        print("  [!]  OpenCLI requires Node.js ≥ 20. Install Node first:")
        print("       https://nodejs.org  (or brew install node)")
        return False

    try:
        install_result = subprocess.run(
            [npm_cmd, "install", "-g", OPENCLI_PACKAGE],
            capture_output=True, encoding="utf-8", errors="replace", timeout=300,
        )
    except (OSError, subprocess.TimeoutExpired):
        install_result = None

    st = opencli_status()
    if (
        install_result is not None
        and install_result.returncode == 0
        and st.installed
        and not st.broken
    ):
        print("  ✅ OpenCLI installed")
        print("  Final manual step required by Chrome: install the browser extension")
        print(f"    1. Open {OPENCLI_EXTENSION_URL}")
        print("    2. Click Add to Chrome")
        print("    3. Run `opencli doctor` to verify the connection")
        return True
    else:
        print(f"  [!]  OpenCLI install failed. Run: npm install -g {OPENCLI_PACKAGE}")
        return False


def _install_reddit_deps():
    """Set up Reddit — desktop prefers OpenCLI, rdt-cli for servers/legacy.

    No zero-config path exists (anonymous .json blocked, official API
    approval-gated since 2025-11) — every backend needs a logged-in session.
    """
    if _detect_environment() != "server":
        installed = _install_opencli_deps()
        print("  Reddit uses OpenCLI with an existing user-controlled reddit.com browser session")
        import shutil
        if shutil.which("rdt"):
            print("  ✅ Existing rdt-cli detected and kept as a fallback backend")
        return installed

    return _install_rdt_cli()


def _install_rdt_cli():
    """Install rdt-cli (pinned git source — PyPI lags upstream)."""
    import shutil
    import subprocess

    print("Setting up Reddit (rdt-cli)...")
    if shutil.which("rdt"):
        print("  ✅ rdt-cli already installed")
        return True
    for tool, args in [
        ("pipx", ["install", _RDT_GIT_SOURCE]),
        ("uv", ["tool", "install", "--from", _RDT_GIT_SOURCE, "rdt-cli"]),
    ]:
        tool_cmd = shutil.which(tool)
        if tool_cmd:
            try:
                result = subprocess.run(
                    [tool_cmd, *args], capture_output=True, encoding="utf-8",
                    errors="replace", timeout=120,
                )
                if result.returncode == 0 and shutil.which("rdt"):
                    print("  ✅ rdt-cli installed")
                    return True
            except (OSError, subprocess.TimeoutExpired):
                pass
    print(f"  [!]  rdt-cli install failed. Run: pipx install '{_RDT_GIT_SOURCE}'")
    return False



def _install_system_deps_safe():
    """Safe mode: check what's installed, print instructions for what's missing."""
    import shutil

    print("Checking system dependencies (safe mode — no auto-install)...")

    deps = [
        ("gh", ["gh"], "GitHub CLI", "https://cli.github.com — or: apt install gh / brew install gh"),
        ("node", ["node", "npm"], "Node.js", "https://nodejs.org — or: apt install nodejs npm"),
    ]

    missing = []
    for name, binaries, label, install_hint in deps:
        found = all(shutil.which(b) for b in binaries)
        if found:
            print(f"  ✅ {label} already installed")
        else:
            print(f"  -- {label} not found")
            missing.append((label, install_hint))

    if missing:
        print()
        print("  To install missing dependencies manually:")
        for label, hint in missing:
            print(f"    {label}: {hint}")
    else:
        print("  All system dependencies are installed!")


def _install_system_deps_dryrun():
    """Dry-run: just show what would be checked/installed."""
    import shutil

    print("[dry-run] System dependency check:")

    checks = [
        ("gh CLI", ["gh"], "apt-get install gh / brew install gh"),
        (
            "Node.js",
            ["node", "npm"],
            "apt-get install nodejs npm / brew install node",
        ),
    ]

    for label, binaries, method in checks:
        found = all(shutil.which(b) for b in binaries)
        if found:
            print(f"  ✅ {label}: already installed, skip")
        else:
            print(f"  {label}: would install via: {method}")



def _install_mcporter():
    """Install mcporter and configure Exa search."""
    import shutil
    import subprocess

    print("Setting up mcporter (search backend)...")

    mcporter_cmd = shutil.which("mcporter")
    if mcporter_cmd:
        print("  ✅ mcporter already installed")
    else:
        npm_cmd = shutil.which("npm")
        if not npm_cmd:
            print("  [!]  mcporter requires Node.js. Install Node.js first:")
            print("     https://nodejs.org/")
            return False
        try:
            install_result = subprocess.run(
                [npm_cmd, "install", "-g", "mcporter"],
                capture_output=True, encoding="utf-8", errors="replace", timeout=120,
            )
            mcporter_cmd = shutil.which("mcporter")
            if install_result.returncode == 0 and mcporter_cmd:
                print("  ✅ mcporter installed")
            else:
                print("  [X] mcporter install failed. Retry: npm install -g mcporter (check network/timeout), or try: npx mcporter@latest list")
                return False
        except (OSError, subprocess.TimeoutExpired) as e:
            print(f"  [X] mcporter install failed: {e}")
            return False

    # Configure Exa MCP (free, no key needed)
    try:
        from agent_reach.channels.mcporter import (
            McporterConfigError,
            configured_server_names,
        )

        r = subprocess.run(
            [mcporter_cmd, "config", "list", "--json"],
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=5,
        )
        if r.returncode != 0:
            raise McporterConfigError("mcporter configuration query failed")
        server_names = configured_server_names(r.stdout)
        if "exa" not in server_names:
            add_result = subprocess.run(
                [
                    mcporter_cmd,
                    "config",
                    "add",
                    "exa",
                    "https://mcp.exa.ai/mcp",
                    "--scope",
                    "home",
                ],
                capture_output=True, encoding="utf-8", errors="replace", timeout=10,
            )
            if add_result.returncode == 0:
                print("  ✅ Exa search configured (free, no API key needed)")
                return True
            else:
                print(
                    "  [!]  Could not configure Exa. Run manually: "
                    "mcporter config add exa https://mcp.exa.ai/mcp --scope home"
                )
                return False
        else:
            print("  ✅ Exa search already configured")
            return True
    except Exception:
        print("  [!]  Could not configure Exa. Run manually: mcporter config add exa https://mcp.exa.ai/mcp --scope home")
        return False



def _install_mcporter_safe():
    """Safe mode: check mcporter status, print instructions."""
    import shutil

    print("Checking mcporter (safe mode)...")

    if shutil.which("mcporter"):
        print("  ✅ mcporter already installed")
        print("  To configure Exa search: mcporter config add exa https://mcp.exa.ai/mcp --scope home")
    else:
        print("  -- mcporter not installed")
        print("  To install: npm install -g mcporter")
        print("  Then configure Exa: mcporter config add exa https://mcp.exa.ai/mcp --scope home")


def _detect_environment():
    """Auto-detect if running on local computer or server."""
    import os

    # Check common server indicators
    indicators = 0

    # SSH session
    if os.environ.get("SSH_CONNECTION") or os.environ.get("SSH_CLIENT"):
        indicators += 2

    # Docker / container
    if os.path.exists("/.dockerenv") or os.path.exists("/run/.containerenv"):
        indicators += 2

    # No display (headless)
    if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
        indicators += 1

    # Cloud VM identifiers
    for cloud_file in ["/sys/hypervisor/uuid", "/sys/class/dmi/id/product_name"]:
        if os.path.exists(cloud_file):
            try:
                with open(cloud_file) as f:
                    content = f.read().lower()
                if any(x in content for x in ["amazon", "google", "microsoft", "digitalocean", "linode", "vultr", "hetzner"]):
                    indicators += 2
            except Exception:
                pass

    # systemd-detect-virt
    try:
        import subprocess
        result = subprocess.run(["systemd-detect-virt"], capture_output=True, encoding="utf-8", errors="replace", timeout=3)
        if result.returncode == 0 and result.stdout.strip() != "none":
            indicators += 1
    except Exception:
        pass

    return "server" if indicators >= 2 else "local"


def _read_configure_value(args) -> str:
    """Read one configure value without echoing secrets by default."""
    values = getattr(args, "value", None) or []
    if getattr(args, "read_stdin", False):
        try:
            value = sys.stdin.read(_MAX_CONFIGURE_VALUE_CHARS + 1)
        except OSError:
            print("Could not read configure value from stdin", file=sys.stderr)
            raise SystemExit(1) from None
        if len(value) > _MAX_CONFIGURE_VALUE_CHARS:
            print("Configure value exceeds the 1 MiB safety limit", file=sys.stderr)
            raise SystemExit(1)
        return value.rstrip("\r\n")

    if values:
        if getattr(args, "key", None) in _SENSITIVE_CONFIG_KEYS:
            print(
                "Warning: positional secrets are deprecated because shell history "
                "and process listings may expose them; omit the value for a hidden "
                "prompt or use --stdin.",
                file=sys.stderr,
            )
        return " ".join(values)

    try:
        interactive = bool(sys.stdin.isatty())
    except (AttributeError, OSError):
        interactive = False
    if not interactive:
        return ""

    import getpass

    try:
        return getpass.getpass(f"Value for {args.key}: ")
    except (EOFError, KeyboardInterrupt):
        print("Configure input cancelled", file=sys.stderr)
        raise SystemExit(1) from None


def _cmd_configure(args):
    """Set an Agent Reach configuration value."""
    import shutil

    from agent_reach.config import Config

    config = Config()

    if not args.key:
        print("Usage: agent-reach configure <key> [--stdin]")
        print("   Omit the value to enter it through a hidden prompt.")
        return

    value = _read_configure_value(args)
    if not value:
        print(f"Missing value for {args.key}")
        raise SystemExit(1)

    if args.key == "proxy":
        config.set("proxy", value)
        print("✅ Proxy saved for Agent Reach to export as HTTP_PROXY/HTTPS_PROXY when needed")

    elif args.key == "twitter-cookies":
        auth_token, ct0 = _parse_twitter_cookie_input(value)

        if auth_token and ct0:
            config.set("twitter_auth_token", auth_token)
            config.set("twitter_ct0", ct0)

            print("✅ Twitter cookies saved to ~/.agent-reach/config.yaml")
            if getattr(args, "sync_legacy_twitter", False):
                from agent_reach.cookie_extract import (
                    _sync_bird_env,
                    _sync_xfetch_session,
                )

                legacy_results = (
                    ("~/.config/xfetch/session.json", _sync_xfetch_session(auth_token, ct0)),
                    ("~/.config/bird/credentials.env", _sync_bird_env(auth_token, ct0)),
                )
                for path, success in legacy_results:
                    outcome = "written" if success else "failed"
                    print(f"  {outcome}: {path}")

            print(
                "  Credentials were not live-verified. Doctor avoids commands that may "
                "fall back to browser-cookie reads."
            )
            if not shutil.which("twitter"):
                print("  [!] twitter-cli is not installed. Run: pipx install twitter-cli")
            else:
                print(
                    "  Note: the standalone twitter command does not read Agent Reach config; "
                    "set TWITTER_AUTH_TOKEN/TWITTER_CT0 explicitly when calling it directly."
                )
        else:
            print("[X] Could not find auth_token and ct0 in your input.")
            print("   Run agent-reach configure twitter-cookies and paste either:")
            print("   1. AUTH_TOKEN and CT0 separated by whitespace")
            print("   2. A Cookie-Editor Header String")
            print("   For automation, pass the same value through --stdin.")
            raise SystemExit(1)

    elif args.key == "youtube-cookies":
        config.set("youtube_cookies_from", value)
        print(f"✅ YouTube cookie source configured: {value}")
        print("   yt-dlp will use cookies from this browser when required.")

    elif args.key == "github-token":
        config.set("github_token", value)
        print("✅ GitHub token configured.")

    elif args.key == "groq-key":
        config.set("groq_api_key", value)
        print("✅ Groq key configured.")

    elif args.key == "openai-key":
        config.set("openai_api_key", value)
        print("✅ OpenAI key configured.")


def _cmd_transcribe(args):
    """Transcribe a URL or local audio file via an explicitly selected provider."""
    from pathlib import Path

    from agent_reach.transcribe import TranscribeError, transcribe
    from agent_reach.utils.text import scrub_url_credentials

    try:
        text = transcribe(
            args.source,
            provider=args.provider,
            allow_provider_fallback=getattr(
                args,
                "allow_provider_fallback",
                False,
            ),
        )
    except TranscribeError as e:
        print(f"❌ {scrub_url_credentials(e)}")
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"✅ Transcript written to {args.output}")
    else:
        print(text)


def _parse_twitter_cookie_input(value: str):
    """Parse Twitter cookie input from either separate values or a cookie header."""
    auth_token = None
    ct0 = None

    if "auth_token=" in value and "ct0=" in value:
        # Full cookie string — parse it.
        for part in value.replace(";", " ").split():
            if part.startswith("auth_token="):
                auth_token = part.split("=", 1)[1]
            elif part.startswith("ct0="):
                ct0 = part.split("=", 1)[1]
    elif len(value.split()) == 2 and "=" not in value:
        # Two separate values: AUTH_TOKEN CT0.
        parts = value.split()
        auth_token = parts[0]
        ct0 = parts[1]

    return auth_token, ct0



def _cmd_uninstall(args):
    """Remove all Agent Reach config, tokens, and skill files."""
    import shutil
    import subprocess

    from agent_reach.utils.paths import home_dir

    dry_run = args.dry_run
    keep_config = args.keep_config

    print()
    print("Agent Reach Uninstaller")
    print("=" * 40)

    if dry_run:
        print("DRY RUN — showing what would be removed (no changes)")
        print()

    removed_any = False
    mcporter_cleanup_skipped = False

    # ── 1. Config directory (~/.agent-reach/) ──
    config_dir = home_dir() / ".agent-reach"
    if not keep_config:
        if os.path.isdir(config_dir):
            if dry_run:
                print(f"[dry-run] Would remove config directory: {config_dir}")
                print("          (contains config.yaml with all tokens/cookies/API keys)")
            else:
                try:
                    shutil.rmtree(config_dir)
                    print(f"  Removed config directory: {config_dir}")
                    removed_any = True
                except Exception as e:
                    print(f"  Could not remove {config_dir}: {e}")
        else:
            print(f"  Config directory not found (already clean): {config_dir}")
    else:
        print(f"  Skipping config directory (--keep-config): {config_dir}")

    # Opt-in legacy copies may be shared with upstream tools. Without a
    # provenance marker it would be unsafe to delete them automatically, so
    # surface every exact path that may still contain Twitter credentials.
    legacy_credential_paths = (
        home_dir() / ".config" / "xfetch" / "session.json",
        home_dir() / ".config" / "bird" / "credentials.env",
    )
    present_legacy_paths = [
        path for path in legacy_credential_paths if os.path.lexists(path)
    ]
    if present_legacy_paths:
        print("  [!] Optional legacy Twitter credential copies were detected; they will not be deleted automatically:")
        for path in present_legacy_paths:
            print(f"      {path}")
        print("      If they are no longer used by xfetch/bird, remove them manually.")

    # ── 2. Skill files ──
    skill_dirs = [
        ("~/.config/opencode/skills/agent-reach", "OpenCode"),
        ("~/.openclaw/skills/agent-reach", "OpenClaw"),
        ("~/.claude/skills/agent-reach", "Claude Code"),
        ("~/.agents/skills/agent-reach", "Agent"),
    ]

    for skill_path_template, platform_name in skill_dirs:
        skill_path = os.path.expanduser(skill_path_template)
        if os.path.isdir(skill_path):
            if dry_run:
                print(f"[dry-run] Would remove {platform_name} skill: {skill_path}")
            else:
                try:
                    if os.path.islink(skill_path):
                        os.unlink(skill_path)
                    else:
                        shutil.rmtree(skill_path)
                    print(f"  Removed {platform_name} skill: {skill_path}")
                    removed_any = True
                except Exception as e:
                    print(f"  Could not remove {skill_path}: {e}")

    # ── 3. mcporter MCP entries ──
    if shutil.which("mcporter"):
        from agent_reach.channels.mcporter import (
            McporterConfigError,
            configured_server_names,
        )

        try:
            result = subprocess.run(
                [
                    "mcporter",
                    "config",
                    "list",
                    "--json",
                ],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            if result.returncode != 0:
                raise McporterConfigError("mcporter config query failed")
            server_names = configured_server_names(result.stdout)
        except (
            McporterConfigError,
            OSError,
            subprocess.TimeoutExpired,
        ):
            mcporter_cleanup_skipped = True
            print(
                "  [!] Could not safely verify the source of the mcporter configuration; "
                "Agent Reach will not automatically delete unverified entries."
            )
        else:
            for mcp_name in ("exa",):
                if mcp_name not in server_names:
                    continue
                mcporter_cleanup_skipped = True
                print(
                    f"  [!] mcporter entry {mcp_name} source cannot be proven to be managed by "
                    "Agent Reach; it was preserved. Remove it manually only if you confirm it is no longer needed."
                )

    # ── 4. Summary and optional steps ──
    print()
    if dry_run:
        print("Dry run complete. No changes were made.")
        print("Run without --dry-run to actually remove the above.")
    else:
        if removed_any:
            print("Agent Reach data removed.")
        elif mcporter_cleanup_skipped:
            print("No proven Agent Reach-managed mcporter data was removed.")
        else:
            print("Nothing to remove — already clean.")

    print()
    print("Optional: remove the Agent Reach Python package itself:")
    print("  pip uninstall agent-reach")
    print()
    print("Optional: remove tools installed by Agent Reach:")
    print("  npm uninstall -g mcporter")
    print("  pipx uninstall twitter-cli")
    print("  npm uninstall -g undici")


def _cmd_doctor(args=None):
    from agent_reach.config import Config
    from agent_reach.doctor import check_all, format_report
    config = Config(read_only=True)
    results = check_all(config)

    if args is not None and getattr(args, "json", False):
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return

    report = format_report(results)
    try:
        from rich import print as rich_print
    except ImportError:
        print(report)
    else:
        rich_print(report)


def _cmd_setup():
    import getpass

    from agent_reach.config import Config

    config = Config()
    print()
    print("Agent Reach Setup")
    print("=" * 40)
    print()

    # Step 1: Exa (via mcporter, no API key required)
    import shutil
    import subprocess

    print("[Recommended] Web search — Exa via mcporter")
    print("  Free MCP route; no local API key required")

    if not shutil.which("mcporter"):
        print("  Current status: mcporter is not installed")
        print("  Install: npm install -g mcporter")
        print("  Then: mcporter config add exa https://mcp.exa.ai/mcp --scope home")
        print()
    else:
        try:
            from agent_reach.channels.mcporter import (
                McporterConfigError,
                configured_server_names,
            )

            r = subprocess.run(
                ["mcporter", "config", "list", "--json"],
                capture_output=True,
                encoding="utf-8",
                errors="replace",
                timeout=10,
            )
            if r.returncode != 0:
                raise McporterConfigError("mcporter configuration query failed")
            if "exa" in configured_server_names(r.stdout):
                print("  Current status: ✅ configured")
            else:
                print("  Current status: not configured")
                setup_now = input("  Configure Exa automatically now? [Y/n]: ").strip().lower()
                if setup_now in ("", "y", "yes"):
                    add_r = subprocess.run(
                        [
                            "mcporter",
                            "config",
                            "add",
                            "exa",
                            "https://mcp.exa.ai/mcp",
                            "--scope",
                            "home",
                        ],
                        capture_output=True, encoding="utf-8", errors="replace", timeout=10,
                    )
                    if add_r.returncode == 0:
                        print("  ✅ Exa configured")
                    else:
                        print("  [!] Automatic setup failed. Run manually:")
                        print("     mcporter config add exa https://mcp.exa.ai/mcp --scope home")
        except Exception:
            print("  [!] Could not inspect Exa configuration. Run manually:")
            print("     mcporter config add exa https://mcp.exa.ai/mcp --scope home")
        print()

    # Step 2: GitHub token
    print("[Optional] GitHub token — increase API limits")
    print("  Without token: 60 requests/hour | with token: 5000 requests/hour")
    print("  Get one at: https://github.com/settings/tokens")
    current = config.get("github_token")
    if current:
        print("  Current status: ✅ configured")
    else:
        key = getpass.getpass("  GITHUB_TOKEN (Enter to skip): ").strip()
        if key:
            config.set("github_token", key)
            print("  ✅ GitHub API limit increased")
        else:
            print("  Skipped. Public GitHub API access still works.")
    print()

    # Step 3: Reddit — rdt-cli
    print("[Info] Reddit requires authentication. Prefer OpenCLI on desktop, or rdt-cli:")
    print(f"  Install: pipx install '{_RDT_GIT_SOURCE}'")
    print("  Then run: rdt login")
    print()

    # Step 4: Groq (Whisper)
    print("[Optional] Groq API — transcribe video when subtitles are unavailable")
    print("  Sign up: https://console.groq.com")
    current = config.get("groq_api_key")
    if current:
        print("  Current status: ✅ configured")
    else:
        key = getpass.getpass("  GROQ_API_KEY (Enter to skip): ").strip()
        if key:
            config.set("groq_api_key", key)
            print("  ✅ Audio transcription enabled")
        else:
            print("  Skipped")
    print()

    # Summary
    print("=" * 40)
    print(f"✅ Configuration saved to {config.config_path}")
    print("Run agent-reach doctor for full status")
    print()


def _classify_update_error(exc):
    """Classify update-check errors for user-friendly diagnostics."""
    import requests

    if isinstance(exc, requests.exceptions.Timeout):
        return "timeout"
    if isinstance(exc, requests.exceptions.ConnectionError):
        msg = str(exc).lower()
        dns_markers = [
            "name or service not known",
            "temporary failure in name resolution",
            "nodename nor servname",
            "getaddrinfo failed",
            "name resolution",
            "dns",
        ]
        if any(marker in msg for marker in dns_markers):
            return "dns"
        return "connection"
    if isinstance(exc, requests.exceptions.HTTPError):
        return "http"
    return "unknown"


def _update_error_text(kind):
    """Map internal error kinds to user-facing text."""
    mapping = {
        "timeout": "network timeout",
        "dns": "DNS resolution failed",
        "rate_limit": "GitHub API rate limit",
        "connection": "network connection failed",
        "server_error": "GitHub service temporarily unavailable",
        "http": "HTTP request failed",
        "unknown": "unknown network error",
    }
    return mapping.get(kind, "request failed")


def _classify_github_response_error(resp):
    """Classify non-200 GitHub responses that merit special handling."""
    if resp is None:
        return "unknown"
    if resp.status_code == 429:
        return "rate_limit"
    if resp.status_code == 403:
        remaining = resp.headers.get("X-RateLimit-Remaining", "")
        if remaining == "0":
            return "rate_limit"
        try:
            message = resp.json().get("message", "").lower()
            if "rate limit" in message:
                return "rate_limit"
        except Exception:
            pass
    if 500 <= resp.status_code < 600:
        return "server_error"
    return None


def _github_get_with_retry(url, timeout=10, retries=3, sleeper=time.sleep):
    """GET GitHub API with retry/backoff and basic error classification."""
    import requests

    for attempt in range(1, retries + 1):
        try:
            resp = requests.get(url, timeout=timeout)
        except requests.exceptions.RequestException as exc:
            if attempt >= retries:
                return None, _classify_update_error(exc), attempt
            sleeper(2 ** (attempt - 1))
            continue

        err_kind = _classify_github_response_error(resp)
        if err_kind in ("rate_limit", "server_error"):
            if attempt >= retries:
                return None, err_kind, attempt
            delay = 2 ** (attempt - 1)
            retry_after = resp.headers.get("Retry-After")
            if err_kind == "rate_limit" and retry_after:
                try:
                    delay = max(delay, float(retry_after))
                except Exception:
                    pass
            sleeper(delay)
            continue

        return resp, None, attempt

    return None, "unknown", retries


#: Full update = package + upstream tools + skill. The one-liner walks an
#: agent through all three (docs/update.md); bare pip only updates the package.
_UPDATE_INSTRUCTIONS = (
    "Recommended update source:\n"
    "  Update Agent Reach from: https://raw.githubusercontent.com/Maxei6/Agent-Reach-English/main/docs/update.md\n"
    "Package-only update:\n"
    "  pip install --upgrade https://github.com/Maxei6/Agent-Reach-English/archive/main.zip"
)


def _is_newer_version(remote: str, local: str) -> bool:
    """True if remote is strictly newer than local (semantic compare).

    A plain != would tell users "update available" when their local build is
    AHEAD of the latest release (e.g. installed from main during a release
    window) — and walk them into a downgrade.
    """
    def parse(v):
        try:
            return tuple(int(x) for x in v.strip().split("."))
        except ValueError:
            return None

    remote_version, local_version = parse(remote), parse(local)
    if remote_version is None or local_version is None:
        return remote != local  # unparseable — fall back to old behavior
    return remote_version > local_version


def _cmd_check_update():
    """Check for newer versions on GitHub."""
    from agent_reach import __version__

    print(f"Current version: v{__version__}")
    release_url = "https://api.github.com/repos/Maxei6/Agent-Reach-English/releases/latest"
    commit_url = "https://api.github.com/repos/Maxei6/Agent-Reach-English/commits/main"

    # Fetch latest release with retry/backoff.
    resp, err, attempts = _github_get_with_retry(release_url, timeout=10, retries=3)
    if err:
        print(f"[!] Could not check for updates({_update_error_text(err)}, retried {attempts} times)")
        return "error"

    if resp.status_code == 200:
        data = resp.json()
        latest = data.get("tag_name", "").lstrip("v")
        body = data.get("body", "")

        if latest and _is_newer_version(latest, __version__):
            print(f"Latest version: v{latest} ← update available!")
            if body:
                print()
                print("Changes:")
                # Show first 20 lines of release notes
                for line in body.strip().split("\n")[:20]:
                    print(f"  {line}")
            print()
            print(_UPDATE_INSTRUCTIONS)
            return "update_available"
        print("✅ Already on the latest version")
        return "up_to_date"

    release_err = _classify_github_response_error(resp)
    if release_err == "rate_limit":
        print("[!] Could not check for updates(GitHub API rate limit, try again later)")
        return "error"

    # No releases yet, fall back to latest main commit.
    resp2, err2, attempts2 = _github_get_with_retry(commit_url, timeout=10, retries=2)
    if err2:
        print(f"[!] Could not check for updates({_update_error_text(err2)}, retried {attempts + attempts2} times)")
        return "error"
    if resp2.status_code == 200:
        commit = resp2.json()
        sha = commit.get("sha", "")[:7]
        msg = commit.get("commit", {}).get("message", "").split("\n")[0]
        date = commit.get("commit", {}).get("committer", {}).get("date", "")[:10]
        print(f"Latest commit: {sha} ({date}) {msg}")
        print()
        print(_UPDATE_INSTRUCTIONS)
        return "unknown"

    commit_err = _classify_github_response_error(resp2)
    if commit_err == "rate_limit":
        print("[!] Could not check for updates(GitHub API rate limit, try again later)")
        return "error"

    print(f"[!] Could not check for updates(GitHub returned {resp2.status_code})")
    return "error"


def _cmd_watch():
    """Quick health check + update check, designed for scheduled tasks.

    Only outputs problems. If everything is fine, outputs a single line.
    """
    from agent_reach import __version__
    from agent_reach.config import Config
    from agent_reach.doctor import check_all

    config = Config(read_only=True)
    issues = []

    # Check channels
    results = check_all(config)
    ok = sum(1 for r in results.values() if r["status"] == "ok")
    total = len(results)

    # Find broken channels (were working, now broken)
    for key, r in results.items():
        if r["status"] in ("off", "error"):
            issues.append(f"[X] {r['name']}：{r['message']}")
        elif r["status"] == "warn":
            issues.append(f"[!] {r['name']}：{r['message']}")

    # Check for updates
    update_available = False
    new_version = ""
    release_body = ""
    resp, err, _attempts = _github_get_with_retry(
        "https://api.github.com/repos/Maxei6/Agent-Reach-English/releases/latest",
        timeout=10,
        retries=2,
    )
    if not err and resp and resp.status_code == 200:
        data = resp.json()
        latest = data.get("tag_name", "").lstrip("v")
        if latest and _is_newer_version(latest, __version__):
            update_available = True
            new_version = latest
            release_body = data.get("body", "")

    # Output
    if not issues and not update_available:
        print(f"Agent Reach: all healthy ({ok}/{total} channels available, v{__version__} latest)")
        return

    print("Agent Reach watch report")
    print("=" * 40)
    print(f"Version: v{__version__}  |  channels: {ok}/{total}")

    if issues:
        print()
        for issue in issues:
            print(f"  {issue}")

    if update_available:
        print()
        print(f"New version available: v{new_version}")
        if release_body:
            for line in release_body.strip().split("\n")[:10]:
                print(f"    {line}")
        print("  Update:")
        print("    Update Agent Reach from: https://raw.githubusercontent.com/Maxei6/Agent-Reach-English/main/docs/update.md")


if __name__ == "__main__":
    main()
