#!/bin/bash
# Proxmox VE helper script

set -euo pipefail

# Load credentials
if [[ -f ~/.proxmox-credentials ]]; then
    source ~/.proxmox-credentials
fi

: "${PROXMOX_HOST:?Set PROXMOX_HOST}"
: "${PROXMOX_TOKEN_ID:?Set PROXMOX_TOKEN_ID}"
: "${PROXMOX_TOKEN_SECRET:?Set PROXMOX_TOKEN_SECRET}"

AUTH="Authorization: PVEAPIToken=$PROXMOX_TOKEN_ID=$PROXMOX_TOKEN_SECRET"

api() {
    local method="${1:-GET}"
    local endpoint="$2"
    shift 2
    curl -ks -X "$method" -H "$AUTH" "$PROXMOX_HOST/api2/json$endpoint" "$@"
}

cmd="${1:-help}"
shift || true

case "$cmd" in
    status)
        echo "=== Nodes ==="
        api GET /cluster/resources?type=node | jq -r '.data[] | "\(.node): \(.status)\(if .cpu then " | CPU: \((.cpu*100)|round)%" else "" end)\(if .maxmem then " | Mem: \((.mem/.maxmem*100)|round)%" else "" end)"'
        ;;
    
    vms|list)
        node="${1:-}"
        if [[ -n "$node" ]]; then
            api GET "/nodes/$node/qemu" | jq -r '.data[] | "\(.vmid)\t\(.name)\t\(.status)"'
        else
            api GET "/cluster/resources?type=vm" | jq -r '.data[] | "\(.vmid)\t\(.name)\t\(.status)\t\(.node)"'
        fi
        ;;
    
    lxc)
        node="${1:?Specify node}"
        api GET "/nodes/$node/lxc" | jq -r '.data[] | "\(.vmid)\t\(.name)\t\(.status)"'
        ;;
    
    start)
        vmid="${1:?Specify VMID}"
        node="${2:-}"
        if [[ -z "$node" ]]; then
            node=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .node")
        fi
        vmtype=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .type")
        api POST "/nodes/$node/$vmtype/$vmid/status/start" | jq
        echo "Starting $vmtype $vmid on $node"
        ;;
    
    stop)
        vmid="${1:?Specify VMID}"
        node="${2:-}"
        if [[ -z "$node" ]]; then
            node=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .node")
        fi
        vmtype=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .type")
        api POST "/nodes/$node/$vmtype/$vmid/status/stop" | jq
        echo "Stopping $vmtype $vmid on $node"
        ;;
    
    shutdown)
        vmid="${1:?Specify VMID}"
        node="${2:-}"
        if [[ -z "$node" ]]; then
            node=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .node")
        fi
        vmtype=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .type")
        api POST "/nodes/$node/$vmtype/$vmid/status/shutdown" | jq
        echo "Shutting down $vmtype $vmid on $node"
        ;;
    
    reboot)
        vmid="${1:?Specify VMID}"
        node="${2:-}"
        if [[ -z "$node" ]]; then
            node=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .node")
        fi
        vmtype=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .type")
        api POST "/nodes/$node/$vmtype/$vmid/status/reboot" | jq
        echo "Rebooting $vmtype $vmid on $node"
        ;;
    
    snap|snapshot)
        vmid="${1:?Specify VMID}"
        snapname="${2:-snap-$(date +%Y%m%d-%H%M%S)}"
        node="${3:-}"
        if [[ -z "$node" ]]; then
            node=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .node")
        fi
        vmtype=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .type")
        api POST "/nodes/$node/$vmtype/$vmid/snapshot" -d "snapname=$snapname" | jq
        echo "Created snapshot $snapname for $vmtype $vmid"
        ;;
    
    snapshots)
        vmid="${1:?Specify VMID}"
        node="${2:-}"
        if [[ -z "$node" ]]; then
            node=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .node")
        fi
        vmtype=$(api GET "/cluster/resources?type=vm" | jq -r ".data[] | select(.vmid==$vmid) | .type")
        api GET "/nodes/$node/$vmtype/$vmid/snapshot" | jq -r '.data[] | "\(.name)\t\(.description // "-")"'
        ;;
    
    tasks)
        node="${1:?Specify node}"
        api GET "/nodes/$node/tasks?limit=10" | jq -r '.data[] | "\(.starttime|todate)\t\(.type)\t\(.status)"'
        ;;
    
    storage)
        node="${1:?Specify node}"
        api GET "/nodes/$node/storage" | jq -r '.data[] | "\(.storage)\t\(.type)\t\(if .total then ((.used/.total*100)|round|tostring + "%") else "N/A" end)"'
        ;;
    
    help|*)
        cat << 'EOF'
Proxmox VE CLI Helper

Usage: pve.sh <command> [args]

Commands:
  status              Show cluster nodes status
  vms [node]          List all VMs (optionally filter by node)
  lxc <node>          List LXC containers on node
  start <vmid>        Start VM/LXC
  stop <vmid>         Force stop VM/LXC
  shutdown <vmid>     Graceful shutdown VM/LXC
  reboot <vmid>       Reboot VM/LXC
  snap <vmid> [name]  Create snapshot
  snapshots <vmid>    List snapshots
  tasks <node>        Show recent tasks
  storage <node>      Show storage status

Environment:
  PROXMOX_HOST         https://your-proxmox:8006
  PROXMOX_TOKEN_ID     user@pam!tokenname
  PROXMOX_TOKEN_SECRET your-token-secret

Or create ~/.proxmox-credentials with these variables.
EOF
        ;;
esac
