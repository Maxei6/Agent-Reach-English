"""Subprocess helpers for consistent cross-platform text handling."""

from __future__ import annotations

import os
import urllib.request
from collections.abc import Mapping

UTF8_ENV = {
    "PYTHONUTF8": "1",
    "PYTHONIOENCODING": "utf-8",
}


def utf8_subprocess_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Return an environment that forces Python child processes into UTF-8 mode."""
    env = dict(base or os.environ)
    env.update(UTF8_ENV)
    return env


def install_subprocess_env(base: Mapping[str, str] | None = None) -> dict[str, str]:
    """Pass the system HTTPS proxy to package installers unless already configured.

    pipx, uv and npm can need the OS proxy on machines where the user has not
    exported HTTPS_PROXY. Preserve all explicit proxy environment settings.
    """
    env = dict(os.environ if base is None else base)
    if env.get("HTTPS_PROXY") or env.get("https_proxy"):
        return env

    try:
        proxies = urllib.request.getproxies()
    except (OSError, ValueError):
        return env
    proxy = proxies.get("https") or proxies.get("http")
    if proxy:
        env["HTTPS_PROXY"] = proxy
        if not env.get("HTTP_PROXY") and not env.get("http_proxy"):
            env["HTTP_PROXY"] = proxy
    return env


def mcporter_utf8_env_args() -> list[str]:
    """Return mcporter --env arguments for UTF-8 Python stdio servers."""
    args = []
    for key, value in UTF8_ENV.items():
        args.extend(["--env", f"{key}={value}"])
    return args
