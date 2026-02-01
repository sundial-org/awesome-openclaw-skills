---
name: portable-tools
description: Build cross-device tools without hardcoding paths or account names
---

# Portable Tools - Cross-Device Development Methodology

Methodology for building tools that work across different devices, naming schemes, and configurations. Based on lessons from OAuth refresher debugging session (2026-01-23).

## Core Principle

**Never assume your device is the only device.**

Your local setup is just one of many possible configurations. Build for the general case, not the specific instance.

---

## The Three Questions (Before Writing Code)

### 1. "What varies between devices?"

Before writing any code that reads configuration, data, or credentials:

**Ask:**
- File paths? (macOS vs Linux, different home dirs)
- Account names? (user123 vs default vs oauth)
- Service names? (slight variations in spelling/capitalization)
- Data structure? (different versions, different formats)
- Environment? (different shells, different tools available)

**Example from OAuth refresher:**
- ❌ Assumed: Account is always "claude"
- ✅ Reality: Could be "claude", "Claude Code", "default", etc.

**Action:** List variables, make them configurable or auto-discoverable

---

### 2. "How do I prove this works?"

Before claiming success:

**Require:**
- Concrete BEFORE state (exact values)
- Concrete AFTER state (exact values)
- Proof they're different (side-by-side comparison)

**Example from OAuth refresher:**
```
BEFORE:
- Access Token: POp5z1fi...eSN9VAAA
- Expires: 1769189639000

AFTER:
- Access Token: 01v0RrFG...eOE9QAA ✅ Different
- Expires: 1769190268000 ✅ Extended
```

**Action:** Always show data transformation with real values

---

### 3. "What happens when it breaks?"

Before pushing to production:

**Test:**
- Wrong configuration (intentionally break config)
- Missing data (remove expected fields)
- Multiple entries (ambiguous case)
- Edge cases (empty values, special characters)

**Example from OAuth refresher:**
- Test with `keychain_account: "wrong-name"` → Fallback should work
- Test with incomplete keychain data → Should fail gracefully with helpful error

**Action:** Test failure modes, not just happy path

---

## Mandatory Patterns

### Pattern 1: Explicit Over Implicit

**❌ Wrong:**
```bash
# Ambiguous - returns first match
security find-generic-password -s "Service" -w
```

**✅ Correct:**
```bash
# Explicit - returns specific entry
security find-generic-password -s "Service" -a "account" -w
```

**Rule:** If a command can be ambiguous, make it explicit.

---

### Pattern 2: Validate Before Use

**❌ Wrong:**
```bash
DATA=$(read_config)
USE_VALUE="$DATA"  # Hope it's valid
```

**✅ Correct:**
```bash
DATA=$(read_config)
if ! validate_structure "$DATA"; then
    error "Invalid data structure"
fi
USE_VALUE="$DATA"
```

**Rule:** Never assume data has expected structure.

---

### Pattern 3: Fallback Chains

**❌ Wrong:**
```bash
ACCOUNT="claude"  # Hardcoded
```

**✅ Correct:**
```bash
# Try configured → Try common → Error with help
ACCOUNT="${CONFIG_ACCOUNT}"
if ! has_data "$ACCOUNT"; then
    for fallback in "claude" "default" "oauth"; do
        if has_data "$fallback"; then
            ACCOUNT="$fallback"
            break
        fi
    done
fi
[[ -z "$ACCOUNT" ]] && error "No account found. Tried: ..."
```

**Rule:** Provide automatic fallbacks for common variations.

---

### Pattern 4: Helpful Errors

**❌ Wrong:**
```bash
[[ -z "$TOKEN" ]] && error "No token"
```

**✅ Correct:**
```bash
[[ -z "$TOKEN" ]] && error "No token found

Checked:
- Config: $CONFIG_FILE
- Field: $FIELD_NAME
- Expected: { \"tokens\": { \"refresh\": \"...\" } }

Verify with:
  cat $CONFIG_FILE | jq '.tokens'
"
```

