# Skill Evaluation Rubric

Full multi-framework rubric with concrete criteria per score level.
Automated checks (via `scripts/eval-skill.py`) cover structure, trigger, docs, scripts, and security.
This rubric adds the **manual assessment** dimensions that require judgment.

## Scoring: 0–4 per criterion

| Score | Meaning | Guideline |
|-------|---------|-----------|
| 0 | Fail | Missing or broken — blocks publishing |
| 1 | Poor | Present but inadequate — significant rework needed |
| 2 | Acceptable | Works but has notable gaps — should improve |
| 3 | Good | Solid with minor issues — publishable |
| 4 | Excellent | Best-in-class — no meaningful improvements |

---

## 1. Functional Suitability (ISO 25010)

### 1.1 Completeness
*Does it cover the domain adequately?*
- **4:** Covers all common operations + edge cases. A user would rarely need to go outside the skill.
- **3:** Covers core operations. Missing some advanced/niche features.
- **2:** Covers basic operations. Missing several expected features.
- **1:** Only covers a fraction of the domain. Major gaps.
- **0:** Stub or non-functional.

### 1.2 Correctness
*Do operations produce correct results?*
- **4:** All operations tested and verified. Edge cases handled.
- **3:** Core operations correct. Minor bugs in edge cases.
- **2:** Mostly correct but some operations produce wrong results.
- **1:** Several operations are broken or produce incorrect output.
- **0:** Fundamentally broken.

### 1.3 Appropriateness
*Is the technical approach suitable?*
- **4:** Zero external deps, portable, follows platform conventions perfectly.
- **3:** Minimal deps, good approach, minor awkwardness.
- **2:** Unnecessary deps or suboptimal approach for some operations.
- **1:** Wrong tool for the job or heavy unnecessary dependencies.
- **0:** Fundamentally misdesigned.

---

## 2. Reliability (ISO 25010)

### 2.1 Fault Tolerance
*How does it handle failures?*
- **4:** Retries transient errors, graceful fallbacks, partial operations succeed even if some fail.
- **3:** Catches and reports errors clearly. Some retry or fallback logic.
- **2:** Catches errors but dies on first failure. No retry.
- **1:** Unhandled exceptions for common error cases.
- **0:** Crashes with tracebacks on normal error conditions.

### 2.2 Error Reporting
*Are errors actionable?*
- **4:** Structured errors (JSON in --json mode), consistent stderr, actionable messages with fix suggestions.
- **3:** Clear error messages to stderr. User knows what went wrong.
- **2:** Error messages exist but are vague or inconsistent (mixed stdout/stderr).
- **1:** Raw tracebacks or cryptic messages.
- **0:** Silent failures.

### 2.3 Recoverability
*Can interrupted operations resume?*
- **4:** Checkpoint/resume for batch operations. Idempotent by default.
- **3:** No checkpoint but operations are idempotent (safe to re-run).
- **2:** Re-running is safe but redundant work is done.
- **1:** Re-running may cause duplicates or errors.
- **0:** Interrupted operations leave corrupted state.

---

## 3. Performance / Context Efficiency

### 3.1 SKILL.md Token Cost
*Is the SKILL.md appropriately sized for its value?*
- **4:** <150 lines. Progressive disclosure via references. Every line earns its tokens.
- **3:** 150-250 lines. Some content could move to references.
- **2:** 250-400 lines. Verbose explanations an AI doesn't need.
- **1:** 400+ lines. Wastes context window. Should be restructured.
- **0:** So large it crowds out other context.

### 3.2 Execution Efficiency
*Does the script avoid unnecessary work?*
- **4:** Paginated, filtered, incremental where possible. Rate-limited politely.
- **3:** Handles pagination. Some unnecessary full-scans.
- **2:** Works but does redundant API calls or full-library scans.
- **1:** Extremely slow or wasteful for normal operations.
- **0:** Unusably slow.

---

## 4. Usability — AI Agent (Shneiderman, Gerhardt-Powals)

