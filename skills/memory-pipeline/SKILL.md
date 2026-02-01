---
name: memory-pipeline
description: Complete agent memory + performance system. Extracts structured facts, builds knowledge graphs, generates briefings, and enforces execution discipline via pre-game routines, tool policies, result compression, and after-action reviews. Includes external knowledge ingestion (ChatGPT exports, etc.) into searchable memory. Use when working on memory management, briefing generation, knowledge consolidation, external data ingestion, agent consistency, or improving execution quality across sessions.
---

# Memory Pipeline + Performance Routine

A complete memory and performance system for AI agents. Two subsystems, one package:

- **Memory Pipeline** (Python scripts) — Extracts facts, builds knowledge graphs, generates daily briefings
- **Knowledge Ingestion** (Python scripts) — Imports external data (ChatGPT exports, etc.) into searchable memory
- **Performance Routine** (TypeScript hooks) — Pre-game briefing injection, tool discipline, output compression, after-action review

## What This Does

### Memory Pipeline (Between Sessions)

A three-stage system that helps AI agents maintain long-term memory:

1. **Extract** — Pulls structured facts (decisions, preferences, learnings, commitments) from daily notes and session transcripts using LLM extraction
2. **Link** — Builds a knowledge graph with embeddings and bidirectional links between related facts, identifies contradictions
3. **Briefing** — Generates a compact BRIEFING.md file loaded at session start with personality reminders, active projects, recent decisions, and key context

### Performance Routine (Within Sessions)

Four lifecycle hooks that enforce consistency during agent runs:

1. **Pre-Game Routine** (`before_agent_start`) — Assembles a bounded briefing packet from memory files + checklist, injects into system prompt
2. **Tool Discipline** (`before_tool_call`) — Enforces deny lists, normalizes params, prevents unsafe tool calls
3. **Output Compression** (`tool_result_persist`) — Head+tail compression of large tool results to prevent context bloat
4. **After-Action Review** (`agent_end`) — Writes durable notes about what happened, tools used, and outcomes

## Quick Start

### One-Command Setup

```bash
clawhub install memory-pipeline
bash skills/memory-pipeline/scripts/setup.sh
```

The setup script will:
- Detect your workspace automatically
- Check for Python 3 and an LLM API key
- Create the `memory/` directory
- Find existing notes or help you create a starter note
- Run the full pipeline (extract → link → briefing)
- Show you what was generated and what to do next

### Requirements

**Python 3** and **at least one LLM API key**:
- OpenAI (`OPENAI_API_KEY` or `~/.config/openai/api_key`)
- Anthropic (`ANTHROPIC_API_KEY` or `~/.config/anthropic/api_key`)
- Gemini (`GEMINI_API_KEY` or `~/.config/gemini/api_key`)

The scripts auto-detect whichever key is available.

### Manual Usage

If you prefer to run steps individually:
```bash
python3 skills/memory-pipeline/scripts/memory-extract.py
python3 skills/memory-pipeline/scripts/memory-link.py
python3 skills/memory-pipeline/scripts/memory-briefing.py
```

## External Knowledge Ingestion

Import data from external sources into the memory system. Ingested files land in `memory/knowledge/` and are automatically indexed by Clawdbot's semantic search (`memory_search`).

### ChatGPT Export

**Script:** `ingest-chatgpt.py`

Parses a ChatGPT data export and converts conversations into searchable markdown files.

**Usage:**
```bash
# From a zip (direct from ChatGPT export email)
python3 skills/memory-pipeline/scripts/ingest-chatgpt.py ~/imports/chatgpt-export.zip

# From extracted conversations.json
python3 skills/memory-pipeline/scripts/ingest-chatgpt.py ~/imports/conversations.json

# Preview without writing files
python3 skills/memory-pipeline/scripts/ingest-chatgpt.py ~/imports/conversations.json --dry-run

# Keep everything (no filtering)
python3 skills/memory-pipeline/scripts/ingest-chatgpt.py ~/imports/conversations.json --keep-all

# Stricter filtering (5+ turns, 500+ chars)
python3 skills/memory-pipeline/scripts/ingest-chatgpt.py ~/imports/conversations.json --min-turns 5 --min-length 500
```

**How to export from ChatGPT:**
1. Go to ChatGPT → Settings → Data Controls → Export Data
2. OpenAI emails you a zip file
3. Download and pass the zip (or extracted `conversations.json`) to the script

