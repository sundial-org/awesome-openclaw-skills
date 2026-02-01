---
name: blockchain_attestation
description: Create verifiable attestations of agent work using Ethereum Attestation Service (EAS), with Base as the default chain.
metadata: {"clawdbot":{"emoji":"⛓️","homepage":"https://attest.org","requires":{"bins":["node"]},"primaryEnv":"EAS_PRIVATE_KEY"}}
---

# Blockchain Attestation (EAS)

This skill creates **onchain** or **offchain** attestations of completed work using the Ethereum Attestation Service (EAS).

Opinionated defaults:
- Default chain: **Base mainnet**
- Default mode: **offchain** (zero gas, still verifiable)
- Default data model: store **hashes** of the task and the deliverable (plus a small agent id and metadata string)

## Safety and privacy rules

1. **Never** put secrets, private keys, tokens, or private user data into onchain attestations.
2. Prefer **offchain** attestations for most use cases.
3. If you need a public timestamp anchor for an offchain attestation, use the **timestamp** command which anchors the UID onchain without publishing the full payload.
4. Only run onchain transactions after the user explicitly requests it or has approved costs.

## Environment variables

Required for signing (offchain or onchain):
- `EAS_PRIVATE_KEY`

Required for onchain transactions and onchain reads:
- `EAS_RPC_URL` (an RPC endpoint for the selected chain)

Optional:
- `EAS_CHAIN` (`base` or `base_sepolia`, default is `base`)
- `CLAWDBOT_AGENT_ID` (overrides the `agentId` field)

## One time setup

Install Node dependencies once:

```bash
cd {baseDir} && npm install
```

## One time per chain: register the schema

This skill uses a single schema:

```
bytes32 taskHash, bytes32 outputHash, string agentId, string metadata
```

Register it (onchain transaction) and persist the resulting schema UID into `schemas.json`:

```bash
cd {baseDir} && node attest.mjs schema register --chain base
```

For Base Sepolia:

```bash
cd {baseDir} && node attest.mjs schema register --chain base_sepolia
```

## Create an attestation (recommended: offchain)

Best default workflow:
1. Provide the task description text
2. Provide the deliverable file path (or deliverable text)
3. Create an offchain attestation
4. Save the signed payload to a file
5. Return UID plus the explorer link to the user

Example:

```bash
cd {baseDir} && node attest.mjs attest \
  --mode offchain \
  --chain base \
  --task-text "Summarize Q4 board deck into 1 page memo" \
  --output-file ./deliverables/memo.pdf \
  --recipient 0x0000000000000000000000000000000000000000 \
  --metadata '{"hashAlg":"sha256","artifact":"memo.pdf"}' \
  --save ./attestations/latest.offchain.json
```

## Timestamp an offchain UID onchain (optional anchor)

```bash
cd {baseDir} && node attest.mjs timestamp --chain base --uid <uid>
```

## Create an onchain attestation (costs gas)

```bash
cd {baseDir} && node attest.mjs attest \
  --mode onchain \
  --chain base \
  --task-text "..." \
  --output-file ./path/to/output \
  --metadata '{"hashAlg":"sha256"}'
```

## Verify

Verify an onchain UID:

```bash
cd {baseDir} && node attest.mjs verify --chain base --uid <uid>
```

Verify an offchain attestation JSON file (as produced by this skill):

```bash
cd {baseDir} && node attest.mjs verify --offchain-file ./attestations/latest.offchain.json
```

## Hash helper

If you need hashes without creating an attestation:

```bash
cd {baseDir} && node attest.mjs hash --file ./deliverables/memo.pdf
```

## Output contract

All commands print a single JSON object to stdout.
- On success: `{ "success": true, ... }`
- On error: `{ "success": false, "error": { "code": "...", "message": "...", "details": ... } }`

This is deliberate so the agent can reliably parse results.
