# Tabstack API Reference

## Base URL
```
https://api.tabstack.ai/v1
```

## Authentication
Bearer token authentication required:
```
Authorization: Bearer <your_api_key>
```

## Endpoints

### 1. Extract JSON
```
POST /extract/json
```
Extract structured data according to a provided JSON schema.

**Request body:**
```json
{
  "url": "https://example.com",
  "schema": {
    "type": "object",
    "properties": {
      "title": {"type": "string"},
      "content": {"type": "string"}
    }
  }
}
```

**Response:**
```json
{
  "title": "Example Page",
  "content": "Page content here..."
}
```

### 2. Extract Markdown
```
POST /extract/markdown
```
Fetches a URL and converts its HTML content to clean Markdown format.

**Request body:**
```json
{
  "url": "https://example.com"
}
```

**Response:**
Markdown text of the page content.

### 3. Generate JSON
```
POST /generate/json
```
Generate JSON from queries (research capabilities).

### 4. Automate
```
POST /automate
```
Browser automation capabilities.

### 5. Research
```
POST /research
```
Research capabilities.

## Response Codes

- **200** - OK
- **400** - Bad request - invalid input
- **401** - Unauthorized - Invalid or missing Bearer token
- **422** - Invalid URL or inaccessible resource
- **500** - Server error

## Rate Limits
Check Tabstack documentation for current rate limits. Default is typically 100 requests per minute.

## Best Practices

1. **Schema Design** - Create specific schemas for each site type
2. **Error Handling** - Implement retry logic for 422/500 errors
3. **Caching** - Cache results to avoid repeated requests
4. **Validation** - Validate extracted data matches schema expectations