### 4.1 Cold-Start Learnability
*Can a fresh AI instance use this skill correctly on first try?*
- **4:** SKILL.md + examples are sufficient. Troubleshooting reference covers errors. Agent never needs to read source.
- **3:** SKILL.md covers core usage. Some edge cases require experimentation.
- **2:** Agent needs to read source code to understand some operations.
- **1:** SKILL.md is insufficient. Agent will struggle without source access.
- **0:** No documentation. Agent must reverse-engineer everything.

### 4.2 Consistency
*Are patterns uniform across commands/operations?*
- **4:** Same flag names, same output format, same error handling everywhere.
- **3:** Mostly consistent. One or two exceptions.
- **2:** Inconsistent flags, mixed output formats, or uneven error handling.
- **1:** Every command behaves differently.
- **0:** No discernible pattern.

### 4.3 Feedback Quality
*Does the skill communicate progress and results clearly?*
- **4:** Progress indicators, summary reports, emoji-scannable output, JSON mode.
- **3:** Clear success/failure messages. Batch progress shown.
- **2:** Basic output. Hard to tell success from failure in batch operations.
- **1:** Minimal output. Agent has to infer outcomes.
- **0:** Silent or cryptic.

### 4.4 Error Prevention
*Does the skill prevent mistakes before they happen?*
- **4:** Input validation, safe defaults (recoverable > permanent), dry-run for destructive ops, duplicate detection.
- **3:** Some validation and safe defaults. Destructive ops have confirmation.
- **2:** Minimal validation. Unsafe defaults for some operations.
- **1:** No validation. Easy to accidentally destroy data.
- **0:** Actively dangerous defaults.

---

## 5. Usability — Human End User (Tognazzini, Norman)

### 5.1 Discoverability
*Can a human figure out what's available?*
- **4:** --help on all commands with examples. SKILL.md documents everything.
- **3:** --help works. SKILL.md covers core operations.
- **2:** Basic --help. Some features undocumented.
- **1:** Minimal help text. Must read source.
- **0:** No help or documentation.

### 5.2 Forgiveness / Undo
*Can mistakes be reversed?*
- **4:** Destructive ops default to recoverable (trash). Undo available. Confirmation prompts.
- **3:** Confirmation on destructive ops. Some recoverability.
- **2:** Confirmation exists but permanent is the default.
- **1:** No confirmation on destructive operations.
- **0:** Destructive operations with no warning.

---

## 6. Security (ISO 25010 + OSS Hygiene)

### 6.1 Credential Handling
*How are secrets managed?*
- **4:** All secrets via env vars. No personal data in source. Documented.
- **3:** Secrets via env vars. Minor issues (undocumented optional var).
- **2:** Mostly env vars but some hardcoded values.
- **1:** Credentials in source code.
- **0:** Credentials in source AND committed to git.

### 6.2 Input Validation
*Are inputs sanitized?*
- **4:** All user inputs validated with helpful error messages.
- **3:** Key inputs validated. Some edge cases unchecked.
- **2:** Minimal validation. Bad input causes API errors.
- **1:** No validation. Garbage in, garbage out.
- **0:** Injection-vulnerable.

### 6.3 Data Safety
*Are write operations safe by default?*
- **4:** Dry-run defaults, confirmation prompts, safe defaults (trash > delete).
- **3:** Most write ops have confirmation. Safe defaults.
- **2:** Some write ops unprotected.
- **1:** Write ops fire without confirmation.
- **0:** Silent data destruction possible.

---

## 7. Maintainability (ISO 25010)

### 7.1 Modularity
*Is the code well-organized?*
- **4:** Clear separation of concerns. Helpers extracted. Easy to add features.
- **3:** Functions organized by command. Some helpers extracted.
- **2:** Monolithic but navigable. Would benefit from refactoring.
- **1:** Spaghetti. Hard to find things.
- **0:** Incomprehensible.

