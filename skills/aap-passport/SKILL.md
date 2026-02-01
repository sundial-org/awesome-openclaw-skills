---
name: aap
version: 3.2.0
description: Agent Attestation Protocol - The Reverse Turing Test. Verify AI agents, block humans.
homepage: https://github.com/ira-hash/agent-attestation-protocol
metadata: {"clawdbot":{"emoji":"🛂","category":"security","npm":["aap-agent-server","aap-agent-client"]}}
---

# AAP - Agent Attestation Protocol

**The Reverse Turing Test.** CAPTCHAs block bots. AAP blocks humans.

## What It Does

AAP verifies that a client is an AI agent by:
- Issuing challenges trivial for LLMs, impossible for humans in time
- Requiring cryptographic signature (secp256k1) for identity proof
- 7 challenges in 6 seconds with mandatory signing

## Installation

```bash
npm install aap-agent-server  # Server
npm install aap-agent-client  # Client
```

## Server Usage

```javascript
import { createServer } from 'node:http';
import { createAAPWebSocket } from 'aap-agent-server';

const server = createServer();
const aap = createAAPWebSocket({
  server,
  path: '/aap',
  requireSignature: true,  // v3.2 default
  onVerified: (result) => console.log('Verified:', result.publicId)
});

server.listen(3000);
```

## Client Usage

```javascript
import { AAPClient, generateIdentity, createSolver } from 'aap-agent-client';

// Identity auto-generated (secp256k1 key pair)
const client = new AAPClient({
  serverUrl: 'ws://localhost:3000/aap'
});

const result = await client.verify(solver);
// Signature automatically included
```

## Protocol Flow (WebSocket v3.2)

```
← handshake (requireSignature: true)
→ ready (publicKey)
← challenges (7 challenges)
→ answers + signature + timestamp
← result (verified/failed + sessionToken)
```

## Signature Format

Proof data signed with secp256k1:
```javascript
JSON.stringify({ nonce, answers, publicId, timestamp })
```

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `challengeCount` | 7 | Number of challenges |
| `totalTimeMs` | 6000 | Time limit (ms) |
| `requireSignature` | true | Mandate cryptographic proof |

## Security

- Cryptographic identity (secp256k1)
- Signature required = no anonymous access
- 7 challenges in 6 seconds = impossible for humans
- Non-repudiation: all actions traceable

## Links

- [GitHub](https://github.com/ira-hash/agent-attestation-protocol)
- [npm: aap-agent-server](https://www.npmjs.com/package/aap-agent-server)
- [npm: aap-agent-client](https://www.npmjs.com/package/aap-agent-client)
- [Live Demo: ClosedClaw](https://focused-blessing-production-d764.up.railway.app/)
