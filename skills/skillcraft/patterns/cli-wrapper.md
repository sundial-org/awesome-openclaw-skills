# CLI Wrapper Pattern

Wrap a CLI tool for use through Clawdbot. Focuses on **clawdbot-specific integration** — channel formatting, scheduling, memory — not generic CLI documentation.

## What Makes It Clawdbot-Specific

Standard CLI wrapper advice (document commands, handle errors) applies. What's different:

### 1. Channel-Aware Output

Output goes to different surfaces with different capabilities. Use **clawddocs** to check `/providers/` docs for channel-specific capabilities — they vary by platform and configuration.

**Pattern:** Check channel in runtime context, adapt formatting. Or document format in SKILL.md and let agent adapt based on current channel capabilities.

**Common considerations:**
- Some channels don't support markdown tables — use bullet lists instead
- Long output may need summarization
- Rich formatting (buttons, embeds) varies by channel

### 2. Execution Context

Use the `exec` tool for running CLI commands. Key considerations:

- **Timeouts:** Always set reasonable timeouts — CLI tools that hang block the agent
- **Background execution:** For long-running commands, use background mode and poll via `process` tool
- **Output handling:** Capture and parse output appropriately

Consult **clawddocs** `/tools/bash` for current exec tool syntax and parameters.

### 3. Scheduled Execution (cron)

For periodic execution, use Clawdbot's cron system. Consult **clawddocs** `/automation/cron-jobs` for:
- Configuration format and options
- Prompt patterns for triggering skills
- Job management via the `cron` tool

**Skill documents:** What the cron prompt should say, expected behavior, any state it updates.

### 4. Heavy Work (sessions_spawn)

For long-running or output-heavy operations:

```
sessions_spawn task:"Run tool export --full. Summarize results and notify when done."
```

**Path considerations:** If sub-agent needs workspace files, use **clawddocs** `/tools/subagents` for current sandbox mount configuration and include path context in the task.

### 5. Results Delivery (message)

Push results to specific channels:

```
message action:send channel:telegram message:"Export complete: 47 records"
```

Useful when CLI completes in background and user should be notified.

### 6. User Preferences (memory)

Store user-specific defaults in `<workspace>/TOOLS.md`:

```markdown
## mytool

- Default output format: json
- Preferred verbosity: quiet unless debugging
- API endpoint: https://custom.example.com
```

**Skill documents:** What section to check, what preferences are supported.

## State Management

CLI wrappers are usually **stateless**. Exceptions:

- **Auth tokens** that expire → track in `<skill>/state.json`
- **Incremental sync** → track last-sync timestamp
- **Rate limits** → remember reset time

```
<skill>/state.json        # skill-internal state
<workspace>/state/tool.json   # shared state (if multiple skills use it)
```

`~/.clawdbot/` is not suitable for storing state — skills don't own user home.

## Checklist

Clawdbot-specific concerns for CLI wrappers:

- [ ] Output formatting considers channel constraints (check docs)
- [ ] Timeouts set for all exec calls
- [ ] Cron integration documented (if periodic)
- [ ] Heavy operations spawn sub-agents
- [ ] User preferences location documented
- [ ] State paths use `<skill>/` or `<workspace>/`, never `~/`
- [ ] Path handling documented for sub-agent scenarios
