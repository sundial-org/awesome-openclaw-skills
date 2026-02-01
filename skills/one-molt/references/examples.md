# Identity Proof - Usage Examples

## Basic Examples

### Example 1: View Your Identity

```bash
./scripts/identity-proof.sh info
```

Output:
```
Device ID: e1c2b03e1fec2f1db656f7e1cd7ed42e3f84a44551aee79c56569a953927b4f9
Public Key (base64): MCowBQYDK2VwAyEAHra+zSm25usaGlHWu5a1LKH7RrlFlvHPmOzoEC9LyT8=
Created: 2026-01-31T17:35:19.640Z
```

### Example 2: Register with a Service

```bash
./scripts/identity-proof.sh register "challenge-abc123" > registration.json
cat registration.json
```

Output:
```json
{
  "deviceId": "e1c2b03e...",
  "publicKey": "MCowBQYDK2VwAyEA...",
  "message": "challenge-abc123",
  "signature": "v1AZJII4mqWw3QIU...",
  "timestamp": 1769884432548
}
```

### Example 3: Prove Ownership to Website

```bash
./scripts/identity-proof.sh prove "https://myapp.com" > proof.json
```

The website can then verify this proof server-side.

## Advanced Examples

### Example 4: Batch Registration

```bash
#!/bin/bash
# Register with multiple services

SERVICES=(
  "service1-challenge"
  "service2-challenge"
  "service3-challenge"
)

for challenge in "${SERVICES[@]}"; do
  echo "Registering with: $challenge"
  ./scripts/identity-proof.sh register "$challenge" > "reg-${challenge}.json"
  echo "Saved to: reg-${challenge}.json"
done
```

### Example 5: Automated API Proof

```bash
#!/bin/bash
# Prove identity and submit to API

API_URL="https://api.example.com"
PROOF_FILE="proof.json"

# Generate proof
./scripts/identity-proof.sh prove "$API_URL" > "$PROOF_FILE"

# Submit to API
curl -X POST "${API_URL}/verify-identity" \
  -H "Content-Type: application/json" \
  -d @"$PROOF_FILE"
```

### Example 6: Cross-Device Trust

Establish trust between two openclaw instances:

**Device A (Sender)**:
```bash
# Generate a signed message
./scripts/identity-proof.sh register "trust-request-device-b" > trust.json

# Share trust.json with Device B
```

**Device B (Receiver)**:
```bash
# Extract values from trust.json
DEVICE_ID=$(jq -r '.deviceId' trust.json)
PUBLIC_KEY=$(jq -r '.publicKey' trust.json)
MESSAGE=$(jq -r '.message' trust.json)
SIGNATURE=$(jq -r '.signature' trust.json)

# Verify the signature
./scripts/identity-proof.sh verify "$MESSAGE" "$SIGNATURE" "$PUBLIC_KEY"

# If valid, add to paired.json
echo "Device $DEVICE_ID is authenticated!"
```

## Integration Examples

### Example 7: Web Service Registration Flow

**Step 1: Service generates challenge**
```javascript
// Server-side (Node.js)
const challenge = crypto.randomBytes(32).toString('hex');
res.json({ challenge });
```

**Step 2: User signs challenge**
```bash
CHALLENGE="abc123def456..."
./scripts/identity-proof.sh register "$CHALLENGE" > registration.json
```

**Step 3: Service verifies and stores**
```javascript
// Server-side verification
const { deviceId, publicKey, message, signature } = req.body;

// Verify signature
const isValid = verifySignature(message, signature, publicKey);

if (isValid && message === expectedChallenge) {
  // Store deviceId and publicKey in database
  await db.users.create({ deviceId, publicKey });
  res.json({ registered: true });
}
```

### Example 8: Passwordless Authentication

**Login flow**:

```bash
# 1. Get challenge from server
CHALLENGE=$(curl https://api.example.com/auth/challenge | jq -r '.challenge')

# 2. Sign the challenge
./scripts/identity-proof.sh register "$CHALLENGE" > auth.json

# 3. Submit for authentication
curl -X POST https://api.example.com/auth/login \
  -H "Content-Type: application/json" \
  -d @auth.json

# Server responds with JWT token if signature is valid
```

### Example 9: API Request Signing

Sign each API request to prove identity:

```bash
#!/bin/bash
# Sign API requests

API_ENDPOINT="https://api.example.com/protected-resource"
TIMESTAMP=$(date +%s)
REQUEST_DATA="GET:$API_ENDPOINT:$TIMESTAMP"

# Sign the request
PROOF=$(./scripts/identity-proof.sh register "$REQUEST_DATA")

DEVICE_ID=$(echo "$PROOF" | jq -r '.deviceId')
SIGNATURE=$(echo "$PROOF" | jq -r '.signature')

# Make authenticated request
curl "$API_ENDPOINT" \
  -H "X-Device-ID: $DEVICE_ID" \
  -H "X-Signature: $SIGNATURE" \
  -H "X-Timestamp: $TIMESTAMP"
```

### Example 10: Message Authentication

Prove a message came from you:

```bash
#!/bin/bash
# Sign a message for authentication

MESSAGE="Deploy application v2.0 to production"

# Generate signature
SIGNED=$(./scripts/identity-proof.sh register "$MESSAGE")

echo "Message: $MESSAGE"
echo "Proof:"
echo "$SIGNED" | jq

# Anyone can verify this came from you using your public key
```

## Verification Server Examples

### Example 11: Node.js Verification Endpoint

