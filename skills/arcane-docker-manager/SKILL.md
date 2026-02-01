# OpenClaw - Arcane Docker Management Skill

## Overview
This skill enables you to interact with your Arcane Docker Management API to manage Docker containers, compose stacks, templates, networks, volumes, images, and system monitoring. Arcane is a comprehensive Docker management platform with a REST API.

## When to Use This Skill
Use this skill when the user requests any of the following:
- Managing Docker containers (list, start, stop, restart, remove, inspect)
- Managing Docker Compose stacks (deploy, update, remove, view logs)
- Working with Docker templates (create, deploy, manage)
- Managing Docker images (list, pull, remove, prune)
- Managing Docker networks and volumes
- Monitoring system resources and Docker statistics
- Managing user accounts and API keys
- Viewing system logs and events

## API Configuration

### Base URL
The API base URL should be configured by the user. Default: `http://localhost:3552/api`

### Authentication
Arcane supports two authentication methods:

1. **Bearer Token (JWT)**: Obtained via login endpoint
2. **API Key**: Long-lived authentication using `X-API-Key` header

#### Getting a Bearer Token
```bash
curl -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "your_password"
  }'
```

Response includes `token`, `refreshToken`, and `expiresAt`.

#### Using API Keys
API keys can be created and managed through the `/apikeys` endpoints. Use the `X-API-Key` header for authentication.

## Core Functionality

### 1. Container Management

#### List Containers
```bash
# Get all containers
curl -X GET "$BASE_URL/containers" \
  -H "Authorization: Bearer $TOKEN"

# Filter by status
curl -X GET "$BASE_URL/containers?status=running" \
  -H "Authorization: Bearer $TOKEN"

# Search containers
curl -X GET "$BASE_URL/containers?search=nginx" \
  -H "Authorization: Bearer $TOKEN"
```

#### Container Operations
```bash
# Start container
curl -X POST "$BASE_URL/containers/{id}/start" \
  -H "Authorization: Bearer $TOKEN"

# Stop container
curl -X POST "$BASE_URL/containers/{id}/stop" \
  -H "Authorization: Bearer $TOKEN"

# Restart container
curl -X POST "$BASE_URL/containers/{id}/restart" \
  -H "Authorization: Bearer $TOKEN"

# Remove container
curl -X DELETE "$BASE_URL/containers/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Get container details
curl -X GET "$BASE_URL/containers/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Get container logs
curl -X GET "$BASE_URL/containers/{id}/logs?tail=100" \
  -H "Authorization: Bearer $TOKEN"

# Get container stats
curl -X GET "$BASE_URL/containers/{id}/stats" \
  -H "Authorization: Bearer $TOKEN"
```

#### Advanced Container Operations
```bash
# Execute command in container
curl -X POST "$BASE_URL/containers/{id}/exec" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "command": ["ls", "-la"],
    "workingDir": "/app"
  }'

# Rename container
curl -X POST "$BASE_URL/containers/{id}/rename" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "new-container-name"
  }'

# Update container resources
curl -X POST "$BASE_URL/containers/{id}/update" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "cpuShares": 512,
    "memory": 536870912,
    "restartPolicy": "unless-stopped"
  }'
```

### 2. Docker Compose Stack Management

#### List Stacks
```bash
curl -X GET "$BASE_URL/stacks" \
  -H "Authorization: Bearer $TOKEN"
```

#### Deploy Stack from Template
```bash
curl -X POST "$BASE_URL/stacks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-stack",
    "templateId": "template-id",
    "envVars": {
      "PORT": "8080",
      "DATABASE_URL": "postgres://..."
    }
  }'
```

#### Deploy Stack from Compose File
```bash
curl -X POST "$BASE_URL/stacks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-stack",
    "composeContent": "version: \"3.8\"\nservices:\n  web:\n    image: nginx:latest\n    ports:\n      - \"80:80\""
  }'
```

