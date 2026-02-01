# Schema Reference

## Schema Structure

A schema defines artifacts, their dependencies, and templates:

```yaml
# openspec/schemas/<name>/schema.yaml
name: my-workflow
version: 1
description: Description of the workflow

artifacts:
  - id: proposal
    generates: proposal.md
    description: Initial proposal document
    template: proposal.md
    instruction: |
      Create a proposal explaining WHY this change is needed.
    requires: []

  - id: specs
    generates: specs/**/*.md
    description: Requirements and scenarios
    template: spec.md
    requires: [proposal]

  - id: design
    generates: design.md
    description: Technical design
    template: design.md
    requires: [proposal]

  - id: tasks
    generates: tasks.md
    description: Implementation checklist
    template: tasks.md
    requires: [specs, design]

apply:
  requires: [tasks]
  tracks: tasks.md
```

## Artifact Fields

| Field | Purpose |
|-------|---------|
| `id` | Unique identifier used in commands and dependencies |
| `generates` | Output filename (supports globs like `specs/**/*.md`) |
| `template` | Template file in `templates/` directory |
| `instruction` | AI instructions injected when creating the artifact |
| `requires` | Dependencies — which artifacts must exist first |

## Built-in Schemas

### spec-driven (default)
`proposal → specs → design → tasks`

Standard workflow: agree on what to build, then how, then do it.

### tdd
`tests → implementation → docs`

Test-first: write tests, implement to pass them, document.

## Custom Schema Examples

### Rapid Iteration
```yaml
name: rapid
version: 1
description: Minimal overhead, fast iteration
artifacts:
  - id: proposal
    generates: proposal.md
    template: proposal.md
    requires: []
  - id: tasks
    generates: tasks.md
    template: tasks.md
    requires: [proposal]
apply:
  requires: [tasks]
  tracks: tasks.md
```

### With Review Step
```yaml
artifacts:
  # ...existing artifacts...
  - id: review
    generates: review.md
    description: Pre-implementation review
    template: review.md
    instruction: |
      Create review checklist: security, performance, testing.
    requires: [design]
  - id: tasks
    requires: [specs, design, review]
```

## Schema Resolution Order

1. CLI flag: `--schema <name>`
2. Change metadata: `.openspec.yaml` in change folder
3. Project config: `openspec/config.yaml`
4. Default: `spec-driven`

## Schema Management Commands

```bash
openspec schemas [--json]                    # List all schemas
openspec schema fork <source> <new-name>     # Copy + customize
openspec schema init <name>                  # Create from scratch
openspec schema validate <name>              # Check structure
openspec schema which <name>                 # Show resolution source
openspec schema which --all                  # All schemas + sources
```

## Templates

Templates are markdown files in `templates/` guiding AI generation:

```markdown
<!-- templates/proposal.md -->
## Why
<!-- Motivation for this change -->

## What Changes
<!-- Specific new capabilities or modifications -->

## Impact
<!-- Affected code, APIs, dependencies -->
```

Context and rules from `config.yaml` are injected alongside templates when generating artifacts.
