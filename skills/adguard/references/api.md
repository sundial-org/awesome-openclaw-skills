# AdGuard Home API Reference

Official documentation: https://github.com/AdguardTeam/AdGuardHome/wiki/API

## Base URL

```
http://<adguard-host>:3000/control
```

## Authentication

All endpoints require basic auth or session cookie from `/login`.

### Login

**POST** `/control/login`

```json
{
  "name": "admin",
  "password": "password_here"
}
```

Returns session cookie valid for subsequent requests.

## Core Endpoints

### GET /status

Get DNS server status and settings.

**Response:**
```json
{
  "protection_enabled": true,
  "dhcp_enabled": false,
  "version": "0.107.47",
  "language": "en"
}
```

### GET /stats

Get DNS statistics.

**Response:**
```json
{
  "time_units": "hours",
  "stats": [],
  "num_dns_queries": 1234,
  "num_blocked_filtering": 156,
  "num_blocked_safebrowsing": 23,
  "num_replaced_safesearch": 5,
  "num_blocked_parental": 0
}
```

### POST /protection

Enable/disable DNS protection.

**Request:**
```json
{
  "enabled": true
}
```

### POST /cache_clear

Clear the DNS cache.

No request body needed.

## Filtering API

### GET /filtering/check_host

Check if a domain is filtered.

**Query:**
```
GET /control/filtering/check_host?host=example.com
```

**Response:**
```json
{
  "is_filtered": true,
  "reason": "Filtered",
  "filter_names": ["Adblock Plus filter"],
  "service_name": ""
}
```

**Reasons:**
- `NotFiltered` — Domain is allowed
- `Filtered` — Domain is blocked by a rule
- `FilteredBlacklist` — Blocked by custom rules
- `FilteredWhitelist` — Allowed by custom rules
- `SafeBrowsingFiltered` — Blocked by safe browsing
- `ParentalFiltered` — Blocked by parental control
- `SafeSearchFiltered` — Safe search enforced

### GET /filtering/status

Get filtering status and configuration.

**Response:**
```json
{
  "enabled": true,
  "filters": [
    {
      "id": 1,
      "enabled": true,
      "url": "https://...",
      "name": "Adblock Plus",
      "rules_count": 12345
    }
  ],
  "user_rules": [
    "||example.com^",
    "@@||whitelist.com^"
  ],
  "whitelist_filters": []
}
```

### POST /filtering/set_rules

Add custom filtering rules.

**Request:**
```json
{
  "rules": "||example.com^"
}
```

Multiple rules separated by newlines:
```json
{
  "rules": "||tracker1.com^\n||tracker2.com^"
}
```

**Rules Syntax:**

| Pattern | Description |
|---------|-------------|
| `\|\|example.com^` | Block example.com and subdomains |
| `\|\|sub.example.com^` | Block only sub.example.com |
| `example.com` | Block exact match |
| `@@\|\|example.com^` | Allow (whitelist) example.com |
| `!` | Comment line |
| `/regex/` | Regex-based rule |

### GET /filtering/config

Get current filter configuration.

**Response:**
```json
{
  "enabled": true,
  "filters": [...],
  "user_rules": [...],
  "whitelist_filters": []
}
```

## Query Log

### GET /querylog

Get recent DNS queries.

**Query parameters:**
- `older_than` — Timestamp of query to start from
- `limit` — Max results (default: 500)

**Response:**
```json
{
  "oldest": 1234567890,
  "data": [
    {
      "time": "2024-01-30T12:34:56Z",
      "domain": "example.com",
      "client": "192.168.1.100",
      "type": "A",
      "answer": "93.184.216.34",
      "status": "NOERROR",
      "upstream": "8.8.8.8:53",
      "cached": false
    }
  ]
}
```

## Error Responses

### 400 Bad Request
Invalid parameters or malformed JSON.

### 401 Unauthorized
Authentication failed or session expired.

### 500 Internal Server Error
Server error. Check AdGuard logs.

## Common Workflows

### Check and Allow a Domain

```bash
# 1. Check current status
curl -b cookies.txt http://localhost:3000/control/filtering/check_host?host=example.com

# 2. If blocked, add allowlist rule
curl -b cookies.txt -X POST http://localhost:3000/control/filtering/set_rules \
  -H "Content-Type: application/json" \
  -d '{"rules":"@@||example.com^"}'
```

### Block a Domain

```bash
curl -b cookies.txt -X POST http://localhost:3000/control/filtering/set_rules \
  -H "Content-Type: application/json" \
  -d '{"rules":"||malware.com^"}'
```

### Get Protection Status

```bash
curl -b cookies.txt http://localhost:3000/control/status
```

### Disable Protection Temporarily

```bash
curl -b cookies.txt -X POST http://localhost:3000/control/protection \
  -H "Content-Type: application/json" \
  -d '{"enabled":false}'
```

## Rate Limiting

AdGuard Home does not implement rate limiting on the API. However, excessive requests may impact performance.

## Caching

DNS responses are cached by AdGuard. Call `/cache_clear` after modifying rules for immediate effect.

## Version Compatibility

This reference covers AdGuard Home v0.107+. Older versions may have different endpoints.

Check your version:
```bash
curl http://localhost:3000/control/status | grep version
```
