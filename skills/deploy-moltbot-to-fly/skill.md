# Deploy Moltbot to Fly.io

Deploy Moltbot (Clawdbot) to Fly.io with proper configuration, persistent storage, and device pairing.

## Overview

Deploying Moltbot to Fly.io requires:
1. Setting up the Fly app with a persistent volume
2. Configuring environment secrets (API keys, gateway token)
3. Creating a proper config file with token authentication
4. Approving device pairing for web UI access

## Prerequisites

Before starting:
- Fly.io CLI installed (`brew install flyctl` or `curl -L https://fly.io/install.sh | sh`)
- Fly.io account and logged in (`fly auth login`)
- Anthropic API key (and optionally OpenAI API key)
- Git installed

## Phase 1: Clone and Setup

### 1.1 Clone the Moltbot Repository

```bash
git clone https://github.com/clawdbot/clawdbot.git moltbot-deploy
cd moltbot-deploy
```

### 1.2 Generate Gateway Token

Generate a secure token for authentication:

```bash
openssl rand -hex 32
```

**IMPORTANT:** Save this token - you'll need it for:
- Fly secrets
- Config file
- Web UI access URL

## Phase 2: Fly.io Configuration

### 2.1 Create fly.toml

Create `fly.toml` with the correct configuration:

```toml
app = 'your-app-name'
primary_region = 'iad'

[build]
  dockerfile = 'Dockerfile'

[env]
  NODE_ENV = 'production'
  CLAWDBOT_PREFER_PNPM = '1'
  CLAWDBOT_STATE_DIR = '/data'
  NODE_OPTIONS = '--max-old-space-size=1536'

[processes]
  app = "node dist/index.js gateway --allow-unconfigured --port 3000 --bind lan"

[http_service]
  internal_port = 3000
  force_https = true
  auto_stop_machines = false
  auto_start_machines = true
  min_machines_running = 1
  processes = ["app"]

[[vm]]
  size = 'shared-cpu-2x'
  memory = '2048mb'

[mounts]
  source = 'moltbot_data'
  destination = '/data'
```

**CRITICAL Settings:**
- `CLAWDBOT_STATE_DIR = '/data'` - Required for proper config persistence
- `--bind lan` - Allows Fly's proxy to reach the gateway
- `http_service` - Newer Fly format (not `[[services]]`)
- `memory = '2048mb'` - 512MB is too small; 2GB recommended

### 2.2 Create App and Volume

```bash
fly apps create your-app-name
fly volumes create moltbot_data --region iad --size 1 -a your-app-name -y
```

Choose a region close to you:
- `iad` - Virginia (US East)
- `lhr` - London
- `sjc` - San Jose (US West)

### 2.3 Set Fly Secrets

```bash
# Set your generated token
fly secrets set CLAWDBOT_GATEWAY_TOKEN="YOUR-TOKEN-HERE" -a your-app-name

# Set API keys
fly secrets set ANTHROPIC_API_KEY="sk-ant-xxxxx" -a your-app-name
fly secrets set OPENAI_API_KEY="sk-xxxxx" -a your-app-name  # Optional
```

**Note:** Secrets are deployed on first `fly deploy`, not immediately.

## Phase 3: Deploy

Deploy the application:

```bash
fly deploy -a your-app-name
```

First deployment takes ~3-5 minutes (building Docker image).

**Wait for gateway to start:**
```bash
fly logs -a your-app-name --no-tail | grep "listening on"
```

You should see:
```
[gateway] listening on ws://0.0.0.0:3000 (PID xxx)
```

## Phase 4: Create Config File

**CRITICAL:** The config file must include the same token as the env var for authentication to work.

### 4.1 SSH into the machine

```bash
fly ssh console -a your-app-name
```

### 4.2 Create the config file

```bash
cat > /data/moltbot.json << 'EOF'
{
  "gateway": {
    "mode": "local",
    "bind": "lan",
    "auth": {
      "mode": "token",
      "token": "YOUR-TOKEN-HERE"
    }
  },
  "agents": {
    "defaults": {
      "model": {
        "primary": "anthropic/claude-opus-4-5"
      }
    }
  },
  "auth": {
    "profiles": {
      "anthropic:default": { "mode": "token", "provider": "anthropic" }
    }
  }
}
EOF
```

**Replace `YOUR-TOKEN-HERE` with your actual token!**

### 4.3 Exit and restart

```bash
exit
fly machine restart <machine-id> -a your-app-name
```

Get machine ID with: `fly machines list -a your-app-name`

## Phase 5: Access and Device Pairing

### 5.1 Wait for DNS propagation

DNS may take 2-5 minutes to propagate. Check status:

```bash
nslookup your-app-name.fly.dev 8.8.8.8
```

If DNS isn't resolving on your machine, flush your DNS cache:

**macOS:**
```bash
sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder
```

**Linux:**
```bash
sudo systemd-resolve --flush-caches
```

### 5.2 Access Web UI

Open in browser with the tokenized URL:

```
https://your-app-name.fly.dev/?token=YOUR-TOKEN-HERE
```

