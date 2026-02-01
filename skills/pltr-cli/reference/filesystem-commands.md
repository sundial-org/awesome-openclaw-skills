# Filesystem Commands

Manage folders, spaces, projects, resources, and permissions.

## RID Formats
- Folders: `ri.compass.main.folder.{uuid}` (root: `ri.compass.main.folder.0`)
- Spaces: `ri.compass.main.space.{uuid}`
- Projects: `ri.compass.main.project.{uuid}`
- Resources: Various patterns depending on type

## Folder Commands

### Create Folder

```bash
pltr folder create NAME [--parent-folder FOLDER_RID] [--format FORMAT]

# Default parent is root: ri.compass.main.folder.0

# Example
pltr folder create "My Project"
pltr folder create "Sub Folder" --parent-folder ri.compass.main.folder.xyz123
```

### Get Folder Info

```bash
pltr folder get FOLDER_RID [--format FORMAT] [--output FILE]

# Example
pltr folder get ri.compass.main.folder.abc123
```

### List Folder Contents

```bash
pltr folder list FOLDER_RID [--page-size N] [--format FORMAT]

# Example - List root folder
pltr folder list ri.compass.main.folder.0

# List with pagination
pltr folder list ri.compass.main.folder.abc123 --page-size 50
```

### Batch Get Folders

```bash
pltr folder batch-get FOLDER_RIDS...

# Max 1000 RIDs

# Example
pltr folder batch-get ri.compass.main.folder.abc123 ri.compass.main.folder.def456
```

## Space Commands

### Create Space

```bash
pltr space create DISPLAY_NAME [OPTIONS]

# Required Options:
#   --enrollment-rid, -e     Enrollment Resource Identifier
#   --organization, -org     Organization RID(s) (can specify multiple)
#   --deletion-policy-org    Organization RID(s) for deletion policy (can specify multiple)

# Optional:
#   --description TEXT       Space description

# Example
pltr space create "Data Science Team" \
  --enrollment-rid ri.enrollment.main.enrollment.abc123 \
  --organization ri.compass.main.organization.xyz456 \
  --deletion-policy-org ri.compass.main.organization.xyz456 \
  --description "Space for analytics work"
```

### Get Space

```bash
pltr space get SPACE_RID [--format FORMAT]
```

### List Spaces

```bash
pltr space list [--organization-rid RID] [--page-size N] [--format FORMAT]
```

### Update Space

```bash
pltr space update SPACE_RID [--display-name TEXT] [--description TEXT]
```

### Delete Space

```bash
pltr space delete SPACE_RID [--yes]
```

## Project Commands

### Create Project

```bash
pltr project create DISPLAY_NAME SPACE_RID [OPTIONS]

# Options:
#   --description TEXT         Project description
#   --organization-rids TEXT   Comma-separated org RIDs
#   --default-roles TEXT       Comma-separated default roles

# Example
pltr project create "ML Pipeline" ri.compass.main.space.abc123 \
  --description "Machine learning pipeline project"
```

### Other Project Commands

```bash
pltr project get PROJECT_RID
pltr project list [--space-rid RID]
pltr project update PROJECT_RID [--display-name TEXT] [--description TEXT]
pltr project delete PROJECT_RID [--confirm]
```

### Add Organizations to Project

```bash
pltr project add-orgs PROJECT_RID --org ORG_RID [--org ORG_RID...]

# Example
pltr project add-orgs ri.compass.main.project.abc123 -o ri.compass.main.org.123 -o ri.compass.main.org.456
```

### Remove Organizations from Project

```bash
pltr project remove-orgs PROJECT_RID --org ORG_RID [--org ORG_RID...]

# Example
pltr project remove-orgs ri.compass.main.project.abc123 -o ri.compass.main.org.123
```

### List Project Organizations

```bash
pltr project list-orgs PROJECT_RID [--page-size N] [--format FORMAT]

# Example
pltr project list-orgs ri.compass.main.project.abc123 --format json
```

### Create Project from Template

```bash
pltr project create-from-template --template-rid TEMPLATE_RID --var "name=value" [OPTIONS]

# Options:
#   --template-rid, -t    Template RID (required)
#   --var, -v             Variable values in format 'name=value' (can specify multiple)
#   --description, -d     Project description
#   --org, -o             Organization RIDs (can specify multiple)

# Example
pltr project create-from-template -t ri.template.main.123 \
  -v "project_name=MyProject" \
  -v "environment=production" \
  -d "Project from template"
```

## Resource Commands

### Get Resource

```bash
pltr resource get RESOURCE_RID [--format FORMAT]
```

### List Resources

```bash
pltr resource list [--folder-rid RID] [--resource-type TYPE] [--page-size N]

# Example
pltr resource list --folder-rid ri.compass.main.folder.abc123 --resource-type dataset
```

### Search Resources

```bash
pltr resource search QUERY [--resource-type TYPE] [--folder-rid RID]

# Example
pltr resource search "sales data" --resource-type dataset
```

