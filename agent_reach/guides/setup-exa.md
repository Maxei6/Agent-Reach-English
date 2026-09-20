# Exa Search Setup

Exa provides semantic web search through MCP.

## Install mcporter

```bash
npm install -g mcporter
```

## Register Exa MCP

```bash
mcporter config add exa https://mcp.exa.ai/mcp --scope home
```

## Verify

```bash
mcporter call exa.web_search_exa query="test" numResults=3
agent-reach doctor --json
```

Agent Reach should distinguish between a config entry existing and a live
backend actually being verified.
