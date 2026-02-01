---
name: netpad
description: "Manage NetPad forms, submissions, users, and RBAC. Use when: (1) Creating forms with custom fields, (2) Submitting data to forms, (3) Querying form submissions, (4) Managing users/groups/roles (RBAC), (5) Installing NetPad apps from marketplace. Requires NETPAD_API_KEY for API, or `netpad login` for CLI."
metadata: {"clawdbot":{"emoji":"📋","requires":{"bins":["curl","jq","netpad"]},"install":[{"id":"cli","kind":"node","package":"@netpad/cli","bins":["netpad"],"label":"Install NetPad CLI (npm)"}],"author":{"name":"Michael Lynn","github":"mrlynn","website":"https://mlynn.org","linkedin":"https://linkedin.com/in/mlynn"}}}
---

# NetPad

Manage forms, submissions, users, and RBAC via CLI and REST API.

## Two Tools

| Tool | Install | Purpose |
|------|---------|---------|
| `netpad` CLI | `npm i -g @netpad/cli` | RBAC, marketplace, packages |
| REST API | curl + API key | Forms, submissions, data |

## Authentication

```bash
export NETPAD_API_KEY="np_live_xxx"  # Production
export NETPAD_API_KEY="np_test_xxx"  # Test (can submit to drafts)
```

All requests use Bearer token:
```bash
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/..."
```

---

## Quick Reference

| Task | Endpoint | Method |
|------|----------|--------|
| List projects | `/projects` | GET |
| List forms | `/forms` | GET |
| Create form | `/forms` | POST |
| Get form | `/forms/{formId}` | GET |
| Update/publish form | `/forms/{formId}` | PATCH |
| Delete form | `/forms/{formId}` | DELETE |
| List submissions | `/forms/{formId}/submissions` | GET |
| Create submission | `/forms/{formId}/submissions` | POST |
| Get submission | `/forms/{formId}/submissions/{id}` | GET |
| Delete submission | `/forms/{formId}/submissions/{id}` | DELETE |

---

## Projects

Forms belong to projects. Get project ID before creating forms.

```bash
# List projects
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/projects" | jq '.data[] | {projectId, name}'
```

---

## Forms

### List Forms

```bash
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms?status=published&pageSize=50"
```

### Create Form

```bash
curl -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
  -H "Content-Type: application/json" \
  "https://www.netpad.io/api/v1/forms" \
  -d '{
    "name": "Contact Form",
    "description": "Simple contact form",
    "projectId": "proj_xxx",
    "fields": [
      {"path": "name", "label": "Name", "type": "text", "required": true},
      {"path": "email", "label": "Email", "type": "email", "required": true},
      {"path": "phone", "label": "Phone", "type": "phone"},
      {"path": "message", "label": "Message", "type": "textarea"}
    ]
  }'
```

### Get Form Details

```bash
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}"
```

### Publish Form

```bash
curl -X PATCH -H "Authorization: Bearer $NETPAD_API_KEY" \
  -H "Content-Type: application/json" \
  "https://www.netpad.io/api/v1/forms/{formId}" \
  -d '{"status": "published"}'
```

### Update Form Fields

```bash
curl -X PATCH -H "Authorization: Bearer $NETPAD_API_KEY" \
  -H "Content-Type: application/json" \
  "https://www.netpad.io/api/v1/forms/{formId}" \
  -d '{
    "fields": [
      {"path": "name", "label": "Full Name", "type": "text", "required": true},
      {"path": "email", "label": "Email Address", "type": "email", "required": true},
      {"path": "company", "label": "Company", "type": "text"},
      {"path": "role", "label": "Role", "type": "select", "options": [
        {"value": "dev", "label": "Developer"},
        {"value": "pm", "label": "Product Manager"},
        {"value": "exec", "label": "Executive"}
      ]}
    ]
  }'
```

### Delete Form

```bash
curl -X DELETE -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}"
```

---

## Submissions

### Submit Data

```bash
curl -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
  -H "Content-Type: application/json" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions" \
  -d '{
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "message": "Hello from the API!"
    }
  }'
```

### List Submissions

```bash
# Recent submissions
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions?pageSize=50"

# With date filter
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions?startDate=2026-01-01T00:00:00Z"

# Sorted ascending
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions?sortOrder=asc"
```

### Get Single Submission

```bash
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions/{submissionId}"
```

### Delete Submission

```bash
curl -X DELETE -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions/{submissionId}"
```

---

## Field Types

| Type | Description | Validation |
|------|-------------|------------|
| `text` | Single line text | minLength, maxLength, pattern |
| `email` | Email address | Built-in validation |
| `phone` | Phone number | Built-in validation |
| `number` | Numeric input | min, max |
| `date` | Date picker | - |
| `select` | Dropdown | options: [{value, label}] |
| `checkbox` | Boolean | - |
| `textarea` | Multi-line text | minLength, maxLength |
| `file` | File upload | - |

### Field Schema

