---
name: komodo
description: Manage Komodo infrastructure - servers, Docker deployments, stacks, builds, and procedures. Use when user asks about server status, container management, deployments, builds, or any Komodo-related infrastructure tasks.
---

# Komodo Skill

Manage servers, Docker containers, stacks, builds, and procedures via Komodo Core API.

## Prerequisites

Set environment variables:
- `KOMODO_ADDRESS` - Komodo Core URL (e.g., `https://komodo.example.com`)
- `KOMODO_API_KEY` - API key (starts with `K-`)
- `KOMODO_API_SECRET` - API secret (starts with `S-`)

## Quick Reference

```bash
# Set env (or source from credentials file)
export KOMODO_ADDRESS="https://komodo.weird.cyou"
export KOMODO_API_KEY="K-..."
export KOMODO_API_SECRET="S-..."

# List resources
python scripts/komodo.py servers
python scripts/komodo.py deployments
python scripts/komodo.py stacks
python scripts/komodo.py builds
python scripts/komodo.py procedures
python scripts/komodo.py repos

# Server operations
python scripts/komodo.py server <name>
python scripts/komodo.py server-stats <name>

# Deployment operations
python scripts/komodo.py deployment <name>
python scripts/komodo.py deploy <name>
python scripts/komodo.py start <name>
python scripts/komodo.py stop <name>
python scripts/komodo.py restart <name>
python scripts/komodo.py logs <name> [lines]

# Stack operations
python scripts/komodo.py stack <name>
python scripts/komodo.py deploy-stack <name>
python scripts/komodo.py start-stack <name>
python scripts/komodo.py stop-stack <name>
python scripts/komodo.py restart-stack <name>
python scripts/komodo.py create-stack <name> <server> <compose.yml> [env_file]
python scripts/komodo.py delete-stack <name>
python scripts/komodo.py stack-logs <name> [service]

# Build operations
python scripts/komodo.py build <name>
python scripts/komodo.py run-build <name>

# Procedure operations
python scripts/komodo.py procedure <name>
python scripts/komodo.py run-procedure <name>
```

## State Indicators

- 🟢 Running/Ok
- 🔴 Stopped
- ⚪ NotDeployed
- 🟡 Unhealthy
- 🔄 Restarting
- 🔨 Building
- ⏳ Pending

## Direct API Calls

For operations not covered by the CLI, use curl:

```bash
# Read operation
curl -X POST "$KOMODO_ADDRESS/read/ListServers" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $KOMODO_API_KEY" \
  -H "X-Api-Secret: $KOMODO_API_SECRET" \
  -d '{}'

# Execute operation
curl -X POST "$KOMODO_ADDRESS/execute/Deploy" \
  -H "Content-Type: application/json" \
  -H "X-Api-Key: $KOMODO_API_KEY" \
  -H "X-Api-Secret: $KOMODO_API_SECRET" \
  -d '{"deployment": "my-deployment"}'
```

## API Reference

Read endpoints: `ListServers`, `ListDeployments`, `ListStacks`, `ListBuilds`, `ListProcedures`, `ListRepos`, `GetSystemStats`, `GetLog`

Execute endpoints: `Deploy`, `StartDeployment`, `StopDeployment`, `RestartDeployment`, `DeployStack`, `StartStack`, `StopStack`, `RestartStack`, `RunBuild`, `RunProcedure`

Full API docs: https://komo.do/docs
