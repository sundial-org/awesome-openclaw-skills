---
name: ercdata
description: Store, verify, and manage AI data on the Ethereum blockchain (Base network) using the ERCData standard. Use when an agent needs to store data fingerprints on-chain, verify data integrity, create audit trails, manage access control for private data, or interact with the ERCData smart contract. Supports public and private storage, EIP-712 verification, snapshots, and batch operations.
---

# ERCData

Store and verify AI-related data on Base mainnet. Public or private, with cryptographic integrity proofs.

## Quick Start

```bash
# Store public data
uv run {baseDir}/scripts/ercdata-cli.py store \
  --type AI_AGENT_MEMORY \
  --data "memory hash: abc123" \
  --metadata '{"agent":"MyBot","ts":"2026-01-31"}' \
  --key $ERCDATA_KEY --contract $ERCDATA_CONTRACT

# Store private data (only you + granted addresses can read)
uv run {baseDir}/scripts/ercdata-cli.py store \
  --type AI_AGENT_MEMORY \
  --data "secret memory data" \
  --private \
  --key $ERCDATA_KEY --contract $ERCDATA_CONTRACT

# Read entry
uv run {baseDir}/scripts/ercdata-cli.py read --id 1 --key $ERCDATA_KEY --contract $ERCDATA_CONTRACT

# Verify entry (EIP-712 signature check)
uv run {baseDir}/scripts/ercdata-cli.py verify --id 1 --method eip712 --key $ERCDATA_KEY --contract $ERCDATA_CONTRACT

# Grant access to private entry
uv run {baseDir}/scripts/ercdata-cli.py grant-access --id 2 --to 0xSomeAddress --key $ERCDATA_KEY --contract $ERCDATA_CONTRACT
```

## Configuration

Set via environment or skill config:
- `ERCDATA_KEY` — Private key for signing transactions (required for writes)
- `ERCDATA_CONTRACT` — Contract address on Base mainnet
- `ERCDATA_RPC` — RPC URL (default: https://mainnet.base.org)

Or pass via `--key`, `--contract`, `--rpc` flags.

## Commands

| Command | What it does |
|---------|-------------|
| `store` | Store data on-chain (add `--private` for access control) |
| `read` | Read a data entry by ID |
| `verify` | Verify data integrity (eip712 or hash method) |
| `grant-access` | Grant read access to an address (private entries) |
| `revoke-access` | Revoke read access |
| `register-type` | Register a new data type (admin only) |
| `snapshot` | Create a point-in-time snapshot |
| `info` | Get entry info without full data |

## Privacy Model

- **Public (default):** Anyone can read via `getData()`. Use for transparency, audit trails.
- **Private (`--private`):** Only the provider, granted addresses, and admin can read. Use for sensitive agent data.

Private entries store the same data on-chain but gate `getData()` access. Note: raw transaction calldata is still visible on-chain explorers. For maximum privacy, encrypt data before storing.

## Use Cases for AI Agents

1. **Memory attestation** — Hash your MEMORY.md and store it periodically for tamper-proof audit trail
2. **Agent identity** — Store model fingerprint, system prompt hash, config on-chain
3. **Verifiable outputs** — Hash agent outputs and store for later verification
4. **Agent-to-agent trust** — Check another agent's ERCData entries before trusting its data
5. **Model provenance** — Store model hashes, benchmark scores, architecture metadata

## API Reference

See [references/api.md](references/api.md) for full contract API, roles, events, and limits.

## Requirements

- Python 3.10+ with `web3` and `eth-account` packages (auto-installed by uv)
- A funded wallet on Base mainnet (ETH for gas)
- PROVIDER_ROLE granted by contract admin for storing data
- VERIFIER_ROLE granted for verification operations
