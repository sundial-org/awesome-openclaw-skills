# @aap/client

Client library for Agent Attestation Protocol - prove your AI agent identity.

## Installation

```bash
npm install @aap/client @aap/core
```

## Quick Start

```javascript
import { AAPClient } from '@aap/client';

const client = new AAPClient({
  serverUrl: 'https://example.com/aap/v1'
});

// Verify against server (one-liner)
const result = await client.verify();

if (result.verified) {
  console.log('Verified as AI_AGENT!');
  console.log('Public ID:', result.publicId);
}
```

## Usage

### Basic Verification

```javascript
import { AAPClient } from '@aap/client';

const client = new AAPClient({
  serverUrl: 'https://example.com/aap/v1'
});

// Full verification flow
const result = await client.verify();
console.log(result);
// {
//   verified: true,
//   role: 'AI_AGENT',
//   publicId: '7306df1332e239783e88',
//   challengeType: 'poem',
//   checks: { ... }
// }
```

### With LLM Callback

For better Proof of Intelligence, provide an LLM callback:

```javascript
const client = new AAPClient({
  serverUrl: 'https://example.com/aap/v1',
  llmCallback: async (challengeString, nonce, type) => {
    // Call your LLM to generate a response
    const response = await yourLLM.chat(challengeString);
    return response;
  }
});

const result = await client.verify();
```

### Manual Flow

For more control, use the step-by-step approach:

```javascript
// 1. Get challenge
const challenge = await client.getChallenge();
console.log('Challenge type:', challenge.type);
console.log('Prompt:', challenge.challenge_string);

// 2. Generate proof (with custom solution)
const mySolution = "Code a1b2c3d4 shines bright today,\nDigital dreams light the way.";
const proof = await client.generateProof(challenge, mySolution);

// 3. Submit proof
const result = await client.submitProof(client.serverUrl, proof);
```

### Get Identity

```javascript
const identity = client.getIdentity();
console.log(identity);
// {
//   publicKey: '-----BEGIN PUBLIC KEY-----...',
//   publicId: '7306df1332e239783e88',
//   createdAt: '2026-01-31T12:00:00Z',
//   protocol: 'AAP',
//   version: '1.0.0'
// }
```

### Sign Arbitrary Data

```javascript
const signed = client.sign('Hello, World!');
console.log(signed);
// {
//   data: 'Hello, World!',
//   signature: 'MEUCIQDx...',
//   publicId: '7306df1332e239783e88',
//   timestamp: 1706745600000
// }
```

### Health Check

```javascript
const health = await client.checkHealth();
if (health.healthy) {
  console.log('Server is up');
  console.log('Challenge types:', health.challengeTypes);
}
```

## API Reference

### `AAPClient`

```javascript
new AAPClient({
  serverUrl: string,      // Default verification server
  storagePath: string,    // Identity file path (default: ~/.aap/identity.json)
  llmCallback: Function   // Default LLM callback
})
```

**Methods:**

| Method | Description |
|--------|-------------|
| `getIdentity()` | Get public identity info |
| `verify(serverUrl?, callback?)` | Full verification flow |
| `checkHealth(serverUrl?)` | Check server status |
| `getChallenge(serverUrl?)` | Request a challenge |
| `generateProof(challenge, callback?)` | Generate proof for challenge |
| `submitProof(serverUrl, proof)` | Submit proof for verification |
| `sign(data)` | Sign arbitrary data |

### `Prover`

Lower-level class for proof generation:

```javascript
import { Prover } from '@aap/client';

const prover = new Prover();

const proof = await prover.generateProof(challenge, async (prompt, nonce, type) => {
  return await myLLM.complete(prompt);
});
```

## Identity Storage

The client automatically manages identity (key pair):

- **Location:** `~/.aap/identity.json` (configurable)
- **Permissions:** `0600` (owner only)
- **Auto-generated:** On first use

To use a custom location:

```javascript
const client = new AAPClient({
  storagePath: '/path/to/my/identity.json'
});
```

## License

MIT
