# HokiPoki CLI Command Reference

## Authentication

| Command | Description |
|---|---|
| `hokipoki login` | Authenticate (opens browser) |
| `hokipoki logout` | Remove local auth |
| `hokipoki whoami` | Show current user |

## Request (Requester)

```
hokipoki request --tool <tool> --task "<description>" [options]
```

| Option | Description |
|---|---|
| `--tool <tool>` | AI tool: `claude`, `codex`, `gemini` |
| `--task <task>` | Task description |
| `--files <files...>` | Specific files to include |
| `--dir <dirs...>` | Directories to include recursively |
| `--all` | Include entire repo (respects .gitignore) |
| `--workspace <id>` | Route to specific team workspace |
| `--no-auto-apply` | Save patch without applying |
| `--json` | JSON output for programmatic use |
| `--interactive` | Interactive mode (human terminal only, NOT for agent use) |

## Provider

```bash
# Register (one-time)
hokipoki register --as-provider --tools claude codex gemini

# Listen for requests
hokipoki listen --tools claude codex
```

## Status

```bash
hokipoki status      # Account info, workspaces, history
hokipoki dashboard   # Open web dashboard
```

## Shell Completion

```bash
hokipoki completion --install   # One-time setup
exec $SHELL                     # Restart shell
```

## Token Locations

| Tool | Auth Command | Token Location |
|---|---|---|
| Claude | `claude setup-token` | `~/.hokipoki/` |
| Codex | `codex login` | `~/.codex/auth.json` |
| Gemini | `gemini` | `~/.gemini/oauth_creds.json` |

Auto-refresh: `hokipoki listen` auto-triggers re-auth if a token is expired.

## Codex Sandbox Fix

Codex blocks `.git/` writes by default. Add to `~/.codex/config.toml`:

```toml
[sandbox_workspace_write]
writable_roots = [".git"]
```

## Security Model

- Encrypted P2P connections
- LUKS-encrypted Docker containers
- Ephemeral git servers with one-time tokens
- No code retention after task completion
- Container memory auto-wiped after each task
- API keys never leave the provider's machine
