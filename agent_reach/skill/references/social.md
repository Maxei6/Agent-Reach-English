# Social platforms

This edition supports Twitter/X, Reddit, Facebook, and Instagram.

Run:

```bash
agent-reach doctor --json
```

before relying on a login-backed backend.

## Twitter / X

Preferred direct CLI when configured:

```bash
twitter search "QUERY" -n 10
```

Agent Reach may store explicit Twitter credential values in its local config
for diagnostics, but the standalone `twitter` command may require
`TWITTER_AUTH_TOKEN` and `TWITTER_CT0` in the child-process environment.
Never print those values.

If the preferred CLI is unavailable and OpenCLI is healthy, use the relevant
OpenCLI Twitter adapter.

## Reddit

There is no reliable zero-login path. Preferred desktop route:

```bash
opencli reddit search "QUERY" -f yaml
```

Alternative where `rdt-cli` is explicitly configured:

```bash
rdt search "QUERY" --limit 10
```

Use an explicit user-controlled login/session. Doctor must not silently import
browser cookies.

## Facebook

```bash
opencli facebook search "QUERY" -f yaml
opencli facebook groups -f yaml
```

Requires an existing browser session controlled by the user.

## Instagram

```bash
opencli instagram search "QUERY" -f yaml
opencli instagram user USERNAME -f yaml
```

Requires an existing browser session controlled by the user.

## Retry policy

If a login-backed command returns empty/authentication output, do not loop
aggressively. Re-run Doctor, verify the browser extension/session or explicit
credentials, and retry once after the user has completed any required login.
