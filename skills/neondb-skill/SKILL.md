---
name: neondb
description: Manage Neon serverless Postgres databases. Create projects, branches, databases, and execute queries. Perfect for agent workflows needing persistent storage with branching (like git for databases), scale-to-zero, and instant provisioning.
homepage: https://neon.tech
metadata: {"openclaw":{"emoji":"🐘","requires":{"bins":["neonctl"]},"install":[{"id":"brew","kind":"brew","package":"neonctl","bins":["neonctl"],"label":"Install neonctl (Homebrew)"},{"id":"npm","kind":"node","package":"neonctl","bins":["neonctl"],"label":"Install neonctl (npm)"}]}}
---

# NeonDB

Neon is **serverless Postgres** — scales to zero, branches like git, instant provisioning. Perfect for AI agents needing databases without ops overhead.

## Why Neon for Agents?

- **Instant databases** — Create in seconds, no server setup
- **Branching** — Fork your database like git (test without affecting prod)
- **Scale-to-zero** — Pay nothing when idle
- **Connection pooling** — Built-in, no PgBouncer needed
- **Generous free tier** — 0.5 GB storage, 190 compute hours/month

## Quick Start

### 1. Install CLI

```bash
# Homebrew (recommended)
brew install neonctl

# Or npm
npm i -g neonctl
```

### 2. Authenticate

```bash
# Interactive (opens browser)
neonctl auth

# Or with API key (get from console.neon.tech)
export NEON_API_KEY=your_api_key_here
```

### 3. Create Your First Project

```bash
neonctl projects create --name "my-agent-db"
```

## Core Commands

### Projects (top-level container)

```bash
# List all projects
neonctl projects list

# Create project
neonctl projects create --name "project-name"

# Delete project
neonctl projects delete <project-id>

# Get project details
neonctl projects get <project-id>
```

### Branches (database snapshots)

```bash
# List branches
neonctl branches list --project-id <project-id>

# Create branch (fork from main)
neonctl branches create --project-id <project-id> --name "dev-branch"

# Create branch from specific point
neonctl branches create --project-id <project-id> --name "restore-test" --parent main --timestamp "2024-01-15T10:00:00Z"

# Reset branch to parent
neonctl branches reset <branch-id> --project-id <project-id> --parent

# Delete branch
neonctl branches delete <branch-id> --project-id <project-id>

# Compare schemas
neonctl branches schema-diff --project-id <project-id> --base-branch main --compare-branch dev
```

### Databases

```bash
# List databases
neonctl databases list --project-id <project-id> --branch <branch-name>

# Create database
neonctl databases create --project-id <project-id> --branch <branch-name> --name "mydb"

# Delete database
neonctl databases delete <db-name> --project-id <project-id> --branch <branch-name>
```

### Connection Strings

```bash
# Get connection string (default branch)
neonctl connection-string --project-id <project-id>

# Get connection string for specific branch
neonctl connection-string <branch-name> --project-id <project-id>

# Pooled connection (recommended for serverless)
neonctl connection-string --project-id <project-id> --pooled

# Extended format (with all details)
neonctl connection-string --project-id <project-id> --extended
```

### Roles (database users)

```bash
# List roles
neonctl roles list --project-id <project-id> --branch <branch-name>

# Create role
neonctl roles create --project-id <project-id> --branch <branch-name> --name "app_user"
```

## Executing Queries

### Using psql

```bash
# Get connection string and connect
neonctl connection-string --project-id <project-id> | xargs psql

# Or direct
psql "$(neonctl connection-string --project-id <project-id>)"
```

### Using the connection string in code

```bash
# Get the string
CONNECTION_STRING=$(neonctl connection-string --project-id <project-id> --pooled)

# Use in any Postgres client
psql "$CONNECTION_STRING" -c "SELECT * FROM users LIMIT 5;"
```

## Context (Avoid Repeating Project ID)

Set context to avoid passing `--project-id` every time:

```bash
# Set project context
neonctl set-context --project-id <project-id>

# Now commands use that project automatically
neonctl branches list
neonctl databases list
neonctl connection-string
```

## Agent Workflow Examples

### Create org database with branches

```bash
# Create project for org
neonctl projects create --name "website-org-db" -o json

# Create production branch (main is created by default)
# Create dev branch for testing
neonctl branches create --name "dev" --project-id <id>

# Get connection strings
neonctl connection-string main --project-id <id> --pooled  # for prod
neonctl connection-string dev --project-id <id> --pooled   # for dev
```

### Create leads table

```bash
# Connect and create schema
psql "$(neonctl cs --project-id <id>)" <<EOF
CREATE TABLE leads (
    id SERIAL PRIMARY KEY,
    business_name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    location VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255),
    website VARCHAR(255),
    status VARCHAR(50) DEFAULT 'identified',
    priority VARCHAR(20) DEFAULT 'medium',
    notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_leads_status ON leads(status);
CREATE INDEX idx_leads_category ON leads(category);
EOF
```

### Branch for experiments

```bash
# Create a branch to test schema changes
neonctl branches create --name "schema-experiment" --project-id <id>

# Test your changes on the branch
psql "$(neonctl cs schema-experiment --project-id <id>)" -c "ALTER TABLE leads ADD COLUMN score INT;"

# If it works, apply to main. If not, just delete the branch
neonctl branches delete schema-experiment --project-id <id>
```

## Output Formats

```bash
# JSON (for parsing)
neonctl projects list -o json

# YAML
neonctl projects list -o yaml

# Table (default, human-readable)
neonctl projects list -o table
```

## Environment Variables

```bash
# API key (required if not using `neonctl auth`)
export NEON_API_KEY=your_key

# Default project (alternative to set-context)
export NEON_PROJECT_ID=your_project_id
```

## Common Patterns

### Check if neonctl is configured

```bash
neonctl me -o json 2>/dev/null && echo "Authenticated" || echo "Need to run: neonctl auth"
```

### Quick database query

```bash
# One-liner query
psql "$(neonctl cs)" -c "SELECT COUNT(*) FROM leads WHERE status='contacted';"
```

### Export to CSV

```bash
psql "$(neonctl cs)" -c "COPY (SELECT * FROM leads) TO STDOUT WITH CSV HEADER" > leads.csv
```

### Import from CSV

```bash
psql "$(neonctl cs)" -c "\COPY leads(business_name,category,location) FROM 'import.csv' WITH CSV HEADER"
```

## Troubleshooting

### "Connection refused"
- Check if branch compute is active (scale-to-zero may have paused it)
- Use `--pooled` connection string for serverless workloads

### "Permission denied"
- Verify API key: `neonctl me`
- Re-authenticate: `neonctl auth`

### Slow first connection
- Normal for scale-to-zero. First connection wakes the compute (~1-2 seconds)
- Use connection pooling to maintain warm connections

## Links

- [Neon Console](https://console.neon.tech) — Web dashboard
- [API Docs](https://api-docs.neon.tech) — REST API reference
- [CLI Reference](https://neon.tech/docs/reference/neon-cli) — Full CLI docs
- [GitHub](https://github.com/neondatabase/neonctl) — CLI source code
