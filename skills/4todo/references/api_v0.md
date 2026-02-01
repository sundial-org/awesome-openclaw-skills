# 4todo Documentation

Use this API to manage your todos and recurring tasks.

## Contents

- Authentication
- Base URL
- Quadrant system
- Workspaces
- Endpoints
  - Workspaces: List Workspaces
  - Todos: Get Todos, Create Todo, Complete Todo, Reorder Todos
  - Recurring Todos: Get Recurring Todos, Create Recurring Todo, Get/Update/Delete Recurring Todo
- Error responses
- Best practices
- Support

## Authentication

Send a Bearer token in the `Authorization` header.

```
Authorization: Bearer YOUR_API_TOKEN
```

Send `Content-Type: application/json` for requests with a body.

Create API tokens in the 4todo app settings.
The app shows a token only once, when you create it.
Store it securely.

## Base URL

```
https://4to.do/api/v0
```

## Command examples (this skill)

All command examples below use `curl` and require `FOURTODO_API_TOKEN`:

```bash
curl -sS \
  -H "Authorization: Bearer $FOURTODO_API_TOKEN" \
  -H "Accept: application/json" \
  "https://4to.do/api/v0/workspaces"
```

## Quadrant System

The Eisenhower Matrix uses four quadrants.

| Code | Description                | Meaning                                                 |
| ---- | -------------------------- | ------------------------------------------------------- |
| `IU` | Important & Urgent         | Do first - Critical tasks requiring immediate attention |
| `IN` | Important & Not Urgent     | Schedule - Important tasks for long-term success        |
| `NU` | Not Important & Urgent     | Delegate - Tasks that need to be done but not by you    |
| `NN` | Not Important & Not Urgent | Eliminate - Low-value tasks to minimize                 |

## Workspaces

`GET /api/v0/todos` requires a workspace ID.

Workspace IDs use the `ws_` prefix.

List workspaces with `GET /api/v0/workspaces`.

A restricted workspace is read-only.
Mutations return `402` with `code: WORKSPACE_RESTRICTED`.

## Endpoints

### Workspaces

#### List Workspaces

List your workspaces.

**GET** `/api/v0/workspaces`

**Example Request (curl):**

```bash
curl -sS -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/workspaces"
```

**Example Response:**

```json
[
  {
    "id": "ws_01hqk8z9w3r2n1p0m4v5x7y6",
    "name": "Default",
    "description": "Your default workspace",
    "icon": "",
    "is_default": true,
    "sort_order": "0|",
    "created_at": "2026-01-15T10:30:00Z",
    "updated_at": "2026-01-15T10:30:00Z"
  }
]
```

### Todos

#### Get Todos

Get pending, non-deleted todos for one workspace.

**GET** `/api/v0/todos`

**Query Parameters:**

| Parameter   | Required | Description                                                                 |
| ----------- | -------- | --------------------------------------------------------------------------- |
| `workspace` | Yes      | Workspace ID (TypeID, `ws_...`)                                             |
| `show`      | No       | Set to `all` to include recurring todo configs as `rec_todo_...` pseudo IDs |

**Response:**

The response is an object keyed by quadrant.
Each value is an array of todo objects.

**Todo fields:**

| Field               | Type         | Description                                                     |
| ------------------- | ------------ | --------------------------------------------------------------- |
| `id`                | string       | Todo ID (`todo_...`) or recurring todo ID (`rec_todo_...`)      |
| `name`              | string       | Todo title                                                      |
| `quadrant`          | string       | `IU`, `IN`, `NU`, `NN`                                          |
| `completed_at`      | string\|null | RFC 3339 timestamp, or `null`                                   |
| `type`              | string       | `regular`, `recurring`, or `recurring_instance`                 |
| `recurring_todo_id` | string       | Present for `recurring` and `recurring_instance`                |
| `recurring_config`  | object       | Present only for `recurring`                                    |

**Recurring config fields (`recurring_config`):**

| Field        | Type         | Description                               |
| ------------ | ------------ | ----------------------------------------- |
| `id`         | string       | Recurring todo ID (`rec_todo_...`)        |
| `title`      | string       | Recurring todo title                       |
| `quadrant`   | string       | `IU`, `IN`, `NU`, `NN`                     |
| `frequency`  | string       | `daily`, `weekly`, or `monthly`            |
| `weekdays`   | string[]     | Use for `weekly`                           |
| `month_day`  | number       | Use for `monthly`                          |
| `timezone`   | string       | IANA timezone                              |
| `start_date` | string       | RFC 3339 timestamp                         |
| `end_date`   | string\|null | RFC 3339 timestamp, or `null`              |
| `rrule`      | string       | Recurrence rule string used by the backend |

