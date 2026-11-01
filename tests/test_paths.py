# -*- coding: utf-8 -*-
"""Behavior tests for cross-platform path and remediation helpers."""

import shutil
import subprocess
from pathlib import Path

import pytest

from agent_reach.utils import paths


def test_posix_ytdlp_fix_is_single_line_executable_and_idempotent(
    monkeypatch, tmp_path
):
    monkeypatch.setattr(paths.sys, "platform", "linux")
    monkeypatch.setattr(paths.Path, "home", classmethod(lambda cls: tmp_path))
    monkeypatch.delenv("XDG_CONFIG_HOME")

    command = paths.render_ytdlp_fix_command()

    assert "\n" not in command
    shell = shutil.which("sh")
    if not shell:
        pytest.skip("POSIX sh is unavailable on this platform")
    subprocess.run([shell, "-c", command], check=True)
    subprocess.run([shell, "-c", command], check=True)

    config = tmp_path / ".config" / "yt-dlp" / "config"
    assert config.read_text(encoding="utf-8") == "--js-runtimes node\n"


def test_ytdlp_config_dir_matches_upstream_first_user_location(
    monkeypatch, tmp_path
):
    from yt_dlp.options import get_user_config_dirs

    config_home = tmp_path / "xdg-config"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config_home))

    expected = Path(next(get_user_config_dirs("yt-dlp")))

    assert paths.get_ytdlp_config_dir() == expected


def test_windows_private_atomic_write_retries_transient_file_lock(monkeypatch, tmp_path):
    target = tmp_path / "settings.txt"
    target.write_text("old", encoding="utf-8")
    original_replace = paths.os.replace
    attempts = []
    sleeps = []

    def temporarily_locked(source, destination):
        attempts.append((source, destination))
        if len(attempts) <= 2:
            raise PermissionError("file temporarily locked")
        return original_replace(source, destination)

    with monkeypatch.context() as patch:
        patch.setattr(paths.sys, "platform", "win32")
        patch.setattr(paths.os, "replace", temporarily_locked)
        patch.setattr(paths.time, "sleep", sleeps.append)
        paths.atomic_write_private_text(target, "new")

    assert target.read_text(encoding="utf-8") == "new"
    assert len(attempts) == 3
    assert sleeps == [0.05, 0.05]


def test_non_windows_private_replace_does_not_retry_permission_error(monkeypatch, tmp_path):
    source = tmp_path / "source"
    target = tmp_path / "target"
    source.write_text("new", encoding="utf-8")
    target.write_text("old", encoding="utf-8")
    attempts = []

    def denied(*args):
        attempts.append(args)
        raise PermissionError("access denied")

    with monkeypatch.context() as patch:
        patch.setattr(paths.sys, "platform", "linux")
        patch.setattr(paths.os, "replace", denied)
        patch.setattr(paths.time, "sleep", lambda _: pytest.fail("no retry expected"))
        with pytest.raises(PermissionError, match="access denied"):
            paths._replace_private_file(source, target)

    assert len(attempts) == 1
    assert target.read_text(encoding="utf-8") == "old"


def test_windows_yaml_config_write_retries_transient_file_lock(monkeypatch, tmp_path):
    from agent_reach import config

    target = tmp_path / "config.yaml"
    target.write_text("old: true\n", encoding="utf-8")
    original_replace = paths.os.replace
    attempts = []

    def locked_once(source, destination):
        attempts.append((source, destination))
        if len(attempts) == 1:
            raise PermissionError("antivirus lock")
        return original_replace(source, destination)

    with monkeypatch.context() as patch:
        patch.setattr(paths.sys, "platform", "win32")
        patch.setattr(paths.os, "replace", locked_once)
        patch.setattr(paths.time, "sleep", lambda _: None)
        config._atomic_write_yaml(target, {"new": True})

    assert target.read_text(encoding="utf-8") == "new: true\n"
    assert len(attempts) == 2
