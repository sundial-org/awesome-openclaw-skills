---
name: servicenow-agent
description: Read-only CLI access to ServiceNow Table, Attachment, Aggregate, and Service Catalog APIs; includes schema inspection and history retrieval (read-only).
read_when:
  - Need to read ServiceNow Table API records
  - Need to query a table or fetch a record by sys_id
  - Need to download attachment content or metadata
  - Need aggregate statistics or service catalog variables
metadata: {"clawdbot":{"emoji":"🧾","requires":{"bins":["node"]}}}
---

# ServiceNow Table API Read Only

Use this skill to read data from ServiceNow via the Table API. Do not create or update or delete records.

## Configuration

Set these environment variables in the .env file in this folder.

- SERVICENOW_DOMAIN instance domain such as myinstance.service-now.com
- SERVICENOW_USERNAME username for basic auth
- SERVICENOW_PASSWORD password for basic auth

If your domain already includes https:// then use it as is. Otherwise requests should be made to:

```
https://$SERVICENOW_DOMAIN
```

## Allowed Operations GET only

Use only the GET endpoints from these files.

- openapi.yaml for Table API
- references/attachment.yaml for Attachment API
- references/aggregate-api.yaml for Aggregate API
- references/service-catalog-api.yaml for Service Catalog API

### List records
- GET /api/now/table/{tableName}

### Get a record by sys_id
- GET /api/now/table/{tableName}/{sys_id}

Never use POST or PUT or PATCH or DELETE.

## Common Query Params Table API

- sysparm_query encoded query such as active=true^priority=1
- sysparm_fields comma separated fields to return
- sysparm_limit limit record count to keep small for safety
- sysparm_display_value true or false or all
- sysparm_exclude_reference_link true to reduce clutter

See openapi.yaml for the full list of parameters.

## CLI

Use the bundled CLI for all reads. It pulls auth from .env by default. You can override with flags.

### Command overview

- list table lists records from a table
- get table sys_id fetches one record by sys_id
- batch file.json runs multiple read requests in one call
- attach reads attachments and file content
- stats table aggregates stats
- schema table lists valid field names and types
- history table sys_id reads full comment and work note timeline
- sc endpoint Service Catalog GET endpoints

### Auth flags

- --domain domain instance domain
- --username user
- --password pass

### Query flags

Use any of these as --sysparm_* flags.

- --sysparm_query
- --sysparm_fields
- --sysparm_limit
- --sysparm_display_value
- --sysparm_exclude_reference_link
- --sysparm_suppress_pagination_header
- --sysparm_view
- --sysparm_query_category
- --sysparm_query_no_domain
- --sysparm_no_count

### Attachment API params

- --sysparm_query
- --sysparm_suppress_pagination_header
- --sysparm_limit
- --sysparm_query_category

### Aggregate API params

- --sysparm_query
- --sysparm_avg_fields
- --sysparm_count
- --sysparm_min_fields
- --sysparm_max_fields
- --sysparm_sum_fields
- --sysparm_group_by
- --sysparm_order_by
- --sysparm_having
- --sysparm_display_value
- --sysparm_query_category

### Service Catalog params

- --sysparm_view
- --sysparm_limit
- --sysparm_text
- --sysparm_offset
- --sysparm_category
- --sysparm_type
- --sysparm_catalog
- --sysparm_top_level_only
- --record_id
- --template_id
- --mode

### Output

- --pretty pretty print JSON output
- --out path save binary attachment content to a file

### Examples

List recent incidents.

```bash
node cli.mjs list incident --sysparm_limit 5 --sysparm_fields number,short_description,priority,sys_id
```

Query with a filter.

```bash
node cli.mjs list cmdb_ci --sysparm_query "operational_status=1^install_status=1" --sysparm_limit 10
```

Fetch a single record.

```bash
node cli.mjs get incident <sys_id> --sysparm_fields number,short_description,opened_at
```

Override auth on the fly.

```bash
node cli.mjs list incident --domain myinstance.service-now.com --username admin --password "***" --sysparm_limit 3
```

Attachment metadata and file download.

```bash
node cli.mjs attach list --sysparm_query "table_name=incident" --sysparm_limit 5
node cli.mjs attach file <sys_id> --out /tmp/attachment.bin
```

Aggregate stats.

```bash
node cli.mjs stats incident --sysparm_query "active=true^priority=1" --sysparm_count true
```

Service Catalog read only GETs.

