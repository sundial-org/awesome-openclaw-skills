#!/bin/bash
# azure-storage-analysis.sh - Analyze storage account usage and estimate costs
# Usage: ./azure-storage-analysis.sh [-g RESOURCE_GROUP] [-s SUBSCRIPTION_ID]

set -e

RESOURCE_GROUP=""
SUBSCRIPTION=""

while getopts "g:s:" opt; do
  case $opt in
    g) RESOURCE_GROUP="$OPTARG" ;;
    s) SUBSCRIPTION="$OPTARG" ;;
    *) echo "Usage: $0 [-g RESOURCE_GROUP] [-s SUBSCRIPTION_ID]"; exit 1 ;;
  esac
done

echo "=== Azure Storage Analysis Report ==="
echo ""

# Build query args
QUERY_ARGS=()
if [ -n "$RESOURCE_GROUP" ]; then
  QUERY_ARGS+=("-g" "$RESOURCE_GROUP")
fi
if [ -n "$SUBSCRIPTION" ]; then
  QUERY_ARGS+=("--subscription" "$SUBSCRIPTION")
fi

echo "Storage Accounts:"
echo "================"

# Get storage accounts
STORAGE_ACCOUNTS=$(az storage account list "${QUERY_ARGS[@]}" --query "[].name" -o tsv)

if [ -z "$STORAGE_ACCOUNTS" ]; then
  echo "No storage accounts found"
  exit 0
fi

for ACCOUNT in $STORAGE_ACCOUNTS; do
  echo ""
  echo "Account: $ACCOUNT"
  echo "---"
  
  # Get account details
  az storage account show -n "$ACCOUNT" "${QUERY_ARGS[@]}" \
    --query "{name: name, sku: sku.name, kind: kind, location: location, https: supportsHttpsTrafficOnly}" \
    --output table
  
  # Get containers and sizes
  echo ""
  echo "Containers & Usage:"
  
  CONTAINERS=$(az storage container list --account-name "$ACCOUNT" --query "[].name" -o tsv 2>/dev/null || true)
  
  if [ -n "$CONTAINERS" ]; then
    for CONTAINER in $CONTAINERS; do
      BLOB_COUNT=$(az storage blob list --account-name "$ACCOUNT" -c "$CONTAINER" --query "length([])" -o tsv 2>/dev/null || echo "0")
      echo "  - $CONTAINER: $BLOB_COUNT blobs"
    done
  else
    echo "  (No containers or no public access)"
  fi
done

echo ""
echo "Report generated at $(date)"
echo ""
echo "For cost estimation, review:"
echo "  - Storage capacity (GB)"
echo "  - Transaction counts"
echo "  - Data egress (to other regions)"
echo "  - Azure pricing: https://azure.microsoft.com/en-us/pricing/details/storage/"
