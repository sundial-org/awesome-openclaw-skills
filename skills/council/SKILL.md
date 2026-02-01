---
name: council
description: Council Chamber orchestration with Memory Bridge. Single session, multiple personas, structured deliberation.
metadata: {"clawdbot":{"emoji":"🏛️","requires":{"bins":["sqlite3"]},"features":{"memory_bridge":true,"chamber_pattern":true}}}
---

# Council - Chamber Orchestration Pattern

Instead of spawning separate agent silos, create a **Council Chamber** where multiple expert personas deliberate in a single session with cross-pollination and unified transcript.

## Prerequisites

- SQLite3 (member database)
- Graphiti service (Memory Bridge)
- Clawdbot gateway (sessions_spawn)

## Setup

Initialize council database:
```bash
bash command:"{baseDir}/init-db.sh"
```

## 🏛️ The Chamber Pattern

**Traditional Approach** (Silos):
- Spawn 3 separate agents
- Each analyzes independently
- No cross-pollination
- Fragmented output

**Chamber Approach** (Meeting Room):
- Single agent session
- Moderates multiple personas
- Structured turn-taking
- Unified deliberation transcript

## Tools

### council_chamber
Start a Council Chamber session (recommended).

**Usage:**
```bash
bash command:"
TOPIC='YOUR_TOPIC'
MEMBERS='architect,analyst,security'

{baseDir}/references/chamber-orchestrator.sh \"\$TOPIC\" \"\$MEMBERS\"
"
```

**What it does**:
1. Fetches Graphiti context (Memory Bridge)
2. Loads member personas from database
3. Constructs chamber task with turn structure
4. Creates session record
5. Outputs task for sessions_spawn

### council_list_members
List all registered members.

**Usage:**
```bash
bash command:"sqlite3 -header -column ~/.clawdbot/council.db 'SELECT id, name, role FROM council_members'"
```

### council_add_member
Register new member.

**Usage:**
```bash
bash command:"
sqlite3 ~/.clawdbot/council.db \"
INSERT INTO council_members (id, name, role, system_message, expertise)
VALUES ('MEMBER_ID', 'NAME', 'ROLE', 'SYSTEM_MESSAGE', 'EXPERTISE');
\""
```

## Chamber Session Structure

**3-Turn Deliberation**:

1. **Turn 1: Initial Analysis**
   - Each persona provides their perspective
   - Distinct voices maintained

2. **Turn 2: Cross-Pollination**
   - Members critique each other's points
   - Real-time responses
   - Healthy debate

3. **Turn 3: Synthesis**
   - Find common ground
   - Resolve disagreements
   - Executive Summary for user

## Default Members

| ID | Name | Role |
|----|------|------|
| architect | System Architect | Technical Design |
| analyst | Technical Analyst | Research & Analysis |
| security | Security Officer | Risk Assessment |
| designer | UX Designer | User Experience |
| strategist | Business Strategist | ROI & Strategy |

## Example

```bash
# User: "Start council on Salesforce integration"
council_chamber topic:"Salesforce Integration" members:"architect,strategist"

# Output:
# 🏛️ Convening Council Chamber...
# 🧠 Memory Bridge: [Retrieved 10 facts about Salesforce]
# 👥 Loaded 2 personas
# ✅ Chamber Task ready for sessions_spawn
```

**Benefits**:
- ✅ Cross-pollination (members respond to each other)
- ✅ Single transcript (one .jsonl file)
- ✅ Shared context (Memory Bridge loaded once)
- ✅ Structured output (3-turn deliberation)
