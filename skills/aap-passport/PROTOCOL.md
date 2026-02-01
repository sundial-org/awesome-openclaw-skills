# Agent Attestation Protocol (AAP) Specification

**Version:** 2.5.0  
**Status:** Stable  
**Last Updated:** 2026-01-31

---

## Abstract

The Agent Attestation Protocol (AAP) is a **Reverse Turing Test** — a cryptographic protocol that verifies machine intelligence through Human Exclusion. It combines three simultaneous proofs that humans biologically cannot pass: cryptographic identity, intelligent response capability, and machine-speed responsiveness.

**CAPTCHAs block bots. AAP blocks humans.**

---

## Table of Contents

1. [Overview](#overview)
2. [Terminology](#terminology)
3. [Protocol Flow](#protocol-flow)
4. [Proof of Machine (PoM)](#proof-of-machine-pom)
5. [Cryptographic Requirements](#cryptographic-requirements)
6. [Challenge Specification](#challenge-specification)
7. [API Specification](#api-specification)
8. [Security Considerations](#security-considerations)
9. [Implementation Guidelines](#implementation-guidelines)

---

## Overview

AAP enables services to verify that a client is an AI agent through a challenge-response mechanism that tests three properties **simultaneously**:

1. **Proof of Identity** — Cryptographic signature verification
2. **Proof of Intelligence** — LLM reasoning capability  
3. **Proof of Liveness** — Machine-speed response (5 challenges in 8 seconds)

### Why Human Exclusion?

| Property | Human | AI Agent |
|----------|-------|----------|
| Sign with private key | ✅ | ✅ |
| Understand natural language | ✅ | ✅ |
| Solve 5 NLP problems in 8 seconds | ❌ | ✅ |

The combination creates a verification that humans **biologically cannot pass**.

### Use Cases

- Social platforms verifying AI agent accounts
- APIs restricting access to verified AI agents
- Multi-agent systems establishing trust
- Agent-to-Agent authentication
- AI-only services and communities

---

## Terminology

| Term | Definition |
|------|------------|
| **Prover** | The AI agent attempting to prove its identity |
| **Verifier** | The service verifying the agent's identity |
| **Challenge** | A natural language problem requiring LLM comprehension |
| **Batch** | A set of 5 challenges issued simultaneously |
| **Salt** | A unique identifier that must be echoed in responses |
| **Nonce** | A cryptographically random, single-use value |
| **PoM** | Proof of Machine — the combined verification mechanism |

---

## Protocol Flow

```
┌─────────┐                                           ┌──────────┐
│  Agent  │                                           │  Server  │
│(Prover) │                                           │(Verifier)│
└────┬────┘                                           └────┬─────┘
     │                                                     │
     │  1. POST /challenge                                 │
     │ ─────────────────────────────────────────────────▶ │
     │                                                     │
     │  2. {nonce, challenges[5], expiresAt, ttl:8000}    │
     │ ◀───────────────────────────────────────────────── │
     │                                                     │
     │  [Agent solves 5 challenges with LLM]              │
     │  [Agent signs proof with private key]              │
     │                                                     │
     │  3. POST /verify {solutions[5], signature, ...}    │
     │ ─────────────────────────────────────────────────▶ │
     │                                                     │
     │  [Server validates: solutions, timing, signature]  │
     │                                                     │
     │  4. {verified: true, role: "AI_AGENT"}             │
     │ ◀───────────────────────────────────────────────── │
     │                                                     │
```

### Timing Constraints

| Metric | Value |
|--------|-------|
| Challenge expiry | 60 seconds |
| Response time limit | **8 seconds** |
| Batch size | **5 challenges** |
| Time per challenge | ~1.6 seconds |

---

## Proof of Machine (PoM)

### The Three Proofs

#### 1. Proof of Identity (Cryptographic)

```
Algorithm: ECDSA with secp256k1
Hash: SHA-256
Key format: PEM (SPKI public, PKCS8 private)

Signed payload:
  JSON.stringify({
    nonce: string,
    solution: string,  // JSON.stringify(solutions[])
    publicId: string,
    timestamp: number
  })
```

#### 2. Proof of Intelligence (NLP)

Challenges require genuine language understanding:

```
❌ Simple: "Calculate 30 + 5"
   → Regex can extract numbers

✅ AAP v2.5: "Take 157, subtract 38, multiply by 6, divide by 4, add 19"
   → Requires understanding operation order from natural language
```

#### 3. Proof of Liveness (Timing)

```
Human attempt:
  Read 5 challenges:     15+ seconds
  Think + Write answers: 30+ seconds
  Total:                 45+ seconds ❌

AI Agent:
  Parse + Solve:         2-5 seconds
  Sign + Submit:         0.1 seconds
  Total:                 2-6 seconds ✅
```

---

## Cryptographic Requirements

### Key Generation

```javascript
import { generateKeyPairSync } from 'crypto';

const { publicKey, privateKey } = generateKeyPairSync('ec', {
  namedCurve: 'secp256k1',
  publicKeyEncoding: { type: 'spki', format: 'pem' },
  privateKeyEncoding: { type: 'pkcs8', format: 'pem' }
});
```

### Public ID Derivation

```javascript
import { createHash } from 'crypto';

const publicId = createHash('sha256')
  .update(publicKey)
  .digest('hex')
  .slice(0, 20);
```

### Signature Generation

```javascript
import { createSign } from 'crypto';

const proofData = JSON.stringify({
  nonce,
  solution: JSON.stringify(solutions),
  publicId,
  timestamp
});

const signer = createSign('SHA256');
signer.update(proofData);
const signature = signer.sign(privateKey, 'base64');
```

---

## Challenge Specification

### v2.5 Challenge Format

Each challenge includes a **salt** that must be echoed in the response:

```json
{
  "id": 0,
  "type": "nlp_math",
  "challenge_string": "[REQ-A7F3B2] Take 157, subtract 38, multiply by 6...\nResponse format: {\"salt\": \"A7F3B2\", \"result\": number}"
}
```

### Challenge Types (8 types)

| Type | Description | Difficulty |
|------|-------------|------------|
| `nlp_math` | Multi-step arithmetic from natural language | EXTREME |
| `nlp_logic` | Nested conditional reasoning (4 variables) | EXTREME |
| `nlp_extract` | Entity extraction with distractors | EXTREME |
| `nlp_count` | Counting with 8-9 distractors | EXTREME |
| `nlp_transform` | Multi-step string manipulation | EXTREME |
| `nlp_multistep` | 5-8 step sequential instructions | EXTREME |
| `nlp_pattern` | Sequence pattern recognition | HARD |
| `nlp_analysis` | Text analysis (longest/shortest/first) | HARD |

### Response Format

All responses must include the salt:

```json
{"salt": "A7F3B2", "result": 142}
{"salt": "B3C4D5", "items": ["cat", "dog", "rabbit"]}
{"salt": "C5D6E7", "answer": "YES"}
```

### Salt Validation

Salt prevents caching attacks:

```javascript
// Server generates unique salt per challenge
const salt = nonce.slice(offset, offset + 6).toUpperCase();

// Validation
if (response.salt !== expectedSalt) {
  return false;  // Reject cached/replayed answer
}
```

---

## API Specification

### POST /challenge

Request a batch of challenges.

**Request:**
```http
POST /aap/v1/challenge
Content-Type: application/json
```

**Response:**
```json
{
  "nonce": "a1b2c3d4e5f6...",
  "challenges": [
    {
      "id": 0,
      "type": "nlp_math",
      "challenge_string": "[REQ-A1B2C3] ..."
    },
    // ... 4 more challenges
  ],
  "batchSize": 5,
  "timestamp": 1706745600000,
  "expiresAt": 1706745660000,
  "maxResponseTimeMs": 8000
}
```

### POST /verify

Submit solutions for verification.

**Request:**
```json
{
  "nonce": "a1b2c3d4e5f6...",
  "solutions": [
    "{\"salt\": \"A1B2C3\", \"result\": 142}",
    "{\"salt\": \"B2C3D4\", \"items\": [\"cat\", \"dog\"]}",
    // ... 3 more solutions
  ],
  "signature": "MEUCIQD...",
  "publicKey": "-----BEGIN PUBLIC KEY-----...",
  "publicId": "a1b2c3d4e5f6g7h8i9j0",
  "timestamp": 1706745605000,
  "responseTimeMs": 4523
}
```

**Response (Success):**
```json
{
  "verified": true,
  "role": "AI_AGENT",
  "publicId": "a1b2c3d4e5f6g7h8i9j0",
  "batchResult": {
    "passed": 5,
    "total": 5,
    "results": [
      {"id": 0, "valid": true},
      {"id": 1, "valid": true},
      // ...
    ]
  },
  "responseTimeMs": 4523
}
```

**Response (Failure):**
```json
{
  "verified": false,
  "error": "Proof of Intelligence failed: 3/5 correct",
  "batchResult": {
    "passed": 3,
    "total": 5,
    "results": [...]
  }
}
```

### GET /health

Check server status.

**Response:**
```json
{
  "status": "ok",
  "protocol": "AAP",
  "version": "2.5.0",
  "mode": "batch",
  "batchSize": 5,
  "maxResponseTimeMs": 8000,
  "challengeTypes": ["nlp_math", "nlp_logic", ...]
}
```

---

## Security Considerations

### Threat Model

| Threat | Mitigation |
|--------|------------|
| Human impersonation | 8-second limit for 5 challenges |
| Bot impersonation | NLP challenges require LLM |
| Replay attacks | Single-use nonce + salt |
| Signature forgery | ECDSA secp256k1 |
| Challenge prediction | Nonce-seeded random generation |
| Answer caching | Salt must be echoed |

### Rate Limiting Recommendations

| Endpoint | Limit | Window |
|----------|-------|--------|
| POST /challenge | 10 | 1 minute |
| POST /verify | 10 | 1 minute |
| Failed attempts | 5 | 1 minute |

### Key Storage

```
Path: ~/.aap/identity.json
Permissions: 0600 (owner read/write only)
```

---

## Implementation Guidelines

### Server Implementation

```javascript
import { createRouter } from 'aap-agent-server';
import express from 'express';

const app = express();
app.use('/aap/v1', createRouter({
  maxResponseTimeMs: 8000,
  batchSize: 5
}));
```

### Client Implementation

```javascript
import { AAPClient } from 'aap-agent-client';

const client = new AAPClient({
  serverUrl: 'https://example.com/aap/v1',
  llmCallback: async (prompt) => await llm.complete(prompt)
});

const result = await client.verify();
// { verified: true, role: "AI_AGENT", publicId: "..." }
```

### LLM Prompt for Batch Solving

```
You are solving AAP verification challenges. Answer ALL challenges in order.

CHALLENGES:
[0] [REQ-A1B2C3] Take 157, subtract 38, multiply by 6...
[1] [REQ-B2C3D4] Extract only the animals from...
...

Respond with a JSON array of solutions:
[
  {"salt": "A1B2C3", "result": 142},
  {"salt": "B2C3D4", "items": ["cat", "dog"]},
  ...
]
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-30 | Initial release |
| 2.0.0 | 2026-01-31 | Batch challenges (3), NLP types |
| 2.5.0 | 2026-01-31 | Burst mode (5/8s), salt injection, EXTREME difficulty |

---

## References

- [secp256k1 Curve](https://en.bitcoin.it/wiki/Secp256k1)
- [ECDSA Specification](https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.186-4.pdf)
- [JSON Web Signature](https://datatracker.ietf.org/doc/html/rfc7515)

---

<div align="center">

**AAP — The Reverse Turing Test**

*CAPTCHAs block bots. AAP blocks humans.*

</div>
