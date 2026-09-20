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

Refreshing the skill is important because this fork's purpose is to keep the
agent-facing instructions English-only.

Do not update from `Panniantong/Agent-Reach` unless the user explicitly wants
to switch back to the upstream edition.

Do not reinstall China-specific channels that this edition intentionally
removed.

After updating, report:

1. the installed Agent Reach version;
2. the Doctor status for retained channels;
3. any manual login/browser-extension step still required.