**Example Request:**

```
GET /api/v0/todos?workspace=ws_01hqk8z9w3r2n1p0m4v5x7y6
```

**Example Request (curl):**

```bash
curl -sS -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/todos?workspace=ws_01hqk8z9w3r2n1p0m4v5x7y6"
```

**Example Response:**

```json
{
  "IU": [
    {
      "id": "todo_01hqk8z9w3r2n1p0m4v5x7y6",
      "name": "Complete project proposal",
      "quadrant": "IU",
      "completed_at": null,
      "type": "regular"
    }
  ],
  "IN": [],
  "NU": [],
  "NN": []
}
```

#### Create Todo

Create a new todo item in a specific quadrant.

**POST** `/api/v0/todos`

**Request Body:**

| Field          | Type   | Required | Description                                                                                |
| -------------- | ------ | -------- | ------------------------------------------------------------------------------------------ |
| `name`         | string | Yes      | Todo item name                                                                             |
| `quadrant`     | string | Yes      | Quadrant type: `IU`, `IN`, `NU`, or `NN`                                                   |
| `workspace_id` | string | No       | Workspace ID (TypeID, `ws_...`). Server uses your default workspace when you omit it.     |

You can also set the `workspace` query parameter.
Use it when you cannot send `workspace_id`.

**Example Request:**

```json
{
  "name": "Complete project proposal",
  "quadrant": "IU",
  "workspace_id": "ws_01hqk8z9w3r2n1p0m4v5x7y6"
}
```

**Example Request (curl):**

```bash
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"name":"Complete project proposal","quadrant":"IU","workspace_id":"ws_01hqk8z9w3r2n1p0m4v5x7y6"}' "https://4to.do/api/v0/todos"
```

**Example Response:**

```json
{
  "message": "Todo created successfully"
}
```

#### Complete Todo

Mark a todo item as completed.

**POST** `/api/v0/todos/:id/complete`

**URL Parameters:**

| Parameter | Description                         |
| --------- | ----------------------------------- |
| `id`      | Todo ID (TypeID format: `todo_...`) |

**Example Request (curl):**

```bash
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/todos/todo_01hqk8z9w3r2n1p0m4v5x7y6/complete"
```

**Example Response:**

```json
{
  "message": "Todo completed successfully"
}
```

This endpoint is idempotent.

**Error Response (404):**

```json
{
  "error": "Todo not found"
}
```

#### Reorder Todos

Reorder todos within the same quadrant or move them between quadrants.

**POST** `/api/v0/todos/reorder`

**Request Body:**

| Field              | Type   | Required | Description                                                               |
| ------------------ | ------ | -------- | ------------------------------------------------------------------------- |
| `moved_todo_id`    | string | Yes      | ID of the todo being moved                                                |
| `previous_todo_id` | string | No       | ID of the todo before the new position (null if moving to first position) |
| `next_todo_id`     | string | No       | ID of the todo after the new position (null if moving to last position)   |
| `quadrant`         | string | Yes      | Target quadrant: `IU`, `IN`, `NU`, or `NN`                                |

If `moved_todo_id` starts with `rec_todo_`, the API updates the recurring todo quadrant.
It ignores `previous_todo_id` and `next_todo_id`.

**Example Request:**

```json
{
  "moved_todo_id": "todo_01hqk8z9w3r2n1p0m4v5x7y6",
  "previous_todo_id": "todo_01hqk8z8x2q1m0n3k4u5w6x7",
  "next_todo_id": null,
  "quadrant": "IN"
}
```

**Example Request (curl):**

```bash
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"moved_todo_id":"todo_01hqk8z9w3r2n1p0m4v5x7y6","previous_todo_id":"todo_01hqk8z8x2q1m0n3k4u5w6x7","next_todo_id":null,"quadrant":"IN"}' "https://4to.do/api/v0/todos/reorder"
```

**Example Response:**

```json
{
  "message": "Todo reordered successfully"
}
```

**Error Response (400):**

```json
{
  "error": "Invalid quadrant type"
}
```

**Error Response (404):**

```json
{
  "error": "Todo not found"
}
```

### Recurring Todos

Recurring todos automatically create new instances based on a schedule.

#### Get Recurring Todos

List recurring todos.

**GET** `/api/v0/recurring-todos`

**Query Parameters:**

