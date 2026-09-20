# Career and LinkedIn

This edition keeps LinkedIn support and removes Boss Zhipin.

## Read a public LinkedIn URL

For public pages, Jina Reader may be sufficient:

```bash
curl -s "https://r.jina.ai/URL"
```

## Rich LinkedIn access

When the LinkedIn MCP backend is configured, use it for richer profile,
company, and job-search operations.

Check status:

```bash
agent-reach doctor --json
```

If the backend is not configured, follow Doctor's English setup message or
`docs/install.md`.

Do not claim a LinkedIn MCP backend is healthy merely because a config entry
exists; distinguish configuration from a verified live connection.
