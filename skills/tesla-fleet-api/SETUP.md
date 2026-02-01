# Tesla Fleet API Skill — Setup Guide

This guide covers **setup + configuration** for the Tesla Fleet API skill.

If you just want the CLI command reference, see `SKILL.md`.

---

## Prerequisites

- Tesla Developer Account + an app created
- A domain you control (for public key hosting + virtual key enrollment)
- `python3`
- macOS (scripts tested on macOS)

---

## State / Files

All runtime state lives outside the skill folder:

`~/.clawdbot/tesla-fleet-api/`

Files:
- `.env` — **provider creds** (client id/secret) and optional overrides
- `config.json` — non-token config (audience/base_url/ca_cert/redirect_uri/domain)
- `auth.json` — tokens (access/refresh)
- `vehicles.json` — cached vehicle list
- `places.json` — named locations (`{"home": {"lat": ..., "lon": ...}}`)

---

## 1) Install + setup Tesla proxy (one-time)

Some commands require Tesla’s end-to-end signing via the local proxy.

```bash
cd skills/tesla-fleet-api
./scripts/setup_proxy.sh
```

This builds `tesla-http-proxy` and generates TLS material under:
`~/.clawdbot/tesla-fleet-api/proxy/`

---

## 2) Create & host your EC keypair

```bash
# Generate P-256 keypair
openssl ecparam -name prime256v1 -genkey -noout -out private-key.pem
openssl ec -in private-key.pem -pubout -out public-key.pem

# Host public key at:
# https://YOUR_DOMAIN/.well-known/appspecific/com.tesla.3p.public-key.pem
```

Store your private key securely (recommended location):
`~/.clawdbot/tesla-fleet-api/YOUR_DOMAIN.tesla.private-key.pem`

---

## 3) Put provider credentials into .env

Create:
`~/.clawdbot/tesla-fleet-api/.env`

```bash
cat > ~/.clawdbot/tesla-fleet-api/.env <<'EOF'
TESLA_CLIENT_ID=YOUR_CLIENT_ID
TESLA_CLIENT_SECRET=YOUR_CLIENT_SECRET
EOF
chmod 600 ~/.clawdbot/tesla-fleet-api/.env
```

Optional overrides you *can* also set in `.env`:
- `TESLA_AUDIENCE` (defaults to EU)
- `TESLA_REDIRECT_URI` (default: `http://localhost:18080/callback`)
- `TESLA_DOMAIN`
- `TESLA_BASE_URL`
- `TESLA_CA_CERT`

---

## 4) Configure non-secret settings (optional)

```bash
python3 scripts/auth.py config set \
  --redirect-uri "http://localhost:18080/callback" \
  --audience "https://fleet-api.prd.eu.vn.cloud.tesla.com"
```

---

## 5) OAuth login (creates auth.json)

Interactive login (manual code paste):

```bash
python3 scripts/auth.py login
```

Automatic login via local callback server:

```bash
python3 scripts/tesla_oauth_local.py --prompt-missing-scopes
```

---

## 6) Register domain + enroll virtual key

```bash
python3 scripts/auth.py register --domain YOUR_DOMAIN.com
```

Then, on your phone (Tesla app installed):

`https://tesla.com/_ak/YOUR_DOMAIN.com`

---

## 7) Start proxy + configure scripts to use it

Start the proxy:

```bash
./scripts/start_proxy.sh ~/.clawdbot/tesla-fleet-api/YOUR_DOMAIN.tesla.private-key.pem
```

Configure the scripts to talk to the local proxy:

```bash
python3 scripts/auth.py config set \
  --base-url "https://localhost:4443" \
  --ca-cert "$HOME/.clawdbot/tesla-fleet-api/proxy/tls-cert.pem"
```

---

## 8) Test

```bash
python3 scripts/vehicles.py
python3 scripts/vehicle_data.py -c
python3 scripts/command.py honk
```

---

## Places (named lat/lon)

```bash
# list
python3 scripts/command.py places list

# set explicit coords
python3 scripts/command.py places set home --lat 48.10033 --lon 17.04217

# set from current vehicle location
python3 scripts/command.py places set school --here

# use in precondition
python3 scripts/command.py precondition add -t 08:00 -d weekdays --place home
```

---

## Troubleshooting

- **Token expired (401):**
  ```bash
  python3 scripts/auth.py refresh
  ```

- **Vehicle asleep / unavailable:**
  ```bash
  python3 scripts/command.py wake
  ```

- **Command not signed / rejected:**
  ensure proxy is running and `base_url` + `ca_cert` are configured.
