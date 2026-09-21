# Search

## Exa semantic web search

Preferred route:

```bash
mcporter call exa.web_search_exa query="QUERY" numResults=5
```

Check availability first when needed:

```bash
agent-reach doctor --json
```

If Exa is not configured, follow the setup guidance from Doctor or
`docs/install.md`. Do not fabricate search results.

For research that needs primary sources, use Exa for discovery and then fetch
the original source pages directly when practical.
