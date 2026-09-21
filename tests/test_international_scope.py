"""Fork-scope regression tests for the English/international edition."""

from __future__ import annotations

import json
import re
from pathlib import Path

from agent_reach.channels import get_all_channels

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "agent_reach"

EXPECTED_CHANNELS = {
    "github",
    "twitter",
    "youtube",
    "reddit",
    "facebook",
    "instagram",
    "linkedin",
    "rss",
    "exa_search",
    "web",
}

REMOVED_MODULES = {
    "bilibili.py",
    "boss.py",
    "v2ex.py",
    "xiaohongshu.py",
    "xiaoyuzhou.py",
    "xueqiu.py",
}


def test_registry_contains_only_international_channels():
    assert {channel.name for channel in get_all_channels()} == EXPECTED_CHANNELS


def test_removed_channel_modules_do_not_exist():
    channel_dir = PACKAGE / "channels"
    assert not ({path.name for path in channel_dir.glob("*.py")} & REMOVED_MODULES)


def test_repository_contains_no_cjk_instruction_text():
    cjk = re.compile(r"[\u3400-\u9fff]")
    offenders = []

    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix not in {".py", ".md", ".txt", ".json", ".sh", ".yml", ".yaml", ".toml"}:
            continue
        if any(part in {".git", ".venv", "venv", "dist", "build"} for part in path.parts):
            continue
        text = path.read_text(encoding="utf-8")
        if cjk.search(text):
            offenders.append(str(path.relative_to(ROOT)))

    assert offenders == [], f"CJK text remains in repository text files: {offenders}"


def test_bundled_mcporter_config_contains_only_exa():
    data = json.loads((ROOT / "config" / "mcporter.json").read_text(encoding="utf-8"))
    assert set(data["mcpServers"]) == {"exa"}


def test_primary_docs_explain_fork_and_install_from_this_repo():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    install = (ROOT / "docs" / "install.md").read_text(encoding="utf-8")

    assert "Why this fork exists" in readme
    assert "English-only" in readme
    assert "MIT" in readme
    assert "Maxei6/Agent-Reach-English" in readme
    assert "Maxei6/Agent-Reach-English" in install
    assert "agent-reach skill --install" in install