### Batch Get Resources

```bash
pltr resource batch-get RESOURCE_RIDS...
```

### Resource Metadata

```bash
# Get metadata
pltr resource get-metadata RESOURCE_RID [--format FORMAT]

# Example
pltr resource get-metadata ri.foundry.main.dataset.abc123 --format json
```

## Resource Lifecycle Commands

### Delete Resource (Move to Trash)

```bash
pltr resource delete RESOURCE_RID [--force]

# Example
pltr resource delete ri.foundry.main.dataset.abc123

# Skip confirmation prompt
pltr resource delete ri.foundry.main.dataset.abc123 --force
```

### Restore Resource from Trash

```bash
pltr resource restore RESOURCE_RID

# Example
pltr resource restore ri.foundry.main.dataset.abc123
```

### Permanently Delete Resource

```bash
pltr resource permanently-delete RESOURCE_RID [--force]

# WARNING: This action is irreversible!

# Example
pltr resource permanently-delete ri.foundry.main.dataset.abc123 --force
```

## Resource Markings Commands

### Add Markings to Resource

```bash
pltr resource add-markings RESOURCE_RID --marking MARKING_ID [--marking MARKING_ID...]

# Example - add single marking
pltr resource add-markings ri.foundry.main.dataset.abc123 -m marking-id-1

# Add multiple markings
pltr resource add-markings ri.foundry.main.dataset.abc123 -m marking-id-1 -m marking-id-2
```

### Remove Markings from Resource

```bash
pltr resource remove-markings RESOURCE_RID --marking MARKING_ID [--marking MARKING_ID...]

# Example
pltr resource remove-markings ri.foundry.main.dataset.abc123 -m marking-id-1 -m marking-id-2
```

### List Resource Markings

```bash
pltr resource list-markings RESOURCE_RID [--page-size N] [--format FORMAT]

# Example
pltr resource list-markings ri.foundry.main.dataset.abc123 --format json
```

### Get Access Requirements

```bash
pltr resource access-requirements RESOURCE_RID [--format FORMAT]

# Returns required organizations and markings for accessing a resource

# Example
pltr resource access-requirements ri.foundry.main.dataset.abc123 --format json
```

## Resource Path Operations

### Batch Get Resources by Path

```bash
pltr resource batch-get-by-path PATHS... [--format FORMAT]

# Get multiple resources by their absolute paths (max 1000)

# Example
pltr resource batch-get-by-path "/Org/Project/Dataset1" "/Org/Project/Dataset2"
```

## Resource Role Commands

### Grant Role

```bash
pltr resource-role grant RESOURCE_RID PRINCIPAL_ID PRINCIPAL_TYPE ROLE_NAME

# PRINCIPAL_TYPE: "User" or "Group"

# Examples
pltr resource-role grant ri.foundry.main.dataset.abc123 john.doe User viewer
pltr resource-role grant ri.foundry.main.dataset.abc123 data-team Group editor
```

### Revoke Role

```bash
pltr resource-role revoke RESOURCE_RID PRINCIPAL_ID PRINCIPAL_TYPE ROLE_NAME
```

### List Roles

```bash
pltr resource-role list RESOURCE_RID [--principal-type TYPE]

# Example
pltr resource-role list ri.foundry.main.dataset.abc123 --principal-type User
```

### Get Principal Roles

```bash
pltr resource-role get-principal-roles PRINCIPAL_ID PRINCIPAL_TYPE [--resource-rid RID]

# Example
pltr resource-role get-principal-roles john.doe User
```

### Bulk Grant/Revoke

```bash
# Bulk grant
pltr resource-role bulk-grant RESOURCE_RID '[
  {"principal_id": "john.doe", "principal_type": "User", "role_name": "viewer"},
  {"principal_id": "data-team", "principal_type": "Group", "role_name": "editor"}
]'

# Bulk revoke
pltr resource-role bulk-revoke RESOURCE_RID '[
  {"principal_id": "john.doe", "principal_type": "User", "role_name": "viewer"}
]'
```

### Available Roles

```bash
pltr resource-role available-roles RESOURCE_RID
```

## Common Patterns

### Create workspace structure
```bash
# Create folders
ROOT=$(pltr folder create "Analytics Work" --format json | jq -r '.rid')
pltr folder create "Raw Data" --parent-folder $ROOT
pltr folder create "Processed" --parent-folder $ROOT
pltr folder create "Reports" --parent-folder $ROOT
```

### Set up team permissions
```bash
DATASET="ri.foundry.main.dataset.customer-data"

# Grant team access
pltr resource-role grant $DATASET data-team Group owner
pltr resource-role grant $DATASET analytics-team Group editor

# Grant individual access
pltr resource-role grant $DATASET john.analyst User viewer
```

### Find resources
```bash
# Search for datasets
pltr resource search "sales" --resource-type dataset --format json --output sales.json

# Get resource details
for rid in $(cat sales.json | jq -r '.[].rid'); do
  pltr resource get "$rid" --format json
done
```
