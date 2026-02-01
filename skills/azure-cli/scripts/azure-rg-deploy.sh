#!/bin/bash
# azure-rg-deploy.sh - Deploy infrastructure to resource group with monitoring
# Usage: ./azure-rg-deploy.sh -g RESOURCE_GROUP -t TEMPLATE_FILE [-p PARAMETERS_FILE]

set -e

RESOURCE_GROUP=""
TEMPLATE_FILE=""
PARAMETERS_FILE=""
DEPLOYMENT_NAME="deploy-$(date +%s)"
WAIT_FOR_COMPLETION=true

while getopts "g:t:p:n:w" opt; do
  case $opt in
    g) RESOURCE_GROUP="$OPTARG" ;;
    t) TEMPLATE_FILE="$OPTARG" ;;
    p) PARAMETERS_FILE="$OPTARG" ;;
    n) DEPLOYMENT_NAME="$OPTARG" ;;
    w) WAIT_FOR_COMPLETION=false ;;
    *) echo "Usage: $0 -g RESOURCE_GROUP -t TEMPLATE_FILE [-p PARAMETERS_FILE] [-n DEPLOYMENT_NAME]"; exit 1 ;;
  esac
done

# Validate inputs
if [ -z "$RESOURCE_GROUP" ] || [ -z "$TEMPLATE_FILE" ]; then
  echo "Error: -g (resource group) and -t (template) are required"
  exit 1
fi

if [ ! -f "$TEMPLATE_FILE" ]; then
  echo "Error: Template file not found: $TEMPLATE_FILE"
  exit 1
fi

if [ -n "$PARAMETERS_FILE" ] && [ ! -f "$PARAMETERS_FILE" ]; then
  echo "Error: Parameters file not found: $PARAMETERS_FILE"
  exit 1
fi

echo "=== Azure Resource Group Deployment ==="
echo ""
echo "Resource Group: $RESOURCE_GROUP"
echo "Template: $TEMPLATE_FILE"
if [ -n "$PARAMETERS_FILE" ]; then
  echo "Parameters: $PARAMETERS_FILE"
fi
echo "Deployment Name: $DEPLOYMENT_NAME"
echo ""

# Validate template first
echo "Step 1: Validating template..."
DEPLOY_ARGS=("-g" "$RESOURCE_GROUP" "--template-file" "$TEMPLATE_FILE")
if [ -n "$PARAMETERS_FILE" ]; then
  DEPLOY_ARGS+=("--parameters" "$PARAMETERS_FILE")
fi

az deployment group validate "${DEPLOY_ARGS[@]}" --output table
echo "✓ Template validation successful"
echo ""

# Deploy
echo "Step 2: Starting deployment..."
DEPLOY_ARGS+=("--name" "$DEPLOYMENT_NAME")

if [ "$WAIT_FOR_COMPLETION" = true ]; then
  az deployment group create "${DEPLOY_ARGS[@]}" --output table
  echo "✓ Deployment completed successfully"
else
  az deployment group create "${DEPLOY_ARGS[@]}" --no-wait --output table
  echo "✓ Deployment started (running in background)"
  echo ""
  echo "Check deployment status with:"
  echo "  az deployment group show -g $RESOURCE_GROUP -n $DEPLOYMENT_NAME"
fi

echo ""
echo "Deployment finished at $(date)"
