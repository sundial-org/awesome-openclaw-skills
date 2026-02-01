# Troubleshooting Guide

## Table of Contents

- [Authentication Issues](#authentication-issues)
- [MFA Problems](#mfa-problems)
- [API Errors](#api-errors)
- [Session Issues](#session-issues)
- [CLI Problems](#cli-problems)

## Authentication Issues

### "Not logged in" Error

**Cause:** No valid session exists.

**Solution:**
```bash
monarch-money auth login
```

### "Invalid credentials" Error

**Cause:** Email or password is incorrect.

**Solutions:**
1. Verify credentials work at https://app.monarchmoney.com
2. Check for typos in environment variables
3. Ensure password doesn't contain shell special characters (use quotes)

```bash
export MONARCH_PASSWORD='pa$$word!with@special#chars'
```

### "Authentication failed" After Working Previously

**Cause:** Session expired or Monarch Money invalidated it.

**Solution:**
```bash
monarch-money auth logout
monarch-money auth login
```

## MFA Problems

### "MFA code required" Error

**Cause:** `MONARCH_MFA_SECRET` not set or invalid.

**Solutions:**

1. **Get your MFA secret:**
   - Login to https://app.monarchmoney.com
   - Settings > Security > Two-Factor Authentication
   - Disable and re-enable MFA
   - Click "Can't scan? View setup key"
   - Copy the base32 string (like `JBSWY3DPEHPK3PXP`)

2. **Set the variable:**
   ```bash
   export MONARCH_MFA_SECRET="YOUR_SECRET_HERE"
   ```

### "MFA code expired" or "Invalid MFA code"

**Cause:** System clock is out of sync. TOTP codes are time-sensitive (30-second windows).

**Solutions:**

1. **Sync system clock:**
   ```bash
   # macOS/Linux
   sudo ntpdate -s time.apple.com

   # Check current time
   date
   ```

2. **Verify the secret is correct:**
   - The secret should be a base32 string (letters A-Z and numbers 2-7)
   - It should NOT be the 6-digit code from your authenticator app
   - Example valid secret: `JBSWY3DPEHPK3PXP`

### MFA Secret vs MFA Code

| Item | Format | Example | Use |
|------|--------|---------|-----|
| MFA Secret | Base32 string | `JBSWY3DPEHPK3PXP` | Set as `MONARCH_MFA_SECRET` |
| MFA Code | 6 digits | `123456` | Entered manually in apps |

The CLI needs the **secret** to generate codes automatically. If you only have the 6-digit code, you need to regenerate MFA in Monarch Money settings.

## API Errors

### 400 Bad Request

**Cause:** Invalid query or mutation.

**Solutions:**
1. Check transaction/category IDs are valid UUIDs
2. Verify required fields are provided
3. Check amount formats (negative for expenses)

### 401 Unauthorized

**Cause:** Session token invalid or expired.

**Solution:**
```bash
monarch-money auth logout
monarch-money auth login
```

### 429 Too Many Requests

**Cause:** Rate limit exceeded.

**Solution:** Wait and retry. The client has built-in rate limiting, but rapid scripted calls may still hit limits.

### 500 Internal Server Error

**Cause:** Monarch Money API issue.

**Solutions:**
1. Wait and retry
2. Check https://status.monarchmoney.com for outages
3. Try with a smaller request (fewer transactions)

### 525 SSL Handshake Failed

**Cause:** Cloudflare protection or network issue.

**Solutions:**
1. Wait 1-2 minutes and retry
2. Check your network connection
3. Try from a different network

## Session Issues

### Session File Location

Sessions are stored at: `~/.mm/session.json`

### Corrupt Session File

**Symptoms:** Unexpected errors, partial logins

**Solution:**
```bash
# Remove session file
rm ~/.mm/session.json

# Re-authenticate
monarch-money auth login
```

### Permission Errors

**Cause:** Session directory has wrong permissions.

**Solution:**
```bash
chmod 700 ~/.mm
chmod 600 ~/.mm/session.json
```

## CLI Problems

### "command not found: monarch-money"

**Cause:** CLI not installed or not in PATH.

**Solutions:**

1. **Install globally:**
   ```bash
   npm install -g monarch-money
   ```

2. **Or use npx:**
   ```bash
   npx monarch-money doctor
   ```

3. **Check npm bin directory is in PATH:**
   ```bash
   npm bin -g
   # Add this path to your shell profile
   ```

### Node.js Version Error

**Cause:** Node.js < 18

**Solution:**
```bash
# Check version
node --version

# Install Node 18+ using nvm
nvm install 18
nvm use 18
```

### JSON Output Not Parsing

**Cause:** Error messages mixing with JSON output.

**Solution:** Errors go to stderr, JSON to stdout. Capture separately:

```bash
monarch-money tx list --limit 5 2>/dev/null | jq .
```

## Diagnostic Commands

### Full System Check

```bash
monarch-money doctor
```

### Check Environment Variables

```bash
echo "Email: ${MONARCH_EMAIL:-(not set)}"
echo "Password: ${MONARCH_PASSWORD:+set}"
echo "MFA: ${MONARCH_MFA_SECRET:+set}"
```

### Test API Connectivity

```bash
curl -s -o /dev/null -w "%{http_code}" https://api.monarch.com/graphql
# Should return 401 (requires auth) not 5xx (server error)
```

### Verbose Logging

Set debug environment variable for more output:

```bash
DEBUG=monarch* monarch-money tx list --limit 1
```
