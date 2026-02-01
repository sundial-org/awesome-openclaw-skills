# Pi-hole Skill

Control your Pi-hole DNS ad blocker via the Pi-hole v6 API.

## Setup

Set your Pi-hole API configuration in Clawdbot config:

```yaml
skills:
  entries:
    pihole:
      apiUrl: "https://pi-hole.local/api"  # v6 API path
      apiToken: "your-app-password-here"       # Get from Pi-hole Admin
      insecure: false                          # Set to true for self-signed certs
```

Alternatively, set environment variables:
```bash
export PIHOLE_API_URL="https://pi-hole.local/api"
export PIHOLE_API_TOKEN="your-app-password-here"
export PIHOLE_INSECURE="false"
```

### Getting API Credentials

1. Open Pi-hole Admin at `http://pi-hole.local/admin`
2. Navigate to **Settings** > **API**
3. Generate an app password
4. Use that password as `apiToken`

## Capabilities

### Status
- Get current Pi-hole status (enabled/disabled)
- View stats: queries blocked, queries today, domains being blocked, active clients
- See recent query activity

### Controls
- **Enable/Disable**: Turn Pi-hole on or off
- **Disable for 5 minutes**: Temporarily disable ad blocking for a short period
- **Disable for custom duration**: Set specific disable time (in minutes)

### Block Analysis
- **Check blocked domains**: See what domains were blocked in a time window
- **Show top blocked**: Most frequently blocked domains

## Usage Examples

```
# Check Pi-hole status
"pihole status"

# Turn off ad blocking
"pihole off"

# Turn on ad blocking
"pihole on"

# Disable for 5 minutes (for a site that needs ads)
"pihole disable 5m"

# Disable for 30 minutes
"pihole disable 30"

# See what was blocked in the last 30 minutes
"pihole blocked"

# See blocked domains in last 10 minutes (600 seconds)
"pihole blocked 600"

# Show statistics
"pihole stats"
```

## API Endpoints (Pi-hole v6)

### Authentication
```
POST /api/auth
Content-Type: application/json
{"password":"your-app-password"}

Response:
{
  "session": {
    "sid": "session-token-here",
    "validity": 1800
  }
}
```

### Status
```
GET /api/dns/blocking
Headers: sid: <session-token>

Response:
{
  "blocking": "enabled" | "disabled",
  "timer": 30  // seconds until re-enable (if disabled with timer)
}
```

### Enable/Disable
```
POST /api/dns/blocking
Headers: sid: <session-token>
Content-Type: application/json

Enable:
{"blocking":true}

Disable:
{"blocking":false}

Disable with timer (seconds):
{"blocking":false,"timer":300}
```

### Stats
```
GET /api/stats/summary
Headers: sid: <session-token>

Response:
{
  "queries": {
    "total": 233512,
    "blocked": 23496,
    "percent_blocked": 10.06
  },
  "gravity": {
    "domains_being_blocked": 165606
  },
  "clients": {
    "active": 45
  }
}
```

### Queries
```
GET /api/queries?start=-<seconds>
Headers: sid: <session-token>

Response:
{
  "queries": [
    {
      "domain": "example.com",
      "status": "GRAVITY",
      "time": 1768363900,
      "type": "A"
    }
  ]
}
```

## v5 vs v6 API Changes

Pi-hole v6 introduced significant API changes:

| Feature | v5 API | v6 API |
|---------|----------|----------|
| Base URL | `/admin/api.php` | `/api` |
| Auth | Token in URL/headers | Session-based |
| Status | `?status` | `/api/dns/blocking` |
| Stats | `?summaryRaw` | `/api/stats/summary` |
| Queries | `?recentBlocked` | `/api/queries` |
| Whitelist | Supported via API | **Not available via API** |

**Important:** Domain whitelisting is no longer available via the v6 API. You must whitelist domains through the Pi-hole Admin UI.

## SSL Certificates

### Production (Valid Cert)
```yaml
{
  "apiUrl": "https://pi-hole.example.com/api",
  "apiToken": "...",
  "insecure": false
}
```

### Self-Signed/Local Cert
```yaml
{
  "apiUrl": "https://pi-hole.local/api",
  "apiToken": "...",
  "insecure": true
}
```

The `insecure` flag adds the `-k` option to curl to bypass certificate validation.

## Security Notes

- Session tokens expire after 30 minutes (1800 seconds)
- API password is sent in JSON body, not URL
- All requests have a 30-second timeout
- Token is not visible in process list (passed via environment)

## Troubleshooting

### "Failed to authenticate"
- Check that `apiToken` matches your Pi-hole app password
- Verify `apiUrl` is correct (must end in `/api`)
- Ensure Pi-hole is accessible from your network

### "Could not determine status"
- Check API URL is reachable
- If using HTTPS with self-signed cert, set `insecure: true`
- Verify API password is correct

### Network Errors
- Ensure clawdbot's machine can reach the Pi-hole
- Check firewall rules allow API access
- Verify URL scheme (http vs https)

## Requirements

- Pi-hole v6 or later
- App password generated in Pi-hole Admin
- Network access to Pi-hole API
- `curl`, `jq` (installed on most Unix systems)