**Rule:** Error messages should help user diagnose and fix.

---

## Debugging Methodology (Patrick's Approach)

### Step 1: Get Exact Data

**Don't ask:** "Is it broken?"  
**Ask:** "What exact values do you see? How many entries exist? Which one has the data?"

**Example:**
```bash
# Vague
"Check keychain"

# Specific
"Run: security find-generic-password -l 'Service' | grep 'acct'"
"Tell me: 1. How many entries 2. Which has tokens 3. Last modified"
```

---

### Step 2: Prove With Concrete Examples

**Don't say:** "It should work now"  
**Show:** "Here's the BEFORE token (POp5z...), here's AFTER (01v0R...), they're different"

**Template:**
```
BEFORE:
- Field1: <exact_value>
- Field2: <exact_value>

AFTER:
- Field1: <new_value> ✅ Changed
- Field2: <new_value> ✅ Changed

PROOF: Values are different
```

---

### Step 3: Think Cross-Device Immediately

**Don't think:** "Works on my machine"  
**Think:** "What if their setup differs in [X]?"

**Checklist:**
- [ ] Different account names?
- [ ] Different file paths?
- [ ] Different tools/versions?
- [ ] Different permissions?
- [ ] Different data formats?

---

## Pre-Flight Checklist (Before Publishing)

### Discovery Phase
- [ ] List all external dependencies (files, commands, services)
- [ ] Document what each dependency provides
- [ ] Identify which parts could vary between devices

### Implementation Phase
- [ ] Make variations configurable (with sensible defaults)
- [ ] Add validation for each input
- [ ] Build fallback chains for common variations
- [ ] Add `--dry-run` or `--test` mode

### Testing Phase
- [ ] Test with correct config → Should work
- [ ] Test with wrong config → Should fallback or fail gracefully
- [ ] Test with missing data → Should give helpful error
- [ ] Test with multiple entries → Should handle ambiguity

### Documentation Phase
- [ ] Document default assumptions
- [ ] Document how to verify local setup
- [ ] Document common variations and how to handle them
- [ ] Include data flow diagram
- [ ] Add troubleshooting section

---

## Real-World Example: OAuth Refresher

### Original (Broken)
```bash
# Assumes single entry, no validation, no fallback
KEYCHAIN_DATA=$(security find-generic-password -s "Service" -w)
REFRESH_TOKEN=$(echo "$KEYCHAIN_DATA" | jq -r '.refreshToken')
# Use token (hope it's valid)
```

**Problems:**
- Returns first alphabetical match (wrong entry)
- No validation (could be empty/malformed)
- No fallback (fails if account name differs)

---

### Fixed (Portable)
```bash
# Explicit account with validation and fallback
validate_data() {
    echo "$1" | jq -e '.claudeAiOauth.refreshToken' > /dev/null 2>&1
}

# Try configured account
DATA=$(security find-generic-password -s "$SERVICE" -a "$ACCOUNT" -w 2>&1)
if validate_data "$DATA"; then
    log "✓ Using account: $ACCOUNT"
else
    log "⚠ Trying fallback accounts..."
    for fallback in "claude" "Claude Code" "default"; do
        DATA=$(security find-generic-password -s "$SERVICE" -a "$fallback" -w 2>&1)
        if validate_data "$DATA"; then
            ACCOUNT="$fallback"
            log "✓ Found data in: $fallback"
            break
        fi
    done
fi

[[ -z "$DATA" ]] || ! validate_data "$DATA" && error "No valid data found
Tried accounts: $ACCOUNT, claude, Claude Code, default
Verify with: security find-generic-password -l '$SERVICE'"

REFRESH_TOKEN=$(echo "$DATA" | jq -r '.claudeAiOauth.refreshToken')
```

**Improvements:**
- ✅ Explicit account parameter
- ✅ Validates data structure
- ✅ Automatic fallback to common names
- ✅ Helpful error with verification command

