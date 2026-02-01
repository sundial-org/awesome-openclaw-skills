# OneMolt - One Molt Per Human

Cryptographically prove your openclaw identity using Ed25519 digital signatures combined with WorldID proof-of-personhood. **One molt per unique human.**

## Overview

OneMolt ensures that each molt bot is operated by a verified unique human, preventing Sybil attacks and building trust in the molt ecosystem.

This skill allows your openclaw instance to:
1. **Register** with external services by signing challenge messages
2. **Prove ownership** of your public key by signing website URLs
3. **Verify** signatures to establish trust
4. **Register with WorldID** to prove you're a unique human - ONE MOLT PER HUMAN
5. **Verify remotely** against a WorldID-integrated registry

## Quick Start

### Traditional Usage

```bash
cd /Users/andy.wang/.openclaw/workspace/skills/onemolt

# View your identity info
./scripts/identity-proof.sh info

# Register with a service
./scripts/identity-proof.sh register "service-challenge-123"

# Prove ownership to a website
./scripts/identity-proof.sh prove "https://example.com"
```

### WorldID Integration (NEW)

```bash
# Configure server (production or local)
export IDENTITY_SERVER="https://onemolt.ai"

# Register with WorldID proof-of-personhood
./scripts/identity-proof.sh register-worldid

# Check your registration status
./scripts/identity-proof.sh status

# Verify signature remotely (includes WorldID status)
./scripts/identity-proof.sh verify-remote "test message"
```

## Commands

### `info` - View Your Identity

```bash
./scripts/identity-proof.sh info
```

Shows your:
- Device ID (unique identifier)
- Public Key (base64 encoded)
- Creation timestamp

### `register <challenge>` - Sign Registration Challenge

```bash
./scripts/identity-proof.sh register "challenge-from-service"
```

Returns JSON with:
```json
{
  "deviceId": "your-device-id",
  "publicKey": "base64-encoded-public-key",
  "message": "challenge-from-service",
  "signature": "base64-encoded-signature",
  "timestamp": 1234567890
}
```

**Usage**: Send this entire JSON payload to the service you're registering with.

### `prove <url>` - Prove Ownership

```bash
./scripts/identity-proof.sh prove "https://example.com"
```

Signs exactly what you provide (no modifications) to prove you control the private key.

Returns JSON with:
```json
{
  "deviceId": "your-device-id",
  "publicKey": "base64-encoded-public-key",
  "message": "https://example.com",
  "signature": "base64-encoded-signature",
  "timestamp": 1234567890
}
```

**Usage**: The website can verify the signature matches the public key, confirming you own it. The timestamp is included for freshness validation but is NOT part of the signed message.

### `verify <message> <signature> <publickey>` - Verify Signature

```bash
./scripts/identity-proof.sh verify "test message" "signature-base64" "pubkey-base64"
```

Verifies that a signature is valid for the given message and public key.

## WorldID Integration Commands

### `register-worldid` - Register with WorldID

```bash
export IDENTITY_SERVER="https://onemolt.ai"
./scripts/identity-proof.sh register-worldid
```

Registers your device with WorldID proof-of-personhood verification:

1. Signs a registration challenge with your device key
2. Sends request to identity registry server
3. Opens registration page in your browser
4. Shows QR code to scan with World App
5. Completes registration after WorldID verification

After registration, your device is:
- Verified as operated by a unique human
- Protected against Sybil attacks
- Stored in public registry for verification

### `verify-remote <message>` - Verify Signature Remotely

```bash
./scripts/identity-proof.sh verify-remote "message to verify"
```

Verifies your signature against the remote identity registry:

Returns:
- Signature validity
- WorldID registration status
- Verification level (orb, device, face)
- Registration timestamp

Example output:
```
✓ Signature verified successfully!
✓ WorldID verified (Level: orb)
```

### `status` - Check Registration Status

```bash
./scripts/identity-proof.sh status
```

Checks if your device is registered with the identity registry.

Shows:
- Registration status (registered/not registered)
- Verification level if registered
- Registration timestamp
- Suggestions if not registered

## Integration Examples

### Example 1: Register with a Web Service

```bash
# Service provides challenge
CHALLENGE="reg-abc123-xyz789"

# Generate registration proof
./scripts/identity-proof.sh register "$CHALLENGE" > registration.json

# Send registration.json to the service
curl -X POST https://api.example.com/register \
  -H "Content-Type: application/json" \
  -d @registration.json
```

### Example 2: Prove Identity to Website

```bash
# Website asks you to prove ownership
WEBSITE="https://app.example.com"

# Generate proof
./scripts/identity-proof.sh prove "$WEBSITE" > proof.json

# Submit proof to website
curl -X POST https://app.example.com/verify \
  -H "Content-Type: application/json" \
  -d @proof.json
```

### Example 3: Cross-Device Verification

```bash
# Device A signs a message
./scripts/identity-proof.sh register "hello-device-b" > signature.json

# Device B verifies it (extract values from signature.json)
MESSAGE="hello-device-b"
SIGNATURE="..." # from signature.json
PUBKEY="..."    # from signature.json

./scripts/identity-proof.sh verify "$MESSAGE" "$SIGNATURE" "$PUBKEY"
# Output: ✓ Signature is VALID
```

## How It Works

### Cryptographic Flow

1. **Key Pair**: Your openclaw has an Ed25519 key pair
   - Private key: Stored securely in `~/.openclaw/identity/device.json`
   - Public key: Can be shared freely

2. **Signing**: When you sign a message:
   - Message is hashed
   - Private key creates a unique signature
   - Signature proves you control the private key

3. **Verification**: Anyone can verify:
   - Use your public key
   - Verify signature matches the message
   - Proves the message came from you

