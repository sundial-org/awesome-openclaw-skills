---
name: dokploy
description: "Manage Dokploy deployments, projects, applications, and domains via the Dokploy API."
emoji: "🐳"
metadata:
  clawdhub:
    requires:
      bins: ["curl", "jq"]
---

# Dokploy Skill

Interact with Dokploy's API to manage projects, applications, domains, and deployments.

## Prerequisites

1. **Dokploy instance** running with API access
2. **API Key** generated from `/settings/profile` → "API/CLI Section"
3. Set the `DOKPLOY_API_URL` environment variable (default: `http://localhost:3000`)

## Configuration

Set these environment variables or use the config command:

```bash
# Dokploy instance URL
export DOKPLOY_API_URL="https://your-dokploy-instance.com"

# Your API token
export DOKPLOY_API_KEY="your-generated-api-key"

# Or run the config command
dokploy-config set --url "https://your-dokploy-instance.com" --key "your-api-key"
```

## Projects

### List all projects
```bash
dokploy-project list
```

### Get project details
```bash
dokploy-project get <project-id>
```

### Create a new project
```bash
dokploy-project create --name "My Project" --description "Description here"
```

### Update a project
```bash
dokploy-project update <project-id> --name "New Name" --description "Updated"
```

### Delete a project
```bash
dokploy-project delete <project-id>
```

## Applications

### List applications in a project
```bash
dokploy-app list --project <project-id>
```

### Get application details
```bash
dokploy-app get <application-id>
```

### Create an application
```bash
dokploy-app create \
  --project <project-id> \
  --name "my-app" \
  --type "docker" \
  --image "nginx:latest"
```

**Application types:** `docker`, `git`, `compose`

### Trigger deployment
```bash
dokploy-app deploy <application-id>
```

### Get deployment logs
```bash
dokploy-app logs <application-id> --deployment <deployment-id>
```

### List deployments
```bash
dokploy-app deployments <application-id>
```

### Update application
```bash
dokploy-app update <application-id> --name "new-name" --env "KEY=VALUE"
```

### Delete an application
```bash
dokploy-app delete <application-id>
```

## Domains

### List domains for an application
```bash
dokploy-domain list --application <application-id>
```

### Get domain details
```bash
dokploy-domain get <domain-id>
```

### Add a domain to an application
```bash
dokploy-domain create \
  --application <application-id> \
  --domain "app.example.com" \
  --path "/" \
  --port 80
```

### Update a domain
```bash
dokploy-domain update <domain-id> --domain "new.example.com"
```

### Delete a domain
```bash
dokploy-domain delete <domain-id>
```

## Environment Variables

### List environment variables for an application
```bash
dokploy-app env list <application-id>
```

### Set environment variable
```bash
dokploy-app env set <application-id> --key "DATABASE_URL" --value "postgres://..."
```

### Delete environment variable
```bash
dokploy-app env delete <application-id> --key "DATABASE_URL"
```

## Utility Commands

### Check API connection
```bash
dokploy-status
```

### View current config
```bash
dokploy-config show
```

## API Reference

Base URL: `$DOKPLOY_API_URL/api`

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/project.all` | GET | List all projects |
| `/project.create` | POST | Create project |
| `/project.byId` | GET | Get project by ID |
| `/project.update` | PATCH | Update project |
| `/project.delete` | DELETE | Delete project |
| `/application.all` | GET | List applications |
| `/application.create` | POST | Create application |
| `/application.byId` | GET | Get application by ID |
| `/application.update` | PATCH | Update application |
| `/application.delete` | DELETE | Delete application |
| `/application.deploy` | POST | Trigger deployment |
| `/deployment.all` | GET | List deployments |
| `/deployment.byId` | GET | Get deployment by ID |
| `/deployment.logs` | GET | Get deployment logs |
| `/domain.all` | GET | List domains |
| `/domain.create` | POST | Create domain |
| `/domain.update` | PATCH | Update domain |
| `/domain.delete` | DELETE | Delete domain |

## Notes

- All API calls require the `x-api-key` header
- Use `jq` for JSON parsing in scripts
- Some operations require admin permissions
- Deployment is asynchronous — use status endpoint to check progress
