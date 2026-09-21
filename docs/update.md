# Update Agent Reach — English / International Edition

Use this repository as the update source:

https://github.com/Maxei6/Agent-Reach-English

## pipx

```bash
pipx install --force https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor --json
```

## pip / virtual environment

```bash
python -m pip install --upgrade --force-reinstall https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor --json
```

Refreshing the skill is mandatory during migration because it replaces Agent Reach in every known skill root that already exists (Agent, OpenCode, OpenClaw, Claude Code, plus OPENCLAW_HOME when configured).

Before updating, identify the active executable and common package locations with `command -v agent-reach`, `pipx list`, and `python -m pip show agent-reach`. Preserve `~/.agent-reach/`. Do not recursively remove unknown virtual environments; report stale copies that cannot be positively identified instead.

Do not update from `Panniantong/Agent-Reach` unless the user explicitly wants
to switch back to the upstream edition.

Do not reinstall China-specific channels that this edition intentionally
removed.

After updating, report:

1. the installed Agent Reach version;
2. the Doctor status for retained channels;
3. any manual login/browser-extension step still required.
