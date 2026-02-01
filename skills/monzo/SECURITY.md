# Security Best Practices

## Choosing a Strong Password

Your `MONZO_KEYRING_PASSWORD` protects your banking credentials. Choose wisely:

- **Minimum 20 characters** recommended
- Use a **unique password** - don't reuse from other services
- Consider using a **password manager** to generate and store it
- Treat it like your banking password (because it is!)

## Multi-User Systems

⚠️ **Important Security Consideration**

This skill stores credentials in your home directory and uses environment variables. On multi-user systems, be aware:

- **Root users** can access your credentials and encryption password
- The password may be visible in **process listings** (`ps`, `/proc`)
- Credentials are loaded into **shell memory** during execution
- **Recommendation**: Only use on systems you fully control and trust

For maximum security, use this skill on:
- Your personal laptop/desktop
- A dedicated server where you're the only user
- A system with full-disk encryption

## Secure Deletion

If you need to remove this skill or change systems:

```bash
# Securely delete credentials (overwrites multiple times)
shred -u ~/.clawdbot/credentials/monzo.json

# Or if shred is not available:
rm -P ~/.clawdbot/credentials/monzo.json  # macOS
srm ~/.clawdbot/credentials/monzo.json    # If srm is installed

# Remove from Clawdbot config
# Edit ~/.clawdbot/clawdbot.json and remove the monzo entry
```

## Webhook Security

If you use the webhooks feature, protect your webhook endpoint:

- **Validate Monzo's signature** on incoming webhooks (see Monzo API docs)
- Use **HTTPS only** (enforced by this skill)
- Implement **rate limiting** on your webhook endpoint
- **Log and monitor** webhook calls for suspicious activity
- Consider using a **webhook secret** if Monzo supports it

## Debug Mode

For troubleshooting, you can enable debug output:

```bash
DEBUG=1 scripts/balance
```

This shows sanitized API responses. Even in debug mode, sensitive IDs are redacted.

## Regular Security Practices

- **Monitor your Monzo app** for API access notifications
- **Review connected apps** periodically in Monzo settings (Account → Settings → Privacy & Security)
- **Revoke access** immediately if you notice suspicious activity
- **Keep this skill updated** for security patches

## What's Protected

- ✅ Credentials encrypted at rest (AES-256-CBC, PBKDF2 100k iterations)
- ✅ OAuth 2.0 with automatic token refresh
- ✅ State parameter validation (CSRF protection)
- ✅ HTTPS-only API communication
- ✅ File permissions locked to owner-only (600)
- ✅ Cryptographically secure random IDs
- ✅ Error messages sanitize sensitive IDs

## Threat Model

This skill protects against:
- ✅ Credentials stolen from disk (encrypted)
- ✅ OAuth CSRF attacks (state validation)
- ✅ Accidental credential exposure (file permissions)
- ✅ Information leakage in logs (sanitized errors)

This skill does NOT protect against:
- ❌ Root/admin access to your system
- ❌ Keyloggers capturing your password
- ❌ Physical access to unlocked machine
- ❌ Malicious code running as your user

If your system is compromised at the OS level, assume your Monzo credentials are compromised too.

## Reporting Security Issues

If you find a security vulnerability in this skill, please report it responsibly:

1. **Do not** open a public GitHub issue
2. Contact the maintainer privately
3. Provide details: affected file, vulnerability type, potential impact
4. Allow reasonable time for a fix before public disclosure

## Encryption Details

For the security-minded:

- **Algorithm**: AES-256-CBC
- **Key Derivation**: PBKDF2 with 100,000 iterations
- **Salt**: Unique per encryption (via OpenSSL)
- **Random Generation**: `openssl rand` (cryptographically secure)

The credentials file at `~/.clawdbot/credentials/monzo.json` is binary-encrypted and unreadable without your password.