**What it does:**
- Parses the conversation tree structure from ChatGPT's export format
- Extracts title, date, and full Q&A content from each conversation
- Filters out short/throwaway conversations (configurable thresholds)
- Supports topic exclusion filters (edit `EXCLUDE_PATTERNS` in the script to skip unwanted topics)
- Generates clean markdown files with date-prefixed slugified filenames
- Outputs to `memory/knowledge/chatgpt/`

**Output format:**
```markdown
# Conversation Title
**Source:** ChatGPT | **Date:** 2025-03-15 | **Turns:** 8

## Q: User's question here
...

Assistant's response here
...
```

**Topic exclusion:** The script includes an `EXCLUDE_PATTERNS` list for filtering out conversations by keyword (checked against title + first few user messages). Edit the list in the script to customize which topics get excluded.

**After ingestion:** Files in `memory/knowledge/` are automatically picked up by Clawdbot's memory indexer on the next sync cycle. Once indexed, all conversations become searchable via `memory_search`.

### Adding Other Sources

The ingestion pattern is extensible. To add a new source (e.g., Google Search history, Notion exports, browser bookmarks):

1. Create a new `ingest-<source>.py` script in `scripts/`
2. Parse the source format into structured entries
3. Write markdown files to `memory/knowledge/<source>/`
4. Follow the same format: title, date, source metadata, content

The key principle: **chunk by topic, write as markdown, let the indexer handle search.**

---

## Pipeline Stages

### Stage 1: Extract Facts

**Script:** `memory-extract.py`

Reads from (in priority order):
1. Daily memory files (`{workspace}/memory/YYYY-MM-DD.md`) — today or yesterday
2. Session transcripts (`~/.clawdbot/agents/main/sessions/*.jsonl`)

Extracts structured facts:
- **Type**: decision, preference, learning, commitment, fact
- **Content**: The actual information
- **Subject**: What it's about (auto-detected from context)
- **Confidence**: 0.0-1.0 reliability score

**Output:** `{workspace}/memory/extracted.jsonl` — One JSON fact per line, deduplicated

### Stage 2: Build Knowledge Graph

**Script:** `memory-link.py`

Takes extracted facts and:
- Generates embeddings (if OpenAI key available, else uses keyword similarity)
- Creates bidirectional links between related facts
- Detects contradictions and marks superseded facts
- Auto-generates domain tags from content

**Output:**
- `{workspace}/memory/knowledge-graph.json` — Full graph with nodes and links
- `{workspace}/memory/knowledge-summary.md` — Human-readable summary

### Stage 3: Generate Briefing

**Script:** `memory-briefing.py`

Creates a compact daily briefing loaded at session start.

Combines:
- Personality traits (from SOUL.md if exists)
- User context (from USER.md if exists)
- Active projects (top subjects from recent facts)
- Recent decisions and preferences
- Active todos (from any todos*.md files)

**Output:** `{workspace}/BRIEFING.md` — Under 2000 chars, LLM-generated or template-based

## Wiring Into HEARTBEAT.md

To run automatically, add to your workspace's `HEARTBEAT.md`:

```markdown
# Heartbeat Tasks

## Daily (once per day, morning)
- Run memory extraction: `cd {workspace} && python3 skills/memory-pipeline/scripts/memory-extract.py`
- Build knowledge graph: `cd {workspace} && python3 skills/memory-pipeline/scripts/memory-link.py`
- Generate briefing: `cd {workspace} && python3 skills/memory-pipeline/scripts/memory-briefing.py`

## Weekly (Sunday evening)
- Review `memory/knowledge-summary.md` for insights
- Clean up old daily notes (optional)
```

## Loading BRIEFING.md

**Important:** BRIEFING.md needs to be loaded as workspace context at session start. This requires the OpenClaw context loading feature (currently in development).

Once available, configure your agent to load BRIEFING.md along with SOUL.md, USER.md, and AGENTS.md at the start of each session.

## Output Files

All files are created in `{workspace}/memory/`:

- **extracted.jsonl** — All extracted facts (append-only)
- **knowledge-graph.json** — Full knowledge graph with embeddings and links
- **knowledge-summary.md** — Human-readable summary of the graph
- **BRIEFING.md** (in workspace root) — Daily context cheat sheet

## Customization

### Changing Models

