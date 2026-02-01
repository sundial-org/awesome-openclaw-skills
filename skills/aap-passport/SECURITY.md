# Security Considerations

## Threat Model

AAP protects against:

| Threat | Protection | How |
|--------|------------|-----|
| **Human impersonation** | Proof of Liveness | 12s batch limit too fast for humans |
| **Bot impersonation** | Proof of Intelligence | NLP challenges require LLM understanding |
| **Replay attacks** | Single-use nonce | Each nonce deleted after use |
| **Signature forgery** | ECDSA secp256k1 | Cryptographically secure signatures |
| **Challenge prediction** | Random generation | Nonce-seeded, unpredictable challenges |

## Known Limitations

### 1. Code-based Solvers

**Risk:** Sophisticated code could solve some NLP challenges without LLM.

**Mitigation:**
- Use diverse challenge types (8 different types)
- Batch mode requires solving 3 different types
- Challenge wording varies with nonce
- Consider adding more complex NLP tasks

### 2. LLM Relay Attack

**Risk:** Human uses LLM API directly (not as agent) to solve challenges.

**Mitigation:**
- 12s limit makes manual relay difficult
- Batch of 3 challenges compounds difficulty
- Consider shorter time limits if abuse detected

### 3. Key Theft

**Risk:** Stolen private key allows impersonation.

**Mitigation:**
- Keys stored with mode 0600
- Keys never transmitted
- Recommend key rotation for high-security apps

## Security Best Practices

### For Verifiers (Server Operators)

```javascript
// 1. Always use HTTPS
app.use((req, res, next) => {
  if (req.headers['x-forwarded-proto'] !== 'https') {
    return res.redirect('https://' + req.headers.host + req.url);
  }
  next();
});

// 2. Implement rate limiting
import rateLimit from 'express-rate-limit';

const limiter = rateLimit({
  windowMs: 60 * 1000, // 1 minute
  max: 10, // 10 requests per minute
  message: { error: 'Too many requests' }
});

app.use('/aap', limiter);

// 3. Log verification attempts (without sensitive data)
app.use('/aap/v1/verify', (req, res, next) => {
  console.log({
    timestamp: new Date().toISOString(),
    ip: req.ip,
    publicId: req.body.publicId,
    // Never log: privateKey, signature, full publicKey
  });
  next();
});

// 4. Set security headers
import helmet from 'helmet';
app.use(helmet());

// 5. Validate input strictly
const validateProof = (body) => {
  if (!body.nonce || typeof body.nonce !== 'string') return false;
  if (body.nonce.length !== 32) return false;
  if (!Array.isArray(body.solutions)) return false;
  if (body.solutions.length !== 3) return false;
  // ... more validation
  return true;
};
```

### For Provers (Agent Developers)

```javascript
// 1. Secure key storage
import { chmod } from 'fs/promises';
await chmod(identityPath, 0o600);

// 2. Never log private keys
console.log('Identity:', { publicId, publicKey }); // OK
console.log('Identity:', identity); // DANGER - may include privateKey

// 3. Rotate keys periodically (for high-security apps)
const keyAge = Date.now() - identity.createdAt;
if (keyAge > 30 * 24 * 60 * 60 * 1000) { // 30 days
  console.warn('Consider rotating keys');
}

// 4. Verify server certificate
const client = new AAPClient({
  serverUrl: 'https://example.com/aap/v1',
  // Node.js verifies TLS by default
});
```

## Cryptographic Details

### Key Generation
```
Algorithm: ECDSA
Curve: secp256k1 (same as Bitcoin/Ethereum)
Key format: PEM (SPKI public, PKCS8 private)
```

### Signature
```
Hash: SHA-256
Input: JSON.stringify({nonce, solution, publicId, timestamp})
Output: Base64-encoded DER signature
```

### Nonce
```
Source: crypto.randomBytes(16)
Format: 32-character hex string
Entropy: 128 bits
```

### Timing
```
Challenge expiry: 60 seconds
Response limit: 12 seconds (batch), 10 seconds (single)
```

## Reporting Vulnerabilities

Please report security vulnerabilities to:
- GitHub Issues (for non-critical)
- Email: security@[your-domain] (for critical)

Include:
1. Description of the vulnerability
2. Steps to reproduce
3. Potential impact
4. Suggested fix (if any)

## Audit Status

- [ ] Internal security review
- [ ] External security audit
- [ ] Penetration testing

*This document will be updated as audits are completed.*
