---
name: Ethereum History
description: Read-only factual data about historical Ethereum mainnet contracts. Use when the user asks about a specific contract address, early Ethereum contracts, deployment era, deployer, bytecode, decompiled code, or documented history (what a contract is and is not). Data is non-opinionated and includes runtime bytecode, decompiled code, and editorial history when available. Base URL https://ethereumhistory.com (or set BASE_URL for local/staging).
---

# Ethereum History — Agent Skill

Ethereum History exposes **read-only, factual** data about historical Ethereum mainnet contracts. Use this skill when the user asks about:

- A specific contract address (what is it, when was it deployed, who deployed it, bytecode, decompiled code, documented history)
- Early Ethereum contracts, deployment era (Frontier, Homestead, DAO fork, etc.), or undocumented/notable contracts
- Contract facts: deployer, deployment block/timestamp, short description, historical summary, links, metadata

All endpoints are **GET only**. No authentication required. Responses are JSON with snake_case keys.

## Base URL

- Production: `https://ethereumhistory.com`
- Manifest (full schema): `GET {BASE_URL}/api/agent/manifest`

## Endpoints

### 1. Contract facts (one address)

**GET** `{BASE_URL}/api/agent/contracts/{address}`

Returns full factual data for one contract: address, era, deployer, deployment block/timestamp, **runtime_bytecode**, **decompiled_code** (when available), short_description, historical_summary, historical_significance, historical_context, token metadata, heuristics, links, metadata. Use when the user provides or asks about a specific contract address.

Example: `GET https://ethereumhistory.com/api/agent/contracts/0xdbf03b407c01e7cd3cbea99509d93f8dddc8c6fb`

### 2. Discovery (list contracts)

**GET** `{BASE_URL}/api/agent/contracts`

Query params (all optional):

- `era_id` — Filter by era (e.g. `frontier`, `homestead`, `dao`, `tangerine`, `spurious`)
- `featured` — `true` or `1` for featured contracts only
- `undocumented_only` — `true` or `1` for contracts with no short_description yet
- `limit` — Max 200, default 50
- `offset` — Pagination offset, default 0

Returns a list with minimal fields: address, era_id, deployer_address, deployment_timestamp, has_short_description, decompilation_success, etherscan_contract_name, token_name, token_symbol. Use for discovery; then fetch full facts via endpoint 1 if needed.

### 3. Temporal queries (by time range)

**GET** `{BASE_URL}/api/agent/contracts?from_timestamp=...&to_timestamp=...`

Query params:

- `from_timestamp` — ISO 8601 (e.g. `2015-07-30T00:00:00Z`)
- `to_timestamp` — ISO 8601
- `era_id`, `limit`, `offset` — Same as discovery

Use when the user asks for contracts deployed in a date range or era.

## Requests and responses

### 1. Contract facts — GET `{BASE_URL}/api/agent/contracts/{address}`

**Request**

- Path: `address` — Ethereum address (0x + 40 hex chars). Required.

**Success (200)**

```json
{
  "data": {
    "address": "string",
    "era_id": "string | null",
    "era": { "id": "string", "name": "string", "start_block": number, "end_block": number | null, "start_date": "string", "end_date": "string | null" } | null,
    "deployer_address": "string | null",
    "deployment_tx_hash": "string | null",
    "deployment_block": number | null,
    "deployment_timestamp": "string | null",
    "runtime_bytecode": "string | null",
    "decompiled_code": "string | null",
    "decompilation_success": boolean,
    "code_size_bytes": number | null,
    "gas_used": number | null,
    "gas_price": "string | null",
    "heuristics": { "contract_type": "string | null", "confidence": number, "is_proxy": boolean, "has_selfdestruct": boolean, "is_erc20_like": boolean },
    "etherscan_contract_name": "string | null",
    "etherscan_verified": boolean,
    "source_code": "string | null",
    "abi": "string | null",
    "token_name": "string | null",
    "token_symbol": "string | null",
    "token_decimals": number | null,
    "token_logo": "string | null",
    "short_description": "string | null",
    "description": "string | null",
    "historical_summary": "string | null",
    "historical_significance": "string | null",
    "historical_context": "string | null",
    "verification_status": "string",
    "links": [{ "id": number, "title": "string | null", "url": "string", "source": "string | null", "note": "string | null", "created_at": "string" }],
    "metadata": [{ "key": "string", "value": "string | null", "json_value": unknown, "source_url": "string | null", "created_at": "string" }]
  },
  "meta": { "timestamp": "string (ISO 8601)", "cached": false }
}
```

**Errors**

- **400** — Invalid address format. Body: `{ "error": "Invalid Ethereum address format. Must be 0x followed by 40 hex characters." }`
- **404** — Contract not found. Body: `{ "error": "Contract not found in our historical archive." }`
- **500** — Server error. Body: `{ "error": "string" }`

---

### 2. Discovery / temporal — GET `{BASE_URL}/api/agent/contracts`

**Request (query params, all optional)**

| Param | Type | Description |
|-------|------|-------------|
| `era_id` | string | Era id: `frontier`, `homestead`, `dao`, `tangerine`, `spurious` |
| `featured` | string | `true` or `1` = featured only; `false` or `0` = no filter |
| `undocumented_only` | string | `true` or `1` = contracts with no short_description |
| `from_timestamp` | string | ISO 8601; deployment_timestamp >= this |
| `to_timestamp` | string | ISO 8601; deployment_timestamp <= this |
| `limit` | number | 1–200, default 50 |
| `offset` | number | Pagination offset, default 0 |

**Success (200)**

```json
{
  "data": [
    {
      "address": "string",
      "era_id": "string | null",
      "deployer_address": "string | null",
      "deployment_timestamp": "string | null",
      "has_short_description": boolean,
      "decompilation_success": boolean,
      "etherscan_contract_name": "string | null",
      "token_name": "string | null",
      "token_symbol": "string | null"
    }
  ],
  "meta": {
    "timestamp": "string (ISO 8601)",
    "cached": false,
    "limit": number,
    "offset": number,
    "count": number
  }
}
```

When the database is not configured, response is still **200** with `"data": []` and `meta.message` indicating discovery requires PostgreSQL.

---

### 3. Manifest — GET `{BASE_URL}/api/agent/manifest`

**Request:** None.

**Success (200):** JSON object with `name`, `id`, `description`, `version`, `base_url`, `capabilities`, `endpoints`, `terms`. See the live URL for full shape.

---

## Usage notes

- **Read-only.** No opinions or editorial stance. Data as documented on EthereumHistory.com.
- **Factual only.** What something is and is not. No hype or persuasion.
- When history (short_description, etc.) is not yet documented, contract facts still include runtime_bytecode and decompiled_code when available.
- For the full machine-readable manifest (capabilities, endpoints, terms), call `GET {BASE_URL}/api/agent/manifest`.
