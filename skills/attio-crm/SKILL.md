---
name: attio
description: Manage Attio CRM records (companies, people, deals, tasks, notes). Search, create, update records and manage deal pipelines.
metadata: {"moltbot":{"emoji":"📇","requires":{"bins":["attio"],"env":["ATTIO_ACCESS_TOKEN"]}}}
---

# Attio CRM

## Quick Commands

```bash
# Search for records
attio search companies "Acme"
attio search deals "Enterprise"
attio search people "John"

# Get record details by ID
attio get companies "record-uuid"
attio get deals "record-uuid"

# Add a note to a record
attio note companies "record-uuid" "Title" "Note content here"

# List notes on a record
attio notes companies "record-uuid"

# See available fields for a record type
attio fields companies
attio fields deals

# Get select field options (e.g., deal stages)
attio options deals stage
```

## Golden Rules

1. **Discover fields first** - Run `attio fields <type>` before updating records
2. **Check select options** - Run `attio options <type> <field>` for dropdown values
3. **Use internal values** - Select fields use internal names, not display labels
4. **When uncertain, use notes** - Put unstructured data in notes, not record fields
5. **Format data correctly** - Numbers as `85`, arrays as `["Value"]`, booleans as `true/false`

## Workflow Index

Load these references as needed:

- **Company workflows** - `references/company_workflows.md`
- **Deal workflows** - `references/deal_workflows.md`
- **Field guide** - `references/field_guide.md`

## Command Reference

| Command | Description |
|---------|-------------|
| `attio search <type> "<query>"` | Search records |
| `attio get <type> <id>` | Get record details |
| `attio update <type> <id> record_data='{...}'` | Update record |
| `attio create <type> record_data='{...}'` | Create record |
| `attio delete <type> <id>` | Delete record |
| `attio note <type> <id> "<title>" "<content>"` | Add note |
| `attio notes <type> <id>` | List notes |
| `attio fields <type>` | List available fields |
| `attio options <type> <field>` | Get select options |

**Record types:** `companies`, `people`, `deals`, `tasks`

## Common Workflows

### Look up a company
```bash
attio search companies "Acme Corp"
```

### Get deal details
```bash
attio get deals "deal-uuid-here"
```

### Add meeting notes to company
```bash
attio note companies "company-uuid" "Meeting Notes" "Discussed pricing. Follow up next week."
```

### Check deal stages before updating
```bash
attio options deals stage
```

### Update deal stage
```bash
attio update deals "deal-uuid" record_data='{"stage":"negotiation"}'
```

## Pipeline Stages

**Never hard-code stage names.** Always check first:
```bash
attio options deals stage
```

Use the internal value (e.g., `negotiation`), not the display label (e.g., "Negotiation").