| Parameter   | Required | Description                    |
| ----------- | -------- | ------------------------------ |
| `workspace` | No       | Filter by workspace (`ws_...`) |

**Example Request (curl):**

```bash
curl -sS -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/recurring-todos?workspace=ws_01hqk8z9w3r2n1p0m4v5x7y6"
```

**Example Response:**

```json
[
  {
    "id": "rec_todo_01hqk8z9w3r2n1p0m4v5x7y6",
    "title": "Morning standup",
    "quadrant": "IU",
    "frequency": "daily",
    "timezone": "America/Los_Angeles",
    "start_date": "2026-01-15T10:30:00Z",
    "end_date": null,
    "rrule": "FREQ=DAILY"
  }
]
```

#### Create Recurring Todo

Create a new recurring todo with a specified frequency.

**POST** `/api/v0/recurring-todos`

**Query Parameters:**

| Parameter   | Required | Description                                                   |
| ----------- | -------- | ------------------------------------------------------------- |
| `workspace` | No       | Target workspace (`ws_...`). Server uses your default when you omit it. |

**Request Body:**

| Field       | Type    | Required    | Description                                                                                       |
| ----------- | ------- | ----------- | ------------------------------------------------------------------------------------------------- |
| `title`     | string  | Yes         | Recurring todo title                                                                              |
| `quadrant`  | string  | Yes         | Quadrant type: `IU`, `IN`, `NU`, or `NN`                                                          |
| `frequency` | string  | Yes         | `daily`, `weekly`, or `monthly`                                                                   |
| `weekdays`  | array   | No          | Recommended for weekly frequency. Use weekday codes: `["MO", "TU", "WE", "TH", "FR", "SA", "SU"]` |
| `month_day` | integer | Conditional | Required for monthly frequency. Day of month (1-31)                                               |
| `end_date`  | string  | No          | End date in RFC 3339 format (example: `"2026-12-31T00:00:00Z"`)                                   |
| `timezone`  | string  | No          | IANA timezone identifier. Server uses `UTC` when you omit it.                                     |

**Example Request (curl):**

```bash
curl -sS -X POST -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"title":"Morning standup","quadrant":"IU","frequency":"daily","timezone":"America/Los_Angeles"}' "https://4to.do/api/v0/recurring-todos?workspace=ws_01hqk8z9w3r2n1p0m4v5x7y6"
```

**Example Request (Daily):**

```json
{
  "title": "Morning standup",
  "quadrant": "IU",
  "frequency": "daily",
  "timezone": "America/Los_Angeles"
}
```

**Example Request (Weekly):**

```json
{
  "title": "Team meeting",
  "quadrant": "IN",
  "frequency": "weekly",
  "weekdays": ["MO", "WE", "FR"],
  "timezone": "America/New_York"
}
```

**Example Request (Monthly):**

```json
{
  "title": "Monthly report",
  "quadrant": "IN",
  "frequency": "monthly",
  "month_day": 1,
  "timezone": "UTC"
}
```

**Example Response:**

```json
{
  "message": "Recurring todo created successfully"
}
```

#### Get Recurring Todo

Retrieve details of a specific recurring todo.

**GET** `/api/v0/recurring-todos/:id`

**URL Parameters:**

| Parameter | Description       |
| --------- | ----------------- |
| `id`      | Recurring todo ID |

**Example Request (curl):**

```bash
curl -sS -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" "https://4to.do/api/v0/recurring-todos/rec_todo_01hqk8z9w3r2n1p0m4v5x7y6"
```

**Example Response:**

```json
{
  "id": "rec_todo_01hqk8z9w3r2n1p0m4v5x7y6",
  "title": "Morning standup",
  "quadrant": "IU",
  "frequency": "daily",
  "timezone": "America/Los_Angeles",
  "start_date": "2026-01-15T10:30:00Z",
  "end_date": null,
  "rrule": "FREQ=DAILY"
}
```

#### Update Recurring Todo

Update an existing recurring todo's properties.

**PUT** `/api/v0/recurring-todos/:id`

**Request Body:**

| Field        | Type    | Required | Description            |
| ------------ | ------- | -------- | ---------------------- |
| `title`      | string  | Yes      | Recurring todo title   |
| `quadrant`   | string  | Yes      | `IU`, `IN`, `NU`, `NN` |
| `frequency`  | string  | Yes      | `daily`, `weekly`, or `monthly` |
| `weekdays`   | array   | No       | Use for `weekly`       |
| `month_day`  | integer | No       | Required for `monthly` |
| `start_date` | string  | No       | RFC 3339 timestamp     |
| `end_date`   | string  | No       | RFC 3339 timestamp     |
| `timezone`   | string  | Yes      | IANA timezone          |

