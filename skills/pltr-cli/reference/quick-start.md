# Quick Start & Authentication

## Installation

```bash
# From PyPI (recommended)
pip install pltr-cli

# Or with pipx (isolated)
pipx install pltr-cli

# Verify installation
pltr --version
```

## Authentication Setup

### Token Authentication (Recommended)

1. Get your API token from Foundry web UI (Settings > API Tokens)
2. Configure pltr-cli:

```bash
pltr configure configure
```

Enter:
- Foundry hostname (e.g., `foundry.company.com`)
- Authentication type: `token`
- API token
- Profile name (e.g., `production`)

### Environment Variables (CI/CD)

```bash
export FOUNDRY_TOKEN="your-token"
export FOUNDRY_HOST="foundry.company.com"
```

### OAuth2 Authentication

```bash
pltr configure configure --profile oauth-prod --auth-type oauth \
  --host foundry.company.com \
  --client-id "your-client-id" \
  --client-secret "your-client-secret"
```

## Verify Connection

```bash
pltr verify
# Expected: "Authentication successful!"
```

## Multiple Profiles

```bash
# Configure multiple profiles
pltr configure configure --profile production
pltr configure configure --profile development

# List profiles
pltr configure list-profiles

# Set default profile
pltr configure set-default production

# Use specific profile
pltr verify --profile development
```

## Profile Management

```bash
# List all profiles
pltr configure list-profiles

# Delete profile
pltr configure delete old-profile --force
```

## Output Formats

```bash
pltr <command> --format table    # Rich table (default)
pltr <command> --format json     # JSON
pltr <command> --format csv      # CSV
pltr <command> --output file.csv # Save to file
```

## Interactive Shell

```bash
pltr shell --profile production

# In shell mode:
pltr (production)> admin user current
pltr (production)> sql execute "SELECT 1"
pltr (production)> exit
```

## Shell Completion

```bash
pltr completion install           # Auto-detect shell
pltr completion install --shell zsh
pltr completion install --shell bash
```

## First Commands to Try

```bash
# Check current user
pltr admin user current

# List ontologies
pltr ontology list

# Simple SQL query
pltr sql execute "SELECT 1 as test"

# Search builds
pltr orchestration builds search
```

## Troubleshooting

### Authentication Failed
- Token expired: Regenerate in Foundry web UI
- Wrong hostname: Don't include `https://`
- Network issues: Check VPN connection

### Command Not Found
- Ensure Python scripts directory is in PATH
- Check virtual environment is activated