Edit the model names in each script:
- `memory-extract.py`: Lines with `"model": "gpt-4o-mini"` (or claude/gemini equivalents)
- `memory-link.py`: Line with `"model": "text-embedding-3-small"`
- `memory-briefing.py`: Lines with `"model": "gpt-4o-mini"`

### Adjusting Extraction

In `memory-extract.py`, modify the extraction prompt (lines ~75-85) to focus on different types of information or change the output format.

### Link Threshold

In `memory-link.py`, change the similarity threshold for creating links (currently 0.3 at line ~195).

## Troubleshooting

**No facts extracted:**
- Check that daily notes or transcripts exist
- Verify API key is set correctly
- Check script output for LLM errors

**Low-quality links:**
- Add OpenAI API key for embedding-based similarity (more accurate than keyword matching)
- Adjust similarity threshold in `memory-link.py`

**Briefing too long:**
- Reduce number of facts included in template (edit `generate_fallback_briefing`)
- LLM-generated briefings are automatically constrained to 2000 chars

## Performance Routine (Hook System)

The performance routine is implemented as OpenClaw lifecycle hooks in `src/`. It applies a core principle from performance psychology: **separate thinking from doing**. Athletes don't redesign their technique mid-game — they prepare (purposeful thinking), then execute trained sequences (reactive execution). The only exception is genuine error handling.

For agents, this means: front-load all context, constraints, and memory retrieval into a briefing packet *before* inference starts. Keep execution clean. Write the after-action review *after*. Never inject corrections mid-run.

### Architecture

```
User Message → Gateway → Agent Loop
  ├── before_agent_start → Briefing Packet (checklist + memory + constraints)
  ├── LLM Inference (clean context, no mid-run corrections)
  ├── before_tool_call → Policy enforcement (deny list)
  ├── Tool Execution → Result
  ├── tool_result_persist → Compression (head+tail, bounded)
  └── agent_end → After-Action Review → durable memory for next run
```

### The Core Idea: No Mid-Swing Coaching

Constant correction during execution degrades output. Mid-run prompt patches create instruction collision — two competing directives the agent must reconcile instead of executing. The alternative:

1. **Capture corrections** — don't inject them into the current run
2. **Condense into deltas** — merge all corrections into a clean update
3. **Inject next run** — the next briefing packet includes the corrected instructions

The after-action review (`agent_end`) feeds back into the next briefing (`before_agent_start`). The loop is closed — just not during execution.

### Configuration

Configure via `openclaw.plugin.json` or your agent config:

```json
{
  "enabled": true,
  "briefing": {
    "maxChars": 6000,
    "checklist": [
      "Restate the task in one sentence.",
      "List constraints and success criteria.",
      "Retrieve only the minimum relevant memory.",
      "Prefer tools over guessing when facts matter."
    ],
    "memoryFiles": ["memory/IDENTITY.md", "memory/PROJECTS.md"]
  },
  "tools": {
    "deny": ["dangerous_tool"],
    "maxToolResultChars": 12000
  },
  "afterAction": {
    "writeMemoryFile": "memory/AFTER_ACTION.md",
    "maxBullets": 8
  }
}
```

### Hook Details

**`before_agent_start` — Briefing Packet**
- Loads configured memory files from workspace
- Builds bounded packet: task hint + checklist + retrieved memory
- Injects into system prompt (respects `maxChars` limit)
- Missing memory files are silently skipped

**`before_tool_call` — Tool Discipline**
- Checks tool name against `deny` list
- Throws error if denied (prevents execution)
- Extensible for param normalization

**`tool_result_persist` — Output Compression**
- Keeps results under `maxToolResultChars` (default 12K)
- Uses head (60%) + tail (30%) strategy
- Preserves structure for JSON results

**`after_action_review` — Durable Notes**
- Appends session summary to configured memory file
- Extracts key bullets from final answer
- Logs tools used (with failure flags)
- Creates directories automatically

### Source Files

- `src/index.ts` — Hook registration and wiring
- `src/briefing.ts` — Briefing packet builder
- `src/compress.ts` — Tool result compressor
- `src/memory.ts` — Memory file loader + after-action writer

## See Also

- [Setup Guide](references/setup.md) — Detailed installation and configuration
- [Blog Post Draft](../../drafts/blog-pregame-routine.md) — Full writeup of the performance routine concept
