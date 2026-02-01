# Deal Management Workflows

## Contents
- Workflow 1: Create Opportunity
- Workflow 2: Progress Stage
- Workflow 3: Track Activities
- Workflow 4: Update Forecast
- Workflow 5: Close Deal
- Quick Reference

---

**Important**: Always run `attio options deals stage` to get valid pipeline stages for your workspace. Stage names vary by workspace configuration.

---

## Workflow 1: Create Opportunity

**When**: Converting a lead to an active deal

**Steps**:

### Step 1: Find the associated company
```bash
attio search companies "domain.com"
```

### Step 2: Check available deal fields
```bash
attio fields deals
```

### Step 3: Check pipeline stages
```bash
attio options deals stage
```

### Step 4: Create the deal
```bash
attio create deals record_data='{"name":"Company Name - Q1 Deal","stage":"qualified","value":50000}'
```

### Step 5: Add context note
```bash
attio note deals "deal-uuid" "Opportunity Context" "Qualified from demo. Primary interest: X. Timeline: 2-4 weeks."
```

**Common Fields** (verify with `attio fields deals`):
- `name` - Deal name (required)
- `stage` - Pipeline stage (required)
- `value` - Deal value
- `owner` - Assigned owner
- `associated_company` - Linked company ID

---

## Workflow 2: Progress Stage

**When**: Moving deal through pipeline stages

**Steps**:

### Step 1: Get current deal details
```bash
attio get deals "deal-uuid"
```

### Step 2: Check valid stages
```bash
attio options deals stage
```

### Step 3: Update stage
```bash
attio update deals "deal-uuid" record_data='{"stage":"demo_completed"}'
```

### Step 4: Document the change
```bash
attio note deals "deal-uuid" "Stage Update: Demo Completed" "Demo went well. Decision maker engaged. Next: send proposal."
```

**Best Practices**:
- Use exact stage values from `attio options deals stage`
- Update probability alongside stage changes
- Document reason for progression

---

## Workflow 3: Track Activities

**When**: Recording meetings, calls, or interactions

**Steps**:

### Step 1: Add activity note
```bash
attio note deals "deal-uuid" "Discovery Call - 2025-01-15" "Attendees: Jane (CEO), John (VP Sales)\n\nDiscussion: Current challenges, timeline, budget\n\nNext Steps: Send proposal by Friday"
```

### Step 2: Update deal fields if needed
```bash
attio update deals "deal-uuid" record_data='{"close_probability":40}'
```

**Note Format Suggestions**:
- Include date in title
- List attendees
- Summarize key discussion points
- Document next steps

---

## Workflow 4: Update Forecast

**When**: Adjusting probability or expected close date

**Steps**:

### Step 1: Review current state
```bash
attio get deals "deal-uuid"
```

### Step 2: Update forecast fields
```bash
attio update deals "deal-uuid" record_data='{"close_probability":65,"value":55000}'
```

### Step 3: Document changes
```bash
attio note deals "deal-uuid" "Forecast Update" "Previous: 40%, $50K\nUpdated: 65%, $55K\nReason: Strong demo, CEO approval"
```

---

## Workflow 5: Close Deal

**When**: Marking deal as won or lost

### For Won Deals:

```bash
# Check won stage name
attio options deals stage

# Update to won
attio update deals "deal-uuid" record_data='{"stage":"won","close_probability":100}'

# Create win summary
attio note deals "deal-uuid" "Deal Won" "Close Date: 2025-01-15\nFinal Value: $55,000\nKey Factors: Strong ROI, quick timeline"
```

### For Lost Deals:

```bash
# Check lost stage and lost_reason options
attio options deals stage
attio options deals lost_reason

# Update to lost (lost_reason is often multi-select - use array)
attio update deals "deal-uuid" record_data='{"stage":"lost","lost_reason":["pricing"]}'

# Create loss analysis
attio note deals "deal-uuid" "Deal Lost - Analysis" "Reason: Budget constraints\nDetails: Approved for next quarter\nFuture: Re-engage in March"
```

**Important**: `lost_reason` is typically multi-select. Wrap values in array: `["pricing", "timing"]`

---

## Quick Reference

**Before any deal operation, run:**
```bash
attio fields deals          # See all available fields
attio options deals stage   # See pipeline stages
```

**Critical Rules**:
- Use API slugs (e.g., `demo_completed`), not display names (e.g., "Demo Completed")
- Multi-select fields need arrays: `["value1", "value2"]`
- Required fields typically: `name`, `stage`
