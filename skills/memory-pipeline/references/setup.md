# Memory Pipeline Setup Guide

Complete setup instructions for the memory-pipeline skill.

## Prerequisites

1. **Python 3.8+** with `requests` library
2. **LLM API Key** — At least one of:
   - OpenAI (recommended — enables embeddings for better linking)
   - Anthropic (Claude Haiku)
   - Gemini (Flash)

## Installation Steps

### 1. Install the Skill

If you received a `.skill` file:
```bash
clawdbot skills install memory-pipeline.skill
```

Or if working with source:
```bash
# Copy to your skills directory
cp -r memory-pipeline ~/.clawdbot/skills/
```

### 2. Set Up API Keys

Choose one (or more) providers:

**OpenAI** (recommended for embeddings):
```bash
# Via environment
export OPENAI_API_KEY="sk-..."

# Via config file
mkdir -p ~/.config/openai
echo "sk-..." > ~/.config/openai/api_key
chmod 600 ~/.config/openai/api_key
```

**Anthropic:**
```bash
export ANTHROPIC_API_KEY="sk-ant-..."
# OR
mkdir -p ~/.config/anthropic
echo "sk-ant-..." > ~/.config/anthropic/api_key
chmod 600 ~/.config/anthropic/api_key
```

**Gemini:**
```bash
export GEMINI_API_KEY="..."
# OR
mkdir -p ~/.config/gemini
echo "..." > ~/.config/gemini/api_key
chmod 600 ~/.config/gemini/api_key
```

### 3. Install Python Dependencies

```bash
pip3 install requests
```

### 4. Make Scripts Executable

```bash
cd ~/.clawdbot/skills/memory-pipeline/scripts
chmod +x memory-extract.py memory-link.py memory-briefing.py
```

### 5. Test the Pipeline

Run each script to verify setup:

```bash
cd ~/.clawdbot/skills/memory-pipeline/scripts

# Extract facts
./memory-extract.py

# Build knowledge graph (requires extracted facts)
./memory-link.py

# Generate briefing (works even without facts)
./memory-briefing.py
```

Check the output:
```bash
ls -lh ~/workspace/memory/
cat ~/workspace/BRIEFING.md
```

## Workspace Setup

The scripts auto-detect your workspace, but you can set it explicitly:

```bash
export CLAWDBOT_WORKSPACE="/path/to/your/workspace"
```

Or create the standard workspace:
```bash
mkdir -p ~/.clawdbot/workspace/memory
```

### Expected Workspace Structure

```
workspace/
├── SOUL.md              # Personality definition (optional)
├── USER.md              # User context (optional)
├── IDENTITY.md          # Agent identity (optional)
├── BRIEFING.md          # Generated daily briefing (output)
├── todos.md             # Task lists (optional)
├── memory/
│   ├── YYYY-MM-DD.md    # Daily notes (input)
│   ├── extracted.jsonl  # Extracted facts (output)
│   ├── knowledge-graph.json  # Knowledge graph (output)
│   └── knowledge-summary.md  # Summary (output)
└── ...
```

Session transcripts are read from:
```
~/.clawdbot/agents/main/sessions/*.jsonl
```

## Automation with HEARTBEAT.md

Add to your workspace's `HEARTBEAT.md` to run automatically:

```markdown
# Heartbeat Tasks

Check these tasks periodically (2-4x per day) and rotate through them:

## Memory Consolidation (Daily)

Run once per day, preferably in the morning:

**Check time:** If it's after 8:00 AM and hasn't run today, proceed.

**Steps:**
1. Extract facts from yesterday's notes:
   ```bash
   cd $CLAWDBOT_WORKSPACE && python3 ~/.clawdbot/skills/memory-pipeline/scripts/memory-extract.py
   ```

2. Build knowledge graph:
   ```bash
   cd $CLAWDBOT_WORKSPACE && python3 ~/.clawdbot/skills/memory-pipeline/scripts/memory-link.py
   ```

3. Generate fresh briefing:
   ```bash
   cd $CLAWDBOT_WORKSPACE && python3 ~/.clawdbot/skills/memory-pipeline/scripts/memory-briefing.py
   ```

**Track execution:** Update `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "memory_consolidation": 1703275200
  }
}
```

## Weekly Review (Optional)

Once per week (Sunday evening):
- Read `memory/knowledge-summary.md` for insights
- Review recent decisions in `extracted.jsonl`
- Archive or clean up old daily notes (>30 days)
```

### Tracking Execution

To prevent duplicate runs, maintain state in `memory/heartbeat-state.json`:

```python
import json
import time
from pathlib import Path

state_file = Path("memory/heartbeat-state.json")
state = json.loads(state_file.read_text()) if state_file.exists() else {}

# Check last run
last_run = state.get("lastChecks", {}).get("memory_consolidation", 0)
now = int(time.time())

# Only run if >18 hours since last run
if now - last_run > 18 * 3600:
    # Run pipeline
    ...
    
    # Update state
    state.setdefault("lastChecks", {})["memory_consolidation"] = now
    state_file.write_text(json.dumps(state, indent=2))
```

## Daily Note Format

The extraction works best with structured daily notes. Example format:

```markdown
# 2025-01-15

## Conversations
- Discussed memory pipeline implementation with user
- Decided to use multi-provider LLM support (OpenAI, Anthropic, Gemini)
- User prefers auto-detection of workspace paths over hardcoded values

## Decisions
- Will package memory-pipeline as a Clawdbot skill
- Scripts should be generalized, not tied to specific personalities
- BRIEFING.md generation should read SOUL.md for personality hints

## Learnings
- Clawdbot skills use YAML frontmatter in SKILL.md for triggering
- The progressive disclosure pattern keeps context window efficient
- Skills can bundle scripts, references, and assets

## Todos
- [ ] Test scripts parse without errors
- [ ] Package skill with package_skill.py
- [ ] Document setup steps in references/setup.md
```

