# NetPad API v1 - Complete Endpoint Reference

Base URL: `https://www.netpad.io/api/v1`

## Authentication

All endpoints require Bearer token authentication:
```
Authorization: Bearer np_live_xxx
```

| Key Type | Format | Usage |
|----------|--------|-------|
| Live | `np_live_xxx` | Production forms (published only) |
| Test | `np_test_xxx` | Testing (can submit to drafts) |

---

## Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/projects` | List all projects |

### Response: List Projects

```json
{
  "success": true,
  "data": [
    {
      "projectId": "proj_xxx",
      "name": "Project Name",
      "slug": "project-name",
      "description": "Project description",
      "organizationId": "org_xxx",
      "createdAt": "2026-01-01T00:00:00.000Z"
    }
  ],
  "requestId": "uuid"
}
```

---

## Forms

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/forms` | List all forms |
| POST | `/forms` | Create form |
| GET | `/forms/{formId}` | Get form details |
| PATCH | `/forms/{formId}` | Update form |
| DELETE | `/forms/{formId}` | Delete form |

### Query Parameters: List Forms

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| pageSize | int | 20 | Items per page (max 100) |
| status | string | - | Filter: `draft` or `published` |
| search | string | - | Search name/description |

### Request: Create Form

```json
{
  "name": "Form Name",
  "description": "Optional description",
  "slug": "url-friendly-slug",
  "projectId": "proj_xxx",
  "fields": [
    {
      "path": "fieldName",
      "label": "Display Label",
      "type": "text",
      "required": true,
      "placeholder": "Hint text",
      "helpText": "Additional guidance",
      "validation": {
        "minLength": 1,
        "maxLength": 500
      }
    }
  ]
}
```

### Request: Update Form

```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "status": "published",
  "fields": [...]
}
```

### Response: Form Detail

```json
{
  "success": true,
  "data": {
    "id": "frm_xxx",
    "slug": "contact-form",
    "name": "Contact Form",
    "description": "A simple contact form",
    "status": "published",
    "responseCount": 42,
    "fields": [...],
    "settings": {
      "submitButtonText": "Submit",
      "successMessage": "Thank you!",
      "redirectUrl": null
    },
    "createdAt": "2026-01-01T00:00:00.000Z",
    "updatedAt": "2026-01-15T00:00:00.000Z",
    "publishedAt": "2026-01-02T00:00:00.000Z"
  },
  "requestId": "uuid"
}
```

---

## Submissions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/forms/{formId}/submissions` | List submissions |
| POST | `/forms/{formId}/submissions` | Create submission |
| GET | `/forms/{formId}/submissions/{submissionId}` | Get submission |
| DELETE | `/forms/{formId}/submissions/{submissionId}` | Delete submission |

### Query Parameters: List Submissions

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| page | int | 1 | Page number |
| pageSize | int | 20 | Items per page (max 100) |
| startDate | datetime | - | Filter after date |
| endDate | datetime | - | Filter before date |
| sortBy | string | submittedAt | Sort field |
| sortOrder | string | desc | `asc` or `desc` |

### Request: Create Submission

```json
{
  "data": {
    "name": "John Doe",
    "email": "john@example.com",
    "message": "Hello!"
  },
  "metadata": {
    "referrer": "https://example.com",
    "customFields": {
      "campaign": "winter2026"
    }
  }
}
```

### Response: Submission Detail

```json
{
  "success": true,
  "data": {
    "id": "sub_xxx",
    "formId": "frm_xxx",
    "data": {
      "name": "John Doe",
      "email": "john@example.com",
      "message": "Hello!"
    },
    "metadata": {
      "submittedAt": "2026-01-15T12:00:00.000Z",
      "ipAddress": "192.168.1.1",
      "userAgent": "Mozilla/5.0...",
      "referrer": "https://example.com"
    }
  },
  "requestId": "uuid"
}
```

---

## System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |

### Response: Health Check

```json
{
  "status": "healthy",
  "timestamp": "2026-01-15T12:00:00.000Z",
  "version": "1.0.0",
  "services": {
    "api": {"status": "up", "responseTime": 5},
    "database": {"status": "up", "responseTime": 12}
  }
}
```

---

## Field Types

| Type | HTML Equivalent | Validation Options |
|------|-----------------|-------------------|
| `text` | `<input type="text">` | minLength, maxLength, pattern |
| `email` | `<input type="email">` | Built-in email format |
| `phone` | `<input type="tel">` | Built-in phone format |
| `number` | `<input type="number">` | min, max |
| `date` | `<input type="date">` | - |
| `select` | `<select>` | options array |
| `checkbox` | `<input type="checkbox">` | - |
| `textarea` | `<textarea>` | minLength, maxLength |
| `file` | `<input type="file">` | - |

### Field Options (for select)

```json
{
  "path": "country",
  "label": "Country",
  "type": "select",
  "options": [
    {"value": "us", "label": "United States"},
    {"value": "ca", "label": "Canada"},
    {"value": "uk", "label": "United Kingdom"}
  ]
}
```

### Field Validation

```json
{
  "path": "age",
  "label": "Age",
  "type": "number",
  "validation": {
    "min": 18,
    "max": 120
  }
}
```

```json
{
  "path": "zipcode",
  "label": "ZIP Code",
  "type": "text",
  "validation": {
    "pattern": "^\\d{5}(-\\d{4})?$"
  }
}
```

---

## Error Codes

| Code | HTTP Status | Description |
|------|-------------|-------------|
| `INVALID_API_KEY` | 401 | Missing or invalid API key |
| `FORBIDDEN` | 403 | No access to resource |
| `NOT_FOUND` | 404 | Resource doesn't exist |
| `VALIDATION_ERROR` | 400 | Invalid request body |
| `DUPLICATE_SLUG` | 409 | Slug already in use |
| `RATE_LIMIT_EXCEEDED` | 429 | Too many requests |
| `FORM_NOT_PUBLISHED` | 400 | Form is draft (use test key) |

### Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": {
      "field": "email",
      "reason": "Invalid email format"
    }
  },
  "requestId": "uuid"
}
```

---

## Rate Limits

| Limit | Value |
|-------|-------|
| Requests per hour | 1,000 |
| Requests per day | 10,000 |

### Rate Limit Headers

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1704067200
Retry-After: 3600
```

---

## Pagination

All list endpoints support pagination:

```json
{
  "success": true,
  "data": [...],
  "pagination": {
    "total": 100,
    "page": 1,
    "pageSize": 20,
    "totalPages": 5,
    "hasMore": true
  }
}
```

To iterate all pages:

```bash
page=1
while true; do
  result=$(curl -s -H "Authorization: Bearer $NETPAD_API_KEY" \
    "https://www.netpad.io/api/v1/forms/$FORM_ID/submissions?page=$page&pageSize=100")
  
  echo "$result" | jq -r '.data[]'
  
  hasMore=$(echo "$result" | jq -r '.pagination.hasMore')
  [[ "$hasMore" != "true" ]] && break
  ((page++))
done
```
