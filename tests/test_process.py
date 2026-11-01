from agent_reach.utils import process
from agent_reach.utils.process import (
    install_subprocess_env,
    mcporter_utf8_env_args,
    utf8_subprocess_env,
)


def test_utf8_subprocess_env_forces_python_utf8():
    env = utf8_subprocess_env({"PYTHONUTF8": "0", "OTHER": "value"})

    assert env["PYTHONUTF8"] == "1"
    assert env["PYTHONIOENCODING"] == "utf-8"
    assert env["OTHER"] == "value"


def test_mcporter_utf8_env_args():
    assert mcporter_utf8_env_args() == [
        "--env",
        "PYTHONUTF8=1",
        "--env",
        "PYTHONIOENCODING=utf-8",
    ]


def test_installer_env_inherits_system_https_proxy(monkeypatch):
    monkeypatch.setattr(
        process.urllib.request,
        "getproxies",
        lambda: {"https": "http://system-proxy.example:8080"},
    )
    env = install_subprocess_env({"PATH": "/usr/bin"})

    assert env["HTTPS_PROXY"] == "http://system-proxy.example:8080"
    assert env["HTTP_PROXY"] == "http://system-proxy.example:8080"
    assert env["PATH"] == "/usr/bin"


def test_installer_env_preserves_explicit_proxies(monkeypatch):
    def unexpected_proxy_probe():
        raise AssertionError("system proxy must not replace explicit settings")

    monkeypatch.setattr(process.urllib.request, "getproxies", unexpected_proxy_probe)
    existing = {
        "HTTPS_PROXY": "http://explicit.example:1234",
        "HTTP_PROXY": "http://another.example:4321",
    }
    assert install_subprocess_env(existing) == existing


def test_installer_env_does_not_overwrite_explicit_http_proxy(monkeypatch):
    monkeypatch.setattr(
        process.urllib.request,
        "getproxies",
        lambda: {"https": "http://system.example:8080"},
    )
    result = install_subprocess_env({"HTTP_PROXY": "http://user.example:8000"})
    assert result["HTTPS_PROXY"] == "http://system.example:8080"
    assert result["HTTP_PROXY"] == "http://user.example:8000"


def test_twitter_installer_forwards_proxy_env(monkeypatch):
    import shutil
    import subprocess
    from types import SimpleNamespace

    from agent_reach import cli

    invocations = []

    def fake_which(command):
        if command == "twitter":
            return "/usr/bin/twitter" if invocations else None
        return "/usr/bin/pipx" if command == "pipx" else None

    def fake_run(argv, **kwargs):
        invocations.append((argv, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(shutil, "which", fake_which)
    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setattr(
        cli, "install_subprocess_env",
        lambda: {"HTTPS_PROXY": "http://system.example:8080"},
    )

    assert cli._install_twitter_deps() is True
    assert invocations[0][1]["env"]["HTTPS_PROXY"] == "http://system.example:8080"
