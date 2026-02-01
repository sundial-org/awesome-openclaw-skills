# Permission Management Workflows

Setting up access control, permissions, and resource roles.

## Space and Project Setup

### Create Team Workspace

```bash
# 1. Get organization info
pltr admin org get my-organization

# 2. Create space (requires enrollment-rid, organization, and deletion-policy-org)
SPACE_RID=$(pltr space create "Data Analytics Team" \
  --enrollment-rid ri.enrollment.main.enrollment.xyz123 \
  --organization ri.compass.main.organization.abc123 \
  --deletion-policy-org ri.compass.main.organization.abc123 \
  --description "Space for analytics and reporting work" \
  --format json | jq -r '.rid')
echo "Created space: $SPACE_RID"

# 3. Create project within space
PROJECT_RID=$(pltr project create "Customer Analytics" --space-rid $SPACE_RID \
  --description "Customer behavior and segmentation analysis" \
  --format json | jq -r '.rid')
echo "Created project: $PROJECT_RID"

# 4. Create folder structure
ROOT_FOLDER=$(pltr folder create "Analytics Work" --format json | jq -r '.rid')
pltr folder create "Raw Data" --parent-folder $ROOT_FOLDER
pltr folder create "Processed Data" --parent-folder $ROOT_FOLDER
pltr folder create "Reports" --parent-folder $ROOT_FOLDER

echo "Workspace setup complete!"
```

## Resource Permission Management

### Check Current Permissions

```bash
DATASET_RID="ri.foundry.main.dataset.customer-data"

# List all permissions
pltr resource-role list $DATASET_RID

# Filter by users only
pltr resource-role list $DATASET_RID --principal-type User

# Check specific user's permissions
pltr resource-role get-principal-roles john.doe User --resource-rid $DATASET_RID
```

### Grant Permissions

```bash
DATASET_RID="ri.foundry.main.dataset.customer-data"

# Grant to individual users
pltr resource-role grant $DATASET_RID john.doe User viewer
pltr resource-role grant $DATASET_RID jane.smith User editor

# Grant to groups
pltr resource-role grant $DATASET_RID data-team Group owner
pltr resource-role grant $DATASET_RID analytics-team Group editor
```

### Bulk Permission Setup

```bash
DATASET_RID="ri.foundry.main.dataset.customer-data"

# Bulk grant multiple permissions
pltr resource-role bulk-grant $DATASET_RID '[
  {"principal_id": "trainee1", "principal_type": "User", "role_name": "viewer"},
  {"principal_id": "trainee2", "principal_type": "User", "role_name": "viewer"},
  {"principal_id": "analyst-team", "principal_type": "Group", "role_name": "editor"},
  {"principal_id": "external-consultant", "principal_type": "User", "role_name": "viewer"}
]'
```

### Revoke Permissions

```bash
DATASET_RID="ri.foundry.main.dataset.customer-data"

# Revoke individual
pltr resource-role revoke $DATASET_RID john.doe User viewer

# Bulk revoke
pltr resource-role bulk-revoke $DATASET_RID '[
  {"principal_id": "old-employee", "principal_type": "User", "role_name": "editor"},
  {"principal_id": "deprecated-team", "principal_type": "Group", "role_name": "viewer"}
]'
```

### Check Available Roles

```bash
# List available roles for resource type
pltr resource-role available-roles ri.foundry.main.dataset.abc123
```

## Permission Audit Script

```bash
#!/bin/bash
# audit_permissions.sh

DATASET_RID="ri.foundry.main.dataset.customer-data"

echo "=== Permission Audit for $DATASET_RID ==="
echo ""

echo "Current permissions:"
pltr resource-role list $DATASET_RID --format table

echo ""
echo "Available roles:"
pltr resource-role available-roles $DATASET_RID --format table

echo ""
echo "Audit complete at $(date)"
```

## User and Group Management

### User Management

```bash
# List all users
pltr admin user list --format csv --output all_users.csv

# Search users
pltr admin user search "data scientist"

# Get user details
pltr admin user get john.doe@company.com

# Check user markings/permissions
pltr admin user markings john.doe@company.com

# Current user info
pltr admin user current
```

### Group Management

```bash
# List groups
pltr admin group list

# Create new group
pltr admin group create "Analytics Team" --description "Business analytics team"

# Get group details
pltr admin group get analytics-team

# Search groups
pltr admin group search "data"

# Delete group
pltr admin group delete old-team --confirm
```

## Resource Organization

### Search and Inspect Resources

```bash
# Search for resources
pltr resource search "sales" --resource-type dataset --format json --output sales.json

# Get details for each resource
for rid in $(cat sales.json | jq -r '.[].rid'); do
  pltr resource get "$rid" --format json
done
```

### Get Resource Metadata

```bash
# Get metadata for a resource
pltr resource get-metadata ri.foundry.main.dataset.sales-analytics --format json
```

## Security Audit

```bash
#!/bin/bash
# security_audit.sh

DATE=$(date +%Y%m%d)

echo "Starting security audit..."

# Export all users
pltr admin user list --format json --output "audit_users_${DATE}.json"

# Export all groups
pltr admin group list --format json --output "audit_groups_${DATE}.json"

# Check admin users
pltr admin user search "admin" --format csv --output "potential_admins_${DATE}.csv"

echo ""
echo "Audit files generated:"
echo "- audit_users_${DATE}.json"
echo "- audit_groups_${DATE}.json"
echo "- potential_admins_${DATE}.csv"
echo ""
echo "Completed at $(date)"
```

## Common Permission Patterns

### Read-Only Access for Analysts

```bash
DATASET="ri.foundry.main.dataset.production-data"

pltr resource-role grant $DATASET analyst-team Group viewer
pltr resource-role grant $DATASET junior-analyst User viewer
```

### Full Access for Data Engineers

```bash
DATASET="ri.foundry.main.dataset.etl-pipeline"

pltr resource-role grant $DATASET data-engineering Group owner
pltr resource-role grant $DATASET lead-engineer User owner
```

### Temporary Access for Contractors

```bash
DATASET="ri.foundry.main.dataset.project-data"

# Grant temporary access
pltr resource-role grant $DATASET contractor@external.com User viewer

# Document for later revocation
echo "contractor@external.com granted viewer access on $(date)" >> access_log.txt
```

## Best Practices

1. **Use groups over individuals**: Easier to manage at scale
2. **Apply least privilege**: Grant minimum required access
3. **Audit regularly**: Export and review permissions periodically
4. **Document access grants**: Keep records of who has access and why
5. **Use bulk operations**: More efficient for multiple changes
6. **Check available roles**: Understand role capabilities before granting
