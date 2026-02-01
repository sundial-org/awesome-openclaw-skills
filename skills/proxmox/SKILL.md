---
name: proxmox
description: Manage Proxmox VE clusters via REST API. Use when user asks to list, start, stop, restart VMs or LXC containers, check node status, create snapshots, view tasks, or manage Proxmox infrastructure. Requires API token or credentials configured.
---

# Proxmox VE Management

## Configuration

Set environment variables or store in `~/.proxmox-credentials`:

```bash
# Option 1: API Token (recommended)
export PROXMOX_HOST="https://192.168.1.100:8006"
export PROXMOX_TOKEN_ID="user@pam!tokenname"
export PROXMOX_TOKEN_SECRET="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"

# Option 2: Credentials file
cat > ~/.proxmox-credentials << 'EOF'
PROXMOX_HOST=https://192.168.1.100:8006
PROXMOX_TOKEN_ID=user@pam!monitoring
PROXMOX_TOKEN_SECRET=your-token-secret
EOF
chmod 600 ~/.proxmox-credentials
```

Create API token in Proxmox: Datacenter → Permissions → API Tokens → Add

## CLI Usage

```bash
# Load credentials
source ~/.proxmox-credentials 2>/dev/null

# Auth header for API token
AUTH="Authorization: PVEAPIToken=$PROXMOX_TOKEN_ID=$PROXMOX_TOKEN_SECRET"
```

## Common Operations

### Cluster & Nodes

```bash
# Cluster status
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/cluster/status" | jq

# List nodes
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes" | jq '.data[] | {node, status, cpu, mem: (.mem/.maxmem*100|round)}'

# Node status
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/status" | jq
```

### List VMs & Containers

```bash
# All VMs on a node
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu" | jq '.data[] | {vmid, name, status, mem: .mem, cpu: (.cpu*100|round)}'

# All LXC containers on a node
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/lxc" | jq '.data[] | {vmid, name, status}'

# Cluster-wide resources
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/cluster/resources?type=vm" | jq '.data[] | {node, vmid, name, type, status}'
```

### VM/Container Control

```bash
# Start VM
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/status/start"

# Stop VM
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/status/stop"

# Shutdown VM (graceful)
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/status/shutdown"

# Reboot VM
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/status/reboot"

# Same for LXC: replace /qemu/ with /lxc/
```

### Snapshots

```bash
# List snapshots
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/snapshot" | jq

# Create snapshot
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/snapshot" \
  -d "snapname=snap1" -d "description=Before update"

# Rollback
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/snapshot/{snapname}/rollback"

# Delete snapshot
curl -ks -X DELETE -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/qemu/{vmid}/snapshot/{snapname}"
```

### Tasks & Logs

```bash
# Recent tasks
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/tasks" | jq '.data[:10] | .[] | {upid, type, status, user}'

# Task log
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/tasks/{upid}/log" | jq -r '.data[].t'
```

### Storage

```bash
# List storage
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/storage" | jq '.data[] | {storage, type, active, used_fraction: (.used/.total*100|round|tostring + "%")}'

# Storage content
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/storage/{storage}/content" | jq
```

### Backups

```bash
# List backups
curl -ks -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/storage/{storage}/content?content=backup" | jq

# Start backup
curl -ks -X POST -H "$AUTH" "$PROXMOX_HOST/api2/json/nodes/{node}/vzdump" \
  -d "vmid={vmid}" -d "storage={storage}" -d "mode=snapshot"
```

## Helper Script

Use `scripts/pve.sh` for common operations:

```bash
./scripts/pve.sh status          # Cluster overview
./scripts/pve.sh vms             # List all VMs
./scripts/pve.sh start {vmid}    # Start VM
./scripts/pve.sh stop {vmid}     # Stop VM
```

## Notes

- Replace `{node}`, `{vmid}`, `{storage}`, `{snapname}` with actual values
- API tokens don't need CSRF tokens for POST/PUT/DELETE
- Use `-k` to skip SSL verification for self-signed certs
- Task operations return UPID for tracking async jobs
