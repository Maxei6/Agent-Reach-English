# CLAUDE.md

## Project

Agent Reach — English / International Edition.

Python CLI + library that gives AI agents read/search access to broadly useful internet platforms. It is an independent MIT-licensed derivative of Panniantong/Agent-Reach.

Purpose of this fork:
- English-only agent-facing skills, docs, diagnostics, and maintained instructions.
- Keep the `agent-reach` package and CLI name for drop-in compatibility.
- Remove China-specific integrations: Bilibili, XiaoHongShu, Boss Zhipin, V2EX, Xueqiu, and Xiaoyuzhou.
- Preserve the upstream architecture instead of reimagining it.

Repository: github.com/Maxei6/Agent-Reach-English
License: MIT

## Commands

- `pip install -e .` — development install
- `pytest tests/ -v` — tests
- `bash test.sh` — integration test
- `python -m agent_reach.cli doctor` — diagnostics
- `python -m agent_reach.cli install --env=auto` — environment/setup check

## Structure

- `agent_reach/cli.py` — CLI entry point
- `agent_reach/config.py` — local config management
- `agent_reach/doctor.py` — diagnostics
- `agent_reach/channels/` — one file per retained platform
- `agent_reach/backends/` — shared backends such as OpenCLI
- `agent_reach/integrations/` — MCP integration
- `agent_reach/skill/` — agent skill
- `agent_reach/guides/` — setup guides
- `tests/` — pytest tests

## Rules

- Keep all agent-facing text in English.
- Do not reintroduce China-specific channels into this fork.
- Keep the package/CLI name `agent-reach` unless there is a strong compatibility reason to change it.
- Preserve the original MIT copyright/license notice.
- Keep upstream attribution in the README.
- Prefer small, modular changes.
- Never log cookies, tokens, or secrets.
- Run tests before proposing changes.
- Make changes on a branch and propose them through a PR; do not push feature work directly to main.
