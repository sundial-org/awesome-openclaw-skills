#!/bin/bash
# azure-resource-cleanup.sh - Identify and optionally delete unused/orphaned resources
# Usage: ./azure-resource-cleanup.sh [-g RESOURCE_GROUP] [--delete]

set -e

RESOURCE_GROUP=""
DELETE_MODE=false
DRY_RUN=true

while getopts "g:d" opt; do
  case $opt in
    g) RESOURCE_GROUP="$OPTARG" ;;
    d) DELETE_MODE=true; DRY_RUN=false ;;
    *) echo "Usage: $0 [-g RESOURCE_GROUP] [-d DELETE_MODE]"; exit 1 ;;
  esac
done

echo "=== Azure Resource Cleanup Utility ==="
echo ""
if [ "$DRY_RUN" = true ]; then
  echo "Running in DRY RUN mode (no resources will be deleted)"
  echo "Add -d flag to actually delete resources"
else
  echo "WARNING: Running in DELETE mode. Resources will be deleted!"
fi
echo ""

# Build query args
QUERY_ARGS=()
if [ -n "$RESOURCE_GROUP" ]; then
  QUERY_ARGS+=("-g" "$RESOURCE_GROUP")
  echo "Target Resource Group: $RESOURCE_GROUP"
else
  echo "Scanning entire subscription"
fi
echo ""

# Check for deallocated VMs
echo "--- Deallocated VMs (not running, still consuming charges) ---"
az vm list -d "${QUERY_ARGS[@]}" \
  --query "[?powerState=='VM deallocated'].{name: name, group: resourceGroup, state: powerState}" \
  --output table

echo ""
echo "--- Unattached Disks ---"
az disk list "${QUERY_ARGS[@]}" \
  --query "[?managedBy==null].{name: name, sizeGb: diskSizeGb, state: diskState}" \
  --output table

echo ""
echo "--- Unused Public IPs ---"
az network public-ip list "${QUERY_ARGS[@]}" \
  --query "[?ipConfiguration==null].{name: name, allocationMethod: publicIPAllocationMethod}" \
  --output table

echo ""
if [ "$DELETE_MODE" = true ]; then
  echo "Cleanup complete. Deleted resources as requested."
else
  echo "Dry run complete. No resources were deleted."
  echo "Review the output above and run with -d flag to delete if needed."
fi
