---
name: openspec
description: Spec-driven development with OpenSpec CLI. Use when building features, migrations, refactors, or any structured development work. Manages proposal → specs → design → tasks → implementation workflows. Supports custom schemas (TDD, rapid, etc.). Trigger on requests involving feature planning, spec writing, change management, or when /opsx commands are mentioned.
---

# OpenSpec — Spec-Driven Development

OpenSpec structures AI-assisted development into trackable changes with artifacts (proposal, specs, design, tasks) that guide implementation.

## Setup

```bash
# Install globally
npm install -g @fission-ai/openspec@latest

# Initialize in a project
cd /path/to/project
openspec init --tools claude

# Update after CLI upgrade
openspec update
```

## Core Workflow

Each change follows: **new → plan → apply → verify → archive**

### 1. Start a Change

```bash
# Create change folder with default schema
openspec new change <name>

# With specific schema
openspec new change <name> --schema tdd-driven
```

### 2. Plan (Create Artifacts)

Use the CLI `instructions` command to get enriched prompts for each artifact:

```bash
# Get instructions for next artifact
openspec instructions --change <name> --json

# Check progress
openspec status --change <name> --json
```

**Artifact sequence (spec-driven schema):**
1. `proposal.md` — Why and what (intent, scope, approach)
2. `specs/` — Requirements + scenarios (Given/When/Then)
3. `design.md` — Technical approach and architecture decisions
4. `tasks.md` — Implementation checklist with checkboxes

### 3. Implement

Read `tasks.md` and work through items, marking `[x]` as complete.

### 4. Verify

```bash
openspec validate --change <name> --json
```

Checks completeness, correctness, and coherence.

### 5. Archive

```bash
openspec archive <name> --yes
```

Merges delta specs into main `openspec/specs/` and moves change to archive.

## Agent Workflow (How to Use as an AI Agent)

When the user asks to build/migrate/refactor something with OpenSpec:

1. **Check project state:**
   ```bash
   openspec list --json           # Active changes
   openspec list --specs --json   # Current specs
   openspec schemas --json        # Available schemas
   ```

2. **Create the change:**
   ```bash
   openspec new change <name> [--schema <schema>]
   ```

3. **For each artifact**, get instructions and create the file:
   ```bash
   openspec instructions <artifact> --change <name> --json
   openspec status --change <name> --json
   ```
   Then write the artifact file to `openspec/changes/<name>/`.

4. **Implement** tasks from `tasks.md`.

5. **Validate and archive:**
   ```bash
   openspec validate <name> --json
   openspec archive <name> --yes
   ```

## CLI Quick Reference

| Command | Purpose |
|---------|---------|
| `openspec list [--specs] [--json]` | List changes or specs |
| `openspec show <name> [--json]` | Show change/spec details |
| `openspec status --change <name> [--json]` | Artifact completion status |
| `openspec instructions [artifact] --change <name> [--json]` | Get enriched creation instructions |
| `openspec validate [name] [--all] [--json]` | Validate changes/specs |
| `openspec archive <name> [--yes]` | Archive completed change |
| `openspec schemas [--json]` | List available schemas |
| `openspec templates [--json]` | Show template paths |
| `openspec config` | View/modify settings |

Always use `--json` for programmatic/agent use.

## Custom Schemas

Schemas define artifact sequences. Create custom ones for different workflows:

```bash
# Fork built-in schema
openspec schema fork spec-driven my-workflow

# Create from scratch
openspec schema init my-workflow

# Validate
openspec schema validate my-workflow
```

Schema files live in `openspec/schemas/<name>/schema.yaml` with templates in `templates/`.

For schema structure details, see [references/schemas.md](references/schemas.md).

## Project Structure

```
project/
├── openspec/
│   ├── config.yaml          # Project config (default schema, context, rules)
│   ├── specs/               # Source of truth — current system behavior
│   ├── changes/             # Active changes (one folder each)
│   │   └── <change-name>/
│   │       ├── .openspec.yaml
│   │       ├── proposal.md
│   │       ├── specs/       # Delta specs (what's changing)
│   │       ├── design.md
│   │       └── tasks.md
│   └── schemas/             # Custom schemas
└── .claude/skills/          # Auto-generated Claude integration
```

## Spec Format

Specs use RFC 2119 keywords (SHALL/MUST/SHOULD/MAY) with Given/When/Then scenarios:

```markdown
### Requirement: User Authentication
The system SHALL issue a JWT token upon successful login.

#### Scenario: Valid credentials
- GIVEN a user with valid credentials
- WHEN the user submits login form
- THEN a JWT token is returned
```

## Delta Specs

Changes don't rewrite specs — they describe deltas (ADDED/MODIFIED/REMOVED) that merge into main specs on archive.

## Config

`openspec/config.yaml` sets defaults:

```yaml
schema: spec-driven      # or tdd-driven, rapid, custom
context: |
  Tech stack: TypeScript, React, Node.js
  Testing: Jest
rules:
  proposal:
    - Include rollback plan
  specs:
    - Use Given/When/Then format
```
