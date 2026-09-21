# Web pages and RSS

## Normal web pages

Use Jina Reader for readable Markdown:

```bash
curl -s "https://r.jina.ai/URL"
```

If Jina returns an anti-bot/interstitial page instead of the target content,
use a site-specific retained tool or a user-controlled browser path rather than
pretending the page was read successfully.

## RSS / Atom

Use Python `feedparser` or the existing Agent Reach RSS channel.

Check availability:

```bash
agent-reach doctor --json
```

Preserve feed titles, item URLs, publication dates, and ordering when those
fields are available.
