# Attio Moltbot Skill

A [Moltbot](https://docs.molt.bot) skill for managing [Attio CRM](https://attio.com) records. Search, create, and update companies, people, deals, and tasks through natural language.

## Features

- **Record Management**: Search, create, update, and delete CRM records
- **Deal Pipelines**: Progress deals through stages, track activities, close deals
- **Notes**: Add structured notes to any record
- **Field Discovery**: Dynamically discover available fields and options
- **Workflow Guidance**: Built-in best practices to avoid common API errors

## Prerequisites

- [Node.js](https://nodejs.org/) v20+
- [Moltbot](https://docs.molt.bot) installed and configured
- [mcporter](https://docs.molt.bot/tools/mcporter) for MCP server management
- [Attio](https://attio.com) account with API access

## Quick Install

```bash
git clone https://github.com/kesslerio/attio-moltbot-skill.git
cd attio-moltbot-skill
./setup.sh
```

The setup script will:
1. Install `attio-mcp` globally if not present
2. Prompt for your Attio API credentials
3. Configure mcporter to connect to Attio
4. Install the skill to `~/.clawdbot/skills/attio/`

## Manual Setup

### 1. Install attio-mcp

```bash
npm install -g attio-mcp
```

### 2. Get Attio Credentials

1. Go to [Attio API Settings](https://app.attio.com/settings/api-tokens)
2. Create a new API token with appropriate permissions
3. Note your Workspace ID from workspace settings

### 3. Configure mcporter

Create `~/.config/mcporter/servers/attio/config.json`:

```json
{
  "name": "attio",
  "type": "stdio",
  "command": "attio-mcp",
  "args": ["start:stdio"],
  "env": {
    "ATTIO_ACCESS_TOKEN": "your_token_here",
    "ATTIO_WORKSPACE_ID": "your_workspace_id"
  }
}
```

### 4. Install the Skill

```bash
# Clone the repository
git clone https://github.com/kesslerio/attio-moltbot-skill.git

# Symlink to skills directory
ln -sf $(pwd)/attio-moltbot-skill ~/.clawdbot/skills/attio
```

### 5. Restart Moltbot

Restart Moltbot to load the new skill.

## Usage

### Via Moltbot (Natural Language)

```
"Search for companies in Attio"
"Create a deal for Acme Corp worth $50k"
"Add a note to the company about our meeting"
"Move the deal to negotiation stage"
```

### Via mcporter (CLI)

```bash
# Search for companies
mcporter call attio.search_records resource_type=companies query="Acme"

# Get deal details
mcporter call attio.get_record_details resource_type=deals record_id="uuid"

# Create a note
mcporter call attio.create_note resource_type=companies record_id="uuid" title="Meeting" content="..."
```

### Via attio CLI

```bash
# Search
attio search companies "Acme"

# Get record
attio get deals "uuid"

# Add note
attio note companies "uuid" "Title" "Content"

# Check fields
attio fields companies
attio options deals stage
```

## Workflow References

The skill includes detailed workflow guides:

- `references/company_workflows.md` - Find, create, update companies
- `references/deal_workflows.md` - Pipeline management, forecasting, closing
- `references/field_guide.md` - Data types, validation, common errors

## Extending for Your Workspace

This skill provides generic Attio workflows. To add workspace-specific configurations:

1. Create a new skill directory (e.g., `my-crm/`)
2. Add a `SKILL.md` that references this skill
3. Add your specific field lists and custom workflows

Example overlay structure:
```
my-crm/
├── SKILL.md              # References attio skill + your specifics
└── references/
    └── my_fields.md      # Your workspace-specific allowed fields
```

## Troubleshooting

### "attio-mcp not found"

```bash
npm install -g attio-mcp
```

### "Invalid API token"

1. Check your token at https://app.attio.com/settings/api-tokens
2. Verify the token has required permissions
3. Update `~/.config/mcporter/servers/attio/config.json`

### "Field not found"

Run `attio fields <type>` to see available fields for your workspace.

### "Invalid option"

For select fields, run `attio options <type> <field>` to get valid values.

## Links

- [attio-mcp](https://github.com/kesslerio/attio-mcp-server) - The MCP server this skill uses
- [Attio API Docs](https://developers.attio.com/)
- [Moltbot Docs](https://docs.molt.bot)

## License

Apache-2.0
