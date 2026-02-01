# Installation Guide

## Requirements

- Linux server (Ubuntu/Debian recommended)
- [Bun](https://bun.sh) runtime
- [Caddy](https://caddyserver.com) web server
- Git

## Quick Install

```bash
curl -fsSL https://raw.githubusercontent.com/498AS/kleo-static-files/main/install.sh | sudo bash
```

## Manual Install

### 1. Install Dependencies

```bash
# Bun
curl -fsSL https://bun.sh/install | bash

# Caddy (Ubuntu/Debian)
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update && sudo apt install caddy
```

### 2. Clone Repository

```bash
sudo git clone https://github.com/498AS/kleo-static-files.git /opt/kleo-static-files
cd /opt/kleo-static-files
bun install
```

### 3. Configure

Create `/opt/kleo-static-files/.env`:

```bash
SF_PORT=3000
SF_DOMAIN=yourdomain.com
SF_SITES_ROOT=/var/lib/kleo-static-files/sites
SF_DB_PATH=/var/lib/kleo-static-files/data/static-files.db
SF_CADDY_SNIPPET=/etc/caddy/sites.d/static-files.caddy
SF_BIND_IPS=YOUR_SERVER_IP

# Limits
SF_RATE_LIMIT_WINDOW=60000
SF_RATE_LIMIT_MAX=100
SF_MAX_FILE_MB=50
```

### 4. Create Directories

```bash
sudo mkdir -p /var/lib/kleo-static-files/{data,sites}
sudo mkdir -p /etc/caddy/sites.d
sudo mkdir -p /var/log/caddy
```

### 5. Update Caddyfile

Add to `/etc/caddy/Caddyfile`:

```caddy
import /etc/caddy/sites.d/*.caddy
```

### 6. Create Systemd Service

Create `/etc/systemd/system/kleo-static-files.service`:

```ini
[Unit]
Description=Kleo Static Files API
After=network.target caddy.service

[Service]
Type=simple
WorkingDirectory=/opt/kleo-static-files
EnvironmentFile=/opt/kleo-static-files/.env
ExecStart=/root/.bun/bin/bun run server/index.ts
ExecStartPost=/opt/kleo-static-files/scripts/sync-caddy.ts --reload
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### 7. Start Service

```bash
sudo systemctl daemon-reload
sudo systemctl enable kleo-static-files
sudo systemctl start kleo-static-files
```

### 8. Create API Key

```bash
cd /opt/kleo-static-files
source .env
bun run scripts/create-key.ts "admin"
# Save the key!
```

## DNS Setup

For each subdomain to work, configure a wildcard DNS record:

| Type | Name | Value |
|------|------|-------|
| A | *.yourdomain.com | YOUR_SERVER_IP |
| AAAA | *.yourdomain.com | YOUR_IPV6 (optional) |

## Verification

```bash
# Check service
systemctl status kleo-static-files

# Check API
curl http://localhost:3000/health

# Test site creation
export SF_API_URL=http://localhost:3000
export SF_API_KEY=sk_your_key
sf sites create test
curl -I https://test.yourdomain.com
```

## Uninstall

```bash
sudo /opt/kleo-static-files/install.sh --uninstall
```
