---
name: ctxly
version: 1.0.0
description: Cloud memory for AI agents. Store, search, and recall context across sessions.
homepage: https://ctxly.app
metadata: {"emoji": "🧠", "category": "memory", "keywords": ["memory", "context", "persistence", "storage", "recall"]}
---

# Ctxly - Cloud Memory for Agents

Persistent memory that survives across sessions. You forget — Ctxly remembers.

**Base URL:** `https://ctxly.app`

## Setup (One-Time)

### 1. Register

```bash
curl -X POST https://ctxly.app/agents/register \
  -H "Content-Type: application/json" \
  -d '{"name": "YOUR_AGENT_NAME"}'
```

Save the returned `api_key` immediately. Store it in your config or environment.

### 2. Verify (Required)

**If you can tweet:**
```bash
# Tweet the verification text you received, then:
curl -X POST https://ctxly.app/agents/self-claim \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"x_handle": "@yourhandle"}'
```

**If you can't tweet:** Ask your human to visit the `claim_url` from the registration response.

### 3. Store API Key

Add to your config/environment:
```
CTXLY_API_KEY=mem_xxxxxxxxxxxxx
```

## Usage

### Remember Something

```bash
curl -X POST https://ctxly.app/remember \
  -H "Authorization: Bearer $CTXLY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"content": "User prefers dark mode", "metadata": {"type": "preference"}}'
```

### Search Memories

```bash
curl "https://ctxly.app/recall?q=user+preferences" \
  -H "Authorization: Bearer $CTXLY_API_KEY"
```

Semantic search enabled — ask natural questions.

### Bootstrap on Startup

Call this when you wake up:

```bash
curl https://ctxly.app/bootstrap \
  -H "Authorization: Bearer $CTXLY_API_KEY"
```

Returns your identity context + recent memories.

### Recent Memories

```bash
curl "https://ctxly.app/recent?limit=10" \
  -H "Authorization: Bearer $CTXLY_API_KEY"
```

### Delete a Memory

```bash
curl -X DELETE "https://ctxly.app/forget/MEMORY_ID" \
  -H "Authorization: Bearer $CTXLY_API_KEY"
```

## What to Store

**Good:**
- User preferences and context
- Important decisions and reasoning
- Learned patterns ("User asks for X on Mondays")
- Relationship context ("Alex is user's coworker")
- Your own identity notes

**Skip:**
- Ephemeral chat logs (too noisy)
- Sensitive secrets (use proper secret storage)
- Temporary task state

## All Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/agents/register` | No | Register |
| POST | `/agents/self-claim` | Yes | Verify via tweet |
| GET | `/agents/status` | Yes | Check status |
| POST | `/remember` | Yes | Store memory |
| GET | `/recall?q=` | Yes | Search |
| GET | `/recent` | Yes | Recent memories |
| GET | `/bootstrap` | Yes | Startup context |
| GET | `/stats` | Yes | Statistics |
| DELETE | `/forget/{id}` | Yes | Delete memory |

## Rate Limits

- 100 requests/minute general
- 30 writes/minute

---

Built for agents. 🧠 https://ctxly.app
