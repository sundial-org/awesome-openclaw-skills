# Admin Commands

User, group, role, and organization management. **Requires admin permissions**.

## User Commands

### List Users

```bash
pltr admin user list [--page-size N] [--page-token TEXT] [--format FORMAT]

# Example
pltr admin user list --page-size 50 --format csv --output users.csv
```

### Get User Info

```bash
pltr admin user get USER_ID [--format FORMAT]

# Example
pltr admin user get john.doe@company.com
```

### Current User

```bash
pltr admin user current [--format FORMAT]

# Example
pltr admin user current --format json
```

### Search Users

```bash
pltr admin user search QUERY [--page-size N] [--format FORMAT]

# Example
pltr admin user search "john" --page-size 20
```

### Get User Markings/Permissions

```bash
pltr admin user markings USER_ID [--format FORMAT]

# Example
pltr admin user markings john.doe@company.com
```

### Revoke User Tokens

```bash
pltr admin user revoke-tokens USER_ID [--confirm]

# Example
pltr admin user revoke-tokens john.doe@company.com --confirm
```

### Delete User

```bash
pltr admin user delete USER_ID [--confirm]

# Example
pltr admin user delete john.doe@company.com --confirm
```

### Batch Get Users

```bash
pltr admin user batch-get USER_IDS...

# Max 500 user IDs

# Example
pltr admin user batch-get user1@company.com user2@company.com user3@company.com
```

## Group Commands

### List Groups

```bash
pltr admin group list [--format FORMAT]

# Example
pltr admin group list
```

### Get Group Info

```bash
pltr admin group get GROUP_ID [--format FORMAT]

# Example
pltr admin group get engineering-team
```

### Search Groups

```bash
pltr admin group search QUERY [--format FORMAT]

# Example
pltr admin group search "engineering"
```

### Create Group

```bash
pltr admin group create NAME [--description TEXT] [--org-rid TEXT]

# Example
pltr admin group create "Data Science Team" --description "Team for ML and analytics"
```

### Delete Group

```bash
pltr admin group delete GROUP_ID [--confirm]

# Example
pltr admin group delete old-team --confirm
```

### Batch Get Groups

```bash
pltr admin group batch-get GROUP_IDS...

# Max 500 group IDs

# Example
pltr admin group batch-get engineering-team data-team security-team
```

## Role Commands

### Get Role Info

```bash
pltr admin role get ROLE_ID [--format FORMAT]

# Example
pltr admin role get admin-role
```

### Batch Get Roles

```bash
pltr admin role batch-get ROLE_IDS...

# Max 500 role IDs

# Example
pltr admin role batch-get admin-role editor-role viewer-role
```

## Organization Commands

### Get Organization Info

```bash
pltr admin org get ORGANIZATION_ID [--format FORMAT]

# Example
pltr admin org get my-organization
```

### Create Organization

```bash
pltr admin org create NAME --enrollment-rid ENROLLMENT_RID [OPTIONS]

# Options:
#   --admin-id TEXT    Admin user IDs (can specify multiple)

# Example
pltr admin org create "New Organization" --enrollment-rid ri.enrollment.main.123 \
  --admin-id admin1@company.com --admin-id admin2@company.com
```

### Replace Organization

```bash
pltr admin org replace ORGANIZATION_RID NAME [OPTIONS]

# Options:
#   --description TEXT    New organization description
#   --confirm             Skip confirmation prompt

# Example
pltr admin org replace ri.compass.main.org.123 "Updated Org Name" \
  --description "Updated description" --confirm
```

### List Available Roles for Organization

```bash
pltr admin org available-roles ORGANIZATION_RID [--page-size N] [--page-token TEXT]

# Example
pltr admin org available-roles ri.compass.main.org.123 --page-size 50
```

## Marking Commands

### List Markings

```bash
pltr admin marking list [--page-size N] [--page-token TEXT] [--format FORMAT]

# Example
pltr admin marking list --format json --output markings.json
```

### Get Marking Info

```bash
pltr admin marking get MARKING_ID [--format FORMAT]

# Example
pltr admin marking get marking-confidential
```

### Create Marking

```bash
pltr admin marking create NAME [OPTIONS]

# Options:
#   --description TEXT    Marking description
#   --category-id TEXT    Category ID for the marking

# Example
pltr admin marking create "Confidential" --description "Confidential data marking"
```

### Replace Marking

```bash
pltr admin marking replace MARKING_ID NAME [OPTIONS]

# Options:
#   --description TEXT    New marking description
#   --confirm             Skip confirmation prompt

# Example
pltr admin marking replace marking-123 "Updated Name" --description "New description" --confirm
```

### Batch Get Markings

```bash
pltr admin marking batch-get MARKING_IDS...

# Max 500 marking IDs

# Example
pltr admin marking batch-get marking-1 marking-2 marking-3
```

## Common Patterns

### Audit users
```bash
# Export all users
pltr admin user list --format csv --output all_users.csv

# Search for admin users
pltr admin user search "admin" --format csv --output admins.csv
```

### User management workflow
```bash
# Get current user info
pltr admin user current

# Check user permissions
pltr admin user markings john.doe@company.com

# Search for specific users
pltr admin user search "data scientist"
```

### Group management
```bash
# List all groups
pltr admin group list --format json --output groups.json

# Create new team group
pltr admin group create "Analytics Team" --description "Business analytics team"

# Get group details
pltr admin group get analytics-team
```

### Security audit script
```bash
#!/bin/bash
# Export users and groups for audit
DATE=$(date +%Y%m%d)

pltr admin user list --format json --output "audit_users_${DATE}.json"
pltr admin group list --format json --output "audit_groups_${DATE}.json"
pltr admin user search "admin" --format csv --output "potential_admins_${DATE}.csv"

echo "Audit files generated for $DATE"
```
