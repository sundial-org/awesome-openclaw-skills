# Azure CLI Skill

**Master Microsoft Azure cloud platform management via command-line interface.**

This AgentSkills-compatible skill provides comprehensive knowledge of the Azure CLI (Command Line Interface) for managing Azure cloud resources, infrastructure, and services.

## What is Azure CLI?

Azure CLI is a cross-platform command-line tool developed by Microsoft for managing Azure cloud resources. It provides complete access to Azure services including:

- **Virtual Machines & Containers** — VMs, VMSS, AKS, Container Instances
- **Networking** — VNets, Load Balancers, VPN, CDN, Application Gateway
- **Storage & Databases** — Storage Accounts, SQL Server, MySQL, PostgreSQL, CosmosDB
- **Application Services** — App Service, Functions, Web Apps, Container Apps
- **Monitoring & Management** — Azure Monitor, Log Analytics, Policy, RBAC
- **DevOps & Automation** — Azure DevOps, Pipelines, Extensions
- **And 50+ more services**

## Installation

### Quick Install

**macOS:**
```bash
brew install azure-cli
```

**Linux:**
```bash
curl -sL https://aka.ms/InstallAzureCliLinux | bash
```

**Windows:**
```powershell
choco install azure-cli
# Or download MSI from https://aka.ms/InstallAzureCliWindowsMSI
```

### Verify Installation

```bash
az --version
az login
```

## Skill Contents

### Main Documentation
- **SKILL.md** — Core Azure CLI skill with essential commands, patterns, and quick-start guides
- **references/REFERENCE.md** — Comprehensive command reference covering all 66 modules and 1000+ commands

### Helper Scripts
Practical bash scripts for common Azure operations:
- `azure-vm-status.sh` — Check VM status and power states
- `azure-resource-cleanup.sh` — Identify and clean up unused resources
- `azure-storage-analysis.sh` — Analyze storage account usage
- `azure-subscription-info.sh` — Get subscription quotas and limits
- `azure-rg-deploy.sh` — Deploy infrastructure with monitoring

**Usage:**
```bash
chmod +x scripts/*.sh
./scripts/azure-vm-status.sh -g myResourceGroup
./scripts/azure-storage-analysis.sh -s mySubscription
```

## Quick Start

### 1. Authenticate
```bash
az login                    # Opens browser for interactive login
```

### 2. Create a Resource Group
```bash
az group create -g myRG -l eastus
```

### 3. Create a Virtual Machine
```bash
az vm create \
  -g myRG \
  -n myVM \
  --image UbuntuLTS \
  --admin-username azureuser \
  --generate-ssh-keys
```

### 4. Manage Resources
```bash
az vm list -g myRG                          # List VMs
az vm show -g myRG -n myVM                  # Get details
az vm start -g myRG -n myVM                 # Start VM
az vm stop -g myRG -n myVM                  # Stop VM
```

## Key Concepts

### Global Parameters (work with all commands)
```bash
--subscription ID           # Target subscription
--resource-group -g RG     # Target resource group
--output -o json|table|tsv|yaml  # Output format
--query JMESPATH_QUERY      # Filter output
--verbose -v                # Verbose output
--help -h                   # Command help
```

### Output Formatting
```bash
# Table (human-readable)
az vm list -g myRG --output table

# JSON (for scripting)
az vm list -g myRG --output json

# Extract specific fields
az vm list -g myRG --query "[].name" -o tsv
```

### JMESPath Queries
```bash
# Get only running VMs
az vm list --query "[?powerState=='VM running'].name"

# Get specific fields
az vm list --query "[].{name: name, size: hardwareProfile.vmSize}"

# Count resources
az vm list --query "length([])"
```

## Common Workflows

### Scale a Web Application
```bash
# Create App Service Plan
az appservice plan create -g myRG -n myplan --sku B2 --is-linux

# Create Web App
az webapp create -g myRG -p myplan -n myapp

# Set configuration
az webapp config appsettings set -g myRG -n myapp \
  --settings WEBSITE_NODE_DEFAULT_VERSION=14.17.0

# Deploy code
az webapp deployment source config-zip -g myRG -n myapp --src myapp.zip

# Monitor performance
az monitor metrics list -g myRG --resource /subscriptions/.../providers/Microsoft.Web/sites/myapp
```

