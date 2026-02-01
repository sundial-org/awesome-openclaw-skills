# Database Query Skill - Installation

## Quick Setup

1. **Install MySQL client** (if not already installed):
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install mysql-client

   # macOS
   brew install mysql-client
   ```

2. **Create configuration directory and file**:
   ```bash
   mkdir -p ~/.config/clawdbot
   cp /usr/lib/node_modules/clawdbot/skills/db-query/scripts/config.example.json ~/.config/clawdbot/db-config.json
   ```

3. **Edit configuration** with your database details:
   ```bash
   nano ~/.config/clawdbot/db-config.json
   ```

4. **Test listing databases**:
   ```bash
   python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py --list
   ```

## Configuration

Each database entry requires:
- `name`: Human-readable description (used to find the database)
- `host`, `port`: Database connection details
- `database`, `user`, `password`: Authentication
- `ssh_tunnel`: Optional SSH tunnel configuration

See `config.example.json` for complete examples.

## SSH Keys

For SSH tunnel authentication, either:
1. **SSH password**: Will prompt for password each time
2. **SSH key-based auth** (recommended): Set up key-based login to remote host

```bash
# Generate SSH key (if needed)
ssh-keygen -t ed25519

# Copy to remote host
ssh-copy-id user@remote.example.com
```
