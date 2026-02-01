# Company Management Workflows

## Contents
- Workflow 1: Find or Create Company
- Workflow 2: Update Company
- Workflow 3: Add Notes to Company
- Quick Tips

---

## Workflow 1: Find or Create Company

**When to use**: Before creating or updating a company to avoid duplicates

**Steps**:

### Step 1: Search by domain (most reliable)
```bash
attio search companies "exact-domain.com"
```

### Step 2: Alternate search by name
```bash
attio search companies "Exact Company Name"
```

### Step 3: Create if not found
```bash
attio create companies record_data='{"name":"Company Name","domains":["company.com"]}'
```

---

## Workflow 2: Update Company

**When to use**: Adding or changing data on an existing company record

**Steps**:

### Step 1: Find the Company
```bash
attio search companies "domain.com"
```

### Step 2: Review Existing Data
```bash
attio get companies "company-uuid"
```

### Step 3: Check Available Fields
```bash
attio fields companies
```

### Step 4: Update Record
```bash
attio update companies "company-uuid" record_data='{"field_name":"value"}'
```

**Important**: Only use fields that exist in your workspace. Run `attio fields companies` first to see what's available.

---

## Workflow 3: Add Notes to Company

**When to use**: Recording unstructured information, meeting notes, research, or data that doesn't fit existing fields

**Steps**:

### Step 1: Find the Company
```bash
attio search companies "Company Name"
```

### Step 2: Add Note
```bash
attio note companies "company-uuid" "Note Title" "Note content here"
```

**Example - Meeting Notes**:
```bash
attio note companies "uuid" "Sales Call - Jan 2025" "Discussed pricing options. Decision maker: CEO. Follow up next week with proposal."
```

**Example - Research**:
```bash
attio note companies "uuid" "Company Research" "Industry: Healthcare\nEmployee Count: ~50\nKey Contact: Jane Doe (VP Sales)"
```

---

## Quick Tips

1. **Always search before creating** - Avoid duplicates by searching first
2. **Use notes for uncertainty** - When unsure if a field exists, use notes
3. **Discover fields first** - Run `attio fields companies` before updating
4. **Format data correctly** - Numbers as `85`, arrays as `["Value"]`, booleans as `true`
5. **Check select options** - For dropdown fields, run `attio options companies <field>`
