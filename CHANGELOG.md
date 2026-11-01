# Changelog

All notable changes to the English / International Edition are documented here.

## Unreleased

### 2026-11-01 — selective upstream maintenance

- Raised the tested yt-dlp baseline to upstream's 2026.8.19 release and kept the official `[default]` dependency set.
- Added macOS CI coverage and a mypy gate, matching useful upstream release hardening without importing the incompatible 1.6 runtime.
- Removed two stray CJK punctuation marks from retained Reddit agent-facing guidance.
- Ported upstream's Windows retry for atomically replacing private files; applied it to both text state and YAML config writes.
- Forwarded OS-detected proxies to pipx, uv and npm package installer subprocesses without replacing explicitly configured proxy values.
- Added cross-platform regression tests for transient Windows file locks and proxy handling.
- Kept the established English/international 1.5 CLI and channel scope; upstream's incompatible 1.6 runtime/browser overhaul is not copied wholesale.

### Fork scope

- Converted the primary README and agent-facing project guidance to English.
- Added a clear explanation of why this fork exists.
- Retained the `agent-reach` package and CLI names for drop-in compatibility.
- Changed repository-facing URLs to `Maxei6/Agent-Reach-English`.
- Removed China-specific integrations from the maintained international edition.
- Refreshed installation and migration instructions so an agent can replace the upstream package while preserving local configuration.

## Upstream history

This repository is derived from https://github.com/Panniantong/Agent-Reach.

For historical changes made before this fork diverged, consult the upstream project's changelog and Git history.

## License

MIT. The upstream copyright and license notice are preserved in `LICENSE`.
