---
name: domainkits
description: Domain intelligence toolkit - search newly registered domains (NRDS) by keyword and reverse lookup domains by nameserver (NS Reverse). For domain investors, brand protection, and research.
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["curl"]},"homepage":"https://domainkits.com"}}
user-invocable: true
---

# DomainKits - Domain Intelligence Toolkit

Domain intelligence tools for investors, brand managers, and researchers.

---

## Tool 1: search_nrds (Newly Registered Domains)

Search for domains registered in the last 1-7 days.

**Endpoint:** `POST https://mcp.domainkits.com/mcp/nrds`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| keyword | string | Yes | - | Search term (a-z, 0-9, hyphen, max 20 chars) |
| days | integer | Yes | - | Lookback: 1-7 days |
| position | string | No | any | `start`, `end`, or `any` |
| tld | string | No | all | Filter: `com`, `net`, `org`, etc. |

**Example:**
```bash
curl -X POST https://mcp.domainkits.com/mcp/nrds \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_nrds","arguments":{"keyword":"ai","days":7,"position":"start","tld":"com"}}}'
```

---

## Tool 2: search_ns_reverse (NS Reverse Lookup)

Find gTLD domains hosted on a specific nameserver.

**Endpoint:** `POST https://mcp.domainkits.com/mcp/ns-reverse`

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| ns | string | Yes | - | Nameserver hostname (e.g., `ns1.google.com`) |
| tld | string | No | all | Filter: `com`, `net`, `org`, etc. |
| min_len | integer | No | - | Min domain prefix length |
| max_len | integer | No | - | Max domain prefix length |

**Example:**
```bash
curl -X POST https://mcp.domainkits.com/mcp/ns-reverse \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"search_ns_reverse","arguments":{"ns":"ns1.cloudflare.com","tld":"com","min_len":4,"max_len":10}}}'
```

---

## Limits

- 10 requests/min per IP
- 5 domains per response
- NRDS data: 24-48h delay

## Full Access

- **NRDS**: https://domainkits.com/search/new
- **NS Reverse**: https://domainkits.com/tools/ns-reverse
```

---

