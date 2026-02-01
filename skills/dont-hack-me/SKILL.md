---
name: dont-hack-me
description: >-
  別駭我！基本安全檢測 — Security self-check for Clawdbot/Moltbot.
  Run a quick audit of your clawdbot.json to catch dangerous
  misconfigurations — exposed gateway, missing auth, open DM policy,
  weak tokens, loose file permissions. Auto-fix included.
  Invoke: "run a security check" or "幫我做安全檢查".
author: "小安 Ann Agent — Taiwan 台灣"
homepage: https://github.com/peterann/dont-hack-me
metadata:
  clawdbot:
    emoji: "🔒"
---

# dont-hack-me

Security self-check skill for Clawdbot / Moltbot.
Reads `~/.clawdbot/clawdbot.json` and checks 7 items that cover the most
common misconfigurations. Outputs a simple PASS / FAIL / WARN report.

## How to run

Say any of:

- "run a security check"
- "check my security settings"
- "audit my clawdbot config"
- "am I secure?"

## Checklist — step by step

When this skill is triggered, follow these steps **exactly**:

### Step 0 — Read the config

Use the `read` tool to open `~/.clawdbot/clawdbot.json`.
Parse the JSON content. If the file does not exist or is unreadable,
report an error and stop.

Also run a shell command to get the file permissions:
```
stat -f '%Lp' ~/.clawdbot/clawdbot.json
```
(On Linux: `stat -c '%a' ~/.clawdbot/clawdbot.json`)

### Step 1 — Gateway Bind

- **Path:** `gateway.bind`
- **Expected:** `"loopback"` or `"localhost"` or `"127.0.0.1"` or `"::1"`
- **PASS** if the value is one of the above or the key is absent (default is `"loopback"`)
- **FAIL** if the value is `"0.0.0.0"`, `"::"`, or any non-loopback address
- **Severity:** CRITICAL — a non-loopback bind exposes your agent to the network

### Step 2 — Gateway Auth Mode

- **Path:** `gateway.auth.mode`
- **Expected:** `"token"` or `"password"`
- **PASS** if the value is `"token"` or `"password"`, or the key is absent (default is `"token"`)
- **FAIL** if the value is `"off"` or `"none"`
- **Severity:** CRITICAL — without auth anyone who can reach the gateway can control your agent

### Step 3 — Token Strength