**Example Request (curl):**

```bash
curl -sS -X PUT -H "Authorization: Bearer $FOURTODO_API_TOKEN" -H "Accept: application/json" -H "Content-Type: application/json" --data-raw '{"title":"Morning standup","quadrant":"IU","frequency":"daily","timezone":"America/Los_Angeles"}' "https://4to.do/api/v0/recurring-todos/rec_todo_01hqk8z9w3r2n1p0m4v5x7y6"
```

**Example Response:**

```json
{
  "message": "Recurring todo updated successfully"
}
```

#### Delete Recurring Todo

Delete a recurring todo. This will stop future instances from being created.

**DELETE** `/api/v0/recurring-todos/:id`

**Example Response:**

```json
{
  "message": "Recurring todo deleted successfully"
}
```

## Error Responses

The API uses standard HTTP status codes to indicate success or failure.

### Status Codes

| Code  | Description                                             |
| ----- | ------------------------------------------------------- |
| `200` | Success - Request completed successfully                |
| `201` | Created - Resource created successfully                 |
| `400` | Bad Request - Invalid request data or parameters        |
| `401` | Unauthorized - Missing or invalid authentication token  |
| `402` | Payment Required - Feature gated or workspace read-only |
| `403` | Forbidden - Access denied                               |
| `404` | Not Found - Requested resource does not exist           |
| `413` | Payload Too Large - Request body is too large           |
| `429` | Too Many Requests - Rate limit exceeded                 |
| `500` | Internal Server Error - Something went wrong on our end |

### Error Response Format

Most error responses use this structure.
Some legacy endpoints return only `error`.

```json
{
  "error": "error_code_or_message",
  "message": "Optional human-readable message"
}
```

**Example Error:**

```json
{
  "error": "invalid_request",
  "message": "Invalid quadrant type"
}
```

### Token Errors

Token auth errors use `401` and JSON responses.

Possible values for `error`:

- `missing authorization header`
- `invalid authorization header`
- `invalid_token`
- `invalid token`
- `token_expired`
- `token_paused`

**Example: token paused**

```json
{
  "error": "token_paused",
  "message": "Your token has been paused because your subscription has expired. Please upgrade your subscription to continue using the API.",
  "upgrade_url": "/settings/subscription"
}
```

**Example: token expired**

```json
{
  "error": "token_expired",
  "message": "Your token has expired. Please create a new token in settings."
}
```

### Rate Limiting

`/api/v0` is rate-limited.

When you exceed the limit, the API returns `429`.
It includes `Retry-After` and `X-RateLimit-*` headers.

**Example: rate limited**

```json
{
  "error": "rate_limited",
  "message": "Too many requests"
}
```

### Feature Gate Errors

Feature gate errors use `402` and a structured JSON response.

Possible values for `code`:

- `FEATURE_UNAVAILABLE`
- `LIMIT_REACHED`
- `WORKSPACE_RESTRICTED`

```json
{
  "code": "FEATURE_UNAVAILABLE",
  "message": "Feature 'recurring_tasks' is not available on your current plan",
  "feature_id": "recurring_tasks",
  "plan_id": "plan_..."
}
```

## Best Practices

### TypeID Format

All IDs in the API use TypeID format for time-sortable, globally unique identifiers:

- Todo IDs: `todo_01hqk8z9w3r2n1p0m4v5x7y6`
- User IDs: `user_01hqk8z9w3r2n1p0m4v5x7y6`
- Recurring Todo IDs: `rec_todo_01hqk8z9w3r2n1p0m4v5x7y6`
- Workspace IDs: `ws_01hqk8z9w3r2n1p0m4v5x7y6`

### Timezones

Always use valid IANA timezone identifiers. Common examples:

- `America/New_York`
- `America/Los_Angeles`
- `Europe/London`
- `Asia/Tokyo`
- `UTC`

### Recurrence Rules

The API exposes a backend `rrule` string.
It uses a small subset of RFC 5545.

- Daily: `FREQ=DAILY`
- Weekly: `FREQ=WEEKLY` or `FREQ=WEEKLY;BYDAY=MO,WE,FR`
- Monthly: `FREQ=MONTHLY;BYMONTHDAY=1`

### Pagination

Currently, API responses are not paginated. This may change in future versions.

## Support

For API support or to report issues:

- Email: support@4to.do

---
