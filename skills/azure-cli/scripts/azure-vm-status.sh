#!/bin/bash
# azure-vm-status.sh - Check VM status across resource group or subscription
# Usage: ./azure-vm-status.sh [-g RESOURCE_GROUP] [-s SUBSCRIPTION_ID]

set -e

RESOURCE_GROUP=""
SUBSCRIPTION=""
FORMAT="table"

while getopts "g:s:o:" opt; do
  case $opt in
    g) RESOURCE_GROUP="$OPTARG" ;;
    s) SUBSCRIPTION="$OPTARG" ;;
    o) FORMAT="$OPTARG" ;;
    *) echo "Usage: $0 [-g RESOURCE_GROUP] [-s SUBSCRIPTION_ID] [-o FORMAT]"; exit 1 ;;
  esac
done

# Build query
QUERY_ARGS=()
if [ -n "$RESOURCE_GROUP" ]; then
  QUERY_ARGS+=("-g" "$RESOURCE_GROUP")
fi
if [ -n "$SUBSCRIPTION" ]; then
  QUERY_ARGS+=("--subscription" "$SUBSCRIPTION")
fi

echo "=== Azure VM Status Report ==="
echo ""
echo "Fetching VM information..."
echo ""

# Get VMs with details
az vm list-ip-addresses "${QUERY_ARGS[@]}" --output "$FORMAT"

echo ""
echo "Status Summary:"
echo "=============="

# Get power state summary
if [ "$FORMAT" = "json" ]; then
  az vm list-ip-addresses "${QUERY_ARGS[@]}" --output json | \
    jq -r '.[] | "\(.virtualMachine.name): \(.virtualMachine.powerState)"'
else
  az vm list-ip-addresses "${QUERY_ARGS[@]}" --output json | \
    jq -r '.[] | "  \(.virtualMachine.name): \(.virtualMachine.powerState)"'
fi

echo ""
echo "Report generated at $(date)"