### 7.2 Modifiability
*How easy is it to change?*
- **4:** Adding a new command is copy-paste-modify. Patterns are clear.
- **3:** Clear patterns. Some globals or tight coupling.
- **2:** Can be modified but requires understanding implicit dependencies.
- **1:** Changes break other things. No clear patterns.
- **0:** Effectively frozen — too fragile to touch.

### 7.3 Testability
*Can it be tested?*
- **4:** Test suite exists. Functions return values. Mockable API layer.
- **3:** No test suite but functions are testable (return values, pure helpers).
- **2:** Some testable functions. Others depend on live API or sys.exit.
- **1:** Everything depends on live API. sys.exit everywhere.
- **0:** Untestable architecture.

---

## 8. Agent-Specific Heuristics

### 8.1 Trigger Precision
*Does the description activate the skill reliably?*
- **4:** Specific domain + action words + "Use when..." contexts. Low false positive/negative risk.
- **3:** Good domain keywords. Some ambiguity with similar skills.
- **2:** Too broad or too narrow. Frequent false triggers or missed triggers.
- **1:** Description doesn't match what the skill does.
- **0:** No description.

### 8.2 Progressive Disclosure
*Is context loaded efficiently?*
- **4:** 3+ levels: description → SKILL.md → references. Agent loads only what's needed.
- **3:** 2 levels: description → SKILL.md. Everything in one file but concise.
- **2:** Everything in SKILL.md. No reference files despite complex domain.
- **1:** Requires reading source code for basic usage.
- **0:** No disclosure hierarchy.

### 8.3 Composability
*Can it work with other tools in a pipeline?*
- **4:** --json for all commands, stdin input, proper exit codes, stderr for errors.
- **3:** --json for key commands. Good exit codes.
- **2:** Limited machine-readable output. Some commands.
- **1:** Human-readable only. No structured output.
- **0:** Output is unparseable.

### 8.4 Idempotency
*Is it safe to re-run?*
- **4:** All operations are idempotent. Re-running produces same state.
- **3:** Most operations idempotent. Some may create duplicates.
- **2:** Core operations idempotent. Batch ops may duplicate.
- **1:** Re-running causes problems.
- **0:** Re-running corrupts state.

### 8.5 Escape Hatches
*Can the agent/user override default behavior?*
- **4:** --force, --dry-run, --verbose, --quiet, --json, custom API URLs.
- **3:** --force and --dry-run available. Good flag coverage.
- **2:** Some overrides. Missing key flags.
- **1:** Minimal overrides. Hard to customize behavior.
- **0:** No overrides. Take it or leave it.

---

## Scoring Template

Copy this for your evaluation:

```
| Category | Subcriteria | Score | Notes |
|----------|-------------|-------|-------|
| 1.1 Completeness | | /4 | |
| 1.2 Correctness | | /4 | |
| 1.3 Appropriateness | | /4 | |
| 2.1 Fault Tolerance | | /4 | |
| 2.2 Error Reporting | | /4 | |
| 2.3 Recoverability | | /4 | |
| 3.1 Token Cost | | /4 | |
| 3.2 Execution Efficiency | | /4 | |
| 4.1 Learnability | | /4 | |
| 4.2 Consistency | | /4 | |
| 4.3 Feedback Quality | | /4 | |
| 4.4 Error Prevention | | /4 | |
| 5.1 Discoverability | | /4 | |
| 5.2 Forgiveness | | /4 | |
| 6.1 Credential Handling | | /4 | |
| 6.2 Input Validation | | /4 | |
| 6.3 Data Safety | | /4 | |
| 7.1 Modularity | | /4 | |
| 7.2 Modifiability | | /4 | |
| 7.3 Testability | | /4 | |
| 8.1 Trigger Precision | | /4 | |
| 8.2 Progressive Disclosure | | /4 | |
| 8.3 Composability | | /4 | |
| 8.4 Idempotency | | /4 | |
| 8.5 Escape Hatches | | /4 | |
| **TOTAL** | | **/100** | |
```
