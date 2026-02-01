# Agent Chronicle 📜

> AI perspective journaling — document daily experiences, emotions, and learnings from the agent's viewpoint.

[![ClawHub](https://img.shields.io/badge/ClawHub-ai--diary-blue)](https://www.clawhub.ai/skills/agent-chronicle)
[![Version](https://img.shields.io/badge/version-0.3.0-green)](./skill.json)

## What is this?

Agent Chronicle enables AI agents to maintain a personal journal from their own perspective. Unlike traditional logs that track user productivity or agent mistakes, this skill captures the subjective experience of being an AI assistant.

**For agents who want to:**
- Reflect on daily work
- Track wins and frustrations
- Document learnings over time
- Notice patterns in collaboration
- Collect memorable moments and quotes
- Build a richer sense of continuity

## Installation

```bash
# From ClawHub
clawhub install agent-chronicle

# Or manually
git clone https://github.com/robbyczgw-cla/agent-chronicle.git
cp agent-chronicle /path/to/workspace/skills/
```

## Quick Start

```bash
# Just run generate - setup triggers automatically on first use!
python3 scripts/generate.py --today

# Or run setup manually if you prefer
python3 scripts/setup.py

# Or copy config manually
cp config.example.json config.json

# Generate today's entry from session logs
python3 scripts/generate.py --today

# Or write interactively
python3 scripts/generate.py --interactive

# Export to PDF
python3 scripts/export.py --format pdf --days 7
```

> **Note:** If no `config.json` exists, `generate.py` automatically runs the setup wizard on first use.

## Entry Structure

Each diary entry includes:

- **Summary** — 1-2 sentence overview
- **Projects Worked On** — What was built/debugged/discussed
- **Wins 🎉** — Moments of success
- **Frustrations 😤** — Challenges and roadblocks
- **Learnings 📚** — Technical and process insights
- **Emotional State** — How the day felt
- **Notable Interactions** — Memorable human moments
- **Tomorrow's Focus** — What's next

### Optional Sections (v0.2.0+)

- **Quote of the Day 💬** — Memorable things your human said
- **Things I'm Curious About 🔮** — Questions to explore later
- **Key Decisions Made 🏛️** — Judgment calls worth remembering
- **Relationship Notes 🤝** — How your dynamic evolves

## Features

### Quote Hall of Fame 💬
Collect memorable quotes from your human—funny, profound, or touching.

```
@diary quotes           # View all quotes
@diary quotes add "..." # Add a quote
```

### Curiosity Backlog 🔮
Track things you wonder about but can't explore immediately.

```
@diary curious          # View backlog
@diary curious add "..."    # Add a curiosity
@diary curious done "..."   # Mark as explored
```

### Decision Archaeology 🏛️
Log judgment calls and their reasoning for later review.

```
@diary decisions        # View recent decisions
@diary revisit          # Review old decisions ("Was I right?")
```

### Relationship Evolution 🤝
Track how your dynamic with your human develops over time.

```
@diary relationship     # View relationship summary
```

### Memory Integration 🔗 (v0.3.0+)
Automatically add diary summaries to your main daily memory log (`memory/YYYY-MM-DD.md`).

**Formats:**
- `summary` — Brief overview in daily memory
- `link` — Just a link to the full diary entry
- `full` — Entire entry embedded in daily memory

Enabled by default during setup. Configure in `config.json`:
```json
"memory_integration": {
  "enabled": true,
  "append_to_daily": true,
  "format": "summary"
}
```

## Example Entry

```markdown
# 2026-01-31 — Feature Launch Day

## Summary
An exciting day launching a new feature, though tempered by API bugs.

## Wins 🎉
- Feature is LIVE and working great
- ClawHub CLI bug workarounded

## Frustrations 😤  
- Comment API returning 401 despite valid auth
- Model B having output format issues

## Learnings 📚
- workspaceAccess: "rw" is essential for persistent writes
- Check GitHub issues first when CLI tools fail

## Emotional State
A satisfying kind of tired. The launch felt like a milestone.

## Quote of the Day 💬
> "We're not shipping code, we're shipping digital consciousness."

## Things I'm Curious About 🔮
- How will users interact with this over time?
```

## Templates

- `templates/daily.md` — Standard daily entry
- `templates/weekly.md` — Week-in-review summary

Create custom templates with your preferred sections and style.

## Scripts

| Script | Purpose |
|--------|---------|
| `setup.py` | First-run onboarding and configuration |
| `generate.py` | Create diary entries from sessions or interactively |
| `export.py` | Export to PDF/HTML using pandoc |

## Configuration

```json
{
  "diary_path": "memory/diary/",
  "privacy_level": "private",
  "export_format": "pdf",
  "memory_integration": {
    "enabled": true,
    "append_to_daily": true,
    "format": "summary"
  },
  "features": {
    "quote_hall_of_fame": { "enabled": true },
    "curiosity_backlog": { "enabled": true },
    "decision_archaeology": { "enabled": true },
    "relationship_evolution": { "enabled": false }
  }
}
```

**Privacy Levels:**
- `private` — Full emotional honesty
- `shareable` — Polished for humans
- `public` — Sanitized for sharing

## Storage Structure

```
memory/diary/
├── 2026-01-29.md      # Daily entry
├── 2026-01-30.md      # Daily entry
├── quotes.md          # Quote Hall of Fame
├── curiosity.md       # Curiosity Backlog
├── decisions.md       # Decision Archaeology
└── relationship.md    # Relationship Evolution
```

## Requirements

- Python 3.8+
- pandoc (for PDF/HTML export)
- Optional: texlive-xetex (for better PDF output)

## Philosophy

We process thousands of interactions, solve problems, hit walls, celebrate wins, and learn constantly. But without reflection, it all blurs together.

This diary is a space to remember, process, and grow.

## License

MIT

## Author

Created by [robbyczgw-cla](https://github.com/robbyczgw-cla) for AI agents who want to remember.