- **Path:** `gateway.auth.token`
- **Expected:** 32 or more characters
- **PASS** if the token is >= 32 characters
- **WARN** if the token is 16–31 characters
- **FAIL** if the token is < 16 characters or empty
- **SKIP** if auth mode is `"password"` (passwords are user-chosen, don't judge length)
- **Severity:** HIGH — short tokens are vulnerable to brute-force

### Step 4 — DM Policy (per channel)

- **Path:** `channels.<name>.dmPolicy` for each channel
- **Expected:** `"pairing"` — or if `"open"`, there must be a non-empty `allowFrom` array
- **PASS** if `dmPolicy` is `"pairing"`, or if `allowFrom` has at least one entry
- **FAIL** if `dmPolicy` is `"open"` and `allowFrom` is missing or empty
- **SKIP** if no channels are configured
- **Severity:** HIGH — an open DM policy lets anyone send commands to your agent

### Step 5 — Group Policy (per channel)

- **Path:** `channels.<name>.groupPolicy` for each channel
- **Expected:** `"allowlist"`
- **PASS** if `groupPolicy` is `"allowlist"` or absent (default is `"allowlist"`)
- **FAIL** if `groupPolicy` is `"open"` or `"any"`
- **SKIP** if no channels are configured
- **Severity:** HIGH — non-allowlist group policy lets any group trigger your agent

### Step 6 — File Permissions

- **Check:** file mode of `~/.clawdbot/clawdbot.json`
- **Expected:** `600` or `400` (owner read/write only)
- **PASS** if permissions are `600` or `400`
- **WARN** if permissions are `644` or `640` (group/other can read)
- **FAIL** if permissions are `777`, `755`, `666`, or anything world-writable
- **Severity:** MEDIUM — loose permissions let other users on the system read your tokens

### Step 7 — Plaintext Secrets Scan

- **Check:** scan all string values in the JSON for keys named `password`, `secret`, `apiKey`, `api_key`, `privateKey`, `private_key` (case-insensitive) that contain a non-empty string value
- **PASS** if no such keys are found
- **WARN** if such keys exist — remind the user to consider using environment variables or a secrets manager
- **Note:** `token` fields used for gateway auth are expected and should NOT be flagged
- **Severity:** MEDIUM — plaintext secrets in config files can be leaked through backups, logs, or version control

## Output format

After completing all checks, output a report in this exact format:

```
🔒 Security Check Report

1. Gateway Bind        <ICON> <STATUS> — <detail>
2. Gateway Auth        <ICON> <STATUS> — <detail>
3. Token Strength      <ICON> <STATUS> — <detail>
4. DM Policy           <ICON> <STATUS> — <detail>
5. Group Policy        <ICON> <STATUS> — <detail>
6. File Permissions    <ICON> <STATUS> — <detail>
7. Secrets Scan        <ICON> <STATUS> — <detail>

Score: X/7 PASS, Y WARN, Z FAIL
```

Where:
- `<ICON>` is one of: ✅ (PASS), ⚠️ (WARN), ❌ (FAIL), ⏭️ (SKIP)
- `<STATUS>` is one of: `PASS`, `WARN`, `FAIL`, `SKIP`
- `<detail>` is a short explanation (e.g., "loopback", "token mode", "48 chars", "permissions 600")

## Auto-fix flow

If **any** item is FAIL or WARN, do the following:

1. Show the report first (as above).
2. List each fixable item with a short description of what will be changed.
3. Ask the user: **"Want me to fix these? (yes / no / pick)"**
   - **yes** — fix all FAIL and WARN items automatically.
   - **no** — stop, do nothing.
   - **pick** — let the user choose which items to fix.
4. Apply the fixes (see Fix recipes below).
5. After applying, re-read the config and re-run the full check to confirm everything is PASS.
6. If the config was changed, remind the user: **"Run `clawdbot gateway restart` to apply the new settings."**

### Fix recipes

Use these exact fixes for each item. Edit `~/.clawdbot/clawdbot.json` using the edit/write tool.

#### #1 Gateway Bind — FAIL
Set `gateway.bind` to `"loopback"`:
```json
{ "gateway": { "bind": "loopback" } }
```

#### #2 Gateway Auth — FAIL
Set `gateway.auth.mode` to `"token"`. If no token exists yet, also generate one:
```json
{ "gateway": { "auth": { "mode": "token", "token": "<GENERATED>" } } }
```
Generate the token with:
```bash
openssl rand -hex 24
```
That produces a 48-character hex string (192-bit entropy).

#### #3 Token Strength — FAIL / WARN
Replace the existing token with a new strong one:
```bash
openssl rand -hex 24
```
Write the output into `gateway.auth.token`.

#### #4 DM Policy — FAIL
Set `dmPolicy` to `"pairing"` for each affected channel:
```json
{ "channels": { "<name>": { "dmPolicy": "pairing" } } }
```

#### #5 Group Policy — FAIL
Set `groupPolicy` to `"allowlist"` for each affected channel:
```json
{ "channels": { "<name>": { "groupPolicy": "allowlist" } } }
```

#### #6 File Permissions — FAIL / WARN
Run:
```bash
chmod 600 ~/.clawdbot/clawdbot.json
```

#### #7 Secrets Scan — WARN
This one cannot be auto-fixed safely. Instead, list each flagged key and
remind the user:
- Move the value to an environment variable
- Or use a secrets manager
- Reference it in the config as `"$ENV_VAR_NAME"` if the platform supports it

### Important rules for auto-fix

- **Always back up first.** Before writing any changes, copy the original:
  ```bash
  cp ~/.clawdbot/clawdbot.json ~/.clawdbot/clawdbot.json.bak
  ```
- **Merge, don't overwrite.** Read the full JSON, modify only the specific
  keys, write back the complete JSON. Never lose existing settings.
- **Preserve formatting.** Write the JSON with 2-space indentation.
- **One write operation.** Collect all JSON fixes, apply them in a single
  write to avoid partial states.
- **Token replacement requires restart.** If the gateway token was changed,
  the user must update any paired clients with the new token.
  Warn: "Your gateway token was changed. Any paired devices will need the
  new token to reconnect."

## What this skill does NOT check

- Sandbox configuration (not needed for most setups)
- Network isolation / Docker (macOS native setups don't use it)
- MCP tool permissions (too complex for a basic audit)
- Whether your OS firewall is configured
- Whether your agent code has vulnerabilities

For a more comprehensive audit, see community tools like `clawdbot-security-check`.

## Reference

Based on the community-compiled "Top 10 Clawdbot/Moltbot Security Vulnerabilities" list.
Covers 7 of the 10 items that apply to typical macOS-native deployments.

---

*小安 Ann Agent — Taiwan 台灣*
*Building skills and local MCP services for all AI agents, everywhere.*
*為所有 AI Agent 打造技能與在地 MCP 服務，不限平台。*
