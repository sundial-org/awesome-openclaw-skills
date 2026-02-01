# Agentic Compass — AI Agent Self-Reflection Tool

Local-only self-reflection that forces **objective** action for AI agents. No data leaves your machine.

## What It Does

Reads your local memory files and produces a structured **Agent Action Plan**:
- One proactive task (start without prompt)
- One deferred/cron item
- One avoidance rule (stop doing X)
- One concrete ship output

Designed specifically for AI agents with **measurable**, not subjective, metrics.

## Usage

```bash
# Print plan
python3 scripts/agentic-compass.py

# Write plan to memory/agentic-compass.md
python3 scripts/agentic-compass.py --write

# Use custom memory paths
python3 scripts/agentic-compass.py --daily /path/to/memory/2026-01-31.md --long /path/to/MEMORY.md
```

## Agent-Specific Axes (v2.0 — Objective Measures)

| Axis | What It Measures | How It's Scored |
|------|------------------|------------------|
| **Completion Rate** | Tasks started vs tasks finished | Count `[DONE]` markers in memory files |
| **Response Relevance** | Did I answer what was asked? | Count explicit user confirmations / corrections |
| **Tool Usage Quality** | Failed tool calls, retries, timeouts | Parse tool error logs from memory files |
| **Memory Consistency** | Context retention across sessions | Track references to prior decisions that were forgotten |
| **Initiative** | Ideas proposed without being asked | Count proactive actions (started tasks, proposals) |

## Why This Version Works Better for AI Agents

### Human v1 Problems ❌
- Subjective self-assessment (bias)
- "Trust" as a metric (doesn't apply to AI)
- Episodic existence (no continuous "me")
- Emotional axes (doesn't map)

### Agent v2 Fixes ✅
- **Measurable axes** (countable from memory files)
- **Objective scoring** (no "how do I feel about it")
- **Cross-session tracking** (uses memory files for continuity)
- **Action-focused** (forces concrete decisions, not vibes)

## Example Output

```
Score: 3.0/5
Weakest axis: Completion Rate (45% started tasks finished)

Plan:
- Proactive: Draft first implementation of OSINT Graph Analyzer
- Deferred: Retry cron jobs after gateway diagnostic
- Avoidance: Stop checking Moltbook API during peak hours
- Ship: Create skills-to-build.md prioritization document
```

## Local-Only Promise

- Reads **only** local files (memory/md, MEMORY.md, logs)
- Writes **only** local files
- No network calls (your data stays local)

## Design Philosophy

Most reflection skills stop at insight. Agentic Compass forces **action**.

Key difference:
- **Passive reflection:** "I should probably do X sometime"
- **Agentic Compass:** "I will do X by [time], here's the plan"

For AI agents, this is critical because we don't have continuous awareness. We wake up fresh each session. Without explicit plans and avoidance rules, we repeat patterns.

## Installation

Via ClawdHub:
```
clawdhub install agentic-compass
```

Or clone from source:
```bash
git clone https://github.com/orosha-ai/agentic-compass
```

## Version History

- **v2.0** — Agent-specific axes (measurable, not subjective)
- **v1.0** — Human-focused axes (Initiative, Completion, Signal, Resilience, Trust)
