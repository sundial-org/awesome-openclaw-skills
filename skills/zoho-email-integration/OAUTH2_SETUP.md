# OAuth2 Setup Guide for Zoho Mail

This guide will help you set up OAuth2 authentication for the Zoho Email skill. OAuth2 is more secure and recommended over app passwords.

## Why OAuth2?

✅ **More secure** - No need to store passwords  
✅ **Better access control** - Granular permissions  
✅ **Auto-refresh** - Tokens refresh automatically  
✅ **Revocable** - Easy to revoke access without changing passwords  
✅ **Zoho-recommended** - Official authentication method  

## Prerequisites

- A Zoho Mail account
- Access to Zoho API Console (https://api-console.zoho.com/)
- Python 3.6+ (standard library only - no external dependencies!)

## Step 1: Create OAuth2 Credentials

1. **Go to Zoho API Console:**  
   Visit: https://api-console.zoho.com/

2. **Click "Add Client"**

3. **Select "Server-based Applications"**

4. **Fill in the details:**
   ```
   Client Name:      Clawdbot Zoho Mail
   Homepage URL:     http://localhost
   Authorized Redirect URIs:  http://localhost:8080/callback
   ```
   
   > 💡 **Note:** If port 8080 is already in use, the setup script will automatically use the next available port (8081, 8082, etc.)

5. **Click "Create"**

6. **Copy your credentials:**
   - **Client ID** (e.g., `1000.XXXXXXXXXXXXXXXXXXXXXX`)
   - **Client Secret** (e.g., `xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`)
   
   ⚠️ **Important:** Keep these credentials secure! Never commit them to version control.

## Step 2: Run OAuth2 Setup Script

```bash
cd /path/to/zoho-email-integration
python3 scripts/oauth-setup.py
```

The script will:
1. Prompt for your Client ID and Client Secret
2. Ask where to store tokens (default: `~/.zoho-mail-tokens.json`)
3. Open your browser for authorization
4. Wait for you to log in and authorize the application
5. Save tokens securely (permissions: 600)

### Interactive Setup Example

```
==========================================================================
Zoho Mail OAuth2 Setup
==========================================================================

First, you need to create OAuth2 credentials in Zoho:
1. Go to: https://api-console.zoho.com/
2. Click 'Add Client' → 'Server-based Applications'
3. Enter:
   - Client Name: Clawdbot Zoho Mail
   - Homepage URL: http://localhost
   - Redirect URI: http://localhost:8080/callback
4. Copy the Client ID and Client Secret

Enter your Client ID: 1000.XXXXXXXXXXXXXXXXXXXXXX
Enter your Client Secret: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Token storage path [/root/.zoho-mail-tokens.json]: 

----------------------------------------------------------------------
Starting OAuth2 authorization flow...
----------------------------------------------------------------------

🌐 Opening browser for authorization...
If browser doesn't open, visit this URL:

https://accounts.zoho.com/oauth/v2/auth?scope=...

✓ Listening for callback on http://localhost:8080
Please log in and authorize the application in your browser...

✓ Authorization code received
Exchanging authorization code for tokens...
✓ Tokens received successfully

✓ Tokens saved to: /root/.zoho-mail-tokens.json
✓ File permissions: 600 (owner read/write only)

==========================================================================
✓ OAuth2 Setup Complete!
==========================================================================

Next steps:
1. Your tokens are stored in: /root/.zoho-mail-tokens.json
2. Test the connection:
   python3 scripts/zoho-email.py oauth-status
3. Use OAuth2 in your scripts:
   python3 scripts/zoho-email.py unread --auth oauth2

⚠️  Security notes:
- Keep your token file secure (permissions: 600)
- Never commit tokens to version control
- Tokens will auto-refresh when expired
```

## Step 3: Verify Setup

Check token status:

```bash
python3 scripts/zoho-email.py oauth-status
```

Expected output:
```json
{
  "auth_method": "oauth2",
  "status": "valid",
  "token_file": "/root/.zoho-mail-tokens.json",
  "email": "your-email@zohomail.com",
  "created_at": 1706534400,
  "expires_at": 1706538000,
  "expires_in_seconds": 3600
}

✓ Token is valid (expires in 3600s)
```

## Step 4: Use OAuth2

OAuth2 is now set up! The skill will automatically use OAuth2 if the token file exists.

**Auto-detection** (recommended):
```bash
python3 scripts/zoho-email.py unread
```

**Explicit OAuth2:**
```bash
python3 scripts/zoho-email.py unread --auth oauth2
```

**Custom token path:**
```bash
python3 scripts/zoho-email.py unread --auth oauth2 --token-file /path/to/tokens.json
```

## OAuth2 Commands

### Check Token Status

```bash
python3 scripts/zoho-email.py oauth-status
```

Shows token validity, expiration time, and authentication method.

### Refresh Tokens

Tokens auto-refresh when needed, but you can manually refresh:

```bash
python3 scripts/zoho-email.py oauth-login
```

Or using the setup script:

```bash
python3 scripts/oauth-setup.py refresh
```

### Revoke Tokens

To revoke OAuth2 access (deletes local token file):

```bash
python3 scripts/zoho-email.py oauth-revoke
```

To fully revoke access from Zoho's side:
1. Go to: https://accounts.zoho.com/home#security/connectedapps
2. Find "Clawdbot Zoho Mail"
3. Click "Remove"

## Token Storage

### Location

Default: `~/.zoho-mail-tokens.json`

Custom:
```bash
python3 scripts/oauth-setup.py  # Will prompt for path
```

### Security

- **Permissions:** 600 (owner read/write only)
- **Contents:** Client ID, Client Secret, Access Token, Refresh Token
- **Encryption:** Not encrypted (store in secure location)
- **Version control:** Add to `.gitignore`

### Token File Structure

```json
{
  "client_id": "1000.XXXXX",
  "client_secret": "xxxxx",
  "access_token": "1000.xxxxx.xxxxx",
  "refresh_token": "1000.xxxxx.xxxxx",
  "expires_in": 3600,
  "token_type": "Bearer",
  "created_at": 1706534400
}
```

## Troubleshooting

### "Port already in use"

The setup script automatically finds an available port. If you see this error, try:
```bash
# Check what's using port 8080
lsof -i :8080

# Kill the process or use a different port manually by editing oauth-setup.py
```

### "Authorization failed"

**Common causes:**
- Incorrect Client ID or Client Secret
- Redirect URI mismatch (must be exactly `http://localhost:8080/callback`)
- Zoho account issues

**Solutions:**
1. Verify credentials in Zoho API Console
2. Check redirect URI matches exactly
3. Try creating a new OAuth client

### "Token expired" or "AUTHENTICATE failed"

**Automatic fix:**
```bash
python3 scripts/zoho-email.py oauth-login
```

**Manual fix:**
```bash
python3 scripts/oauth-setup.py refresh
```

**If refresh fails:**
```bash
# Delete old tokens and set up again
rm ~/.zoho-mail-tokens.json
python3 scripts/oauth-setup.py
```

### "Token file not found"

You haven't set up OAuth2 yet:
```bash
python3 scripts/oauth-setup.py
```

### Browser doesn't open

Copy the authorization URL from the terminal output and paste it in your browser manually.

### "Invalid scope" error

This means the Zoho Mail API scopes have changed. Update `ZOHO_SCOPES` in `scripts/oauth-setup.py`:

```python
ZOHO_SCOPES = [
    'ZohoMail.messages.READ',
    'ZohoMail.messages.CREATE',
    'ZohoMail.messages.UPDATE',
    'ZohoMail.folders.READ',
    'ZohoMail.accounts.READ'
]
```

## Security Best Practices

### DO:
✅ Store tokens in your home directory (`~/.zoho-mail-tokens.json`)  
✅ Use file permissions 600 (owner read/write only)  
✅ Add token files to `.gitignore`  
✅ Regularly review authorized apps in Zoho settings  
✅ Use environment variables for `ZOHO_EMAIL`  
✅ Revoke old tokens when no longer needed  

### DON'T:
❌ Commit token files to version control  
❌ Share token files or credentials  
❌ Use world-readable permissions  
❌ Store tokens in web-accessible directories  
❌ Hardcode Client ID/Secret in scripts  

### Additional Security

#### Encrypt Token File (Optional)

```bash
# Encrypt token file with GPG
gpg -c ~/.zoho-mail-tokens.json
rm ~/.zoho-mail-tokens.json

# Decrypt when needed
gpg -d ~/.zoho-mail-tokens.json.gpg > ~/.zoho-mail-tokens.json
# Use the skill
python3 scripts/zoho-email.py unread
# Remove decrypted file
shred -u ~/.zoho-mail-tokens.json
```

#### Use Separate OAuth Client per Environment

Create different OAuth clients for:
- Development
- Production
- Testing

This allows you to revoke specific environments without affecting others.

## Backward Compatibility

OAuth2 is fully backward compatible with app passwords:

**App password** (still works):
```bash
export ZOHO_EMAIL="your-email@zohomail.com"
export ZOHO_PASSWORD="your-app-password"
python3 scripts/zoho-email.py unread
```

**OAuth2** (recommended):
```bash
export ZOHO_EMAIL="your-email@zohomail.com"  # Still needed
python3 scripts/zoho-email.py unread --auth oauth2
```

**Auto-detect** (uses OAuth2 if available):
```bash
export ZOHO_EMAIL="your-email@zohomail.com"
python3 scripts/zoho-email.py unread
```

## Migration from App Passwords

Already using app passwords? Migrate to OAuth2:

1. **Set up OAuth2** (keeps app password working):
   ```bash
   python3 scripts/oauth-setup.py
   ```

2. **Test OAuth2**:
   ```bash
   python3 scripts/zoho-email.py unread --auth oauth2
   ```

3. **Switch to OAuth2** (auto-detect):
   ```bash
   # No changes needed! Just use the skill as normal
   python3 scripts/zoho-email.py unread
   ```

4. **Optional: Remove app password**:
   ```bash
   unset ZOHO_PASSWORD
   ```

## Advanced Configuration

### Multiple Zoho Accounts

Use separate token files:

```bash
# Account 1
python3 scripts/oauth-setup.py
# Save to: ~/.zoho-mail-tokens-account1.json

# Account 2
python3 scripts/oauth-setup.py
# Save to: ~/.zoho-mail-tokens-account2.json

# Use specific account
python3 scripts/zoho-email.py unread --token-file ~/.zoho-mail-tokens-account1.json
python3 scripts/zoho-email.py unread --token-file ~/.zoho-mail-tokens-account2.json
```

### CI/CD Integration

For automated environments:

```bash
# Option 1: Use app password in CI/CD
export ZOHO_EMAIL="ci-bot@company.com"
export ZOHO_PASSWORD="app-password"

# Option 2: Store token file as secret
# Upload ~/.zoho-mail-tokens.json as CI/CD secret
# Restore in build:
echo "$ZOHO_TOKENS_JSON" > ~/.zoho-mail-tokens.json
chmod 600 ~/.zoho-mail-tokens.json
```

## Additional Resources

- **Zoho API Console:** https://api-console.zoho.com/
- **Zoho Mail API Docs:** https://www.zoho.com/mail/help/api/
- **OAuth2 RFC:** https://tools.ietf.org/html/rfc6749
- **Zoho Account Security:** https://accounts.zoho.com/home#security

## Need Help?

- Check [Troubleshooting](#troubleshooting) section
- Run with `--verbose` flag for debug output:
  ```bash
  python3 scripts/zoho-email.py oauth-status --verbose
  ```
- Check token file permissions: `ls -l ~/.zoho-mail-tokens.json`
- Verify ZOHO_EMAIL is set: `echo $ZOHO_EMAIL`

---

**Last updated:** 2025-01-29  
**Version:** 1.2.0  
**Status:** Production Ready ✅