### Deploy Infrastructure with Templates
```bash
# Validate template
az deployment group validate -g myRG --template-file template.json

# Deploy
az deployment group create -g myRG --template-file template.json --parameters params.json

# Monitor deployment
az deployment group show -g myRG -n deployment_name
```

### Automate with Bash Scripts
```bash
#!/bin/bash
set -e  # Exit on error

# Create resource group
az group create -g myRG -l eastus

# Create and configure VM
VM_ID=$(az vm create -g myRG -n myVM --image UbuntuLTS \
  --query id --output tsv)

# Run startup script
az vm run-command invoke -g myRG -n myVM \
  --command-id RunShellScript \
  --scripts "sudo apt-get update && sudo apt-get install -y nginx"

echo "VM deployed: $VM_ID"
```

## Best Practices

1. **Use defaults to reduce typing:**
   ```bash
   az configure --defaults group=myRG location=eastus
   ```

2. **Authenticate securely:**
   - Use `az login` for interactive sessions
   - Use service principals with environment variables for automation
   - Never hardcode credentials in scripts

3. **Format output for scripting:**
   ```bash
   # Extract values with --query and -o tsv
   VM_ID=$(az vm create ... --query id --output tsv)
   ```

4. **Use --no-wait for long operations:**
   ```bash
   az vm create ... --no-wait
   az vm show -g RG -n VM --query provisioningState  # Check later
   ```

5. **Tag resources for cost tracking:**
   ```bash
   az vm create -g RG -n VM ... --tags env=prod team=backend cost-center=123
   ```

6. **Enable error handling in scripts:**
   ```bash
   set -e                # Exit on error
   set -u                # Exit on undefined variable
   set -o pipefail       # Exit if pipe fails
   ```

## Documentation

- **Main Skill Guide:** [SKILL.md](SKILL.md)
- **Command Reference:** [references/REFERENCE.md](references/REFERENCE.md)
- **Helper Scripts:** [scripts/](scripts/)
- **Official Azure CLI Docs:** https://learn.microsoft.com/en-us/cli/azure/
- **GitHub Repository:** https://github.com/Azure/azure-cli

## Getting Help

### Built-in Help
```bash
az --help                          # General help
az vm --help                        # Module help
az vm create --help                 # Command help
az find "search term"              # Find commands
```

### Resources
- **Microsoft Learn:** https://learn.microsoft.com/en-us/cli/azure/
- **Command Reference:** https://learn.microsoft.com/en-us/cli/azure/reference-index
- **GitHub Issues:** https://github.com/Azure/azure-cli/issues
- **Stack Overflow:** Tag with `azure-cli`

## Authentication Methods

### Interactive Login (Development)
```bash
az login
```

### Service Principal (Automation/CI-CD)
```bash
az login --service-principal \
  --username $AZURE_CLIENT_ID \
  --password $AZURE_CLIENT_SECRET \
  --tenant $AZURE_TENANT_ID
```

### Managed Identity (Azure Resources)
```bash
# On Azure VM, Container, or Function
az login --identity
```

### Token-based (Advanced)
```bash
az login --service-principal -u $CLIENT_ID --password-stdin --tenant $TENANT_ID
```

## License

MIT License - See [LICENSE](LICENSE) file for details

## Source Information

- **Project:** Azure CLI
- **Repository:** https://github.com/Azure/azure-cli
- **Latest Version:** 2.82.0 (as of January 2026)
- **Language:** Python
- **Community:** 4,400+ stars, 1,200+ contributors

## Contributing

This skill is based on official Azure CLI documentation and source code. For issues or improvements with Azure CLI itself, visit https://github.com/Azure/azure-cli

---

**Skill Version:** 1.0.0  
**Last Updated:** January 24, 2026  
**Author:** Dennis de Vaal <d.devaal@gmail.com>
