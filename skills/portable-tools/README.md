# Portable Tools

Build tools that work on everyone's device, not just yours.

**The problem:** Your code works perfectly on your machine but breaks on others because of hardcoded paths, account names, or missing validation.

**This skill:** A proven methodology for building tools that auto-discover setup variations and work universally.

---

## 📋 Requirements

- bash
- Basic understanding of shell scripts

---

## ⚡ What It Does

**Your tools work on any device without manual configuration.**

This skill provides:
- Three discovery questions to ask before coding
- Four core patterns for universal tools
- An automated pre-publish checklist
- Real-world examples from debugging sessions

Learned from fixing tools that failed on other devices despite working perfectly locally.

---

## 🚀 Installation

```bash
clawdhub install portable-tools
```

---

## 🔧 How It Works

**Result:** You build tools once and they work everywhere.

**Before writing any code, answer three questions:**

1. **What varies between devices?**
   - Account names, file paths, data formats, OS versions?

2. **How do I prove this works?**
   - Can I show BEFORE/AFTER with real values from different setups?

3. **What happens when it breaks?**
   - Have I tested with wrong config, missing data, edge cases?

**Then implement using four core patterns:**

### Pattern 1: Be Explicit

**Don't assume.** Pass parameters explicitly.

```bash
# ❌ Ambiguous
find_entry "service"

# ✅ Explicit  
find_entry "service" "account"
```

### Pattern 2: Validate First

**Check structure before use.**

```bash
DATA=$(read_config)
validate "$DATA" || error "Invalid structure"
```

### Pattern 3: Build Fallbacks

**Try alternatives when configured value fails.**

```bash
for candidate in "$configured" "default" "fallback"; do
    if has_data "$candidate"; then break; fi
done
```

### Pattern 4: Give Helpful Errors

**Show what you tried and how to verify.**

```bash
error "Not found

Tried: $attempts
Verify with: command_to_check"
```

**Before publishing, run the automated checklist:**

```bash
bash ~/clawd/skills/portable-tools/pre-publish-checklist.sh /path/to/your/code
```

Output:
```
✅ No hardcoded paths
✅ Has validation patterns
⚠️  Errors could be more helpful
```

**Success metric:** Someone with a different setup can use your tool without asking you questions.

---
---

# 📚 Additional Information

**Everything below is optional.** The four patterns above handle most cases.

This section contains:
- Full methodology guide
- Real-world case studies
- Integration examples

**You don't need to read this to start building portable tools.**

---

<details>
<summary><b>Full Methodology Guide</b></summary>

<br>

See `SKILL.md` for complete patterns and anti-patterns.

**Key topics covered:**
- Discovery phase (list what varies)
- Implementation patterns in detail
- Testing phase (wrong config, missing data, edge cases)
- Pre-flight checklist breakdown
- Common anti-patterns to avoid

</details>

<details>
<summary><b>Real-World Example: OAuth Refresher</b></summary>

<br>

**The problem:**

Script assumed single keychain entry. Read the wrong one.

**Root cause:**

Didn't ask "what varies between devices" upfront.

**Symptoms:**
- Worked on one device
- Failed on others with "no refresh token found"  
- Actually had TWO keychain entries (metadata vs full data)

**Fix applied:**

1. Made account name explicit (not ambiguous)
2. Validated data structure before use
3. Built automatic fallback to common names
4. Added helpful errors with verification commands

**Result:** Works across all device setups without configuration.

See full postmortem in `SKILL.md`.

</details>

<details>
<summary><b>Integration With Other Workflows</b></summary>

<br>

### With sprint-plan.md

Add to testing section:
```markdown
## Cross-Device Testing
- [ ] Test with different account names
- [ ] Test with wrong config
- [ ] Test with missing data
```

### With PRIVACY-CHECKLIST.md

Before publishing:
```markdown
## Portability Check
- [ ] No hardcoded paths
- [ ] Validation on all inputs
- [ ] Helpful errors
```

### With publisher

Answer the three questions upfront when designing new skills.

</details>

---

## License

MIT
