# dSIPRouter Skill

A powerful Bash-based skill for interacting with the dSIPRouter REST API. Generated from the included Postman collection, this skill provides a convenient CLI and a safe curl-based calling convention.

Are you looking for our MCP Server?  It's located [here](https://github.com/dOpensource/dsiprouter-mcp)

## Installation

### Prerequisites

Before installing this skill, ensure you have the following tools available on your system:

- **curl** — For making HTTP requests
- **jq** — For JSON processing and formatting
- **Bash** — Version 4.0 or later

You can verify these are installed:
```bash
command -v curl && command -v jq && bash --version
```

On macOS, install missing tools using Homebrew:
```bash
brew install curl jq
```

On Linux (Ubuntu/Debian):
```bash
sudo apt-get install curl jq
```

### Installation Steps

1. **Clone or copy the repository:**
```bash
git clone https://github.com/dOpensource/dsiprouter-skill
cd dsiprouter-skill
```

2. **Make the CLI executable:**
```bash
chmod +x bin/dsiprouter.sh
```

3. **Add to your PATH (optional but recommended):**
```bash
# Copy to a directory in your PATH
sudo cp bin/dsiprouter.sh /usr/local/bin/

# Or add the current directory to PATH in your shell profile
export PATH="$PWD/bin:$PATH"
```

4. **Configure environment variables:**

Set the required environment variables for your dSIPRouter instance:

```bash
export DSIP_ADDR="your-dsiprouter-host"    # e.g., "192.168.1.100" or "dsip.example.com"
export DSIP_TOKEN="your-api-bearer-token"  # Your API token from dSIPRouter
```

For self-signed certificates, you can also set:
```bash
export DSIP_INSECURE=1  # Allows connections to servers with self-signed TLS certificates
```

To make these permanent, add them to your shell profile (~/.bashrc, ~/.zshrc, etc.).

## Quick Start

### List Available Commands

```bash
dsiprouter.sh help
```

### Basic Usage Examples

**List all endpoint groups:**
```bash
dsiprouter.sh endpointgroups:list | jq .
```

**Get a specific endpoint group:**
```bash
dsiprouter.sh endpointgroups:get | jq .
```

**Create an inbound mapping:**
```bash
dsiprouter.sh inboundmapping:create '{"did":"13132222223","servers":["#22"],"name":"My Location"}' | jq .
```

**Check Kamailio statistics:**
```bash
dsiprouter.sh kamailio:list | jq .
```

**Reload Kamailio after making changes:**
```bash
dsiprouter.sh kamailio:reload | jq .
```

## Available Skills

This skill provides command groups organized by resource type. Each command follows the pattern:

```bash
dsiprouter.sh <resource>:<action> [options]
```

### Endpoint Groups
Manage endpoint groups and SIP endpoints:

- `endpointgroups:list` — List all endpoint groups
- `endpointgroups:get` — Get details of a specific endpoint group
- `endpointgroups:create` — Create a new endpoint group
- `endpointgroups:update` — Update an existing endpoint group
- `endpointgroups:delete` — Delete an endpoint group

### Kamailio Management
Monitor and manage the Kamailio SIP server:

- `kamailio:list` — Get Kamailio call statistics
- `kamailio:reload` — Trigger a Kamailio reload (required after configuration changes)

### Inbound Mapping
Configure DID (Direct Inward Dialing) to endpoint mapping:

- `inboundmapping:list` — List all inbound mappings
- `inboundmapping:create` — Create a new inbound mapping
- `inboundmapping:update` — Update an existing inbound mapping
- `inboundmapping:delete` — Delete an inbound mapping

### Leases
Manage endpoint leases:

- `leases:list` — List active endpoint leases
- `leases:revoke` — Revoke an endpoint lease

### Carrier Groups
Manage carrier/trunk configurations:

- `carriergroups:list` — List all carrier groups
- `carriergroups:create` — Create a new carrier group

### Authentication
User management:

- `auth:create` — Create a new API user

## Safe Calling Convention

This skill implements a safe `curl` wrapper with the following features:

- **Automatic authentication** — Includes the Bearer token from `DSIP_TOKEN`
- **Error handling** — Shows errors and exits on failure
- **Timeout protection** — 5-second connection timeout, 30-second max time
- **TLS flexibility** — Optional insecure mode for self-signed certificates
- **Content negotiation** — Automatically sets JSON headers

The underlying function:
```bash
dsip_api() {
  local method="$1"; shift
  local path="$1"; shift

  local insecure=()
  if [ "${DSIP_INSECURE:-}" = "1" ]; then insecure=(-k); fi

  curl "${insecure[@]}" --silent --show-error --fail-with-body \
    --connect-timeout 5 --max-time 30 \
    -H "Authorization: Bearer ${DSIP_TOKEN}" \
    -H "Content-Type: application/json" \
    -X "${method}" "https://${DSIP_ADDR}:5000${path}" \
    "$@"
}
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `DSIP_ADDR` | Yes | Hostname or IP address of your dSIPRouter instance (without scheme) |
| `DSIP_TOKEN` | Yes | Bearer token for API authentication |
| `DSIP_INSECURE` | No | Set to `1` to allow self-signed TLS certificates |

## API Base URL

All requests are sent to:
```
https://$DSIP_ADDR:5000/api/v1
```

## Common Workflows

### 1. Verify Connection
```bash
dsiprouter.sh endpointgroups:list | jq '.count'
```

### 2. Create an Endpoint Group
```bash
dsiprouter.sh endpointgroups:create '{
  "name": "My Endpoints",
  "sip_profile_id": 1
}' | jq .
```

### 3. Create an Inbound Mapping
```bash
dsiprouter.sh inboundmapping:create '{
  "did": "13132222223",
  "servers": ["#22"],
  "name": "Main Office",
  "prefix": "",
  "strip": 0
}' | jq .
```

### 4. Reload Configuration
After making changes, reload Kamailio:
```bash
dsiprouter.sh kamailio:reload | jq .
```

## Troubleshooting

**Connection timeout:**
```
error: Failed to connect to dSIPRouter
```
- Verify `DSIP_ADDR` is correct and accessible
- Check network connectivity: `ping $DSIP_ADDR`
- Ensure port 5000 is open

**Authentication error (401):**
```
error: Unauthorized
```
- Verify `DSIP_TOKEN` is correct
- Check that your token hasn't expired

**SSL/TLS certificate errors:**
```
error: SSL certificate problem
```
- For self-signed certificates, set `DSIP_INSECURE=1`
- Or add your certificate to the system trust store

**Command not found:**
```
dsiprouter: command not found
```
- Verify the script is executable: `chmod +x bin/dsiprouter.sh`
- Ensure the directory is in your PATH or use the full path: `./bin/dsiprouter`

## Additional Resources

- See [SKILL.md](SKILL.md) for detailed API documentation
- Check the [Postman collection](postman/dsiprouter.postman_collection.json) for API examples
- Consult the [LICENSE](LICENSE.txt) for usage terms
