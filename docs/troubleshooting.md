# Troubleshooting

## Start with Doctor

```bash
agent-reach doctor --json
```

Use the reported channel, status, message, and active backend instead of
guessing.

## Twitter/X credentials are configured but the CLI still fails

Agent Reach can store explicit Twitter credentials for diagnostics, but the
standalone `twitter` command may require them in its own environment:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
twitter status
```

Never print the secret values.

If network routing requires a proxy, set it explicitly for the process:

```bash
export HTTP_PROXY="http://host:port"
export HTTPS_PROXY="http://host:port"
```

## Reddit is unavailable

Reddit normally requires an authenticated route. On desktop, verify OpenCLI and
the user's existing browser session:

```bash
opencli doctor
opencli reddit search "test" -f yaml
```

Where rdt-cli is used, verify its explicit credential/session setup. Do not
silently import browser cookies.

## OpenCLI is installed but not connected

1. Keep Chrome/Edge open.
2. Confirm the OpenCLI extension is installed and enabled.
3. Run:

```bash
opencli doctor
```

A file existing on disk does not prove that a browser extension is loaded or
connected.

## GitHub CLI is present but not authenticated

```bash
gh auth login
```

Doctor avoids performing commands that may mutate authentication state.

## YouTube / yt-dlp problems

Upgrade yt-dlp and ensure a supported JavaScript runtime such as Node.js is
available:

```bash
python -m pip install -U "yt-dlp[default]"
node --version
yt-dlp --version
```

Then rerun Doctor.

## Exa is not configured

```bash
npm install -g mcporter
mcporter config add exa https://mcp.exa.ai/mcp --scope home
agent-reach doctor --json
```

## This fork unexpectedly shows a China-specific channel

That is not expected. The English/international edition intentionally removes
Bilibili, XiaoHongShu, Boss Zhipin, V2EX, Xueqiu, and Xiaoyuzhou.

Verify that the package and skill were installed from:

https://github.com/Maxei6/Agent-Reach-English

Then force-refresh the package and run:

```bash
agent-reach skill --install
agent-reach doctor --json
```
