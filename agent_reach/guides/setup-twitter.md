# Twitter/X Setup

Basic public URLs may be readable through the normal web route. Search and
timeline capabilities use twitter-cli or another healthy retained backend.

## Install twitter-cli

With explicit permission:

```bash
agent-reach install --env=auto --system --channels=twitter
```

## Configure explicit cookies

Export the relevant x.com cookies manually with a user-controlled tool such as
Cookie-Editor, then run:

```bash
agent-reach configure twitter-cookies
```

Agent Reach stores the values locally for diagnostics. The standalone
`twitter` CLI may still require:

```bash
export TWITTER_AUTH_TOKEN="..."
export TWITTER_CT0="..."
```

Do not print these values.

## Verify

```bash
agent-reach doctor --json
twitter status
```

Only run a live Twitter command when the user's task requires it and the
credentials are explicitly available.