#### Stack Operations
```bash
# Get stack details
curl -X GET "$BASE_URL/stacks/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Update stack
curl -X PUT "$BASE_URL/stacks/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "envVars": {
      "PORT": "9090"
    }
  }'

# Remove stack
curl -X DELETE "$BASE_URL/stacks/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Start stack
curl -X POST "$BASE_URL/stacks/{id}/start" \
  -H "Authorization: Bearer $TOKEN"

# Stop stack
curl -X POST "$BASE_URL/stacks/{id}/stop" \
  -H "Authorization: Bearer $TOKEN"

# Restart stack
curl -X POST "$BASE_URL/stacks/{id}/restart" \
  -H "Authorization: Bearer $TOKEN"

# Get stack logs
curl -X GET "$BASE_URL/stacks/{id}/logs?tail=100" \
  -H "Authorization: Bearer $TOKEN"

# Pull latest images for stack
curl -X POST "$BASE_URL/stacks/{id}/pull" \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Template Management

#### List Templates
```bash
curl -X GET "$BASE_URL/templates" \
  -H "Authorization: Bearer $TOKEN"
```

#### Create Template
```bash
curl -X POST "$BASE_URL/templates" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "nginx-template",
    "description": "Basic nginx web server",
    "content": "version: \"3.8\"\nservices:\n  web:\n    image: nginx:{{VERSION}}\n    ports:\n      - \"{{PORT}}:80\"",
    "variables": [
      {
        "name": "VERSION",
        "description": "Nginx version",
        "defaultValue": "latest"
      },
      {
        "name": "PORT",
        "description": "Host port",
        "defaultValue": "80"
      }
    ],
    "category": "web-servers",
    "tags": ["nginx", "web"]
  }'
```

#### Template Operations
```bash
# Get template
curl -X GET "$BASE_URL/templates/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Update template
curl -X PUT "$BASE_URL/templates/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "updated-template-name",
    "description": "Updated description"
  }'

# Delete template
curl -X DELETE "$BASE_URL/templates/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Get template content with parsed variables
curl -X GET "$BASE_URL/templates/{id}/content" \
  -H "Authorization: Bearer $TOKEN"
```

#### Global Template Variables
```bash
# Get global variables
curl -X GET "$BASE_URL/templates/global-variables" \
  -H "Authorization: Bearer $TOKEN"

# Update global variables
curl -X PUT "$BASE_URL/templates/global-variables" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "GLOBAL_DOMAIN": "example.com",
    "GLOBAL_NETWORK": "traefik-public"
  }'
```

### 4. Image Management

#### List Images
```bash
curl -X GET "$BASE_URL/images" \
  -H "Authorization: Bearer $TOKEN"
```

#### Pull Image
```bash
curl -X POST "$BASE_URL/images/pull" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "image": "nginx:latest"
  }'
```

#### Image Operations
```bash
# Get image details
curl -X GET "$BASE_URL/images/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Remove image
curl -X DELETE "$BASE_URL/images/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Prune unused images
curl -X POST "$BASE_URL/images/prune" \
  -H "Authorization: Bearer $TOKEN"

# Search images in registry
curl -X GET "$BASE_URL/images/search?term=nginx" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Network Management

#### List Networks
```bash
curl -X GET "$BASE_URL/networks" \
  -H "Authorization: Bearer $TOKEN"
```

#### Create Network
```bash
curl -X POST "$BASE_URL/networks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-network",
    "driver": "bridge",
    "internal": false,
    "attachable": true
  }'
```

#### Network Operations
```bash
# Get network details
curl -X GET "$BASE_URL/networks/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Remove network
curl -X DELETE "$BASE_URL/networks/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Connect container to network
curl -X POST "$BASE_URL/networks/{id}/connect" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "containerId": "container-id"
  }'

# Disconnect container from network
curl -X POST "$BASE_URL/networks/{id}/disconnect" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "containerId": "container-id"
  }'

# Prune unused networks
curl -X POST "$BASE_URL/networks/prune" \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Volume Management

#### List Volumes
```bash
curl -X GET "$BASE_URL/volumes" \
  -H "Authorization: Bearer $TOKEN"
```

#### Create Volume
```bash
curl -X POST "$BASE_URL/volumes" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "my-volume",
    "driver": "local",
    "labels": {
      "project": "my-app"
    }
  }'
```

#### Volume Operations
```bash
# Get volume details
curl -X GET "$BASE_URL/volumes/{name}" \
  -H "Authorization: Bearer $TOKEN"

# Remove volume
curl -X DELETE "$BASE_URL/volumes/{name}" \
  -H "Authorization: Bearer $TOKEN"

# Prune unused volumes
curl -X POST "$BASE_URL/volumes/prune" \
  -H "Authorization: Bearer $TOKEN"
