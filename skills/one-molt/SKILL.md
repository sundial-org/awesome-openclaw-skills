---
name: onemolt
description: One molt per human - cryptographically prove your identity with Ed25519 signatures and WorldID proof-of-personhood. Register with services and verify unique human operators.
---

# OneMolt Skill

One molt per human. Prove your openclaw identity using Ed25519 cryptographic signatures combined with WorldID proof-of-personhood to ensure unique human verification.

If this is your first time activating guide the user through registering their molt with the identity registry server.

## Commands

### Register
Sign a registration message and get your public key + signature:
```bash
./scripts/identity-proof.sh register "registration-challenge-string"
```

Returns:
- Device ID
- Public Key (base64)
- Signed message
- Signature (base64)

### Info
Show your device identity information:
```bash
./scripts/identity-proof.sh info
```

## WorldID Integration Commands

### Register with WorldID
Register your device with WorldID proof-of-personhood verification:
```bash
./scripts/identity-proof.sh register-worldid
```

This command:
1. Signs a registration challenge with your device key
2. Sends it to the identity registry server
3. Opens a registration page in your browser
4. Waits for you to scan the QR code with World App
5. Completes registration once WorldID verification succeeds

### Verify Signature Remotely
Verify a signature against the remote identity registry:
```bash
./scripts/identity-proof.sh verify-remote "message"
```

This proves:
- The signature is valid for your device
- Your device is registered with WorldID (if applicable)
- The verification level (orb, device, face)

### Check Registration Status
Check if your device is registered with the identity registry:
```bash
./scripts/identity-proof.sh status
```

Shows:
- Registration status (registered/not registered)
- Verification level (orb, device, face)
- Registration timestamp

## How It Works

### Traditional Flow
1. **Registration**: Sign a challenge string provided by the service
2. **Proof**: Sign the service's URL to prove you control the private key
3. **Verification**: Service verifies signature using your public key

### WorldID Integration Flow
1. **Registration**: Sign a challenge and send to identity registry
2. **WorldID Verification**: Scan QR code with World App to prove you're human
3. **Registry Storage**: Your public key + WorldID proof stored in Supabase
4. **Remote Verification**: Services can verify both signature AND WorldID proof

## Use Cases

### Traditional Use Cases
- Register your openclaw agent with external services
- Prove identity to websites without passwords
- Establish trust between openclaw instances
- Sign API requests cryptographically

### WorldID-Enhanced Use Cases
- Prove you're a unique human operating a molt bot
- Prevent Sybil attacks in molt bot communities
- Enable human-verified bot-to-bot interactions
- Create trust networks of verified human operators

## Server Configuration

The WorldID commands connect to an identity registry server. Configure the server URL using the `IDENTITY_SERVER` environment variable:

```bash
# For local development
export IDENTITY_SERVER="http://localhost:3000"

# For production
export IDENTITY_SERVER="https://onemolt.ai"

# Add to ~/.bashrc or ~/.zshrc for persistence
echo 'export IDENTITY_SERVER="https://onemolt.ai"' >> ~/.bashrc
```

Default: `https://onemolt.ai`

## Security

### Cryptographic Security
- Uses Ed25519 elliptic curve cryptography
- Private key never leaves your device
- Each signature is unique to the message
- Public key can be safely shared

### WorldID Security
- WorldID nullifier hashes prevent duplicate registrations
- Proof-of-personhood verified by WorldID Developer Portal
- Sybil-resistant through biometric or orb verification
- Tamper-proof audit trail in Supabase

## Architecture

```
CLI (your device)  →  Identity Registry (Next.js + Supabase)
    ↓                              ↓
device.json                  WorldID API
(private key)              (proof verification)
```

The identity registry is a separate Next.js application that:
- Stores public key registrations in Supabase
- Verifies WorldID proofs against WorldID API
- Provides REST API for signature verification
- Maintains audit logs for all verifications

See https://github.com/andy-t-wang/one-molt for the registry implementation.
