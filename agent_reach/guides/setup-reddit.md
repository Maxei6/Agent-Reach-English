# Reddit Setup

Reddit generally requires an authenticated route.

## Desktop: OpenCLI

```bash
agent-reach install --env=local --system --channels=opencli
opencli doctor
opencli reddit search "query" -f yaml
```

Use an existing browser session controlled by the user.

## Alternative: rdt-cli

If rdt-cli is already installed/configured:

```bash
rdt search "query" --limit 10
```

Do not silently read browser cookies. If authentication is missing, ask the
user to complete the required login or provide an explicit supported credential
export.

## Fallback discovery

Exa can discover Reddit pages:

```bash
mcporter call exa.web_search_exa query="site:reddit.com query" numResults=5
```
