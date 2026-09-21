# Contributing to Agent Reach — English / International Edition

This repository is an English-only international derivative of Agent Reach.

## Scope

Changes should preserve the upstream capability-router architecture while keeping the fork focused on broadly useful international platforms.

Do not reintroduce Bilibili, XiaoHongShu, Boss Zhipin, V2EX, Xueqiu, or Xiaoyuzhou into this edition.

All maintained code comments, user-facing strings, tests, documentation, and agent skill instructions should be in English.

## Development setup

```bash
git clone https://github.com/Maxei6/Agent-Reach-English.git
cd Agent-Reach-English
python -m pip install -e ".[dev]"
```

## Checks

```bash
ruff check agent_reach tests
mypy agent_reach
pytest
```

## Adding or changing a channel

1. Keep one platform per file in `agent_reach/channels/`.
2. Follow the existing channel contract.
3. Add or update tests.
4. Register the channel in `agent_reach/channels/__init__.py`.
5. Update the English skill/docs.
6. Avoid hidden credential reads and never log secrets.

## Pull requests

Use a branch, keep changes focused, and run the test suite before proposing the PR.

## Upstream

This fork is derived from https://github.com/Panniantong/Agent-Reach and remains under the MIT license. Preserve the existing LICENSE file and upstream copyright notice.
