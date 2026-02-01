# ActiveCampaign Skill for Moltbot

ActiveCampaign CRM integration for sales automation and pipeline management.

## Features

- **Contacts**: Create, sync, search, and tag leads
- **Deals**: Manage sales pipeline stages
- **Tags**: Segment and organize contacts
- **Automations**: Trigger email sequences
- **Custom Fields**: Comprehensive field mapping system for order, shipping, billing, and subscription data
- **Lists**: Contact list management

## Quick Setup

### 1. Credentials

```bash
mkdir -p ~/.config/activecampaign
echo "https://youraccount.api-us1.com" > ~/.config/activecampaign/url
echo "your-api-key" > ~/.config/activecampaign/api_key
```

### 2. Custom Fields (Optional)

```bash
# Create field configuration from sample
activecampaign config init

# Edit with your ActiveCampaign field IDs
nano ~/.config/activecampaign/fields.json
```

**Note:** The `fields.json` file is gitignored and contains your private field IDs.

## Usage

```bash
# Contacts
activecampaign contacts sync "email@clinic.com" "Dr." "Smith"
activecampaign contacts add-tag <contact_id> <tag_id>

# Deals
activecampaign deals list
activecampaign deals create "Clinic Name" <stage_id> 5000

# Tags
activecampaign tags list
activecampaign tags create "Demo Requested"

# Automations
activecampaign automations list

# Custom Fields
activecampaign fields list
activecampaign fields get order_fields.order_id
```

## Field Configuration

The skill includes comprehensive field mappings for:

| Category | Examples |
|----------|----------|
| Order | Order ID, Number, Date, Total, Tax, Status, Currency, Payment |
| Shipping | Name, Address, City, State, Postal Code, Country, Method, Cost |
| Billing | Address, City, State, Postal Code, Country |
| Subscription | ID, Status, Plan, Amount, Currency, Interval, Start, Trial End |

See `activecampaign-fields-sample.json` for the complete field reference.

## Installation

Install via Moltbot's skill registry or clone directly:

```bash
git clone https://github.com/kesslerio/activecampaign-moltbot-skill.git
cd activecampaign-moltbot-skill
```

## Integration

This skill integrates with:
- `shapescale-crm` - Attio CRM for source of truth
- `shapescale-sales` - Sales qualification workflows
- `campaign-orchestrator` - Multi-channel follow-up campaigns

## License

MIT
