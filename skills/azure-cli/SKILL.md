---
name: Azure CLI
description: Comprehensive Azure Cloud Platform management via command-line interface
license: MIT
metadata:
  author: Dennis de Vaal <d.devaal@gmail.com>
  version: "1.0.0"
  keywords: "azure,cloud,infrastructure,devops,iac,management,scripting"
repository: https://github.com/Azure/azure-cli
compatibility:
  - platform: macOS
    min_version: "10.12"
  - platform: Linux
    min_version: "Ubuntu 18.04"
  - platform: Windows
    min_version: "Windows 10"
---

# Azure CLI Skill

**Master the Azure command-line interface for cloud infrastructure management, automation, and DevOps workflows.**

Azure CLI is Microsoft's powerful cross-platform command-line tool for managing Azure resources. This skill provides comprehensive knowledge of Azure CLI commands, authentication, resource management, and automation patterns.

## What You'll Learn

### Core Concepts
- Azure subscription and resource group architecture
- Authentication methods and credential management
- Resource Provider organization and registration
- Global parameters, output formatting, and query syntax
- Automation scripting and error handling

### Major Service Areas (66 command modules)
- **Compute:** Virtual Machines, Scale Sets, Kubernetes (AKS), Containers
- **Networking:** Virtual Networks, Load Balancers, CDN, Traffic Manager
- **Storage & Data:** Storage Accounts, Data Lake, Cosmos DB, Databases
- **Application Services:** App Service, Functions, Container Apps
- **Databases:** SQL Server, MySQL, PostgreSQL, CosmosDB
- **Integration & Messaging:** Event Hubs, Service Bus, Logic Apps
- **Monitoring & Management:** Azure Monitor, Policy, RBAC, Cost Management
- **AI & Machine Learning:** Cognitive Services, Machine Learning
- **DevOps:** Azure DevOps, Pipelines, Extensions

## Quick Start

### Installation

**macOS:**
```bash
brew install azure-cli
```

**Linux (Ubuntu/Debian):**
```bash
curl -sL https://aka.ms/InstallAzureCliLinux | bash
```

**Windows:**
```powershell
choco install azure-cli
# Or download MSI from https://aka.ms/InstallAzureCliWindowsMSI
```

**Verify Installation:**
```bash
az --version          # Show version
az --help             # Show general help
```

### First Steps

```bash
# 1. Login to Azure (opens browser for authentication)
az login

# 2. View your subscriptions
az account list

# 3. Set default subscription (optional)
az account set --subscription "My Subscription"

# 4. Create a resource group
az group create -g myResourceGroup -l eastus

# 5. List your resource groups
az group list
```

## Essential Commands

### Authentication & Accounts

```bash
az login                                    # Interactive login
az login --service-principal -u APP_ID -p PASSWORD -t TENANT_ID
az login --identity                         # Managed identity
az logout                                   # Sign out
az account show                             # Current account
az account list                             # All accounts
az account set --subscription SUBSCRIPTION  # Set default
```

### Global Flags (Use with Any Command)

```bash
--subscription ID       # Target subscription
--resource-group -g RG  # Target resource group
--output -o json|table|tsv|yaml  # Output format
--query JMESPATH_QUERY  # Filter/extract output
--verbose -v            # Verbose output
--debug                 # Debug mode
--help -h               # Command help
```

### Resource Groups

```bash
az group list           # List all resource groups
az group create -g RG -l LOCATION  # Create
az group delete -g RG   # Delete
az group show -g RG     # Get details
az group update -g RG --tags key=value  # Update tags
```

### Virtual Machines (Compute)

```bash
az vm create -g RG -n VM_NAME --image UbuntuLTS
az vm list -g RG
az vm show -g RG -n VM_NAME
az vm start -g RG -n VM_NAME
az vm stop -g RG -n VM_NAME
az vm restart -g RG -n VM_NAME
az vm delete -g RG -n VM_NAME
```

### Storage Operations

```bash
az storage account create -g RG -n ACCOUNT --sku Standard_LRS
az storage account list
az storage container create --account-name ACCOUNT -n CONTAINER
az storage blob upload --account-name ACCOUNT -c CONTAINER -n BLOB -f LOCAL_FILE
az storage blob download --account-name ACCOUNT -c CONTAINER -n BLOB -f LOCAL_FILE
```

### Azure Kubernetes Service (AKS)

```bash
az aks create -g RG -n CLUSTER --node-count 2
az aks get-credentials -g RG -n CLUSTER
az aks list
az aks show -g RG -n CLUSTER
az aks delete -g RG -n CLUSTER
```

