# ActiveCampaign CLI - Troubleshooting & Notes

## Account Limitations

ActiveCampaign **trial accounts** have limited API access:

| Operation | Trial Account | Paid Account |
|-----------|---------------|--------------|
| Contact Read | ✅ Working | ✅ Working |
| Contact Create/Update | ✅ Working | ✅ Working |
| Deal Create | ❌ Blocked | ✅ Working |
| Deal List | ✅ Working | ✅ Working |
| Pipeline List | ❌ Blocked | ✅ Working |
| Tag Add/Create | ❌ Blocked | ✅ Working |
| Lists List | ❌ Blocked | ✅ Working |

**Workaround:** Use `deal_stage_list` to infer pipeline structure from stage IDs (stages include `pipeline` field).

## Known API Issues

### contact_list Returns Empty

`contact_list` with `api_version=3` does not work for listing all contacts.

**Fix:** The CLI now uses `contact_paginator` instead.

### JSON vs Form-Data

Some endpoints require form-data format, not JSON:
- `contact_add` - Works with form-data only
- `contact_sync` - Works with form-data only
- `deal_add` - Requires form-data with all fields

### contact_tag_add Returns "Contact does not exist"

This is an ActiveCampaign API quirk. The contact exists and can be read, but tagging via API may fail on trial accounts.

### Pipeline & Deal Group List Blocked

`pipeline_list` and `deal_group_list` return "You are not authorized" on trial accounts. Use `deal_stage_list` to see stages with their pipeline IDs.

## Verified Working Endpoints

### Contacts
- `contact_paginator` - List contacts with pagination
- `contact_view` - Get single contact by ID
- `contact_add` - Create new contact (form-data)
- `contact_sync` - Create or update contact (form-data)

### Deals
- `deal_list` - List deals
- `deal_view` - Get single deal

### Stages & Pipelines
- `deal_stage_list` - List all stages (includes pipeline ID)

### Tags
- `tags_list` - List all tags

## CLI Command Format

```bash
# Contacts
activecampaign contacts list                    # List all contacts
activecampaign contacts sync "email@test.com" "First" "Last"
activecampaign contacts get <id>

# Deals
activecampaign deals list                       # List deals
activecampaign deals get <id>                   # Get deal details

# Stages
activecampaign stages list                      # List pipeline stages
```
