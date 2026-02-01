# pltr-cli Claude Code Skill

This directory contains a Claude Code skill for working with Palantir Foundry using the pltr-cli.

## Installation

### Use Within This Repository

The skill is automatically available when using Claude Code in this repository.

### Install Globally

```bash
cp -r claude_skill ~/.claude/skills/pltr
```

## Structure

```
claude_skill/
├── SKILL.md                    # Main skill definition
├── reference/                  # Command references (loaded on-demand)
│   ├── quick-start.md         # Setup and authentication
│   ├── dataset-commands.md    # Dataset operations
│   ├── sql-commands.md        # SQL queries
│   ├── orchestration-commands.md  # Builds, jobs, schedules
│   ├── ontology-commands.md   # Ontology operations
│   ├── admin-commands.md      # User/group management
│   ├── filesystem-commands.md # Folders, spaces, projects
│   ├── connectivity-commands.md   # Connections, imports
│   └── mediasets-commands.md  # Media operations
└── workflows/                  # Common patterns
    ├── data-analysis.md       # Analysis workflows
    ├── data-pipeline.md       # ETL and pipelines
    └── permission-management.md   # Access control
```

## Usage

Ask Claude Code questions about Foundry tasks:

- "How do I query a dataset?"
- "Help me set up a daily build schedule"
- "Grant viewer access to john.doe on my dataset"
- "Execute SQL query to count rows"

Claude will automatically use this skill to provide accurate guidance.

## Documentation

See [docs/user-guide/claude-skill.md](../docs/user-guide/claude-skill.md) for full documentation.
