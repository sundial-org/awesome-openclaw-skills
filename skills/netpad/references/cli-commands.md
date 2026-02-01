# NetPad CLI Reference (@netpad/cli)

Install: `npm i -g @netpad/cli`

## Commands Overview

| Command | Description |
|---------|-------------|
| `login` | Authenticate with NetPad (browser) |
| `logout` | Clear stored credentials |
| `whoami` | Show current auth status |
| `search` | Search npm for NetPad packages |
| `install` | Install a NetPad app/plugin |
| `list` | List installed packages |
| `create-app` | Scaffold new app package |
| `submit` | Submit to marketplace |
| `users` | Manage org members |
| `groups` | Manage user groups |
| `roles` | Manage roles & permissions |
| `assign` | Assign role to user/group |
| `unassign` | Remove role assignment |
| `permissions` | View/check permissions |

---

## Authentication

```bash
netpad login                    # Opens browser for OAuth
netpad login --api-key np_xxx   # Use API key directly
netpad whoami                   # Show current user/org
netpad logout                   # Clear stored credentials
```

---

## Marketplace

### Search Packages

```bash
netpad search "forms"
netpad search "helpdesk"
netpad search --tag workflow
```

### Install Package

```bash
netpad install @netpad/helpdesk-app
netpad install @netpad/survey-templates
netpad install @scope/package-name
```

### List Installed

```bash
netpad list
netpad list --json
```

### Create New App

```bash
netpad create-app my-app
netpad create-app my-app --template basic
netpad create-app my-app --template workflow
```

### Submit to Marketplace

```bash
netpad submit ./my-app
netpad submit ./my-app --public
netpad submit ./my-app --private
```

---

## RBAC - Users

Manage organization members.

```bash
# List all members
netpad users list -o org_xxx

# List with specific role
netpad users list -o org_xxx --role admin

# Add user to org
netpad users add user@example.com -o org_xxx --role member

# Update user role
netpad users update user@example.com -o org_xxx --role admin

# Remove user from org
netpad users remove user@example.com -o org_xxx
```

### User Roles

| Role | Permissions |
|------|-------------|
| `admin` | Full access, manage members |
| `member` | Create/edit forms, view submissions |
| `viewer` | Read-only access |

---

## RBAC - Groups

Manage user groups/teams for bulk role assignment.

```bash
# List groups
netpad groups list -o org_xxx

# Create group
netpad groups create "Engineering" -o org_xxx
netpad groups create "Marketing" -o org_xxx --description "Marketing team"

# Get group details
netpad groups get grp_xxx -o org_xxx

# Add member to group
netpad groups add-member grp_xxx user@example.com -o org_xxx

# Remove member from group
netpad groups remove-member grp_xxx user@example.com -o org_xxx

# Delete group
netpad groups delete grp_xxx -o org_xxx
```

---

## RBAC - Roles

Manage builtin and custom roles.

### Builtin Roles

| Role | Description |
|------|-------------|
| `org:admin` | Full organization access |
| `org:member` | Standard member access |
| `org:viewer` | Read-only access |
| `project:admin` | Full project access |
| `project:editor` | Edit forms and workflows |
| `project:viewer` | View project content |
| `form:admin` | Manage specific form |
| `form:submitter` | Submit to form only |

### Custom Roles

```bash
# List all roles
netpad roles list -o org_xxx

# Create custom role (inherits from builtin)
netpad roles create "Reviewer" -o org_xxx \
  --base viewer \
  --description "Can review and comment on submissions"

# Create role with specific permissions
netpad roles create "DataExporter" -o org_xxx \
  --permissions "submissions:read,submissions:export"

# Get role details
netpad roles get role_xxx -o org_xxx

# Update role
netpad roles update role_xxx -o org_xxx --description "Updated description"

# Delete custom role
netpad roles delete role_xxx -o org_xxx
```

---

## RBAC - Assignments

Assign roles to users or groups.

```bash
# Assign role to user
netpad assign user user@example.com role_xxx -o org_xxx

# Assign role to group
netpad assign group grp_xxx role_xxx -o org_xxx

# Assign with scope (project-level)
netpad assign user user@example.com role_xxx -o org_xxx --scope project:proj_xxx

# Assign with scope (form-level)
netpad assign user user@example.com role_xxx -o org_xxx --scope form:frm_xxx

# List assignments
netpad assign list -o org_xxx

# Remove assignment
netpad unassign user user@example.com role_xxx -o org_xxx
netpad unassign group grp_xxx role_xxx -o org_xxx
```

---

## RBAC - Permissions

View and check permissions.

```bash
# List all available permissions
netpad permissions list -o org_xxx

# Check user's effective permissions
netpad permissions check user@example.com -o org_xxx

# Check if user can perform action
netpad permissions can user@example.com "forms:create" -o org_xxx

# Check group permissions
netpad permissions check-group grp_xxx -o org_xxx
```

### Permission Format

Permissions follow `resource:action` pattern:

| Permission | Description |
|------------|-------------|
| `forms:create` | Create new forms |
| `forms:read` | View forms |
| `forms:update` | Edit forms |
| `forms:delete` | Delete forms |
| `forms:publish` | Publish/unpublish forms |
| `submissions:read` | View submissions |
| `submissions:create` | Submit to forms |
| `submissions:delete` | Delete submissions |
| `submissions:export` | Export submission data |
| `users:read` | View org members |
| `users:manage` | Add/remove/update members |
| `groups:manage` | Manage groups |
| `roles:manage` | Manage custom roles |
| `settings:manage` | Manage org settings |

---

## Global Options

These options work with most commands:

| Option | Description |
|--------|-------------|
| `-o, --org <orgId>` | Organization ID |
| `--api-url <url>` | Custom API URL |
| `--api-key <key>` | API key (instead of login) |
| `--json` | Output as JSON |
| `-h, --help` | Show help |

---

## Examples

### Onboard New Team Member

```bash
# Add user to org
netpad users add newdev@company.com -o org_xxx --role member

# Add to Engineering group
netpad groups add-member grp_engineering newdev@company.com -o org_xxx

# Give project-specific access
netpad assign user newdev@company.com project:editor -o org_xxx --scope project:proj_xxx
```

### Create Review Workflow

```bash
# Create Reviewer role
netpad roles create "Reviewer" -o org_xxx \
  --base viewer \
  --permissions "submissions:read,forms:read"

# Create Reviewers group
netpad groups create "Reviewers" -o org_xxx

# Assign role to group
netpad assign group grp_reviewers role_reviewer -o org_xxx
```

### Audit Permissions

```bash
# Check what a user can do
netpad permissions check user@example.com -o org_xxx

# List all role assignments
netpad assign list -o org_xxx --json | jq '.[] | {user, role, scope}'
```
