# Install Agent Reach — English / International Edition

Repository: https://github.com/Maxei6/Agent-Reach-English

This fork exists so AI agents load English-only Agent Reach instructions and so
international deployments do not carry China-specific channels they do not use.

## Fresh installation

### pipx (recommended)

```bash
pipx install https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor --json
```

### pip / virtual environment

```bash
python -m pip install https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor --json
```

Do not install an unrelated package merely by running `pip install agent-reach`.
Install this repository directly from GitHub.

## Replace the original upstream installation

Preserve `~/.agent-reach/`. It may contain the user's configuration and
credentials.

First determine how the command is installed:

```bash
command -v agent-reach || which agent-reach
pipx list 2>/dev/null | grep -i agent-reach || true
```

### Existing pipx installation

```bash
pipx uninstall agent-reach
pipx install https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor --json
```

### Existing pip / venv installation

Use the same Python environment that currently owns the command:

```bash
python -m pip uninstall -y agent-reach
python -m pip install https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor --json
```

The `skill --install` step is mandatory during migration: it replaces the
previous bundled agent instructions with this fork's English-only skill.

Do not run `agent-reach uninstall` during migration unless you explicitly want
to remove Agent Reach configuration as well.

## Environment check

The safe default is read-only:

```bash
agent-reach install --env=auto
```

To allow Agent Reach to install supported system/upstream dependencies:

```bash
agent-reach install --env=auto --system
```

Review the command's output before installing optional login-backed channels.

## Retained optional channels

This edition keeps the following platform families:

- Twitter/X
- Reddit
- Facebook
- Instagram
- LinkedIn
- YouTube
- GitHub
- Exa web search
- RSS/Atom
- normal web pages

The following upstream integrations are deliberately not part of this edition:
Bilibili, XiaoHongShu, Boss Zhipin, V2EX, Xueqiu, and Xiaoyuzhou.

## OpenCLI

On desktop machines, OpenCLI can provide browser-session-backed access to
supported social platforms.

```bash
agent-reach install --env=local --system --channels=opencli
opencli doctor
```

The user may need to install/enable the OpenCLI browser extension and log into
the desired website in their own browser. Do not silently extract browser
cookies.

## Twitter/X

Install the CLI only with explicit permission:

```bash
agent-reach install --env=auto --system --channels=twitter
```

For explicit Cookie-Editor exports:

```bash
agent-reach configure twitter-cookies
```

The standalone `twitter` command may require:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

Never print these values.

## Reddit

Desktop preferred route:

```bash
agent-reach install --env=local --system --channels=opencli
opencli reddit search "query" -f yaml
```

Alternative where rdt-cli is installed/configured:

```bash
rdt search "query" --limit 10
```

## Facebook / Instagram

Use OpenCLI with an existing browser session controlled by the user:

```bash
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml
```

## LinkedIn

Basic public pages can be read through Jina Reader. Richer LinkedIn capability
uses the optional LinkedIn MCP route when configured.

## Exa

```bash
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp --scope home
agent-reach doctor --json
```

## Verification

Finish every install or migration with:

```bash
agent-reach version
agent-reach doctor --json
```

Confirm that the installed skill points to
`https://github.com/Maxei6/Agent-Reach-English`.
