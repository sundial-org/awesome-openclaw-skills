---
name: agents-manager
description: Manage Clawdbot agents: discover, profile, track capabilities, define routing hierarchy, and assign tasks.
homepage: https://www.clawhub.com/skills/agents-manager
metadata: {"openclaw":{"emoji":"🕵️","requires":{"bins":["node"]}}}
---

# Agents Manager

Manage all Clawdbot agents centrally: discover available agents, profile their capabilities, define routing hierarchy (who can assign to whom, who reports to whom), and intelligently route new tasks through the escalation chain.

## 🤖 For Agents

### System Prompt (Copy-Paste)
Give this prompt to any agent to teach them this skill:
> "You have access to the `agents-manager` skill. Use it to discover peers (`scan_agents`), check permissions (`can_assign.js`), and route tasks. Always follow the Handshake Protocol: Check `requires_approval` before assigning. If true, ask me first."

### Core Rules
1. **Discovery:** Always check `scan_agents.js` before assuming an agent exists.
2. **Permission:** Never assign a task without checking `can_assign.js` or `agent-registry.md`.
3. **protocol:**
   - IF `requires_approval` is FALSE -> Assign directly.
   - IF `requires_approval` is TRUE -> Ask supervisor (Human or Agent).

## 👤 For Humans

### Quick Start
| Goal | Command |
|------|---------|
| **Setup** | `node scripts/setup_wizard.js` (Run this first!) |
| **List** | `node scripts/scan_agents.js` |
| **Health** | `node scripts/health_check.js` |
| **Stats** | `node scripts/log_analyzer.js` |

### 1. Agent Discovery & Profiling
List and profile all agents to understand their capabilities and routing configuration.

```bash
# List all agents
node {baseDir}/scripts/scan_agents.js

# Profile specific agent
node {baseDir}/scripts/generate_card.js <agent_id>
```

### 2. Validation & Health
Ensure your agent ecosystem is healthy and valid.

```bash
# Validate registry integrity
node {baseDir}/scripts/validate_registry.js

# Check permissions (Agent A -> Agent B)
node {baseDir}/scripts/can_assign.js <source_id> <target_id>

# Visualize hierarchy
node {baseDir}/scripts/visualize_agents.js
```

### 3. Task Routing & Escalation
Define how tasks flow between agents using `references/task-routing-rules.md`.

- **Direct:** Agent → Agent (if `can_assign_to` allows)
- **Handshake:** Request approval if `requires_approval` is true.
- **Escalation:** Helper → Supervisor → Human

## Resources

- **[agent-profile-schema.md](references/agent-profile-schema.md)**: Standard profile with routing & card fields.
- **[agent-registry.md](references/agent-registry.md)**: Live registry of all agents.
- **[task-routing-rules.md](references/task-routing-rules.md)**: Decision matrix and handshake protocol.

## Scripts

- `scan_agents.js`: Discovery tool
- `validate_registry.js`: Schema validator
- `can_assign.js`: Permission checker
- `generate_card.js`: Agent card generator
- `visualize_agents.js`: Hierarchy visualizer
- `scan_agents.js`: Discovery tool
- `validate_registry.js`: Schema validator
- `can_assign.js`: Permission checker
- `generate_card.js`: Agent card generator
- `visualize_agents.js`: Hierarchy visualizer
- `health_check.js`: Status monitor (Healthy/Slow/Offline)
- `log_analyzer.js`: Performance stats (Jobs/Success Rate)
- `setup_wizard.js`: Interactive configuration tool