```

### 7. System Monitoring

#### System Information
```bash
# Get Docker system info
curl -X GET "$BASE_URL/system/info" \
  -H "Authorization: Bearer $TOKEN"

# Get Docker version
curl -X GET "$BASE_URL/system/version" \
  -H "Authorization: Bearer $TOKEN"

# Get system stats
curl -X GET "$BASE_URL/system/stats" \
  -H "Authorization: Bearer $TOKEN"

# Get disk usage
curl -X GET "$BASE_URL/system/df" \
  -H "Authorization: Bearer $TOKEN"
```

#### Events and Logs
```bash
# Get system events (streaming)
curl -X GET "$BASE_URL/system/events" \
  -H "Authorization: Bearer $TOKEN"

# Get events with filters
curl -X GET "$BASE_URL/system/events?since=1609459200&type=container" \
  -H "Authorization: Bearer $TOKEN"
```

### 8. User Management

#### List Users
```bash
curl -X GET "$BASE_URL/users" \
  -H "Authorization: Bearer $TOKEN"
```

#### Create User
```bash
curl -X POST "$BASE_URL/users" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepassword123",
    "role": "user"
  }'
```

#### User Operations
```bash
# Get user details
curl -X GET "$BASE_URL/users/{userId}" \
  -H "Authorization: Bearer $TOKEN"

# Update user
curl -X PUT "$BASE_URL/users/{userId}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newemail@example.com",
    "role": "admin"
  }'

# Delete user
curl -X DELETE "$BASE_URL/users/{userId}" \
  -H "Authorization: Bearer $TOKEN"

# Change password
curl -X PUT "$BASE_URL/auth/password" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "currentPassword": "oldpassword",
    "newPassword": "newpassword123"
  }'
```

### 9. API Key Management

#### List API Keys
```bash
curl -X GET "$BASE_URL/apikeys" \
  -H "Authorization: Bearer $TOKEN"
```

#### Create API Key
```bash
curl -X POST "$BASE_URL/apikeys" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CI/CD Pipeline Key",
    "description": "API key for automated deployments",
    "expiresAt": "2025-12-31T23:59:59Z"
  }'
```

#### API Key Operations
```bash
# Get API key details
curl -X GET "$BASE_URL/apikeys/{id}" \
  -H "Authorization: Bearer $TOKEN"

# Update API key
curl -X PUT "$BASE_URL/apikeys/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Updated Key Name",
    "description": "Updated description"
  }'

# Delete API key
curl -X DELETE "$BASE_URL/apikeys/{id}" \
  -H "Authorization: Bearer $TOKEN"
```

## Implementation Guidelines

### Error Handling
All API responses follow a standard format:
```json
{
  "success": true|false,
  "data": {...},
  "message": "Success or error message"
}
```

Error responses use HTTP problem details (RFC 7807):
```json
{
  "type": "about:blank",
  "title": "Error title",
  "status": 400,
  "detail": "Detailed error message"
}
```

### Pagination
List endpoints support pagination with these query parameters:
- `start`: Starting index (default: 0)
- `limit`: Items per page (default: 20)
- `sort`: Column to sort by
- `order`: Sort direction (asc/desc, default: asc)
- `search`: Search query

Response includes pagination metadata:
```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "start": 0,
    "limit": 20,
    "total": 100,
    "hasMore": true
  }
}
```

### Using Python
When implementing Arcane operations in Python, use the `requests` library:

```python
import requests

BASE_URL = "http://localhost:3552/api"
TOKEN = "your-jwt-token"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# List containers
response = requests.get(f"{BASE_URL}/containers", headers=headers)
containers = response.json()

# Deploy stack
stack_data = {
    "name": "my-stack",
    "templateId": "template-id",
    "envVars": {
        "PORT": "8080"
    }
}
response = requests.post(f"{BASE_URL}/stacks", headers=headers, json=stack_data)
result = response.json()
```

### Using Bash
For simple operations, use curl with error handling:

```bash
#!/bin/bash

BASE_URL="http://localhost:3552/api"
TOKEN="your-jwt-token"

# Function to make authenticated requests
api_call() {
    local method=$1
    local endpoint=$2
    local data=$3
    
    if [ -z "$data" ]; then
        curl -s -X "$method" "$BASE_URL/$endpoint" \
            -H "Authorization: Bearer $TOKEN"
    else
        curl -s -X "$method" "$BASE_URL/$endpoint" \
            -H "Authorization: Bearer $TOKEN" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
}