```bash
node cli.mjs sc catalogs --sysparm_text "laptop" --sysparm_limit 5
node cli.mjs sc items --sysparm_text "mac" --sysparm_limit 5
node cli.mjs sc item <sys_id>
node cli.mjs sc item-variables <sys_id>
```

### Service Catalog endpoints GET only

- cart
- delivery-address user_id
- validate-categories
- on-change-choices entity_id
- catalogs
- catalog sys_id
- catalog-categories sys_id
- category sys_id
- items
- item sys_id
- item-variables sys_id
- item-delegation item_sys_id user_sys_id
- producer-record producer_id record_id
- record-wizard record_id wizard_id
- generate-stage-pool quantity
- step-configs
- wishlist
- wishlist-item cart_item_id
- wizard sys_id

### Schema Inspection

Use this if you are unsure of a field name.

```bash
node cli.mjs schema incident
```

### Reading Ticket History

Use this to read the full conversation instead of just the current state.

```bash
node cli.mjs history incident <sys_id>
```

### Specialist presets

Create JSON batch files under specialists/ to run multiple reads at once.

- specialists/incidents.json

Each entry supports sysparm_* fields plus these items.

- name label in the batch output
- table target table
- sys_id optional single record fetch

Run a batch preset.

```bash
node cli.mjs batch specialists/incidents.json --pretty
```

## Output

The Table API returns JSON by default. Results appear under result.

## Notes

- Keep result sizes small with sysparm_limit.
- Use sysparm_fields to avoid large payloads.
- This skill is read only by design.

## Summary of the Agent Toolkit

- list and get show the current state of records.
- attach shows files and screenshots.
- stats shows analytics and aggregates.
- sc shows requested item variables.
- schema shows the database map to correct errors.
- history shows the timeline of human conversations.

## Observations & Notes (important)

- Service Catalog endpoints may return empty arrays depending on catalog content and search text — try more specific `--sysparm_text` terms or increase `--sysparm_limit`.
- `sysparm_display_value` is enabled by default for table reads to return human-friendly values (e.g., user names instead of sys_ids). If you need raw system ids, pass `--sysparm_display_value false`.
- Keep `--sysparm_limit` small for agent-initiated queries to avoid large payloads and timeouts. Prefer `stats` for counts or aggregates instead of downloading many rows.
- Attachments: metadata is available via `attach list`/`attach get`; use `attach file <sys_id> --out <path>` to download binary content for local analysis.
- Schema inspection (`schema`) avoids guessing field names and is the recommended first step before reading unknown tables.
- History (`history`) fetches journal entries (comments/work_notes) from `sys_journal_field` and is useful to read the full conversation thread for a ticket.
- Use `--pretty` to make JSON outputs readable for human review and to help the agent summarize long results.

## Recommended Batch Presets

I recommend these specialist JSON presets under `specialists/` to speed up common read workflows. They are safe (read-only) and demonstrate how to combine related reads.

1) `specialists/inspect_incident_schema.json` — schema inspection for `incident`:

```json
[
  {
    "name": "schema-incident",
    "table": "sys_dictionary",
    "sysparm_query": "name=incident^elementISNOTEMPTY",
    "sysparm_fields": "element,column_label,internal_type,reference",
    "sysparm_limit": 500
  }
]
```

2) `specialists/incident_history_template.json` — history template (replace `<SYS_ID>` with the target sys_id before running):

```json
[
  {
    "name": "incident-history",
    "table": "sys_journal_field",
    "sysparm_query": "name=incident^element_id=<SYS_ID>",
    "sysparm_fields": "value,element,sys_created_on,sys_created_by",
    "sysparm_order_by": "sys_created_on",
    "sysparm_limit": 500
  }
]
```

3) `specialists/attachments_incident.json` — recent attachments for incident table:

```json
[
  {
    "name": "recent-incident-attachments",
    "table": "attachment",
    "sysparm_query": "table_name=incident",
    "sysparm_fields": "sys_id,file_name,content_type,table_sys_id,sys_created_on",
    "sysparm_limit": 20
  }
]
```

How to use these:
- For schema: `node cli.mjs batch specialists/inspect_incident_schema.json --pretty`
- For history: replace `<SYS_ID>` then `node cli.mjs batch specialists/incident_history_template.json --pretty` (or run `node cli.mjs history incident <SYS_ID> --pretty`)
- For attachments: `node cli.mjs batch specialists/attachments_incident.json --pretty`, then `node cli.mjs attach file <sys_id> --out /tmp/file` to download a file.

These presets are intentionally read-only and conservative (limits set small). Feel free to ask for additional presets (P1 dashboards, recent changes, escalations).