You'll see "disconnected (1008): pairing required" - this is normal!

### 5.3 Approve Device Pairing

While the browser is open and attempting to connect, approve the pairing:

```bash
fly ssh console -a your-app-name
```

Then run:

```bash
node -e "
const fs = require('fs');
const pending = JSON.parse(fs.readFileSync('/data/devices/pending.json'));
const paired = JSON.parse(fs.readFileSync('/data/devices/paired.json') || '{}');
const requestId = Object.keys(pending)[0];
if (requestId) {
  const device = pending[requestId];
  paired[device.deviceId] = {
    deviceId: device.deviceId,
    publicKey: device.publicKey,
    platform: device.platform,
    clientId: device.clientId,
    role: device.role,
    roles: device.roles,
    scopes: device.scopes,
    approvedAt: Date.now(),
    approvedBy: 'cli'
  };
  delete pending[requestId];
  fs.writeFileSync('/data/devices/pending.json', JSON.stringify(pending, null, 2));
  fs.writeFileSync('/data/devices/paired.json', JSON.stringify(paired, null, 2));
  console.log('Approved device:', device.deviceId);
} else {
  console.log('No pending devices');
}
"
```

### 5.4 Refresh Browser

After approval, refresh your browser. You should now be connected! 🎉

## Troubleshooting

### Gateway Token Mismatch

**Symptoms:** `unauthorized: gateway token mismatch`

**Fix:** Token in config file must match the env var:

```bash
# Check env var token
fly ssh console -a your-app-name -C "printenv CLAWDBOT_GATEWAY_TOKEN"

# Update config file to match
fly ssh console -a your-app-name
# Edit /data/moltbot.json and update gateway.auth.token
```

### App Not Listening / Connection Refused

**Symptoms:** `instance refused connection` or `not listening on expected address`

**Fix:** Ensure `--bind lan` in fly.toml and gateway is fully started:

```bash
fly logs -a your-app-name --no-tail | tail -50
```

Wait 30-60 seconds after deploy for gateway to initialize.

### DNS Not Resolving

**Symptoms:** `Could not resolve host`

**Fix:** 
1. Wait 2-5 minutes for DNS propagation
2. Use Google DNS: `8.8.8.8` or `1.1.1.1`
3. Flush local DNS cache (see Phase 5.1)

### Config Validation Errors

**Symptoms:** Gateway exits with "Invalid input" or validation errors

**Fix:** Check config syntax:

```bash
fly ssh console -a your-app-name -C "cat /data/moltbot.json"
```

Common issues:
- **Invalid `auth.mode`**: Only `"token"` is valid (not `"off"`)
- Missing commas in JSON
- Mismatched quotes

### State Not Persisting

**Symptoms:** Config/devices reset after restart

**Fix:** Ensure `CLAWDBOT_STATE_DIR=/data` is set in fly.toml `[env]` section.

### Stuck Deployment

**Symptoms:** Machine keeps restarting or won't stabilize

**Nuclear option (fastest):**

```bash
fly apps destroy your-app-name -y
# Then re-run Phase 2 onwards with fresh setup
```

## Advanced: Trusted Proxies (Optional)

If you see proxy warnings in logs, add trusted proxies:

```bash
fly ssh console -a your-app-name
```

```bash
node -e "
const fs = require('fs');
const config = JSON.parse(fs.readFileSync('/data/moltbot.json'));
config.gateway.trustedProxies = [
  '172.16.0.0/12',
  '10.0.0.0/8'
];
fs.writeFileSync('/data/moltbot.json', JSON.stringify(config, null, 2));
console.log('Trusted proxies configured');
"
```

Restart machine after changes.

## Quick Reference

```bash
# Check status
fly status -a APP

# View logs
fly logs -a APP --no-tail | tail -50

# SSH into machine
fly ssh console -a APP

# Restart machine
fly machines list -a APP  # Get machine ID
fly machine restart <machine-id> -a APP

# Check secrets
fly secrets list -a APP

# Get gateway token
fly ssh console -a APP -C "printenv CLAWDBOT_GATEWAY_TOKEN"

# Redeploy
fly deploy -a APP
```

## Updates

To update Moltbot:

```bash
cd moltbot-deploy
git pull
fly deploy -a your-app-name
```

Config and paired devices persist on the volume across updates.

## Key Lessons

1. **`CLAWDBOT_STATE_DIR=/data`** is critical - without it, config location is wrong
2. **Token must be in BOTH** env var AND config file
3. **Use `http_service`** not `[[services]]` (newer Fly format)
4. **Device pairing is required** even with token auth
5. **DNS takes time** - wait 2-5 minutes, flush cache if needed
6. **Fresh deploy is often faster** than debugging corrupted state
7. **2GB RAM minimum** - 512MB will OOM, 1GB may work but 2GB is recommended

## Resources

- [Fly.io Documentation](https://fly.io/docs/)
- [Moltbot Official Docs](https://docs.molt.bot/platforms/fly)
- [Clawdbot GitHub](https://github.com/clawdbot/clawdbot)
