# GitHub

Use the official GitHub CLI when possible.

```bash
gh repo view OWNER/REPO
gh search repos "QUERY" --sort stars --limit 10
gh search code "QUERY" --repo OWNER/REPO
gh issue list --repo OWNER/REPO
gh pr list --repo OWNER/REPO
```

For private repositories or authenticated operations, the user must have
completed `gh auth login`.

Use `agent-reach doctor --json` to inspect the local GitHub capability state.
Never print tokens or credentials.
