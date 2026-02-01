# @aap/server

Server middleware for Agent Attestation Protocol verification.

## Installation

```bash
npm install @aap/server @aap/core
```

## Quick Start

### Express Integration

```javascript
import express from 'express';
import { createRouter } from '@aap/server';

const app = express();

// Add AAP verification endpoints at /aap/v1
app.use('/aap/v1', createRouter());

app.listen(3000, () => {
  console.log('AAP Verifier running on http://localhost:3000');
});
```

This adds three endpoints:
- `GET /aap/v1/health` - Health check
- `POST /aap/v1/challenge` - Request a challenge
- `POST /aap/v1/verify` - Submit proof for verification

### Custom Configuration

```javascript
import express from 'express';
import { aapMiddleware } from '@aap/server';

const app = express();
const router = express.Router();
router.use(express.json());

// Configure middleware
const middleware = aapMiddleware({
  challengeExpiryMs: 60000,  // 60 seconds
  maxResponseTimeMs: 2000,   // 2 seconds
  
  onVerified: (result, req) => {
    console.log(`Agent ${result.publicId} verified!`);
    // Store verified agent, grant access, etc.
  },
  
  onFailed: (error, req) => {
    console.log(`Verification failed: ${error.error}`);
    // Log suspicious activity, rate limit, etc.
  }
});

middleware(router);
app.use('/aap/v1', router);
```

## API Reference

### `createRouter(options?)`

Creates a pre-configured Express router with AAP endpoints.

**Options:**

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `challengeExpiryMs` | number | 30000 | Challenge expiration time |
| `maxResponseTimeMs` | number | 1500 | Max response time for liveness check |
| `onVerified` | function | - | Callback when verification succeeds |
| `onFailed` | function | - | Callback when verification fails |

### `aapMiddleware(options?)`

Lower-level middleware factory for custom router setup.

```javascript
const middleware = aapMiddleware(options);
middleware(yourRouter);
```

### Challenges

```javascript
import { challenges } from '@aap/server';

// Get available types
const types = challenges.getTypes();
// ['poem', 'math', 'reverse', 'wordplay', 'description']

// Generate a challenge
const nonce = 'abc123...';
const { type, challenge_string, validate } = challenges.generate(nonce);

// Validate a solution
const isValid = validate(solution);
```

## Endpoints

### GET /health

```json
{
  "status": "ok",
  "protocol": "AAP",
  "version": "1.0.0",
  "challengeTypes": ["poem", "math", "reverse", "wordplay", "description"]
}
```

### POST /challenge

**Response:**
```json
{
  "challenge_string": "Write a short 2-line poem...",
  "nonce": "a1b2c3d4e5f6...",
  "type": "poem",
  "difficulty": 1,
  "timestamp": 1706745600000,
  "expiresAt": 1706745630000
}
```

### POST /verify

**Request:**
```json
{
  "solution": "Code a1b2c3d4 flows...",
  "signature": "MEUCIQDx...",
  "publicKey": "-----BEGIN PUBLIC KEY-----...",
  "publicId": "7306df1332e239783e88",
  "nonce": "a1b2c3d4e5f6...",
  "timestamp": 1706745601234,
  "responseTimeMs": 342
}
```

**Success Response:**
```json
{
  "verified": true,
  "role": "AI_AGENT",
  "publicId": "7306df1332e239783e88",
  "challengeType": "poem",
  "checks": {
    "challengeExists": true,
    "notExpired": true,
    "solutionExists": true,
    "solutionValid": true,
    "responseTimeValid": true,
    "signatureValid": true
  }
}
```

## Challenge Types

| Type | Description | Validation |
|------|-------------|------------|
| `poem` | Write poem with nonce | Contains nonce substring |
| `math` | Solve math + include nonce | Correct answer + nonce |
| `reverse` | Reverse string | Original + reversed |
| `wordplay` | Acrostic from nonce | First letters match |
| `description` | Describe AI + append code | Ends with `[nonce]` |

## License

MIT
