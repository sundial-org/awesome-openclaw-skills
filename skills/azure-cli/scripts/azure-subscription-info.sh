#!/bin/bash
# azure-subscription-info.sh - Get subscription quotas, limits, and usage information
# Usage: ./azure-subscription-info.sh [-s SUBSCRIPTION_ID]

set -e

SUBSCRIPTION=""

while getopts "s:" opt; do
  case $opt in
    s) SUBSCRIPTION="$OPTARG" ;;
    *) echo "Usage: $0 [-s SUBSCRIPTION_ID]"; exit 1 ;;
  esac
done

echo "=== Azure Subscription Information ==="
echo ""

# Build query args
QUERY_ARGS=()
if [ -n "$SUBSCRIPTION" ]; then
  QUERY_ARGS+=("--subscription" "$SUBSCRIPTION")
fi

# Get subscription details
echo "Subscription Details:"
echo "===================="
az account show "${QUERY_ARGS[@]}" --output table
echo ""

# Get available locations
echo "Available Regions:"
echo "=================="
az account list-locations --query "[].displayName" -o table | head -20
echo ""

# Get usage information
echo "Resource Usage:"
echo "==============="
echo ""

echo "Compute Usage:"
az vm usage list "${QUERY_ARGS[@]}" \
  --output table 2>/dev/null || echo "(Usage details not available)"

echo ""
echo "Subscription Summary:"
echo "===================="

# Count resources
RESOURCE_COUNT=$(az resource list "${QUERY_ARGS[@]}" --query "length([])" -o tsv 2>/dev/null || echo "0")
echo "Total Resources: $RESOURCE_COUNT"

# Count by type
echo ""
echo "Resources by Type:"
az resource list "${QUERY_ARGS[@]}" \
  --query "groupBy(type)[] | {type: [0].type, count: length(@)}" \
  --output table 2>/dev/null || echo "(Resource count not available)"

echo ""
echo "Generated at $(date)"