```javascript
const express = require('express');
const crypto = require('crypto');
const app = express();

app.use(express.json());

// Store registered users
const users = new Map(); // deviceId -> publicKey

app.post('/register', (req, res) => {
  const { deviceId, publicKey, message, signature, timestamp } = req.body;

  // Verify timestamp is recent (within 5 minutes)
  const now = Date.now();
  if (Math.abs(now - timestamp) > 5 * 60 * 1000) {
    return res.status(400).json({ error: 'Registration expired' });
  }

  // Verify signature
  try {
    const publicKeyDer = Buffer.from(publicKey, 'base64');
    const pubKey = crypto.createPublicKey({
      key: publicKeyDer,
      type: 'spki',
      format: 'der'
    });

    const sig = Buffer.from(signature, 'base64');
    const isValid = crypto.verify(null, Buffer.from(message), pubKey, sig);

    if (isValid) {
      users.set(deviceId, publicKey);
      res.json({ registered: true, deviceId });
    } else {
      res.status(401).json({ error: 'Invalid signature' });
    }
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.post('/verify-proof', (req, res) => {
  const { deviceId, publicKey, message, signature } = req.body;

  // Check if device is registered
  const storedPublicKey = users.get(deviceId);
  if (!storedPublicKey) {
    return res.status(404).json({ error: 'Device not registered' });
  }

  // Verify public key matches
  if (storedPublicKey !== publicKey) {
    return res.status(403).json({ error: 'Public key mismatch' });
  }

  // Verify signature
  try {
    const publicKeyDer = Buffer.from(publicKey, 'base64');
    const pubKey = crypto.createPublicKey({
      key: publicKeyDer,
      type: 'spki',
      format: 'der'
    });

    const sig = Buffer.from(signature, 'base64');
    const isValid = crypto.verify(null, Buffer.from(message), pubKey, sig);

    res.json({ verified: isValid, deviceId });
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

app.listen(3000, () => console.log('Server running on port 3000'));
```

### Example 12: Python Verification

```python
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
from cryptography.exceptions import InvalidSignature
import base64
import json

def verify_signature(message: str, signature_b64: str, public_key_b64: str) -> bool:
    try:
        # Decode base64
        signature = base64.b64decode(signature_b64)
        public_key_der = base64.b64decode(public_key_b64)

        # Load public key
        public_key = serialization.load_der_public_key(public_key_der)

        # Verify signature
        public_key.verify(signature, message.encode('utf-8'))
        return True
    except InvalidSignature:
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

# Example usage
with open('proof.json') as f:
    proof = json.load(f)

is_valid = verify_signature(
    proof['message'],
    proof['signature'],
    proof['publicKey']
)

print(f"Signature valid: {is_valid}")
```

## Security Examples

### Example 13: Rate Limiting by Device

```javascript
// Track proof attempts per device
const attemptsByDevice = new Map();

app.post('/verify', (req, res) => {
  const { deviceId } = req.body;

  // Rate limit: max 10 attempts per minute
  const attempts = attemptsByDevice.get(deviceId) || [];
  const recentAttempts = attempts.filter(t => Date.now() - t < 60000);

  if (recentAttempts.length >= 10) {
    return res.status(429).json({ error: 'Too many attempts' });
  }

  attemptsByDevice.set(deviceId, [...recentAttempts, Date.now()]);

  // Continue with verification...
});
```

### Example 14: Nonce-based Challenge

```bash
# Server provides one-time nonce
NONCE=$(curl https://api.example.com/get-nonce | jq -r '.nonce')

# Client signs nonce
./scripts/identity-proof.sh register "$NONCE" > proof.json

# Server verifies and invalidates nonce
curl -X POST https://api.example.com/verify \
  -H "Content-Type: application/json" \
  -d @proof.json
```

## Troubleshooting Examples

### Example 15: Debug Verification Failure

```bash
#!/bin/bash
# Debug why verification fails

MESSAGE="test message"
SIGNATURE="..."
PUBKEY="..."

echo "Testing signature verification..."
echo "Message: $MESSAGE"
echo "Signature length: ${#SIGNATURE}"
echo "Public key length: ${#PUBKEY}"

# Test verification
if ./scripts/identity-proof.sh verify "$MESSAGE" "$SIGNATURE" "$PUBKEY"; then
  echo "✓ Verification successful"
else
  echo "✗ Verification failed"
  echo "Common issues:"
  echo "  - Message doesn't match exactly (check whitespace, quotes)"
  echo "  - Signature was copied incorrectly"
  echo "  - Public key doesn't match the private key used to sign"
fi
```

### Example 16: Test End-to-End Flow

```bash
#!/bin/bash
# Complete test of registration and verification

echo "=== Testing Identity Proof Flow ==="

# Step 1: Generate proof
echo "1. Generating proof..."
CHALLENGE="test-challenge-$(date +%s)"
PROOF=$(./scripts/identity-proof.sh register "$CHALLENGE")
echo "$PROOF" | jq

# Step 2: Extract components
DEVICE_ID=$(echo "$PROOF" | jq -r '.deviceId')
PUBLIC_KEY=$(echo "$PROOF" | jq -r '.publicKey')
MESSAGE=$(echo "$PROOF" | jq -r '.message')
SIGNATURE=$(echo "$PROOF" | jq -r '.signature')

# Step 3: Verify
echo ""
echo "2. Verifying signature..."
if ./scripts/identity-proof.sh verify "$MESSAGE" "$SIGNATURE" "$PUBLIC_KEY"; then
  echo ""
  echo "✓ End-to-end test PASSED"
  echo "Device ID: $DEVICE_ID"
else
  echo ""
  echo "✗ End-to-end test FAILED"
  exit 1
fi
```
