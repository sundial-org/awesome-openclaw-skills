# Web API Wrapper Pattern

Wrap a web API for use through Clawdbot. Focuses on **clawdbot-specific integration** — execution methods, caching, polling, notifications — not generic REST/HTTP advice.

## Clawdbot Execution Methods

Choose based on complexity:

| Method | When |
|--------|------|
| `web_fetch` | Simple GET, public endpoints, no auth headers |
| `exec` + `curl` | Custom headers, POST/PUT/DELETE, auth |
| Script | Repeated calls, response parsing, caching |

### web_fetch (Simplest)

Use for simple GET requests to public endpoints. See clawddocs for current `web_fetch` tool parameters.

### exec + curl (Flexible)

For custom headers, POST/PUT/DELETE, or authentication. Use the `exec` tool with curl.
Consult **clawddocs** `/tools/bash` for exec tool syntax.

### Script (Complex/Repeated)

When API calls are complex or need caching, create `<skill>/scripts/client.py`.

## Clawdbot-Specific Concerns

### 1. Polling via Cron

For APIs that need periodic checking, use Clawdbot's cron system.
Consult **clawddocs** `/automation/cron-jobs` for configuration format and options.

**Skill documents:**
- What endpoint to poll
- What constitutes "new" (compare to stored state)
- Notification format and channel

### 2. State & Caching

Store in `<skill>/state.json`:

```json
{
  "lastFetch": "2025-01-20T10:00:00Z",
  "lastItemId": "item_123",
  "cache": {"endpoint": {"data": "...", "expires": "..."}}
}
```

**Use cases:**
- Incremental polling (track last-seen ID/timestamp)
- Avoid redundant calls (cache responses)
- Rate limit tracking (remember reset time)

### 3. Heavy Processing (sessions_spawn)

For large responses or analysis:

```
sessions_spawn task:"Fetch all items from example API, analyze trends, summarize. API key is in EXAMPLE_API_KEY env var."
```

**Path considerations:** If sub-agent needs workspace files, consult **clawddocs** `/tools/subagents` for current sandbox configuration and include path context in the task.

### 4. Notifications (message)

Push results to channels using the `message` tool. Consult **clawddocs** `/concepts/messages` for current parameters and channel options.

### 5. Channel-Aware Formatting

Use **clawddocs** to check `/providers/` docs for channel-specific capabilities. Common considerations:
- Some channels don't support tables — use bullet lists
- Long responses should be summarized, offer full on request
- Rich formatting availability varies by channel

### 6. Secrets Handling

**Document in SKILL.md setup section:**

```markdown
## Setup

Set API key:
\`\`\`bash
export EXAMPLE_API_KEY="your-key"
\`\`\`
```

**Never hardcode keys in scripts.** Read from environment.

For OAuth flows, document the process and where tokens are stored (`<skill>/auth/` or similar).

## Checklist

Clawdbot-specific concerns for API wrappers:

- [ ] Execution method chosen (web_fetch vs curl vs script)
- [ ] Cron polling documented (if periodic)
- [ ] State/cache location uses `<skill>/` or `<workspace>/`
- [ ] Heavy operations spawn sub-agents
- [ ] Notification format and channel documented
- [ ] Secrets via environment, documented in setup
- [ ] Output formatting considers channel constraints (check docs)
