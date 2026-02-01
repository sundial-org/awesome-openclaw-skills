# Composable Pattern Examples

These illustrate how Clawdbot primitives combine in non-obvious ways. Use clawddocs to verify current tool capabilities.

## 1. Visual Monitoring Pipeline
**Tools:** nodes + image + canvas + message

A skill that watches for physical-world changes:
- `nodes camera_snap` captures from a device camera (e.g., monitor a doorway, plant, 3D printer)
- `image` analyzes the photo for specific conditions (person present? print complete? plant wilting?)
- State tracks previous analysis; script compares to detect meaningful changes
- On change: `message` notifies user, `canvas` presents a dashboard with history
- `cron` schedules periodic checks; intensity varies by time (frequent during expected events)

**Composition:** physical sensor → AI vision → state machine → multi-output. Neither a pure monitor nor a pure API wrapper.

## 2. Parallel Research Aggregator
**Tools:** sessions_spawn + web_search + web_fetch + browser + canvas

A skill for deep research on a topic:
- Parse user query into research facets (e.g., "market analysis of X" → competitors, pricing, trends, news)
- `sessions_spawn` parallel sub-agents, each tackling one facet
- Sub-agents use `web_search` for discovery, `web_fetch` for content extraction
- For JS-heavy sites, sub-agents use `browser` with snapshot for data extraction
- Parent monitors via `sessions_list`, aggregates results when complete
- `canvas` presents structured findings with citations
- Memory logs the research for future reference

**Composition:** task decomposition → parallel execution → aggregation → rich presentation. Shows sub-agent orchestration at scale.

## 3. Location-Aware Context Switcher
**Tools:** nodes + cron + memory + message

A skill that adapts behavior based on physical location:
- `nodes location_get` checks device position (with appropriate permissions)
- Script compares to known locations (home, office, gym — stored in skill state or TOOLS.md)
- Context switch triggers different behaviors:
  - Arriving at office → summarize overnight emails, today's calendar
  - Leaving office → switch to personal context, check personal todos
  - Arriving home → home automation triggers (if integrated), family calendar
- `cron` polls location periodically; `memory` tracks context history
- `message` delivers context-appropriate briefings

**Composition:** physical context → behavior routing → multi-domain integration. The skill becomes a context-aware assistant layer.

## 4. Cross-Channel Thread Tracker
**Tools:** message + memory_search + sessions_send

A skill that maintains conversation continuity across channels:
- When user mentions a topic, `memory_search` finds related prior discussions (any channel)
- Script extracts thread summaries, key decisions, open items
- If discussion continues from another channel, agent bridges context:
  - "Continuing from your Telegram chat with X on Jan 15..."
  - Relevant history summarized, open questions surfaced
- Cross-references stored in memory; `sessions_send` can notify related sessions
- Works across Discord/Telegram/WhatsApp/Slack with channel-appropriate formatting

**Composition:** semantic memory → cross-channel context → continuity preservation. Memory becomes the unifying layer.

## 5. Scheduled Report Generator
**Tools:** cron + exec + browser + canvas + message

A skill for periodic reporting from external systems:
- `cron` triggers at scheduled time (e.g., daily standup, weekly metrics)
- Script orchestrates data gathering:
  - `exec` runs local commands (git stats, server metrics, file counts)
  - `browser` logs into authenticated dashboards, extracts data via snapshot
  - `web_fetch` pulls from APIs
- Agent synthesizes into report format appropriate for audience
- `canvas` renders visual report; `message` distributes to configured channel(s)
- State tracks report history for trend analysis

**Composition:** scheduled trigger → multi-source gathering → synthesis → distribution. A reporting pipeline that spans local and remote sources.

## 6. Interactive Approval Workflow
**Tools:** message + cron + memory + gateway

A skill for multi-step processes requiring user decisions:
- User initiates a request (e.g., "deploy to production", "send the newsletter")
- Skill performs pre-checks, presents summary with inline buttons:
  - ✅ Approve | ❌ Reject | ⏸️ Defer
- On defer: `cron` schedules follow-up reminder
- On approve: skill executes action, logs to memory
- On reject: logs reason, notifies relevant parties
- State machine tracks workflow progress across sessions
- `gateway` config changes if workflow modifies Clawdbot behavior

**Composition:** request → validation → interactive decision → conditional execution. Agent becomes workflow orchestrator.

## 7. Adaptive Learning Loop
**Tools:** image/browser + memory + cron + message

A skill that improves based on feedback:
- Performs some analysis or classification task (image analysis, content categorization)
- Presents result to user with feedback mechanism
- User corrections stored in memory (`memory/` or skill state)
- Script builds correction history; agent adapts prompting based on past errors
- `cron` periodically reviews correction patterns, suggests skill updates
- Meta-improvement: skill can propose SKILL.md refinements based on error patterns

**Composition:** task execution → feedback capture → pattern learning → self-improvement. The skill gets better over time.

---

## Why These Patterns Work

| Phase | Who | What |
|-------|-----|------|
| 1. Parse & route | Agent | Understand intent, extract parameters, choose script |
| 2. Gather data | Script | Deterministic fetching, no judgment needed |
| 3. Synthesize & act | Agent | Interpret data, make judgments, compose output, trigger actions |

The script doesn't decide *what matters* — it just reliably fetches everything. The agent doesn't wrestle with API calls — it focuses on understanding and judgment.
