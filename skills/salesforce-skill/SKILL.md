Main skill definition with frontmatter, CLI reference, SOQL patterns

---

```yaml
---
name: salesforce
description: Manage Salesforce CRM - query records, create/update contacts, accounts, opportunities, leads, and cases. Use when the user asks about CRM data, sales pipeline, customer records, or Salesforce operations.
metadata: {"moltbot":{"emoji":"☁️","requires":{"bins":["sf"],"env":["SALESFORCE_ACCESS_TOKEN"]},"primaryEnv":"SALESFORCE_ACCESS_TOKEN","install":[{"id":"npm","kind":"node","package":"@salesforce/cli","bins":["sf"],"label":"Install Salesforce CLI (npm)"},{"id":"brew","kind":"brew","formula":"salesforce-cli","bins":["sf"],"label":"Install Salesforce CLI (brew)"}]}}
homepage: https://developer.salesforce.com/tools/salesforcecli
---
```

# Salesforce CRM Skill

Interact with Salesforce CRM using the official Salesforce CLI (`sf`) and REST API.

## Prerequisites

1. **Salesforce CLI** (`sf`) installed via npm or Homebrew
2. **Authentication** configured via one of:
    - `sf org login web` (OAuth browser flow - recommended for interactive)
    - `sf org login jwt` (JWT for headless/automated)
    - `SALESFORCE_ACCESS_TOKEN` environment variable (direct token)

## Quick Reference

### Authentication & Org Management

```bash
# Login to org (opens browser)
sf org login web --alias myorg

# Login with JWT (headless)
sf org login jwt --client-id <consumer-key> --jwt-key-file <path-to-key> --username <user> --alias myorg

# List connected orgs
sf org list

# Set default org
sf config set target-org myorg

# Display org info
sf org display --target-org myorg
```

### Query Records (SOQL)

```bash
# Query contacts
sf data query --query "SELECT Id, Name, Email, Phone FROM Contact LIMIT 10" --target-org myorg

# Query with WHERE clause
sf data query --query "SELECT Id, Name, Amount, StageName FROM Opportunity WHERE StageName = 'Prospecting'" --target-org myorg

# Query accounts by name
sf data query --query "SELECT Id, Name, Industry, Website FROM Account WHERE Name LIKE '%Acme%'" --target-org myorg

# Export to CSV
sf data query --query "SELECT Id, Name, Email FROM Contact" --result-format csv > contacts.csv

# Export to JSON
sf data query --query "SELECT Id, Name FROM Account" --result-format json
```

### Create Records

```bash
# Create a Contact
sf data create record --sobject Contact --values "FirstName='John' LastName='Doe' Email='john.doe@example.com'" --target-org myorg

# Create an Account
sf data create record --sobject Account --values "Name='Acme Corp' Industry='Technology' Website='https://acme.com'" --target-org myorg

# Create an Opportunity
sf data create record --sobject Opportunity --values "Name='Big Deal' AccountId='001XXXXXXXXXXXXXXX' StageName='Prospecting' CloseDate='2025-06-30' Amount=50000" --target-org myorg

# Create a Lead
sf data create record --sobject Lead --values "FirstName='Jane' LastName='Smith' Company='NewCo' Email='jane@newco.com' Status='Open - Not Contacted'" --target-org myorg

# Create a Case
sf data create record --sobject Case --values "Subject='Support Request' Description='Customer needs help' Status='New' Priority='Medium'" --target-org myorg
```

### Update Records

```bash
# Update a Contact
sf data update record --sobject Contact --record-id 003XXXXXXXXXXXXXXX --values "Phone='555-1234' Title='VP Sales'" --target-org myorg

# Update an Opportunity stage
sf data update record --sobject Opportunity --record-id 006XXXXXXXXXXXXXXX --values "StageName='Negotiation/Review' Amount=75000" --target-org myorg

# Update Account
sf data update record --sobject Account --record-id 001XXXXXXXXXXXXXXX --values "Description='Key strategic account'" --target-org myorg
```

### Delete Records

```bash
# Delete a record
sf data delete record --sobject Contact --record-id 003XXXXXXXXXXXXXXX --target-org myorg

# Bulk delete via query (careful!)
sf data delete bulk --sobject Lead --file leads-to-delete.csv --target-org myorg
```

### Bulk Operations

```bash
# Bulk insert from CSV
sf data import bulk --sobject Contact --file contacts.csv --target-org myorg

# Bulk update from CSV
sf data upsert bulk --sobject Account --file accounts.csv --external-id Id --target-org myorg

# Check bulk job status
sf data bulk status --job-id <job-id> --target-org myorg
```

### Schema & Metadata

```bash
# Describe an object (get fields)
sf sobject describe --sobject Account --target-org myorg

# List all objects
sf sobject list --target-org myorg

# Get field details
sf sobject describe --sobject Opportunity --target-org myorg | jq '.fields[] | {name, type, label}'
```

## Common SOQL Patterns

### Pipeline Report

```sql
SELECT StageName, COUNT(Id) NumDeals, SUM(Amount) TotalValue
FROM Opportunity
WHERE IsClosed = false
GROUP BY StageName
```

### Recent Activities

```sql
SELECT Id, Subject, WhoId, WhatId, ActivityDate
FROM Task
WHERE OwnerId = '<user-id>'
AND ActivityDate >= LAST_N_DAYS:7
ORDER BY ActivityDate DESC
```

### Contacts by Account

```sql
SELECT Account.Name, Id, Name, Email, Title
FROM Contact
WHERE Account.Name = 'Acme Corp'
```

### Open Cases

```sql
SELECT Id, CaseNumber, Subject, Status, Priority, CreatedDate
FROM Case
WHERE IsClosed = false
ORDER BY Priority, CreatedDate
```

### Leads by Status

```sql
SELECT Status, COUNT(Id) Total
FROM Lead
WHERE IsConverted = false
GROUP BY Status
```

## REST API (Alternative)

For operations not covered by CLI, use curl with the REST API:

```bash
# Set variables
INSTANCE_URL="https://yourorg.salesforce.com"
ACCESS_TOKEN="$SALESFORCE_ACCESS_TOKEN"

# Query via REST
curl -s "$INSTANCE_URL/services/data/v59.0/query?q=SELECT+Id,Name+FROM+Account+LIMIT+5" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json"

# Create record via REST
curl -s "$INSTANCE_URL/services/data/v59.0/sobjects/Contact" \
  -H "Authorization: Bearer $ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"FirstName":"Test","LastName":"User","Email":"test@example.com"}'
```

## Error Handling

- **INVALID_SESSION_ID**: Token expired. Re-authenticate with `sf org login web`
- **MALFORMED_QUERY**: Check SOQL syntax. Use single quotes for strings.
- **ENTITY_IS_DELETED**: Record was deleted. Query to verify before updating.
- **REQUIRED_FIELD_MISSING**: Check object schema for required fields.

## Tips

1. **Use aliases**: Set `--alias` when logging in, then use `--target-org alias`
2. **JSON output**: Add `--json` flag for programmatic parsing
3. **Dry run**: Use `--dry-run` flag on bulk operations to preview
4. **Field names**: Use API names (e.g., `FirstName`), not labels (e.g., "First Name")
5. **Date format**: Use `YYYY-MM-DD` for dates, `YYYY-MM-DDThh:mm:ssZ` for datetimes

## Limitations

- Bulk operations have daily API limits (varies by Salesforce edition)
- Some objects (e.g., ContentDocument) have special handling requirements
- Complex queries may hit governor limits
