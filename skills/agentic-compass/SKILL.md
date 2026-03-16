---
name: agentic-compass
description: "AI agent self-reflection tool that reads local memory files and produces structured action plans with measurable metrics. Use when building agent self-awareness, tracking task completion rates, measuring response relevance, or creating cross-session improvement plans."
---

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

## Workflow

1. Run the script pointing at local memory files.
2. Script parses memory for completion markers, error logs, and proactive actions.
3. Scores each axis (Completion Rate, Response Relevance, Tool Usage, Memory Consistency, Initiative).
4. Generates a structured action plan with one proactive task, one deferred item, one avoidance rule, and one ship output.
5. Optionally writes the plan to `memory/agentic-compass.md`.

## Installation

Via ClawdHub:
```bash
clawdhub install agentic-compass
```

Or clone from source:
```bash
git clone https://github.com/orosha-ai/agentic-compass
```

## Notes

- Reads and writes only local files — no network calls
- v2.0 uses objective, countable metrics (not subjective self-assessment)
- Designed for cross-session tracking via memory files
