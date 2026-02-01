---
name: pltr-cli
description: Helps you work with Palantir Foundry using the pltr CLI. Use this when you need to query datasets, manage orchestration builds, work with ontologies, run SQL queries, manage folders/spaces/projects, copy datasets, or perform admin operations in Foundry. Triggers: Foundry, pltr, dataset, SQL query, ontology, build, schedule, RID.
---

# pltr-cli: Palantir Foundry CLI

This skill helps you use the pltr-cli to interact with Palantir Foundry effectively.

## Compatibility

- **Skill version**: 1.1.0
- **pltr-cli version**: 0.12.0+
- **Python**: 3.9, 3.10, 3.11, 3.12
- **Dependencies**: foundry-platform-sdk >= 1.69.0

## Overview

pltr-cli is a comprehensive CLI with 100+ commands for:
- **Dataset operations**: Get info, list files, download files, manage branches and transactions
- **SQL queries**: Execute queries, export results, manage async queries
- **Ontology**: List ontologies, object types, objects, execute actions and queries
- **Orchestration**: Manage builds, jobs, and schedules
- **Filesystem**: Folders, spaces, projects, resources
- **Admin**: User, group, role management
- **Connectivity**: External connections and data imports
- **MediaSets**: Media file management
- **Language Models**: Interact with Anthropic Claude models and OpenAI embeddings
- **Streams**: Create and manage streaming datasets, publish real-time data
- **Functions**: Execute queries and inspect value types
- **AIP Agents**: Manage AI agents, sessions, and versions
- **Models**: ML model registry for model and version management

## Critical Concepts

### RID-Based API
The Foundry API is **RID-based** (Resource Identifier). Most commands require RIDs:
- **Datasets**: `ri.foundry.main.dataset.{uuid}`
- **Folders**: `ri.compass.main.folder.{uuid}` (root: `ri.compass.main.folder.0`)
- **Builds**: `ri.orchestration.main.build.{uuid}`
- **Schedules**: `ri.orchestration.main.schedule.{uuid}`
- **Ontologies**: `ri.ontology.main.ontology.{uuid}`

Users must know RIDs in advance (from Foundry web UI or previous API calls).

### Authentication
Before using any command, ensure authentication is configured:
```bash
# Configure interactively
pltr configure configure

# Or use environment variables
export FOUNDRY_TOKEN="your-token"
export FOUNDRY_HOST="foundry.company.com"

# Verify connection
pltr verify
```

### Output Formats
All commands support multiple output formats:
```bash
pltr <command> --format table    # Default: Rich table
pltr <command> --format json     # JSON output
pltr <command> --format csv      # CSV format
pltr <command> --output file.csv # Save to file
```

### Profile Selection
Use `--profile` to switch between Foundry instances:
```bash
pltr <command> --profile production
pltr <command> --profile development
```

## Reference Files

Load these files based on the user's task:

| Task Type | Reference File |
|-----------|----------------|
| Setup, authentication, getting started | `reference/quick-start.md` |
| Dataset operations (get, files, branches, transactions) | `reference/dataset-commands.md` |
| SQL queries | `reference/sql-commands.md` |
| Builds, jobs, schedules | `reference/orchestration-commands.md` |
| Ontologies, objects, actions | `reference/ontology-commands.md` |
| Users, groups, roles, orgs | `reference/admin-commands.md` |
| Folders, spaces, projects, resources, permissions | `reference/filesystem-commands.md` |
| Connections, imports | `reference/connectivity-commands.md` |
| Media sets, media items | `reference/mediasets-commands.md` |
| Anthropic Claude models, OpenAI embeddings | `reference/language-models-commands.md` |
| Streaming datasets, real-time data publishing | `reference/streams-commands.md` |
| Functions queries, value types | `reference/functions-commands.md` |
| AIP Agents, sessions, versions | `reference/aip-agents-commands.md` |
| ML model registry, model versions | `reference/models-commands.md` |

## Workflow Files

For common multi-step tasks:

| Workflow | File |
|----------|------|
| Data exploration, SQL analysis, ontology queries | `workflows/data-analysis.md` |
| ETL pipelines, scheduled jobs, data quality | `workflows/data-pipeline.md` |
| Setting up permissions, resource roles, access control | `workflows/permission-management.md` |

## Common Commands Quick Reference

```bash
# Verify setup
pltr verify

# Current user info
pltr admin user current

# Execute SQL query
pltr sql execute "SELECT * FROM my_table LIMIT 10"

# Get dataset info
pltr dataset get ri.foundry.main.dataset.abc123

# List files in dataset
pltr dataset files list ri.foundry.main.dataset.abc123

# Download file from dataset
pltr dataset files get ri.foundry.main.dataset.abc123 "/path/file.csv" "./local.csv"

# Copy dataset to another folder
pltr cp ri.foundry.main.dataset.abc123 ri.compass.main.folder.target456

# List folder contents
pltr folder list ri.compass.main.folder.0  # root folder

# Search builds
pltr orchestration builds search

# Interactive shell mode
pltr shell

# Send message to Claude model
pltr language-models anthropic messages ri.language-models.main.model.xxx \
    --message "Explain this concept"

# Generate embeddings
pltr language-models openai embeddings ri.language-models.main.model.xxx \
    --input "Sample text"

# Create streaming dataset
pltr streams dataset create my-stream \
    --folder ri.compass.main.folder.xxx \
    --schema '{"fieldSchemaList": [{"name": "value", "type": "STRING"}]}'

# Publish record to stream
pltr streams stream publish ri.foundry.main.dataset.xxx \
    --branch master \
    --record '{"value": "hello"}'

# Execute a function query
pltr functions query execute myQuery --parameters '{"limit": 10}'

# Get AIP Agent info
pltr aip-agents get ri.foundry.main.agent.abc123

# List agent sessions
pltr aip-agents sessions list ri.foundry.main.agent.abc123

# Get ML model info
pltr models model get ri.foundry.main.model.abc123

# List model versions
pltr models version list ri.foundry.main.model.abc123
```

## Best Practices

1. **Always verify authentication first**: Run `pltr verify` before starting work
2. **Use appropriate output format**: JSON for programmatic use, CSV for spreadsheets, table for readability
3. **Use async for large queries**: `pltr sql submit` + `pltr sql wait` for long-running queries
4. **Export results**: Use `--output` to save results for further analysis
5. **Use shell mode for exploration**: `pltr shell` provides tab completion and history

## Getting Help

```bash
pltr --help                    # All commands
pltr <command> --help          # Command help
pltr <command> <sub> --help    # Subcommand help
```