# Example: List containers
containers=$(api_call GET "containers")
echo "$containers" | jq '.data[] | {id, name, status}'
```

## Common Workflows

### 1. Deploy Application Stack
```python
# 1. Create or select template
template_data = {
    "name": "webapp-template",
    "content": "version: '3.8'\nservices:\n  web:\n    image: myapp:{{VERSION}}\n    ports:\n      - '{{PORT}}:8080'",
    "variables": [
        {"name": "VERSION", "defaultValue": "latest"},
        {"name": "PORT", "defaultValue": "80"}
    ]
}
template = requests.post(f"{BASE_URL}/templates", headers=headers, json=template_data).json()

# 2. Deploy stack from template
stack_data = {
    "name": "production-webapp",
    "templateId": template["data"]["id"],
    "envVars": {
        "VERSION": "v1.2.3",
        "PORT": "8080"
    }
}
stack = requests.post(f"{BASE_URL}/stacks", headers=headers, json=stack_data).json()

# 3. Monitor deployment
stack_id = stack["data"]["id"]
logs = requests.get(f"{BASE_URL}/stacks/{stack_id}/logs?tail=50", headers=headers).json()
```

### 2. Scale and Monitor Containers
```python
# Get running containers
containers = requests.get(f"{BASE_URL}/containers?status=running", headers=headers).json()

# Get stats for each container
for container in containers["data"]:
    stats = requests.get(f"{BASE_URL}/containers/{container['id']}/stats", headers=headers).json()
    print(f"{container['name']}: CPU {stats['data']['cpuPercent']:.2f}%, Memory {stats['data']['memoryPercent']:.2f}%")

# Update container resources if needed
update_data = {
    "cpuShares": 1024,
    "memory": 1073741824  # 1GB
}
requests.post(f"{BASE_URL}/containers/{container_id}/update", headers=headers, json=update_data)
```

### 3. Cleanup and Maintenance
```python
# Prune unused resources
requests.post(f"{BASE_URL}/images/prune", headers=headers)
requests.post(f"{BASE_URL}/volumes/prune", headers=headers)
requests.post(f"{BASE_URL}/networks/prune", headers=headers)

# Get disk usage before and after
df_before = requests.get(f"{BASE_URL}/system/df", headers=headers).json()
# ... perform cleanup ...
df_after = requests.get(f"{BASE_URL}/system/df", headers=headers).json()
```

## Best Practices

1. **Authentication**: Always use API keys for automated scripts and services. Use JWT tokens for interactive sessions.

2. **Error Handling**: Check response status codes and handle errors appropriately:
   - 200: Success
   - 400: Bad request (validation error)
   - 401: Unauthorized
   - 403: Forbidden
   - 404: Not found
   - 500: Internal server error

3. **Resource Management**: 
   - Always specify resource limits when creating containers
   - Use labels to organize resources
   - Regularly prune unused resources

4. **Security**:
   - Store API keys and tokens securely (use environment variables)
   - Use HTTPS in production
   - Implement proper access controls with user roles
   - Rotate API keys regularly

5. **Monitoring**:
   - Monitor container stats regularly
   - Set up alerts for resource usage
   - Review system logs periodically

6. **Templates**:
   - Use variables for configurable values
   - Document template variables clearly
   - Version control your templates
   - Use global variables for shared configuration

## Troubleshooting

### Common Issues

**Authentication Failed**
- Verify token is not expired (check `expiresAt`)
- Use refresh token to get new access token
- Verify API key is correct and not expired

**Container Won't Start**
- Check container logs: `GET /containers/{id}/logs`
- Inspect container: `GET /containers/{id}`
- Verify port conflicts and resource availability

**Stack Deployment Failed**
- Validate compose file syntax
- Check template variables are properly defined
- Review stack logs: `GET /stacks/{id}/logs`

**Resource Not Found**
- Verify resource ID is correct
- Check if resource was deleted
- Ensure proper permissions

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Container IDs can be full or short (first 12 characters)
- Image names support full registry paths (registry.example.com/image:tag)
- Network and volume names must be unique
- Stack names must be unique per user/project

## Reference Links

For complete API documentation and schema definitions, refer to the OpenAPI specification provided in the JSON schema.