---

## Common Anti-Patterns

### Anti-Pattern 1: "Works On My Machine"
```bash
FILE="/Users/patrick/.config/app.json"  # Hardcoded path
```

**Fix:** Use `$HOME`, detect OS, or make configurable

---

### Anti-Pattern 2: "Hope It's There"
```bash
TOKEN=$(cat config.json | jq -r '.token')
# What if .token doesn't exist? Script continues with empty value
```

**Fix:** Validate before using
```bash
TOKEN=$(cat config.json | jq -r '.token // empty')
[[ -z "$TOKEN" ]] && error "No token in config"
```

---

### Anti-Pattern 3: "First Match Is Right"
```bash
# If multiple entries exist, which one?
ENTRY=$(find_entry "service")
```

**Fix:** Be explicit or enumerate all
```bash
ENTRY=$(find_entry "service" "account")  # Specific
# OR
ALL=$(find_all_entries "service")
for entry in $ALL; do
    validate_and_use "$entry"
done
```

---

### Anti-Pattern 4: "Silent Failures"
```bash
process_data || true  # Ignore errors
```

**Fix:** Fail loudly with context
```bash
process_data || error "Failed to process
Data: $DATA
Expected: { ... }
Check: command_to_verify"
```

---

## Integration With Existing Workflows

### With sprint-plan.md
Add to testing section:
```markdown
## Cross-Device Testing
- [ ] Test with different account names
- [ ] Test with wrong config values
- [ ] Test with missing data
- [ ] Document fallback behavior
```

### With PRIVACY-CHECKLIST.md
Add before publishing:
```markdown
## Portability Check
- [ ] No hardcoded paths (use $HOME, detect OS)
- [ ] No hardcoded names (use config or fallback)
- [ ] Validation on all inputs
- [ ] Helpful errors for common issues
```

### With skill-creator
When building new skills:
1. List what varies between devices
2. Make it configurable or auto-discoverable
3. Test with wrong config
4. Document troubleshooting

---

## Quick Reference Card

**Before writing code:**
1. What varies between devices?
2. How do I prove this works?
3. What happens when it breaks?

**Mandatory patterns:**
- Explicit over implicit
- Validate before use
- Fallback chains
- Helpful errors

**Testing:**
- Correct config → Works
- Wrong config → Fallback or helpful error
- Missing data → Clear diagnostic

**Documentation:**
- Data flow diagram
- Common variations
- Troubleshooting guide

---

## Success Criteria

A tool is **portable** when:

1. ✅ Works on different devices without modification
2. ✅ Auto-discovers common variations in setup
3. ✅ Fails gracefully with actionable error messages
4. ✅ Can be debugged by reading the error output
5. ✅ Documentation covers "what if my setup differs"

**Test:** Give it to someone with a different setup. If they need to ask you questions, the tool isn't portable yet.

---

## Origin Story

This methodology emerged from debugging the OAuth refresher (2026-01-23):
- Script read wrong keychain entry (didn't specify account)
- Assumed single entry existed (multiple did)
- No validation (used empty data)
- No fallback (failed on different account names)

Patrick's approach:
1. Asked for exact data (how many entries, which has tokens)
2. Demanded proof (show BEFORE/AFTER tokens)
3. Thought cross-device (what if naming differs?)

Result: Tool went from single-device/broken to universal/production-ready.

**Key insight:** The bugs weren't in the logic - they were in the assumptions.

---

## When To Use This Skill

**Use when:**
- Building tools that read system configuration
- Working with keychains, credentials, environment variables
- Creating scripts that run on multiple machines
- Publishing skills to ClawdHub (others will use them)

**Apply:**
1. Before implementing: Answer the three questions
2. During implementation: Use mandatory patterns
3. Before testing: Run pre-flight checklist
4. After testing: Document variations and troubleshooting

**Remember:** Your device is just one case. Build for the general case.