## Output Files Explained

### extracted.jsonl

JSONL file (one JSON object per line) containing all extracted facts:

```json
{"type": "decision", "content": "Will use multi-provider LLM support", "subject": "memory-pipeline", "confidence": 0.9, "date": "2025-01-15", "source": "daily-note"}
{"type": "learning", "content": "Clawdbot skills use progressive disclosure to manage context", "subject": "Clawdbot", "confidence": 0.85, "date": "2025-01-15", "source": "daily-note"}
```

This file is **append-only** and **deduplicated** — new facts are only added if they don't already exist.

### knowledge-graph.json

Full knowledge graph structure:

```json
{
  "nodes": [
    {
      "id": 0,
      "type": "decision",
      "content": "...",
      "subject": "...",
      "date": "2025-01-15",
      "confidence": 0.9,
      "keywords": ["keyword1", "keyword2"],
      "tags": ["decision", "project-name"],
      "embedding": [0.123, -0.456, ...],
      "links": [1, 5, 12]
    }
  ],
  "links": [
    {
      "source": 0,
      "target": 1,
      "strength": 0.85,
      "type": "related"
    }
  ],
  "metadata": {
    "created": "2025-01-15T10:30:00",
    "total_facts": 42,
    "has_embeddings": true
  }
}
```

### knowledge-summary.md

Human-readable summary organized by:
- Facts grouped by subject
- Recent decisions
- Recent learnings
- Contradiction tracking

### BRIEFING.md

Daily briefing loaded at session start (requires OpenClaw context loading).

Example output:

```markdown
# BRIEFING.md
*Auto-generated 2025-01-15 10:30*

## Personality Quick-Check
- Professional but direct communication style
- Prefers efficiency over verbosity
- Values technical accuracy

## Active Projects
- **memory-pipeline**: Implementing generalized memory consolidation system
- **Clawdbot**: Contributing skills and improvements
- **documentation**: Writing setup guides and references

## Recent Decisions
- Will package memory-pipeline as installable skill
- Scripts auto-detect workspace paths instead of hardcoding
- Support multiple LLM providers for flexibility

## Key Context
- Working with Clawdbot skill system
- Following progressive disclosure pattern for documentation
- API keys set via environment or ~/.config files

## Don't Forget
- Check `memory_search` BEFORE answering questions about past work
- Write important decisions and learnings to daily notes
```

## Troubleshooting

### "No source text found to extract from"

**Cause:** No daily notes or session transcripts exist.

**Solution:**
1. Create a daily note: `echo "# $(date +%Y-%m-%d)" > workspace/memory/$(date +%Y-%m-%d).md`
2. Or wait for session transcripts to accumulate in `~/.clawdbot/agents/main/sessions/`

### "No API key found"

**Cause:** No LLM API key configured.

**Solution:** Set one of the API keys as shown in step 2 above.

### "Embedding error" or low-quality links

**Cause:** OpenAI API key not available (falling back to keyword similarity).

**Solution:** Add OpenAI API key for better embedding-based linking.

### Scripts not executable

**Cause:** File permissions.

**Solution:**
```bash
chmod +x ~/.clawdbot/skills/memory-pipeline/scripts/*.py
```

### Empty or poor quality briefing

**Cause:** Not enough extracted facts or LLM generation failed.

**Solution:**
1. Run `memory-extract.py` first to populate facts
2. Check API key is working
3. Falls back to template-based briefing if LLM fails (this is expected behavior)

## Advanced Configuration

### Custom Workspace Location

Set explicitly in scripts or via environment:

```bash
export CLAWDBOT_WORKSPACE="/custom/path"
```

### Different LLM Models

Edit the scripts to use different models:

**memory-extract.py:**
- Line ~75: Change `"model": "gpt-4o-mini"` to your preferred model

**memory-link.py:**
- Line ~60: Change `"model": "text-embedding-3-small"` for embeddings

**memory-briefing.py:**
- Line ~145: Change model for briefing generation

### Extraction Prompt Customization

Edit `memory-extract.py` around line 75-85 to customize what gets extracted:

```python
prompt = f"""Extract structured facts focusing on:
- Technical decisions and architecture choices
- API integrations and their configurations
- Performance metrics and optimizations
- Bug fixes and their root causes

For each fact, output JSON with: type, content, subject, confidence

Text to analyze:
{text[:8000]}"""
```

### Link Similarity Threshold

In `memory-link.py` line ~195:

```python
# Default: 0.3 (30% similarity)
if similarity > 0.3:  # Adjust this value
    # Create link
```

Lower = more links (potentially noisy)  
Higher = fewer links (potentially missing connections)

## Integration with Other Skills

The memory-pipeline outputs can be used by other skills:

**memory_search skill** (if available):
- Query `extracted.jsonl` for past facts
- Search `knowledge-graph.json` for related information

**context-manager skill** (if available):
- Load relevant sections from `knowledge-summary.md`
- Include BRIEFING.md in session context

**agent-reflection skill** (if available):
- Analyze `knowledge-graph.json` for patterns
- Identify gaps in knowledge or contradictions

## Migration from Existing Systems

If you have existing memory files:

1. **Convert to daily notes format:**
   ```bash
   # Your existing notes → memory/YYYY-MM-DD.md format
   ```

2. **Run initial extraction:**
   ```bash
   ./memory-extract.py
   ```

3. **Build graph:**
   ```bash
   ./memory-link.py
   ```

The system is additive — it won't break existing files.
