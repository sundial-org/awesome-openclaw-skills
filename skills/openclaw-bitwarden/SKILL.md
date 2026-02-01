---
name: bitwarden
description: Set up and use Bitwarden CLI (bw). Use when installing the CLI, unlocking vault, or reading/generating secrets via bw. Handles session management with BW_SESSION.
homepage: https://bitwarden.com/help/cli/
metadata: {"openclaw":{"emoji":"🔐","requires":{"bins":["bw","tmux"]},"install":[{"id":"brew-bw","kind":"brew","formula":"bitwarden-cli","bins":["bw"],"label":"Install Bitwarden CLI (brew)"},{"id":"brew-tmux","kind":"brew","formula":"tmux","bins":["tmux"],"label":"Install tmux (brew)"}]}}
---

# Bitwarden CLI

Manage passwords and secrets via the Bitwarden CLI.

## References

- `references/get-started.md` (install + login + unlock flow)
- `references/cli-examples.md` (real `bw` examples)

## Workflow

1. Check CLI present: `bw --version`.
2. Check login status: `bw status` (returns JSON with status field).
3. If not logged in: `bw login` (stores API key, prompts for master password).
4. REQUIRED: create a fresh tmux session for all `bw` commands.
5. Unlock vault inside tmux: `bw unlock` (outputs session key).
6. Export session key: `export BW_SESSION="<key>"`.
7. Verify access: `bw sync` then `bw list items --search test`.

## REQUIRED tmux session

The Bitwarden CLI requires the BW_SESSION environment variable for authenticated commands. To persist the session across commands, always run `bw` inside a dedicated tmux session.

Example (see `tmux` skill for socket conventions):

```bash
SOCKET_DIR="${CLAWDBOT_TMUX_SOCKET_DIR:-${TMPDIR:-/tmp}/openclaw-tmux-sockets}"
mkdir -p "$SOCKET_DIR"
SOCKET="$SOCKET_DIR/openclaw-bw.sock"
SESSION="bw-auth-$(date +%Y%m%d-%H%M%S)"

tmux -S "$SOCKET" new -d -s "$SESSION" -n shell

# Unlock and capture session key
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'export BW_SESSION=$(bw unlock --raw)' Enter
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'bw sync' Enter
tmux -S "$SOCKET" send-keys -t "$SESSION":0.0 -- 'bw list items --search github' Enter

# Capture output
tmux -S "$SOCKET" capture-pane -p -J -t "$SESSION":0.0 -S -200

# Cleanup when done
tmux -S "$SOCKET" kill-session -t "$SESSION"
```

## Common Commands

| Command | Description |
|---------|-------------|
| `bw status` | Check login/lock status (JSON) |
| `bw login` | Login with email/password or API key |
| `bw unlock` | Unlock vault, returns session key |
| `bw lock` | Lock vault |
| `bw sync` | Sync vault with server |
| `bw list items` | List all items |
| `bw list items --search <query>` | Search items |
| `bw get item <id-or-name>` | Get specific item (JSON) |
| `bw get password <id-or-name>` | Get just the password |
| `bw get username <id-or-name>` | Get just the username |
| `bw get totp <id-or-name>` | Get TOTP code |
| `bw generate -ulns --length 32` | Generate password |

## Guardrails

- Never paste secrets into logs, chat, or code.
- Always use tmux to maintain BW_SESSION across commands.
- Prefer `bw get password` over parsing full item JSON when only password needed.
- If command returns "Vault is locked", re-run `bw unlock` inside tmux.
- Do not run authenticated `bw` commands outside tmux; the session won't persist.
- Lock vault when done: `bw lock`.

## Testing with Vaultwarden

This skill includes a Docker Compose setup for local testing with [Vaultwarden](https://github.com/dani-garcia/vaultwarden) (self-hosted Bitwarden-compatible server).

### Quick Start

```bash
# Install mkcert and generate local certs (one-time)
brew install mkcert
mkcert -install
cd /path/to/openclaw-bitwarden
mkdir -p certs && cd certs
mkcert localhost 127.0.0.1 ::1
cd ..

# Start Vaultwarden + Caddy
docker compose up -d

# Configure bw CLI to use local server
bw config server https://localhost:8443

# Create a test account via web UI at https://localhost:8443
# Or run the setup script:
./scripts/setup-test-account.sh

# Test the skill workflow
./scripts/test-skill-workflow.sh
```

### Test Credentials

- **Server URL:** https://localhost:8443
- **Admin Panel:** https://localhost:8443/admin (token: `test-admin-token-12345`)
- **Suggested test account:** test@example.com / TestPassword123!

### Node.js CA Trust

The bw CLI requires the mkcert CA to be trusted. Export before running bw commands:

```bash
export NODE_EXTRA_CA_CERTS="$(mkcert -CAROOT)/rootCA.pem"
```

Or add to your shell profile for persistence.

### Cleanup

```bash
docker compose down -v  # Remove container and data
```
