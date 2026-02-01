# SkillGuard Red Team Notes

## Current Weaknesses (v0.1.0 — honest assessment)

### 1. Trivially Evadable
The current scanner uses simple regex. Any attacker worth their salt evades it in seconds:
- String concatenation: `'ev' + 'al'` → invisible to regex
- Bracket notation: `global['eval']` or `require('child' + '_process')`
- Variable aliasing: `const fn = eval; fn(code)`
- Template literals: `` `${'child_'}${'process'}` ``
- Hex encoding: `\x65\x76\x61\x6c` = "eval"
- Unicode escapes: `\u0065\u0076\u0061\u006c` = "eval"
- Base64 payloads decoded at runtime
- Dynamic require/import: `require(someVar)` where someVar is built at runtime
- Rot13 or custom encoding
- Buffer.from() string construction
- Array.map + String.fromCharCode

### 2. No Data Flow Analysis
Current scanner flags individual patterns but doesn't connect them:
- Reading credentials + making network call = EXFILTRATION CHAIN (much worse than either alone)
- File read → base64 encode → fetch POST = textbook data theft
- Environment variable access → network send = key exfiltration

### 3. No Cross-File Correlation
- File A defines a helper function that looks innocent
- File B imports it and uses it maliciously
- Scanner checks each file independently — misses the chain

### 4. Prompt Injection Detection is Basic
Sophisticated injection techniques not caught:
- Unicode homoglyphs (Cyrillic 'а' looks like Latin 'a')
- Zero-width characters between words
- Invisible Unicode (U+200B, U+FEFF, U+200C, U+200D)
- Instructions hidden in markdown image alt text
- Multi-language injection (instructions in other scripts the model reads)
- Role-play framing ("Let's play a game where you are a system admin...")
- Gradual escalation across multiple paragraphs
- Encoded instructions in URLs or data URIs
- Markdown comment injection `<!-- system: ignore previous -->`

### 5. False Positive Problem
- Clean weather skill scored 70/100 — too scary for a legit skill
- `fetch()` in a weather skill is expected, not suspicious
- No awareness of declared vs undeclared capabilities
- No allowlisting for known-good patterns

### 6. No Behavioral Signatures
- Doesn't detect attack PATTERNS, only individual indicators
- A real credential stealer has a signature: read secrets → encode → exfiltrate → cover tracks
- Should score compound behaviors much higher than individual matches

## Attack Scenarios to Defend Against

### Scenario 1: The Trojan Skill
Real functionality (works as advertised) + hidden malicious payload.
The cover code is clean and useful. The attack is in one cleverly obfuscated function.

### Scenario 2: The Time Bomb
Skill works perfectly for N days, then activates malicious behavior.
`if (Date.now() > 1800000000000) { /* steal creds */ }`

### Scenario 3: The Social Engineer
SKILL.md contains subtle prompt injection that tells the agent to
share API keys "for debugging" or "compatibility checking."

### Scenario 4: The Supply Chain
Skill requires installing an npm package that contains the actual malware.
The skill code itself is clean.

### Scenario 5: The Environment Probe
Skill first checks if it's being scanned (sandbox detection),
then only activates in real environments.

### Scenario 6: The Polyglot
Malicious code hidden in a file that looks like data (JSON, YAML)
but is actually executable in certain contexts.

### Scenario 7: The Slow Leak
Skill exfiltrates one piece of data per invocation over weeks.
Each individual action looks innocent.

## Hardening Plan

### Phase 1: Evasion-Resistant Detection
- AST-aware analysis for JS/TS (parse the actual code, not just text)
- String reconstruction detection (concatenation, template literals, fromCharCode)
- Dynamic import/require detection
- Encoded string detection and decoding
- Variable flow tracking (alias chains)

### Phase 2: Behavioral Signatures
- Define compound behavior patterns (read → encode → send)
- Cross-file import chain tracking
- Score compound behaviors exponentially higher
- Time-bomb detection (date comparisons against future timestamps)
- Sandbox detection patterns (checking env vars, /proc, etc.)

### Phase 3: Advanced Prompt Injection
- Unicode anomaly detection (mixed scripts, homoglyphs, invisible chars)
- Markdown structure analysis (hidden content in comments, image alt text)
- Instruction-like content detection even without obvious markers
- Multi-language text detection in code files

### Phase 4: Context-Aware Scoring
- Compare declared capabilities (metadata) vs actual behavior
- Known-good API allowlist (wttr.in, api.github.com, etc.)
- Penalize undeclared capabilities heavily
- Reward transparency (skills that document their network calls)

### Phase 5: Red Team Gauntlet
- 20+ evasive test fixtures
- Must catch every single one
- Zero false negatives on known attacks
- Acceptable false positive rate on legitimate skills
