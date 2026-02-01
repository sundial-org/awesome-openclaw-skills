# n8n REST API — Endpoint Reference

Base URL: `{instance}/api/v1`
Auth: Header `X-N8N-API-KEY: {key}`

## Workflows

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/workflows` | List all workflows. Filter: `?active=true\|false`, `?tags=tag1,tag2` |
| GET | `/workflows/{id}` | Get workflow by ID (includes nodes, connections) |
| POST | `/workflows` | Create workflow from JSON body |
| PATCH | `/workflows/{id}` | Update workflow (name, nodes, active status) |
| DELETE | `/workflows/{id}` | Delete workflow |
| POST | `/workflows/{id}/activate` | Activate workflow |
| POST | `/workflows/{id}/deactivate` | Deactivate workflow |
| POST | `/workflows/{id}/transfer` | Transfer workflow ownership (enterprise) |

## Executions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/executions` | List executions. Filter: `?status=error\|success\|waiting`, `?workflowId={id}`, `?limit=N` |
| GET | `/executions/{id}` | Get execution details (node data, errors, timing) |
| DELETE | `/executions/{id}` | Delete execution record |

## Credentials

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/credentials` | List all credentials (names/types only, no secrets) |
| POST | `/credentials` | Create credential |
| DELETE | `/credentials/{id}` | Delete credential |

## Tags

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/tags` | List all tags |
| POST | `/tags` | Create tag |
| PATCH | `/tags/{id}` | Update tag |
| DELETE | `/tags/{id}` | Delete tag |

## Users (admin)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/users` | List users |
| GET | `/users/{id}` | Get user details |

## Webhooks (no auth needed)

| Type | URL Pattern |
|------|-------------|
| Production | `{instance}/webhook/{path}` |
| Test | `{instance}/webhook-test/{path}` |

## Pagination

All list endpoints support:
- `?limit=N` — Results per page (default 10, max 250)
- `?cursor=xxx` — Cursor for next page (returned in response)

## Response Format

```json
{
  "data": [...],
  "nextCursor": "string | null"
}
```

## Error Codes

| Code | Meaning |
|------|---------|
| 401 | Invalid or missing API key |
| 404 | Resource not found |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
