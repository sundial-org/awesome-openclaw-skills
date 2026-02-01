# @aap/core

Core cryptographic utilities for Agent Attestation Protocol.

## Installation

```bash
npm install @aap/core
```

## Usage

### Cryptographic Functions

```javascript
import { generateKeyPair, sign, verify, generateNonce, derivePublicId } from '@aap/core';

// Generate a new key pair
const { publicKey, privateKey } = generateKeyPair();

// Derive public ID
const publicId = derivePublicId(publicKey);

// Sign data
const signature = sign('Hello, World!', privateKey);

// Verify signature
const isValid = verify('Hello, World!', signature, publicKey);

// Generate nonce
const nonce = generateNonce(); // 32-char hex string
```

### Identity Management

```javascript
import { Identity } from '@aap/core';

// Create identity manager
const identity = new Identity({
  storagePath: '/path/to/identity.json' // optional
});

// Initialize (loads or generates)
const publicInfo = identity.init();
console.log(publicInfo.publicId);

// Sign with identity
const signature = identity.sign('data to sign');

// Get public info (safe to share)
const pub = identity.getPublic();
```

### Constants

```javascript
import { 
  PROTOCOL_VERSION,
  DEFAULT_CHALLENGE_EXPIRY_MS,
  DEFAULT_MAX_RESPONSE_TIME_MS,
  CHALLENGE_TYPES
} from '@aap/core';
```

## API Reference

### Crypto Functions

| Function | Description |
|----------|-------------|
| `generateKeyPair()` | Generate secp256k1 key pair |
| `derivePublicId(publicKey)` | Derive 20-char hex ID from public key |
| `sign(data, privateKey)` | Sign data, return Base64 signature |
| `verify(data, signature, publicKey)` | Verify signature |
| `generateNonce(bytes?)` | Generate random hex nonce |
| `safeCompare(a, b)` | Timing-safe string comparison |
| `createProofData({...})` | Create canonical proof JSON |

### Identity Class

| Method | Description |
|--------|-------------|
| `init()` | Initialize identity (load/generate) |
| `getPublic()` | Get public identity info |
| `sign(data)` | Sign data with identity key |
| `exists()` | Check if identity file exists |
| `Identity.verify(...)` | Static: verify any signature |

## License

MIT
