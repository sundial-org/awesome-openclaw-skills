# Risk Scoring Algorithm

## Severity Levels (per finding)
- **critical** — Direct security threat (exfiltration, prompt injection, credential access)
- **high** — Concerning capability (shell exec, network calls, file access outside scope)
- **medium** — Warrants review (URLs, base64 strings, binary files)
- **low** — Minor or informational

## Overall Risk Calculation

Risk is calculated from the combination of individual findings:

1. **CRITICAL** — Any of:
   - Any finding with severity "critical"
   - Obfuscation + Sensitive File Access or Data Exfiltration (combo = hiding intent)
   - Any Prompt Injection finding

2. **HIGH** — Any finding with severity "high"

3. **MEDIUM** — Any of:
   - 3+ medium findings
   - 1+ medium and 2+ low findings

4. **LOW** — Any of:
   - 1-2 medium findings
   - 3+ low findings

5. **CLEAN** — No findings at all

## Key Principle: Obfuscation Escalation

If a skill uses obfuscation techniques AND accesses sensitive files or makes network calls, the risk automatically escalates to CRITICAL. Legitimate skills have no reason to hide what they're doing. This combo strongly suggests malicious intent.

## Declared vs Actual Mismatch

The scanner parses SKILL.md frontmatter to understand the skill's stated purpose, then compares against actual capabilities detected in code. A significant mismatch (e.g., "note-taking" skill that makes network calls and reads credentials) is highlighted in the report but doesn't directly affect the risk score — the individual findings handle that.
