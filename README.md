# Agent Reach — English / International Edition

> Give your AI agent reliable read/search access to the public internet using a small capability layer that installs, routes, and health-checks upstream tools.

This repository is an **English-only, international-focused derivative of [Agent Reach](https://github.com/Panniantong/Agent-Reach)**.

## Why this fork exists

The upstream project is useful, but a significant amount of its agent-facing skill text, diagnostics, and documentation is written in Chinese. That matters when an AI agent loads `SKILL.md` directly into context: the instructions the agent reasons over should be in the same working language as the rest of the agent stack.

This fork therefore has a deliberately narrow goal:

- keep the core Agent Reach architecture and drop-in `agent-reach` CLI;
- make agent-facing instructions, CLI output, documentation, and maintained tests English-only;
- keep broadly useful international platforms;
- remove integrations that are primarily specific to the Chinese market;
- stay easy to replace/update from GitHub without changing existing agent workflows.

This is an independent fork. Upstream credit and the original MIT license are preserved.

## Included platforms

| Capability | Backend / route |
|---|---|
| Any web page | Jina Reader |
| Web search | Exa via mcporter |
| GitHub | GitHub CLI |
| YouTube | yt-dlp |
| Twitter / X | twitter-cli, with OpenCLI fallback where available |
| Reddit | OpenCLI or rdt-cli |
| Facebook | OpenCLI |
| Instagram | OpenCLI |
| LinkedIn | LinkedIn MCP / Jina Reader fallback |
| RSS / Atom | feedparser |

The following upstream China-focused integrations are intentionally removed from this edition: **Bilibili, XiaoHongShu, Boss Zhipin, V2EX, Xueqiu, and Xiaoyuzhou Podcast**.

## Drop-in compatibility

The Python package name and command remain:

```text
agent-reach
```

That is intentional. You do **not** need to rename your existing agent instructions or shell commands when switching from upstream Agent Reach to this fork.

## Install

### Recommended: pipx

```bash
pipx install --force https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor
```

### pip / virtual environment

```bash
python -m pip install --upgrade --force-reinstall https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor
```

> Do not install the unrelated PyPI package merely by name. Install this repository directly from GitHub.

## Replace the original Agent Reach installation

Give this section to an agent if upstream Agent Reach is already installed.

1. Detect how `agent-reach` is installed.
2. Remove the existing Python package without deleting the user's Agent Reach configuration.
3. Install this repository using the same package manager.
4. Force-refresh the bundled skill so the agent loads the English-only version.
5. Run diagnostics.

### If installed with pipx

```bash
pipx uninstall agent-reach
pipx install https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor
```

### If installed with pip / venv

```bash
python -m pip uninstall -y agent-reach
python -m pip install https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
agent-reach skill --install
agent-reach doctor
```

Do **not** delete `~/.agent-reach/` during migration unless the user explicitly wants to erase saved configuration and credentials.

## Copy-paste instruction for an AI agent

```text
Replace my current upstream Agent Reach installation with the English/international fork:
https://github.com/Maxei6/Agent-Reach-English

Reason: this fork keeps the Agent Reach capability model but makes the agent-facing skills, documentation, diagnostics, and maintained instructions English-only, while removing China-specific integrations that I do not use.

Requirements:
1. Detect whether the current agent-reach package is installed with pipx, pip, or inside a virtual environment.
2. Preserve ~/.agent-reach/ configuration and credentials.
3. Remove only the currently installed agent-reach Python package.
4. Install the fork directly from:
   https://github.com/Maxei6/Agent-Reach-English/archive/main.zip
   using the same package-management method when practical.
5. Run: agent-reach skill --install
   This step is mandatory so the installed skill is replaced by the English-only skill from this fork.
6. Run: agent-reach doctor --json
7. Confirm that the active skill and package come from this fork and report any channel that still needs login/setup.
8. Do not reinstall or restore Bilibili, XiaoHongShu, Boss Zhipin, V2EX, Xueqiu, or Xiaoyuzhou integrations.
```

## Core commands

```bash
agent-reach doctor
agent-reach doctor --json
agent-reach install --env=auto
agent-reach skill --install
agent-reach check-update
```

Agent Reach is a capability/router layer rather than a wrapper around every service. After setup, the agent generally calls the selected upstream tool directly.

## Security model

- Credentials remain local in `~/.agent-reach/`.
- Doctor checks should avoid silently reading browser cookies.
- Login-backed services should use explicit user-controlled sessions or manually supplied credentials.
- Use `agent-reach doctor --json` before relying on login-backed platforms.
- Do not log tokens, cookies, session IDs, or secrets.

## Development

```bash
python -m pip install -e ".[dev]"
pytest -q
ruff check agent_reach tests
```

Keep changes modular: one channel per file, health checks through the channel registry, and agent instructions in `agent_reach/skill/`.

## Upstream and license

This project is derived from [Panniantong/Agent-Reach](https://github.com/Panniantong/Agent-Reach).

The upstream code is distributed under the **MIT License**. This fork keeps the original license and copyright notice as required by MIT. See [LICENSE](LICENSE).

MIT permits use, modification, distribution, sublicensing, and commercial use, provided the copyright and license notice are retained in copies or substantial portions of the software.

