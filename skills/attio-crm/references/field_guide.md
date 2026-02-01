# Field Validation & Formatting Guide

## Golden Rule

**When uncertain about a field, use notes instead of record updates.**

```bash
# Safe: Always works
attio note companies "uuid" "Additional Info" "Industry: Healthcare\nEmployee Count: 50"

# Risky: May fail if field doesn't exist
attio update companies "uuid" record_data='{"industry":"Healthcare"}'
```

---

## Discover Fields First

Before updating any record, check what fields exist:

```bash
# List all fields for a record type
attio fields companies
attio fields deals
attio fields people

# Get options for select/dropdown fields
attio options companies lead_status
attio options deals stage
```

---

## Data Type Formatting

| Type | Correct | Wrong |
|------|---------|-------|
| **Number** | `85` | `"85"`, `"8.5/10"` |
| **Array** | `["Health Care"]` | `"Health Care"` |
| **Boolean** | `true`, `false` | `"true"`, `"false"` |
| **Select** | `"potential_customer"` | `"Potential Customer"` |

### Array Fields

Many fields require arrays even for single values:

| Field Type | Correct | Wrong |
|------------|---------|-------|
| Multi-select | `["Option A"]` | `"Option A"` |
| Domains | `["example.com"]` | `"example.com"` |
| Email addresses | `["email@co.com"]` | `"email@co.com"` |
| Tags/Categories | `["Tag1", "Tag2"]` | `"Tag1, Tag2"` |
| Linked records | `["record-uuid"]` | `"record-uuid"` |

---

## Select Field Validation

Select/dropdown fields use internal values, not display labels.

**Step 1**: Get field options
```bash
attio options deals stage
```

**Step 2**: Use the internal value
```
Output shows:
  Display Name: "Demo Completed"
  Internal Value: "demo_completed"
```

**Step 3**: Use internal value in updates
```bash
# Correct
attio update deals "uuid" record_data='{"stage":"demo_completed"}'

# Wrong - will fail
attio update deals "uuid" record_data='{"stage":"Demo Completed"}'
```

---

## Common API Errors

| Error | Cause | Solution |
|-------|-------|----------|
| `"expects array"` | Single value for array field | Wrap in array: `["value"]` |
| `"Invalid option 'X'"` | Wrong select value | Use internal value, not display label |
| `"attribute 'X' not found"` | Field doesn't exist | Run `attio fields <type>` to verify |
| `"invalid type"` | Wrong data type | Check formatting table above |

---

## Relationship Fields

Linking records to other records requires UUIDs:

| Field Type | Format | How to Get IDs |
|------------|--------|----------------|
| Single link | UUID string | `attio search <type> "query"` |
| Multi link | Array of UUIDs | `["uuid1", "uuid2"]` |

**Example**: Link a deal to a company
```bash
# First, find the company
attio search companies "Acme Corp"
# Note the UUID from results

# Then link it
attio update deals "deal-uuid" record_data='{"associated_company":"company-uuid"}'
```

---

## Best Practices

1. **Always discover first** - Run `attio fields <type>` before any update
2. **Check select options** - Run `attio options <type> <field>` for dropdowns
3. **Use internal values** - Select fields use slugs like `demo_completed`, not `"Demo Completed"`
4. **Wrap arrays** - When in doubt, wrap in `["value"]`
5. **Use notes for unknowns** - Put uncertain data in notes, not record fields
