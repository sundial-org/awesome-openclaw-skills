---
name: db-query
description: Query project databases with automatic SSH tunnel management. Use when you need to execute SQL queries against configured databases, especially those accessible only via SSH tunnels. Automatically manages SSH connection lifecycle (establishes tunnel before query, closes after). Supports multiple databases distinguished by description/name from config file.
---

# Database Query

## Overview

Query databases through a centralized configuration file with automatic SSH tunnel management. Handles connection details, SSH tunnel setup/teardown, and query execution.

## Configuration

### Setup

1. **Create config file** at `~/.config/clawdbot/db-config.json`:
   ```bash
   mkdir -p ~/.config/clawdbot
   # Copy example config and edit
   cp /usr/lib/node_modules/clawdbot/skills/db-query/scripts/config.example.json ~/.config/clawdbot/db-config.json
   ```

2. **Add database entries** with these fields:
   - `name`: Description used to find the database (required)
   - `host`: Database host (required)
   - `port`: Database port (default: 3306)
   - `database`: Database name (required)
   - `user`: Database user (required)
   - `password`: Database password (required)
   - `ssh_tunnel`: Optional SSH tunnel configuration

3. **SSH tunnel configuration** (if needed):
   - `enabled`: true/false
   - `ssh_host`: Remote SSH host
   - `ssh_user`: SSH username
   - `ssh_port`: SSH port (default: 22)
   - `local_port`: Local port to forward (e.g., 3307)
   - `remote_host`: Remote database host behind SSH (default: localhost)
   - `remote_port`: Remote database port (default: 3306)

### Example Config

```json
{
  "databases": [
    {
      "name": "生产用户库",
      "host": "localhost",
      "port": 3306,
      "database": "user_db",
      "user": "db_user",
      "password": "secret",
      "ssh_tunnel": {
        "enabled": true,
        "ssh_host": "prod.example.com",
        "ssh_user": "deploy",
        "local_port": 3307
      }
    }
  ]
}
```

## Usage

### List Databases

```bash
python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py --list
```

### Query a Database

```bash
python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py \
  --database "生产用户库" \
  --query "SELECT * FROM users LIMIT 10"
```

The script will:
1. Find database by matching description in config
2. Start SSH tunnel (if configured)
3. Execute query
4. **Automatically close SSH tunnel** (important for cleanup)

### With Custom Config Path

```bash
python3 /usr/lib/node_modules/clawdbot/skills/db-query/scripts/db_query.py \
  --config /path/to/custom-config.json \
  --database "test" \
  --query "SHOW TABLES"
```

## Requirements

- MySQL client: `apt install mysql-client` or equivalent
- SSH client: usually pre-installed on Linux/Mac
- Python 3.6+

## Notes

- SSH tunnels are automatically closed after query execution
- Use `--list` to see all configured databases and their descriptions
- Database search is case-insensitive partial match on `name` field
- Local ports for SSH tunnels should be unique per database
