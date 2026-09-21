---
name: agent-reach
description: >
  MUST USE when the user wants to research, search, look up, find, or read
  information from the public internet, or when the user shares a public URL
  from Twitter/X, Reddit, Facebook, Instagram, YouTube, GitHub, LinkedIn, an
  RSS/Atom feed, or a normal web page.

  This is the English/international edition of Agent Reach. It intentionally
  excludes China-specific integrations. Use `agent-reach doctor --json` to
  inspect available backends before using login-backed platforms.

  NOT for posting, commenting, liking, or other write actions. NOT for
  transforming content after it has already been fetched.
metadata:
  homepage: https://github.com/Maxei6/Agent-Reach-English
---

# Agent Reach — English / International Edition

Agent Reach is an internet capability router. It helps the agent choose and
health-check upstream tools, then the agent calls those upstream tools directly.

## Scope

Supported capabilities in this edition:

- Web pages
- Exa web search
- GitHub
- YouTube
- Twitter / X
- Reddit
- Facebook
- Instagram
- LinkedIn
- RSS / Atom

Do not install, suggest, or restore Bilibili, XiaoHongShu, Boss Zhipin, V2EX,
Xueqiu, or Xiaoyuzhou integrations in this edition.

## Standing rules

1. For Twitter/X, Reddit, Facebook, Instagram, or LinkedIn, run
   `agent-reach doctor --json` before relying on a backend.
2. Respect `active_backend` when Doctor provides one.
3. Never print cookies, access tokens, session IDs, or secret values.
4. Do not silently read browser cookies. Use explicit user-controlled sessions
   or credentials.
5. For broad research, combine sources when useful: Exa for discovery,
   platform-native tools for discussions, GitHub for code, and Jina Reader for
   normal web pages.
6. Keep temporary files in `/tmp/`; persistent Agent Reach state belongs in
   `~/.agent-reach/`.
7. If a dedicated first-party or already-installed skill is clearly better for
   the requested service, prefer it instead of duplicating capability.

## Routing table

| Intent | Reference |
|---|---|
| Web / semantic search | [references/search.md](references/search.md) |
| Twitter, Reddit, Facebook, Instagram | [references/social.md](references/social.md) |
| LinkedIn / jobs research | [references/career.md](references/career.md) |
| GitHub / code | [references/dev.md](references/dev.md) |
| Web pages / RSS | [references/web.md](references/web.md) |
| YouTube / video transcripts | [references/video.md](references/video.md) |

## Common commands

```bash
# Environment / routing status
agent-reach doctor --json

# Exa semantic web search
mcporter call exa.web_search_exa query="query" numResults=5

# Read a normal web page
curl -s "https://r.jina.ai/https://example.com/page"

# Search GitHub repositories
gh search repos "query" --sort stars --limit 10

# Extract YouTube subtitles without downloading video
yt-dlp --write-sub --write-auto-sub --skip-download -o "/tmp/%(id)s" "URL"

# Twitter/X
twitter search "query" -n 10

# Reddit
opencli reddit search "query" -f yaml
# or, where configured:
rdt search "query" --limit 10

# Facebook / Instagram through an existing user-controlled browser session
opencli facebook search "query" -f yaml
opencli instagram search "query" -f yaml
```

## Failure behavior

If a command fails:

1. Re-run `agent-reach doctor --json`.
2. Read the matching reference file.
3. Follow the documented backend/setup path.
4. Do not invent credential locations or scrape private browser state.
5. If the service requires the user to log in or click a browser-extension
   prompt, ask for that explicit user action and continue after it is complete.

## Updating this fork

Use only this repository as the update source:

https://github.com/Maxei6/Agent-Reach-English

Do not update from the upstream repository unless the user explicitly asks to
switch back to upstream Agent Reach.
