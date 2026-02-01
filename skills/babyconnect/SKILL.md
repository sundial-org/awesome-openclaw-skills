---
name: activecampaign
description: ActiveCampaign CRM integration for lead management, deal tracking, and email automation. Use for syncing demo leads, managing clinic sales pipeline, and triggering follow-up sequences.
metadata: {"clawdbot":{"emoji":"📧","requires":{"bins":["activecampaign"],"env":["ACTIVECAMPAIGN_URL","ACTIVECAMPAIGN_API_KEY"]},"primaryEnv":["ACTIVECAMPAIGN_URL","ACTIVECAMPAIGN_API_KEY"]}}
---

# ActiveCampaign Skill 📧

ActiveCampaign integration for CRM automation and sales pipeline management.

## Purpose

Manage leads, deals, and email automations for sales:
- **Contacts**: Sync demo attendees, leads, and prospects
- **Deals**: Track sales pipeline stages
- **Tags**: Segment leads (demo-requested, nurture, close-ready)
- **Automations**: Trigger email sequences based on actions
- **Custom Fields**: Map order, shipping, billing, and subscription data

## Setup

### 1. Credentials

```bash
# Create config directory
mkdir -p ~/.config/activecampaign

# Add credentials
echo "https://youraccount.api-us1.com" > ~/.config/activecampaign/url
echo "your-api-key" > ~/.config/activecampaign/api_key

# Or use environment variables
export ACTIVECAMPAIGN_URL="https://youraccount.api-us1.com"
export ACTIVECAMPAIGN_API_KEY="your-api-key"
```

Get API credentials from ActiveCampaign:
- **URL**: Settings → Developer → API Access
- **API Key**: Settings → Developer → API Access

### 2. Custom Fields Configuration (Optional)

The skill supports custom field mappings for order, shipping, billing, and subscription data.

```bash
# Initialize config from sample
activecampaign config init

# Edit with your field IDs
nano ~/.config/activecampaign/fields.json
```

The config file is **gitignored** and should not be committed.

## Usage

```bash
# Contacts
activecampaign contacts list                    # List all contacts
activecampaign contacts create "email@test.com" "First" "Last"
activecampaign contacts sync "email@test.com" "First" "Last"
activecampaign contacts get <id>
activecampaign contacts search "clinic"
activecampaign contacts add-tag <id> <tag_id>
activecampaign contacts remove-tag <id> <tag_id>

# Deals
activecampaign deals list
activecampaign deals create "Clinic Name" <stage_id> <value>
activecampaign deals update <id> stage=<stage_id> value=<value>
activecampaign deals get <id>

# Tags
activecampaign tags list
activecampaign tags create "Demo Requested"

# Automations
activecampaign automations list
activecampaign automations add-contact <contact_id> <automation_id>

# Custom Fields
activecampaign fields list                    # List configured fields
activecampaign fields get order_fields.order_id
activecampaign fields set-field <contact_id> <field_id> <value>

# Lists
activecampaign lists list
activecampaign lists add-contact <list_id> <contact_id>

# Configuration
activecampaign config init                    # Create fields.json from sample
activecampaign config path                    # Show config file path
```

## Custom Fields Configuration

The skill includes a comprehensive field configuration system for:

| Category | Fields |
|----------|--------|
| **Order** | Order ID, Number, Date, Total, Tax, Status, Subtotal, Discount, Currency, Payment details |
| **Shipping** | Name, Address 1/2, City, State, Postal Code, Country, Method, Cost |
| **Billing** | Address 1/2, City, State, Postal Code, Country |
| **Subscription** | ID, Status, Plan, Amount, Currency, Interval, Start, Trial End |
| **Additional** | Company, Product info, Lead Campaign, Notes, Birthday, etc. |

### Setting Field Values

```bash
# Get field ID from config
activecampaign fields get order_fields.order_id
# Output: 7

# Set field value on contact
activecampaign fields set-field <contact_id> 7 "ORD-12345"
```

## Rate Limits

- **5 requests per second** max
- The wrapper handles rate limiting automatically

## Related Skills

- `shapescale-crm` - Attio CRM integration (source of truth)
- `shapescale-sales` - Sales workflows and qualification
- `campaign-orchestrator` - Multi-channel follow-up campaigns