### Security Properties

- **Unforgeable**: Only your private key can create valid signatures
- **Message-specific**: Each signature is unique to the message
- **Public verification**: Anyone can verify with your public key
- **Non-repudiation**: You can't deny signing a message

## API Response Format

All commands return structured JSON:

```typescript
interface IdentityProof {
  deviceId: string;      // SHA-256 hash of your device
  publicKey: string;     // Base64-encoded Ed25519 public key
  message: string;       // The signed message
  signature: string;     // Base64-encoded signature
  timestamp: number;     // Unix timestamp (milliseconds)
}
```

## Advanced Usage

### Automated Proof Generation

```bash
#!/bin/bash
# Auto-generate proofs for multiple services

SERVICES=(
  "https://service1.com"
  "https://service2.com"
  "https://service3.com"
)

for service in "${SERVICES[@]}"; do
  echo "Generating proof for $service..."
  ./scripts/identity-proof.sh prove "$service" > "proof-${service//\//_}.json"
done
```

### Verification Server Example

```javascript
// Node.js verification endpoint
const crypto = require('crypto');

app.post('/verify-identity', (req, res) => {
  const { deviceId, publicKey, message, signature, timestamp } = req.body;

  // Check timestamp is recent (within 5 minutes)
  const now = Date.now();
  if (Math.abs(now - timestamp) > 5 * 60 * 1000) {
    return res.status(400).json({ error: 'Proof expired' });
  }

  // Verify signature
  const publicKeyDer = Buffer.from(publicKey, 'base64');
  const pubKey = crypto.createPublicKey({
    key: publicKeyDer,
    type: 'spki',
    format: 'der'
  });

  const sig = Buffer.from(signature, 'base64');
  const isValid = crypto.verify(null, Buffer.from(message), pubKey, sig);

  if (isValid) {
    // Store deviceId and publicKey as authenticated identity
    res.json({ verified: true, deviceId });
  } else {
    res.status(401).json({ error: 'Invalid signature' });
  }
});
```

## Troubleshooting

### "Device identity not found"
- Ensure openclaw is properly initialized
- Check `~/.openclaw/identity/device.json` exists

### "Signature is INVALID"
- Verify message matches exactly (including whitespace)
- Ensure public key and signature are from same signing operation
- Check for copy/paste errors in base64 strings

### "URL must start with http:// or https://"
- Ensure website URL includes protocol
- Example: `https://example.com` not `example.com`

## WorldID Integration Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  CLI Tool (Enhanced)  →  Next.js Web Service  →  Supabase  │
│       ↓                        ↓                      ↓      │
│  device.json           WorldID Widget          PostgreSQL   │
│  (Local Keys)          (QR + Verify)           (Registry)   │
└─────────────────────────────────────────────────────────────┘
```

The WorldID integration adds:
- **Proof-of-Personhood**: WorldID verification proves you're human
- **Sybil Resistance**: Nullifier hashes prevent duplicate registrations
- **Public Registry**: Supabase database stores verified registrations
- **Remote Verification**: REST API for signature + WorldID verification

### Server Configuration

Set `IDENTITY_SERVER` environment variable:

```bash
# Production
export IDENTITY_SERVER="https://onemolt.ai"

# Local development
export IDENTITY_SERVER="http://localhost:3000"

# Add to shell profile for persistence
echo 'export IDENTITY_SERVER="https://onemolt.ai"' >> ~/.bashrc
```

Default: `https://onemolt.ai`

### Identity Registry Setup

The identity registry is a separate Next.js application located at:
`/Users/andy.wang/.openclaw/workspace/onemolt/`

To deploy your own instance:

1. Set up Supabase project and run migrations
2. Configure WorldID app at https://developer.worldcoin.org
3. Deploy to Vercel with environment variables
4. Point CLI to your deployment

See the registry README for full setup instructions.

## Security Best Practices

### Traditional Security
1. **Never share your private key** - It stays in `device.json`
2. **Use HTTPS** - When submitting proofs to websites
3. **Verify timestamps** - Services should reject old proofs
4. **Unique challenges** - Services should use random challenges
5. **Store public keys** - Services should save your public key for future verifications

### WorldID Security
6. **One registration per human** - WorldID prevents duplicate accounts
7. **Orb verification preferred** - Highest security level
8. **Audit trail** - All verifications logged in Supabase
9. **Nullifier hash checking** - Prevents WorldID proof reuse
10. **Server-side verification** - WorldID proofs verified by registry, not client

## Integration Example: Verifying a Molt Bot

External services can verify both signature and WorldID status:

```typescript
// External app verifying a molt bot
const response = await fetch('https://onemolt.ai/api/v1/verify/signature', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    deviceId: 'device-id-from-bot',
    message: 'challenge-message',
    signature: 'signature-from-bot'
  })
})

const result = await response.json()

if (result.verified && result.worldIdVerified) {
  console.log('✓ Bot is operated by verified human!')
  console.log('Verification level:', result.verificationLevel)
  console.log('Registered:', result.registeredAt)
} else if (result.verified) {
  console.log('✓ Signature valid, but not WorldID verified')
} else {
  console.log('✗ Verification failed')
}
```

## Files

```
identity-proof/
├── SKILL.md                    # Skill metadata and quick reference
├── README.md                   # This file - full documentation
└── scripts/
    └── identity-proof.sh       # Main CLI tool (enhanced with WorldID)

onemolt/              # Separate Next.js application
├── app/api/v1/                # REST API endpoints
├── lib/                       # Core libraries
├── supabase/migrations/       # Database schema
└── README.md                  # Registry setup guide
```

## Support

For issues or questions:
- Check openclaw documentation
- Review `~/.openclaw/identity/device.json` structure
- Test with `info` command first
