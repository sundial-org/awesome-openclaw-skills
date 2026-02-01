# UniFi Skill

Monitor your UniFi network via the local gateway API from Clawdbot.

## What It Does

- **Devices** — list APs, switches, gateway with status and uptime
- **Clients** — show connected devices (hostname, IP, signal, AP)
- **Health** — site-wide health status (WAN, LAN, WLAN)
- **DPI** — top applications by bandwidth
- **Alerts** — recent alarms and events

All operations are **read-only** and safe for monitoring.

## Setup

### 1. Create a Local Admin Account

1. Open your UniFi OS console (e.g., `https://10.1.0.1`)
2. Go to **OS Settings → Admins & Users**
3. Create a new **local admin** (not cloud/Ubiquiti account)
4. Note the username and password

### 2. Create Credentials File

```bash
mkdir -p ~/.clawdbot/credentials/unifi
cp config.json.example ~/.clawdbot/credentials/unifi/config.json
# Edit with your actual values
```

Or create manually:

```json
{
  "url": "https://10.1.0.1",
  "username": "api",
  "password": "your-password-here",
  "site": "default"
}
```

### 3. Test It

```bash
./scripts/unifi-api.sh
source ./scripts/unifi-api.sh && unifi_get "stat/health"
```

## Usage Examples

### Full dashboard

```bash
bash scripts/dashboard.sh          # Human-readable
bash scripts/dashboard.sh json     # JSON output
```

### Devices

```bash
bash scripts/devices.sh            # All UniFi devices
bash scripts/devices.sh json       # JSON output
```

### Clients

```bash
bash scripts/clients.sh            # Active clients
bash scripts/clients.sh json       # JSON output
```

### Health

```bash
bash scripts/health.sh             # Network health status
```

### Top applications (DPI)

```bash
bash scripts/top-apps.sh           # Top 10 by bandwidth
bash scripts/top-apps.sh 15        # Top 15
```

### Alerts

```bash
bash scripts/alerts.sh             # Last 20 alerts
bash scripts/alerts.sh 50          # Last 50
```

## Environment Variables (Alternative)

```bash
export UNIFI_URL="https://10.1.0.1"
export UNIFI_USER="api"
export UNIFI_PASS="your-password"
export UNIFI_SITE="default"
```

## Troubleshooting

**"UniFi not configured"**  
→ Check your config file exists at `~/.clawdbot/credentials/unifi/config.json`

**"Login failed (empty cookie file)"**  
→ Wrong username/password. Must be a **local** admin, not Ubiquiti cloud account.

**SSL certificate error**  
→ UniFi uses self-signed certs. The scripts use `-k` to skip verification.

**Empty data or "Invalid site"**  
→ Most setups use `default`. Check your site name in the UniFi Network URL.

## License

MIT