## Common Patterns

### Pattern 1: Output Formatting
```bash
# Get only specific fields
az vm list --query "[].{name: name, state: powerState}"

# Get just the names
az vm list --query "[].name" -o tsv

# Filter and extract
az vm list --query "[?powerState=='VM running'].name"
```

### Pattern 2: Automation & Scripting
```bash
#!/bin/bash
set -e  # Exit on error

# Get VM ID
VM_ID=$(az vm create \
  -g myRG \
  -n myVM \
  --image UbuntuLTS \
  --query id \
  --output tsv)

echo "Created VM: $VM_ID"

# Check provisioning state
az vm show --ids "$VM_ID" --query provisioningState
```

### Pattern 3: Batch Operations
```bash
# Delete all VMs in a resource group
az vm list -g myRG -d --query "[].id" -o tsv | xargs az vm delete --ids

# List all resources by tag
az resource list --tag env=production
```

### Pattern 4: Using Defaults
```bash
# Set defaults to reduce typing
az configure --defaults group=myRG subscription=mySubscription location=eastus

# Now commands are simpler
az vm create -n myVM --image UbuntuLTS  # group, subscription, location inherited
```

## Helper Scripts

This skill includes helper bash scripts for common operations:

- **azure-vm-status.sh** — Check VM status across subscription
- **azure-resource-cleanup.sh** — Identify and remove unused resources
- **azure-storage-analysis.sh** — Analyze storage account usage and costs
- **azure-subscription-info.sh** — Get subscription quotas and limits
- **azure-rg-deploy.sh** — Deploy infrastructure with monitoring

**Usage:**
```bash
./scripts/azure-vm-status.sh -g myResourceGroup
./scripts/azure-storage-analysis.sh --subscription mySubscription
```

## Advanced Topics

### Output Querying with JMESPath
Azure CLI supports powerful output filtering using JMESPath:

```bash
# Sort results
az vm list --query "sort_by([], &name)"

# Complex filtering
az vm list --query "[?location=='eastus' && powerState=='VM running'].name"

# Aggregation
az vm list --query "length([])"  # Count VMs
```

### Error Handling
```bash
# Check exit codes
az vm create -g RG -n VM --image UbuntuLTS
if [ $? -eq 0 ]; then
  echo "VM created successfully"
else
  echo "Failed to create VM"
  exit 1
fi
```

### Authentication Methods

**Service Principal (Automation):**
```bash
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

**Managed Identity (Azure Resources):**
```bash
# On an Azure VM or Container Instance
az login --identity
```

**Token-based (CI/CD):**
```bash
echo "$AZURE_ACCESS_TOKEN" | az login --service-principal -u $AZURE_CLIENT_ID --password-stdin --tenant $AZURE_TENANT_ID
```

## Key Resources

- **Official Documentation:** https://learn.microsoft.com/en-us/cli/azure/
- **Command Reference:** https://learn.microsoft.com/en-us/cli/azure/reference-index
- **GitHub Repository:** https://github.com/Azure/azure-cli
- **Comprehensive Guide:** See [references/REFERENCE.md](references/REFERENCE.md)
- **Release Notes:** https://github.com/Azure/azure-cli/releases

## Tips & Tricks

1. **Enable Tab Completion:**
   ```bash
   # macOS with Homebrew
   eval "$(az completion init zsh)"
   
   # Linux (bash)
   eval "$(az completion init bash)"
   ```

2. **Find Commands Quickly:**
   ```bash
   az find "create virtual machine"  # Search for commands
   ```

3. **Use --no-wait for Long Operations:**
   ```bash
   az vm create -g RG -n VM --image UbuntuLTS --no-wait
   # Check status later with az vm show
   ```

4. **Save Frequently Used Parameters:**
   ```bash
   az configure --defaults group=myRG location=eastus
   ```

5. **Combine with Other Tools:**
   ```bash
   # Use with jq for advanced JSON processing
   az vm list | jq '.[] | select(.powerState == "VM running") | .name'
   
   # Use with xargs for batch operations
   az storage account list --query "[].name" -o tsv | xargs -I {} az storage account show -g RG -n {}
   ```

## Next Steps

- Review [references/REFERENCE.md](references/REFERENCE.md) for comprehensive command documentation
- Explore helper scripts in the `scripts/` directory
- Practice with non-production resources first
- Review Azure best practices and cost optimization strategies

---

**Version:** 1.0.0  
**License:** MIT  
**Compatible with:** Azure CLI v2.50+, Azure Subscription
