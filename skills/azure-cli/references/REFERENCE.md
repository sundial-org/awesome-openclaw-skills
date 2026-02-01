# Azure CLI Complete Command Reference

**This is a comprehensive reference for all major Azure CLI commands and modules.**

---

## Table of Contents

1. [Global Commands](#global-commands)
2. [Account & Subscription Management](#account--subscription-management)
3. [Resource Management](#resource-management)
4. [Compute Services](#compute-services)
5. [Networking](#networking)
6. [Storage & Data](#storage--data)
7. [Databases](#databases)
8. [Application Services](#application-services)
9. [Integration & Messaging](#integration--messaging)
10. [Monitoring & Management](#monitoring--management)
11. [Advanced Features](#advanced-features)

---

## Global Commands

These commands work across all Azure CLI modules.

### Authentication
```
az login                              # Interactive browser-based login
az login --service-principal -u APP_ID -p PASSWORD -t TENANT_ID  # Service principal
az login --identity                   # Managed identity on Azure resources
az login --use-device-code            # Device code flow (headless)
az logout                             # Sign out
az logout --username user@example.com # Sign out specific account
```

### Account Management
```
az account show                       # Show current account
az account list                       # List all accessible accounts
az account list-locations             # List available Azure regions
az account set --subscription ID      # Set default subscription
az account get-access-token           # Get access token
az account get-access-token --resource https://management.azure.com
```

### Cloud & Environment
```
az cloud list                         # List available cloud environments
az cloud set --name AzureCloud        # Switch cloud (AzureCloud, AzureChinaCloud, etc.)
az cloud show                         # Show current cloud info
```

### General Help & Configuration
```
az --version                          # Show CLI version
az --help                             # Show general help
az -h                                 # Short help
az command-name --help                # Help for specific command
az find "search terms"                # Find commands by description
az configure                          # Interactive configuration
az configure --defaults group=RG subscription=SUB location=eastus
```

---

## Account & Subscription Management

### Subscription Commands
```
az account list                       # List all subscriptions
az account list --output table        # List with table output
az account show                       # Show current subscription details
az account set --subscription "SUBSCRIPTION_ID"  # Set default
az account set --subscription "SUBSCRIPTION_NAME"
az account clear                      # Clear all cached credentials
az account lock create --name LOCK_NAME --resource-group RG  # Create resource lock
az account lock list                  # List locks on subscription
```

### Billing
```
az billing account list               # List billing accounts
az billing invoice list               # List invoices
az billing invoice show --name INVOICE_NAME
az consumption usage list             # Show usage details
```

### Support & Support Tickets
```
az support create                     # Create support ticket
az support show --resource-group RG  # Show ticket status
az support list                       # List support tickets
az support update --ticket-id ID --status Closed
```

---

## Resource Management

### Resource Groups
```
az group create -g RG_NAME -l LOCATION              # Create resource group
az group list                                        # List all resource groups
az group list --output table                         # List with table output
az group show -g RG_NAME                             # Get resource group details
az group delete -g RG_NAME                           # Delete resource group
az group delete -g RG_NAME --yes --no-wait          # Delete without confirmation
az group update -g RG_NAME --tags env=prod team=backend  # Add tags
az group export -g RG_NAME                           # Export as ARM template
az group wait -g RG_NAME --created                   # Wait for creation
```

### Resources
```
az resource list                                     # List all resources
az resource list -g RG_NAME                          # List in resource group
az resource list --tag env=production                # Filter by tag
az resource show -g RG_NAME -n RESOURCE_NAME --resource-type TYPE
az resource update -g RG_NAME -n NAME --set property.subproperty=value
az resource delete -g RG_NAME -n NAME --resource-type TYPE
az resource invoke-action -g RG_NAME -n NAME --action actionName
```

### Deployments
```
az deployment group create -g RG_NAME --template-file template.json --parameters params.json
az deployment group list -g RG_NAME                  # List deployments
az deployment group show -g RG_NAME -n DEPLOY_NAME  # Get deployment details
az deployment group validate -g RG_NAME --template-file template.json
az deployment group delete -g RG_NAME -n DEPLOY_NAME
az deployment operation list -g RG_NAME -n DEPLOY_NAME  # List deployment operations
az deployment sub create --location eastus --template-file template.json  # Subscription level
az deployment tenant create --location eastus --template-file template.json  # Tenant level
```

### Locks
```
az lock create -g RG_NAME -n LOCK_NAME --lock-type CanNotDelete  # Lock (delete protection)
az lock create -g RG_NAME -n LOCK_NAME --lock-type ReadOnly      # Read-only lock
az lock list -g RG_NAME                              # List locks
az lock delete -g RG_NAME -n LOCK_NAME               # Delete lock
```

### Tags
```
az tag list                                          # List all tags
az tag create -n TAG_NAME                            # Create tag
az tag update -n TAG_NAME --operation Merge          # Update tags
az tag create-list PATH_TO_TAGS_FILE                 # Create tags from file
```

---

## Compute Services

### Virtual Machines (VM)

**Creation & Management:**
```
az vm create -g RG_NAME -n VM_NAME --image UbuntuLTS --admin-username azureuser --generate-ssh-keys
az vm create -g RG_NAME -n VM_NAME --image Win2019Datacenter --admin-username azureuser --admin-password PASSWORD
az vm list                                           # List all VMs
az vm list -g RG_NAME                                # List in resource group
az vm show -g RG_NAME -n VM_NAME                     # Get VM details
az vm delete -g RG_NAME -n VM_NAME                   # Delete VM
```

**Power Management:**
```
az vm start -g RG_NAME -n VM_NAME                    # Start VM
az vm stop -g RG_NAME -n VM_NAME                     # Stop VM (keep resources allocated)
az vm deallocate -g RG_NAME -n VM_NAME               # Deallocate VM (release resources)
az vm restart -g RG_NAME -n VM_NAME                  # Restart VM
az vm redeploy -g RG_NAME -n VM_NAME                 # Redeploy VM
```

**Network & Access:**
```
az vm open-port -g RG_NAME -n VM_NAME --port 80     # Open port in NSG
az vm open-port -g RG_NAME -n VM_NAME --port 3306 --priority 1000
az vm list-ip-addresses -g RG_NAME                   # List IP addresses
az vm show -g RG_NAME -n VM_NAME -d --query publicIps  # Get public IP
```

**Remote Access:**
```
az vm run-command invoke -g RG_NAME -n VM_NAME --command-id RunShellScript --scripts "echo hello"
az vm run-command invoke -g RG_NAME -n VM_NAME --command-id RunPowerShellScript --scripts "dir"
az vm run-command list -g RG_NAME -n VM_NAME         # List available run commands
az vm user update -g RG_NAME -n VM_NAME -u USERNAME --password PASSWORD
```

**Disks & Storage:**
```
az vm disk attach -g RG_NAME --vm-name VM_NAME -n DISK_NAME
az vm disk attach -g RG_NAME --vm-name VM_NAME --new -s 10  # Create & attach new 10GB disk
az vm disk detach -g RG_NAME --vm-name VM_NAME -n DISK_NAME
az vm unmanaged-disk attach -g RG_NAME --vm-name VM_NAME -n DISK_NAME --vhd-uri VHD_URI
```

**Extensions & Configuration:**
```
az vm extension set -g RG_NAME --vm-name VM_NAME -n CustomScript --publisher Microsoft.Compute --version 1.10
az vm extension set -g RG_NAME --vm-name VM_NAME -n CustomScript --settings '{"script":"bash myscript.sh"}'
az vm extension list -g RG_NAME --vm-name VM_NAME    # List extensions
az vm extension delete -g RG_NAME --vm-name VM_NAME -n EXTENSION_NAME
```

**VM Images:**
```
az vm image list                                     # List available images
az vm image list --all                               # List all images including non-standard
az vm image show -g RG_NAME --publisher PUBLISHER --offer OFFER --sku SKU --version latest
az vm image list-publishers -l eastus                # List publishers in region
az vm image list-offers -l eastus --publisher Microsoft
az vm image list-skus -l eastus --publisher Microsoft --offer WindowsServer
```

### Virtual Machine Scale Sets (VMSS)

```
az vmss create -g RG_NAME -n VMSS_NAME --image UbuntuLTS --admin-username azureuser
az vmss list -g RG_NAME                              # List scale sets
az vmss show -g RG_NAME -n VMSS_NAME                 # Get scale set details
az vmss delete -g RG_NAME -n VMSS_NAME               # Delete scale set
az vmss scale -g RG_NAME -n VMSS_NAME --new-capacity 5  # Scale to 5 instances
az vmss update-instances -g RG_NAME -n VMSS_NAME --instance-ids "*"  # Update all instances
az vmss start -g RG_NAME -n VMSS_NAME                # Start all instances
az vmss stop -g RG_NAME -n VMSS_NAME                 # Stop all instances
az vmss restart -g RG_NAME -n VMSS_NAME              # Restart all instances
az vmss list-instances -g RG_NAME -n VMSS_NAME       # List instances
az vmss reimage -g RG_NAME -n VMSS_NAME --instance-ids "0" "1"  # Reimage instances
```

### Kubernetes (AKS)

```
az aks create -g RG_NAME -n CLUSTER_NAME --node-count 2 --generate-ssh-keys
az aks list                                          # List all AKS clusters
az aks list -g RG_NAME                               # List in resource group
az aks show -g RG_NAME -n CLUSTER_NAME               # Get cluster details
az aks delete -g RG_NAME -n CLUSTER_NAME             # Delete cluster
az aks get-credentials -g RG_NAME -n CLUSTER_NAME    # Get kubeconfig
az aks get-credentials -g RG_NAME -n CLUSTER_NAME --admin  # Get admin credentials
az aks nodepool add -g RG_NAME --cluster-name CLUSTER -n nodepool2 --node-count 3
az aks nodepool list -g RG_NAME --cluster-name CLUSTER  # List node pools
az aks nodepool delete -g RG_NAME --cluster-name CLUSTER -n nodepool2
az aks enable-addons -g RG_NAME -n CLUSTER_NAME --addons monitoring http_application_routing
az aks disable-addons -g RG_NAME -n CLUSTER_NAME --addons monitoring
az aks upgrade -g RG_NAME -n CLUSTER_NAME --kubernetes-version 1.24.0
az aks scale -g RG_NAME -n CLUSTER_NAME --node-count 5  # Scale node pool
```

### Container Services

**Azure Container Instances (ACI):**
```
az container create -g RG_NAME -n CONTAINER_NAME --image IMAGE --ports 80 443
az container list -g RG_NAME                         # List containers
az container show -g RG_NAME -n CONTAINER_NAME       # Get container details
az container delete -g RG_NAME -n CONTAINER_NAME     # Delete container
az container logs -g RG_NAME -n CONTAINER_NAME       # View logs
az container exec -g RG_NAME -n CONTAINER_NAME --exec-command /bin/sh  # Interactive shell
az container attach -g RG_NAME -n CONTAINER_NAME     # Attach to output
```

**Azure Container Registry (ACR):**
```
az acr create -g RG_NAME -n REGISTRY_NAME --sku Basic  # Create registry
az acr list                                          # List registries
az acr show -n REGISTRY_NAME                         # Get registry details
az acr delete -n REGISTRY_NAME                       # Delete registry
az acr repository list -n REGISTRY_NAME              # List repositories
az acr repository show -n REGISTRY_NAME -r REPO_NAME  # Get repository details
az acr build -r REGISTRY_NAME -t IMAGE:TAG .         # Build and push image
az acr login -n REGISTRY_NAME                        # Login to registry
az acr credential show -n REGISTRY_NAME              # Get login credentials
az acr run -r REGISTRY_NAME -f acr-task.yaml .       # Run ACR task
```

---

## Networking

### Virtual Networks (VNet)

```
az network vnet create -g RG_NAME -n VNET_NAME --address-prefix 10.0.0.0/16
az network vnet list -g RG_NAME                      # List virtual networks
az network vnet show -g RG_NAME -n VNET_NAME         # Get vnet details
az network vnet delete -g RG_NAME -n VNET_NAME       # Delete vnet
az network vnet update -g RG_NAME -n VNET_NAME --add addressSpace.addressPrefixes '10.1.0.0/16'
```

### Subnets

```
az network vnet subnet create -g RG_NAME --vnet-name VNET_NAME -n SUBNET_NAME --address-prefix 10.0.0.0/24
az network vnet subnet list -g RG_NAME --vnet-name VNET_NAME  # List subnets
az network vnet subnet show -g RG_NAME --vnet-name VNET_NAME -n SUBNET_NAME
az network vnet subnet delete -g RG_NAME --vnet-name VNET_NAME -n SUBNET_NAME
az network vnet subnet update -g RG_NAME --vnet-name VNET_NAME -n SUBNET_NAME --service-endpoints Microsoft.Storage
```

### Network Security Groups (NSG)

```
az network nsg create -g RG_NAME -n NSG_NAME         # Create NSG
az network nsg list -g RG_NAME                       # List NSGs
az network nsg show -g RG_NAME -n NSG_NAME           # Get NSG details
az network nsg delete -g RG_NAME -n NSG_NAME         # Delete NSG

# Rules
az network nsg rule create -g RG_NAME --nsg-name NSG_NAME -n RULE_NAME \
  --priority 1000 --source-address-prefixes '*' --destination-port-ranges 22 443 \
  --access Allow --protocol Tcp

az network nsg rule list -g RG_NAME --nsg-name NSG_NAME  # List rules
az network nsg rule delete -g RG_NAME --nsg-name NSG_NAME -n RULE_NAME
```

### Public IP Addresses

```
az network public-ip create -g RG_NAME -n PUBLIC_IP_NAME  # Create public IP
az network public-ip list -g RG_NAME                # List public IPs
az network public-ip show -g RG_NAME -n PUBLIC_IP_NAME
az network public-ip delete -g RG_NAME -n PUBLIC_IP_NAME
az network public-ip update -g RG_NAME -n PUBLIC_IP_NAME --allocation-method Static
```

### Network Interfaces (NIC)

```
az network nic create -g RG_NAME -n NIC_NAME --subnet SUBNET_ID --vnet-name VNET_NAME
az network nic list -g RG_NAME                      # List NICs
az network nic show -g RG_NAME -n NIC_NAME          # Get NIC details
az network nic delete -g RG_NAME -n NIC_NAME        # Delete NIC
az network nic ip-config create -g RG_NAME --nic-name NIC_NAME -n CONFIG_NAME  # Add IP config
```

### Load Balancers

```
az network lb create -g RG_NAME -n LB_NAME --sku Standard  # Create load balancer
az network lb list -g RG_NAME                       # List load balancers
az network lb show -g RG_NAME -n LB_NAME            # Get LB details
az network lb delete -g RG_NAME -n LB_NAME          # Delete LB

# Rules
az network lb rule create -g RG_NAME --lb-name LB_NAME -n RULE_NAME \
  --protocol tcp --frontend-port 80 --backend-port 80 \
  --frontend-ip-name FrontendIPConfig --backend-pool-name BackendPool

az network lb rule list -g RG_NAME --lb-name LB_NAME
az network lb probe create -g RG_NAME --lb-name LB_NAME -n PROBE_NAME \
  --protocol http --port 80 --path /health
```

### Application Gateway

```
az network application-gateway create -g RG_NAME -n APPGW_NAME \
  --capacity 2 --sku Standard_v2 --http-settings-cookie-based-affinity Disabled
az network application-gateway list -g RG_NAME      # List app gateways
az network application-gateway show -g RG_NAME -n APPGW_NAME
az network application-gateway delete -g RG_NAME -n APPGW_NAME
```

### DNS

```
az network dns zone create -g RG_NAME -n ZONE_NAME  # Create DNS zone
az network dns zone list -g RG_NAME                 # List DNS zones
az network dns zone show -g RG_NAME -n ZONE_NAME    # Get zone details
az network dns zone delete -g RG_NAME -n ZONE_NAME  # Delete zone

# Records
az network dns record-set a create -g RG_NAME -z ZONE_NAME -n RECORD_NAME
az network dns record-set a add-record -g RG_NAME -z ZONE_NAME -n RECORD_NAME -a IP_ADDRESS
az network dns record-set a list -g RG_NAME -z ZONE_NAME  # List A records
az network dns record-set a delete -g RG_NAME -z ZONE_NAME -n RECORD_NAME
```

---

## Storage & Data

### Storage Accounts

```
az storage account create -g RG_NAME -n STORAGE_NAME --sku Standard_LRS
az storage account list                             # List storage accounts
az storage account list -g RG_NAME                  # List in resource group
az storage account show -g RG_NAME -n STORAGE_NAME  # Get account details
az storage account delete -g RG_NAME -n STORAGE_NAME
az storage account update -g RG_NAME -n STORAGE_NAME --https-only true
az storage account show-connection-string -g RG_NAME -n STORAGE_NAME  # Get connection string
```

### Blob Storage

```
az storage container create --account-name STORAGE_NAME -n CONTAINER_NAME
az storage container list --account-name STORAGE_NAME  # List containers
az storage container show --account-name STORAGE_NAME -n CONTAINER_NAME
az storage container delete --account-name STORAGE_NAME -n CONTAINER_NAME

# Blobs
az storage blob upload --account-name STORAGE_NAME -c CONTAINER_NAME -n BLOB_NAME -f LOCAL_FILE
az storage blob download --account-name STORAGE_NAME -c CONTAINER_NAME -n BLOB_NAME -f LOCAL_FILE
az storage blob list --account-name STORAGE_NAME -c CONTAINER_NAME  # List blobs
az storage blob show --account-name STORAGE_NAME -c CONTAINER_NAME -n BLOB_NAME
az storage blob delete --account-name STORAGE_NAME -c CONTAINER_NAME -n BLOB_NAME
az storage blob copy start --account-name STORAGE_NAME -c CONTAINER_NAME -b BLOB_NAME --source-uri SOURCE_URI
```

### File Shares

```
az storage share create --account-name STORAGE_NAME -n SHARE_NAME
az storage share list --account-name STORAGE_NAME   # List file shares
az storage share delete --account-name STORAGE_NAME -n SHARE_NAME

# Files
az storage file upload --account-name STORAGE_NAME -s SHARE_NAME -p FILE_PATH --file-path LOCAL_FILE
az storage file download --account-name STORAGE_NAME -s SHARE_NAME -p FILE_PATH -f LOCAL_FILE
az storage file list --account-name STORAGE_NAME -s SHARE_NAME --path DIR_PATH
```

### Queue & Table Storage

```
az storage queue create --account-name STORAGE_NAME -n QUEUE_NAME
az storage queue list --account-name STORAGE_NAME
az storage queue delete --account-name STORAGE_NAME -n QUEUE_NAME
az storage message put --account-name STORAGE_NAME -q QUEUE_NAME --content MESSAGE_CONTENT
az storage message get --account-name STORAGE_NAME -q QUEUE_NAME  # Peek message
az storage message delete --account-name STORAGE_NAME -q QUEUE_NAME --id MESSAGE_ID

az storage table create --account-name STORAGE_NAME -n TABLE_NAME
az storage table list --account-name STORAGE_NAME
```

### Data Lake Storage

```
az datalake fs create -n FILESYSTEM_NAME --account-name STORAGE_NAME
az datalake fs list --account-name STORAGE_NAME     # List file systems
az datalake fs delete -n FILESYSTEM_NAME --account-name STORAGE_NAME

# Files and directories
az datalake fs file create --account-name STORAGE_NAME --file-system FS -p DIRECTORY/FILE
az datalake fs file upload --account-name STORAGE_NAME --file-system FS -s LOCAL_FILE -p REMOTE_PATH
az datalake fs file download --account-name STORAGE_NAME --file-system FS -s REMOTE_PATH -d LOCAL_FILE
az datalake fs directory create --account-name STORAGE_NAME --file-system FS -p DIRECTORY_PATH
```

---

## Databases

### SQL Server & Database

```
az sql server create -g RG_NAME -n SERVER_NAME -u ADMIN_USER -p PASSWORD
az sql server list                                  # List SQL servers
az sql server show -g RG_NAME -n SERVER_NAME        # Get server details
az sql server delete -g RG_NAME -n SERVER_NAME      # Delete server

# Firewall Rules
az sql server firewall-rule create -g RG_NAME -s SERVER_NAME -n RULE_NAME \
  --start-ip-address IP_START --end-ip-address IP_END
az sql server firewall-rule list -g RG_NAME -s SERVER_NAME
az sql server firewall-rule delete -g RG_NAME -s SERVER_NAME -n RULE_NAME

# Allow Azure Services
az sql server firewall-rule create -g RG_NAME -s SERVER_NAME -n AllowAzureServices \
  --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

# Databases
az sql db create -g RG_NAME -s SERVER_NAME -n DATABASE_NAME --service-objective S0
az sql db list -g RG_NAME -s SERVER_NAME            # List databases
az sql db show -g RG_NAME -s SERVER_NAME -n DATABASE_NAME
az sql db delete -g RG_NAME -s SERVER_NAME -n DATABASE_NAME
az sql db pause -g RG_NAME -s SERVER_NAME -n DATABASE_NAME  # Pause (DW only)
az sql db resume -g RG_NAME -s SERVER_NAME -n DATABASE_NAME  # Resume (DW only)
```

### MySQL Server

```
az mysql server create -g RG_NAME -n SERVER_NAME -u ADMIN_USER -p PASSWORD \
  --sku-name B_Gen5_1 --storage-size 51200
az mysql server list                                # List MySQL servers
az mysql server show -g RG_NAME -n SERVER_NAME     # Get server details
az mysql server delete -g RG_NAME -n SERVER_NAME   # Delete server
az mysql server restart -g RG_NAME -n SERVER_NAME  # Restart server

# Firewall Rules
az mysql server firewall-rule create -g RG_NAME -s SERVER_NAME -n RULE_NAME \
  --start-ip-address IP_START --end-ip-address IP_END
az mysql server firewall-rule list -g RG_NAME -s SERVER_NAME

# Databases
az mysql db create -g RG_NAME -s SERVER_NAME -n DATABASE_NAME  # Create database
az mysql db list -g RG_NAME -s SERVER_NAME         # List databases
az mysql db delete -g RG_NAME -s SERVER_NAME -n DATABASE_NAME
```

### PostgreSQL Server

```
az postgres server create -g RG_NAME -n SERVER_NAME -u ADMIN_USER -p PASSWORD \
  --sku-name B_Gen5_1 --storage-size 51200
az postgres server list                             # List PostgreSQL servers
az postgres server show -g RG_NAME -n SERVER_NAME  # Get server details
az postgres server delete -g RG_NAME -n SERVER_NAME  # Delete server

# Firewall Rules
az postgres server firewall-rule create -g RG_NAME -s SERVER_NAME -n RULE_NAME \
  --start-ip-address IP_START --end-ip-address IP_END

# Databases
az postgres db create -g RG_NAME -s SERVER_NAME -n DATABASE_NAME
az postgres db list -g RG_NAME -s SERVER_NAME
```

### CosmosDB

```
az cosmosdb create -g RG_NAME -n ACCOUNT_NAME --kind GlobalDocumentDB
az cosmosdb list                                    # List CosmosDB accounts
az cosmosdb show -g RG_NAME -n ACCOUNT_NAME         # Get account details
az cosmosdb delete -g RG_NAME -n ACCOUNT_NAME       # Delete account

# Databases & Collections
az cosmosdb database create -g RG_NAME --account-name ACCOUNT_NAME -n DATABASE_NAME
az cosmosdb database list -g RG_NAME --account-name ACCOUNT_NAME
az cosmosdb collection create -g RG_NAME --account-name ACCOUNT_NAME -d DATABASE_NAME \
  -c COLLECTION_NAME --partition-key-path /id
```

### Redis Cache

```
az redis create -g RG_NAME -n CACHE_NAME --sku Basic --vm-size c0
az redis list                                       # List Redis caches
az redis show -g RG_NAME -n CACHE_NAME              # Get cache details
az redis delete -g RG_NAME -n CACHE_NAME            # Delete cache
az redis keys -g RG_NAME -n CACHE_NAME              # List cache keys
az redis force-reboot -g RG_NAME -n CACHE_NAME      # Force reboot
```

---

## Application Services

### App Service Plans

```
az appservice plan create -g RG_NAME -n PLAN_NAME --sku B1 --is-linux
az appservice plan list                             # List plans
az appservice plan show -g RG_NAME -n PLAN_NAME     # Get plan details
az appservice plan delete -g RG_NAME -n PLAN_NAME   # Delete plan
az appservice plan update -g RG_NAME -n PLAN_NAME --sku P1V2  # Change SKU
```

### Web Apps

```
az webapp create -g RG_NAME -p PLAN_NAME -n APP_NAME
az webapp list                                      # List web apps
az webapp list -g RG_NAME                           # List in resource group
az webapp show -g RG_NAME -n APP_NAME                # Get app details
az webapp delete -g RG_NAME -n APP_NAME              # Delete app

# Start/Stop
az webapp start -g RG_NAME -n APP_NAME              # Start app
az webapp stop -g RG_NAME -n APP_NAME               # Stop app
az webapp restart -g RG_NAME -n APP_NAME            # Restart app

# Configuration
az webapp config appsettings set -g RG_NAME -n APP_NAME --settings KEY1=value1 KEY2=value2
az webapp config appsettings list -g RG_NAME -n APP_NAME  # List settings
az webapp config connection-string set -g RG_NAME -n APP_NAME -t SQLServer \
  -c "Server=server.database.windows.net;Database=db;User=user;Password=pass"

# Deployment
az webapp deployment source config-zip -g RG_NAME -n APP_NAME --src app.zip
az webapp deployment source config-git -g RG_NAME -n APP_NAME --repo-url REPO_URL --branch master
az webapp deployment list-publishing-profiles -g RG_NAME -n APP_NAME
```

### Function Apps

```
az functionapp create -g RG_NAME -n FUNC_APP_NAME -p PLAN_NAME --runtime python
az functionapp list                                 # List function apps
az functionapp show -g RG_NAME -n FUNC_APP_NAME     # Get app details
az functionapp delete -g RG_NAME -n FUNC_APP_NAME   # Delete app

# Configuration
az functionapp config appsettings set -g RG_NAME -n FUNC_APP_NAME --settings KEY=value
az functionapp cors add -g RG_NAME -n FUNC_APP_NAME --allowed-origins '*'

# Deployment
az functionapp deployment source config-zip -g RG_NAME -n FUNC_APP_NAME --src function.zip
```

### Deployment Slots

```
az webapp deployment slot create -g RG_NAME -n APP_NAME --slot SLOT_NAME
az webapp deployment slot list -g RG_NAME -n APP_NAME  # List slots
az webapp deployment slot swap -g RG_NAME -n APP_NAME --slot SLOT_NAME
az webapp deployment slot delete -g RG_NAME -n APP_NAME --slot SLOT_NAME
```

---

## Integration & Messaging

### Event Hubs

```
az eventhubs namespace create -g RG_NAME -n NAMESPACE_NAME --sku Basic
az eventhubs namespace list                         # List namespaces
az eventhubs create -g RG_NAME -n EVENT_HUB_NAME --namespace-name NAMESPACE_NAME
az eventhubs list -g RG_NAME --namespace-name NAMESPACE_NAME  # List event hubs
az eventhubs consumer-group create -g RG_NAME --namespace-name NAMESPACE_NAME \
  --eventhub-name EVENT_HUB_NAME -n CONSUMER_GROUP_NAME
```

### Service Bus

```
az servicebus namespace create -g RG_NAME -n NAMESPACE_NAME --sku Basic
az servicebus namespace list                        # List namespaces
az servicebus queue create -g RG_NAME --namespace-name NAMESPACE_NAME -n QUEUE_NAME
az servicebus queue list -g RG_NAME --namespace-name NAMESPACE_NAME
az servicebus topic create -g RG_NAME --namespace-name NAMESPACE_NAME -n TOPIC_NAME
az servicebus subscription create -g RG_NAME --namespace-name NAMESPACE_NAME \
  --topic-name TOPIC_NAME -n SUBSCRIPTION_NAME
```

### Logic Apps

```
az logicapp create -g RG_NAME -n LOGIC_APP_NAME --definition DEFINITION_FILE
az logicapp list                                    # List logic apps
az logicapp show -g RG_NAME -n LOGIC_APP_NAME       # Get app details
az logicapp delete -g RG_NAME -n LOGIC_APP_NAME     # Delete app
az logicapp trigger list -g RG_NAME -n LOGIC_APP_NAME  # List triggers
az logicapp run list -g RG_NAME -n LOGIC_APP_NAME   # List runs
```

---

## Monitoring & Management

### Azure Monitor

```
az monitor metrics list-definitions -g RG_NAME --resource RESOURCE_ID  # List metric definitions
az monitor metrics list -g RG_NAME --resource RESOURCE_ID \
  --metric "Percentage CPU"  # Get metric data

# Alerts
az monitor metrics alert create -g RG_NAME -n ALERT_NAME \
  --scopes RESOURCE_ID \
  --condition "avg Percentage CPU > 80" \
  --action RESOURCE_ID

az monitor metrics alert list -g RG_NAME            # List metric alerts
az monitor metrics alert show -g RG_NAME -n ALERT_NAME
az monitor metrics alert delete -g RG_NAME -n ALERT_NAME

# Action Groups
az monitor action-group create -g RG_NAME -n ACTION_GROUP_NAME
az monitor action-group list -g RG_NAME             # List action groups
az monitor action-group show -g RG_NAME -n ACTION_GROUP_NAME
```

### Log Analytics

```
az monitor log-analytics workspace create -g RG_NAME -n WORKSPACE_NAME
az monitor log-analytics workspace list              # List workspaces
az monitor log-analytics workspace show -g RG_NAME -n WORKSPACE_NAME
az monitor log-analytics workspace delete -g RG_NAME -n WORKSPACE_NAME

# Queries
az monitor log-analytics query -w WORKSPACE_ID --analytics-query "AzureActivity | take 10"
```

### Diagnostic Settings

```
az monitor diagnostic-settings create -n DIAGNOSTIC_NAME \
  --resource RESOURCE_ID \
  --logs '[{"category": "AllLogs", "enabled": true}]' \
  --metrics '[{"category": "AllMetrics", "enabled": true}]' \
  --workspace WORKSPACE_ID

az monitor diagnostic-settings list --resource RESOURCE_ID
az monitor diagnostic-settings show -n DIAGNOSTIC_NAME --resource RESOURCE_ID
az monitor diagnostic-settings delete -n DIAGNOSTIC_NAME --resource RESOURCE_ID
```

### Policy

```
az policy definition list                           # List policy definitions
az policy definition show -n POLICY_NAME             # Get policy details
az policy assignment create -d POLICY_ID -s SUBSCRIPTION_ID  # Assign policy
az policy assignment list                           # List assignments
az policy assignment delete -n ASSIGNMENT_NAME      # Delete assignment
```

### RBAC (Role-Based Access Control)

```
az role definition list                             # List role definitions
az role definition show -n "Contributor"            # Get role details

# Role Assignments
az role assignment create --assignee PRINCIPAL_ID --role "Contributor" \
  --resource-group RG_NAME
az role assignment list -g RG_NAME                  # List assignments
az role assignment list --assignee PRINCIPAL_ID     # List user's assignments
az role assignment delete --assignee PRINCIPAL_ID --role "Contributor" -g RG_NAME

# Service Principals
az ad sp create-for-rbac --name ServicePrincipalName \
  --role Contributor --scopes /subscriptions/SUBSCRIPTION_ID
az ad sp list                                       # List service principals
az ad sp show --id PRINCIPAL_ID                     # Get SP details
az ad sp delete --id PRINCIPAL_ID                   # Delete service principal
```

### Cost Management

```
az consumption usage list --subscription SUBSCRIPTION_ID  # Get usage
az consumption usage list --subscription SUBSCRIPTION_ID --billing-period-name PERIOD
az consumption budget list                          # List budgets
az consumption budget create -g RG_NAME -n BUDGET_NAME --amount AMOUNT \
  --time-grain Monthly --start-date START_DATE
```

---

## Advanced Features

### Output Querying with JMESPath

```bash
# Get specific fields
az vm list --query "[].name"                        # List only VM names
az vm list --query "[].{name: name, state: powerState}"  # Multiple fields

# Filter results
az vm list --query "[?powerState=='VM running'].name"
az vm list --query "[?location=='eastus'].{name: name, vmSize: hardwareProfile.vmSize}"

# Sort results
az vm list --query "sort_by([], &name)"             # Sort by name
az vm list --query "reverse(sort_by([], &hardwareProfile.vmSize))"

# Aggregate
az vm list --query "length([])"                     # Count VMs
az vm list --query "max_by([], &hardwareProfile.vmSize)"  # Get largest
```

### Configuration & Defaults

```
az configure                                        # Interactive setup
az configure --defaults group=myRG subscription=mySub location=eastus
az configure --list-defaults                        # Show defaults
az configure --remove defaults.group                # Remove default
```

### Extensions

```
az extension list                                   # List installed extensions
az extension show -n EXTENSION_NAME                 # Get extension details
az extension add -n EXTENSION_NAME                  # Install extension
az extension remove -n EXTENSION_NAME               # Uninstall extension
az extension update --name EXTENSION_NAME           # Update extension
```

### Scripting with Bash

```bash
#!/bin/bash
set -e  # Exit on error

# Get resource ID and store in variable
RESOURCE_ID=$(az resource show -g myRG -n myResource \
  --resource-type Microsoft.Compute/virtualMachines \
  --query id --output tsv)

# Use in another command
az monitor diagnostic-settings create -n diag \
  --resource "$RESOURCE_ID" \
  --logs '[{"category": "AllLogs", "enabled": true}]'
```

---

**This reference covers the most frequently used Azure CLI commands. For complete documentation, visit https://learn.microsoft.com/en-us/cli/azure/**

---

**Last Updated:** January 24, 2026
