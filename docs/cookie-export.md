# Cookie Export Guide

Use explicit cookie exports only when a retained platform actually requires
them. Never place cookies in command-line arguments or logs.

## Twitter/X

1. Log in to https://x.com in your own browser.
2. Use a user-controlled cookie export tool such as Cookie-Editor.
3. Export the cookie header.
4. Run:

```bash
agent-reach configure twitter-cookies
```

The command uses a hidden prompt. For automation, send the same value over
stdin:

```bash
printf '%s' "$COOKIE_EXPORT" | agent-reach configure twitter-cookies --stdin
```

Agent Reach stores the explicit `auth_token` and `ct0` values locally for
Doctor/config checks. The standalone `twitter` CLI may still require
`TWITTER_AUTH_TOKEN` and `TWITTER_CT0` in its process environment.

## Browser-session platforms

For Reddit, Facebook, and Instagram, the preferred desktop route is OpenCLI
with an existing browser session controlled by the user.

Do not silently read browser-cookie databases. If a login is required, ask the
user to complete it in their browser, then verify the backend with:

```bash
opencli doctor
agent-reach doctor --json
```

## Security

- Treat cookies as passwords.
- Do not paste them into shell history or public logs.
- Do not commit them to Git.
- Use dedicated/secondary accounts where appropriate.
- Remove expired credentials from local Agent Reach config when no longer needed.
