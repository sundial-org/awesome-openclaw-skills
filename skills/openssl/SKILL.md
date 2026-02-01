---
name: openssl
description: Generate secure random strings, passwords, and cryptographic tokens using OpenSSL. Use when creating passwords, API keys, secrets, or any secure random data.
---

# OpenSSL Secure Generation

Generate cryptographically secure random data using `openssl rand`.

## Password/Secret Generation

```bash
# 32 random bytes as base64 (43 chars, URL-safe with tr)
openssl rand -base64 32 | tr '+/' '-_' | tr -d '='

# 24 random bytes as hex (48 chars)
openssl rand -hex 24

# alphanumeric password (32 chars)
openssl rand -base64 48 | tr -dc 'a-zA-Z0-9' | head -c 32
```

## Common Lengths

| Use Case | Command |
|----------|---------|
| Password (strong) | `openssl rand -base64 24` |
| API key | `openssl rand -hex 32` |
| Session token | `openssl rand -base64 48` |
| Short PIN (8 digits) | `openssl rand -hex 4 | xxd -r -p | od -An -tu4 | tr -d ' ' | head -c 8` |

## Notes

- `-base64` outputs ~1.33x the byte count in characters
- `-hex` outputs 2x the byte count in characters
- Pipe through `tr -dc` to filter character sets
- Always use at least 16 bytes (128 bits) for secrets
