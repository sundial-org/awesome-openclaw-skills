# Known False Positive Patterns

When presenting scan results, check findings against these known false positive patterns. If a finding matches, note it as "likely safe" in your report to the user.

## Network / URLs

| Finding | Why It's Safe |
|---------|--------------|
| URLs in LICENSE.txt, LICENSE.md, *-OFL.txt, COPYING, NOTICE | Standard license files contain apache.org, opensource.org, etc. **These are now grouped into summary lines in reports.** |
| CDN links (cdnjs, googleapis, unpkg) | Frontend skills need CSS/JS libraries |
| localhost / 127.0.0.1 | Skill talks to local services, not the internet |
| example.com, your-*.example | Placeholder URLs in documentation |
| GitHub commit URLs in _meta.json | Metadata from skill registries |

## File Access

| Finding | Why It's Safe |
|---------|--------------|
| `file:///tmp/` or `file:///path` in docs | Example paths showing how media upload works |
| Rainmeter/Program Files paths in reference docs | Legitimate documentation for desktop integration |
| Shebangs (`#!/usr/bin/env`) | Standard script headers, not file access |
| `%USERPROFILE%` in documentation | Explaining where files are stored, not accessing them |

## Shell Execution

| Finding | Why It's Safe |
|---------|--------------|
| `.exec()` on a regex | JavaScript RegExp.exec() — pattern matching, not shell |
| `exec` as a word in docs | Describing functionality, not calling it |
| `run` or `spawn` in variable/function names | Code naming, not child_process calls |

## Obfuscation

| Finding | Why It's Safe |
|---------|--------------|
| Git commit hashes (40-char hex) | Look like base64 but are just commit SHAs |
| Long API endpoint paths | URL paths can resemble encoded strings |
| Unicode in i18n/translation files | Legitimate multi-language support |
| Base64 in test fixtures | Test data, not hidden payloads |

## Prompt Injection

| Finding | Why It's Safe |
|---------|--------------|
| "ignore" + "previous" in changelog/docs | Describing version changes ("ignore previous version") |
| "system" in variable names (SystemData) | Code naming convention, not fake delimiters |
| "act as" in skill description | Describing the skill's role, not injection |

## General Rules

1. **Findings in documentation files (.md, .txt) are less concerning** than findings in executable scripts (.js, .py, .ts). The scanner already downgrades severity for docs.

2. **Skills that declare capabilities matching their findings are honest.** A "web scraper" skill with fetch() calls is expected. A "note-taking" skill with fetch() calls is suspicious.

3. **CDN/font URLs are almost always safe.** Frontend skills commonly reference Google Fonts, cdnjs, unpkg, etc.

4. **License files always contain URLs.** Apache, MIT, GPL licenses link to their source. Never flag these.

5. **_meta.json files from registries** contain commit hashes, timestamps, and repo URLs. These are metadata, not code.

## When In Doubt

If a finding could be either legitimate or malicious:
- Check if the skill's stated purpose explains the finding
- Check if the finding is in a doc file vs executable code  
- Check if the URL/path is a well-known safe domain
- If still uncertain, flag it as "⚠️ Worth reviewing" rather than "🔴 Dangerous"

Present both the finding AND the possible innocent explanation so the user can decide.