```json
{
  "path": "fieldName",
  "label": "Display Label",
  "type": "text",
  "required": true,
  "placeholder": "Hint text",
  "helpText": "Additional guidance",
  "options": [{"value": "a", "label": "Option A"}],
  "validation": {
    "minLength": 1,
    "maxLength": 500,
    "pattern": "^[A-Z].*",
    "min": 0,
    "max": 100
  }
}
```

---

## Common Patterns

### Create and Publish Form

```bash
# 1. Create draft
RESULT=$(curl -s -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
  -H "Content-Type: application/json" \
  "https://www.netpad.io/api/v1/forms" \
  -d '{"name":"Survey","projectId":"proj_xxx","fields":[...]}')
FORM_ID=$(echo $RESULT | jq -r '.data.id')

# 2. Publish
curl -X PATCH -H "Authorization: Bearer $NETPAD_API_KEY" \
  -H "Content-Type: application/json" \
  "https://www.netpad.io/api/v1/forms/$FORM_ID" \
  -d '{"status":"published"}'
```

### Export All Submissions

```bash
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms/{formId}/submissions?pageSize=1000" \
  | jq '.data[].data'
```

### Bulk Submit

```bash
for row in $(cat data.json | jq -c '.[]'); do
  curl -s -X POST -H "Authorization: Bearer $NETPAD_API_KEY" \
    -H "Content-Type: application/json" \
    "https://www.netpad.io/api/v1/forms/{formId}/submissions" \
    -d "{\"data\":$row}"
done
```

### Search Forms

```bash
curl -H "Authorization: Bearer $NETPAD_API_KEY" \
  "https://www.netpad.io/api/v1/forms?search=contact&status=published"
```

---

## Helper Script

Use `scripts/netpad.sh` for common operations:

```bash
# Make executable
chmod +x scripts/netpad.sh

# Usage
./scripts/netpad.sh projects list
./scripts/netpad.sh forms list published
./scripts/netpad.sh forms create "Contact Form" proj_xxx
./scripts/netpad.sh forms publish frm_xxx
./scripts/netpad.sh submissions list frm_xxx
./scripts/netpad.sh submissions create frm_xxx '{"name":"John","email":"john@example.com"}'
./scripts/netpad.sh submissions export frm_xxx > data.jsonl
./scripts/netpad.sh submissions count frm_xxx
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Requests/hour | 1,000 |
| Requests/day | 10,000 |

Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`

---

## Response Format

### Success

```json
{
  "success": true,
  "data": { ... },
  "pagination": {"total": 100, "page": 1, "pageSize": 20, "hasMore": true},
  "requestId": "uuid"
}
```

### Error

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Description",
    "details": {}
  },
  "requestId": "uuid"
}
```

---

## Environment Variables

```bash
# Required for REST API
export NETPAD_API_KEY="np_live_xxx"

# Optional (for local/staging)
export NETPAD_BASE_URL="https://staging.netpad.io/api/v1"
```

---

## NetPad CLI (@netpad/cli)

Install: `npm i -g @netpad/cli`

### Authentication

```bash
netpad login              # Opens browser
netpad whoami             # Check auth status
netpad logout             # Clear credentials
```

### Marketplace & Packages

```bash
# Search for apps
netpad search "helpdesk"

# Install an app
netpad install @netpad/helpdesk-app

# List installed
netpad list

# Create new app scaffold
netpad create-app my-app

# Submit to marketplace
netpad submit ./my-app
```

### RBAC - Users

```bash
# List org members
netpad users list -o org_xxx

# Add user
netpad users add user@example.com -o org_xxx --role member

# Change role
netpad users update user@example.com -o org_xxx --role admin

# Remove user
netpad users remove user@example.com -o org_xxx
```

### RBAC - Groups

```bash
# List groups
netpad groups list -o org_xxx

# Create group
netpad groups create "Engineering" -o org_xxx

# Add user to group
netpad groups add-member grp_xxx user@example.com -o org_xxx

# Delete group
netpad groups delete grp_xxx -o org_xxx
```

### RBAC - Roles

```bash
# List roles (builtin + custom)
netpad roles list -o org_xxx

# Create custom role
netpad roles create "Reviewer" -o org_xxx --base viewer --description "Can review submissions"

# View role details
netpad roles get role_xxx -o org_xxx

# Delete custom role
netpad roles delete role_xxx -o org_xxx
```

### RBAC - Assignments

```bash
# Assign role to user
netpad assign user user@example.com role_xxx -o org_xxx

# Assign role to group
netpad assign group grp_xxx role_xxx -o org_xxx

# Remove assignment
netpad unassign user user@example.com role_xxx -o org_xxx
```

### RBAC - Permissions

```bash
# List all permissions
netpad permissions list -o org_xxx

# Check user's effective permissions
netpad permissions check user@example.com -o org_xxx
```

---

## References

- `references/api-endpoints.md` — Complete REST API endpoint docs
- `references/cli-commands.md` — Full CLI command reference

---

## Author

**Michael Lynn** — Principal Staff Developer Advocate at MongoDB

- 🌐 Website: [mlynn.org](https://mlynn.org)
- 🐙 GitHub: [@mrlynn](https://github.com/mrlynn)
- 💼 LinkedIn: [linkedin.com/in/mlynn](https://linkedin.com/in/mlynn)
