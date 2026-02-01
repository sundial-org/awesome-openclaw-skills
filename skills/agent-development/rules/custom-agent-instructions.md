---
globs: ["**/.claude/agents/*.md", "**/agents/*.md", "**/.claude/settings.json"]
---

# Custom Agent Design Principles

## 1. Declarative Over Imperative

Describe **what** to accomplish, not **how** to use tools.

Claude Code's harness already includes tool selection guidance - prescriptive instructions can conflict with it.

## 2. Give All Tools to All Agents

Don't micromanage tool lists per agent. Use a standard full toolset:

```yaml
tools: Read, Write, Edit, Glob, Grep, Bash
```

**Why**: Simpler config, more flexibility, trust the model to choose.

## 3. Use Allowlists for Bash Commands

Instead of restricting Bash access, allowlist safe commands in `.claude/settings.json`:

```json
{
  "permissions": {
    "allow": [
      "Write",
      "Edit",
      "WebFetch(domain:*)",
      "Bash(cd *)",
      "Bash(cp *)",
      "Bash(mkdir *)",
      "Bash(ls *)",
      "Bash(find *)",
      "Bash(cat *)",
      "Bash(head *)",
      "Bash(tail *)",
      "Bash(wc *)",
      "Bash(pwd)",
      "Bash(echo *)",
      "Bash(grep *)",
      "Bash(diff *)",
      "Bash(mv *)",
      "Bash(touch *)",
      "Bash(basename *)",
      "Bash(dirname *)",
      "Bash(sort *)",
      "Bash(uniq *)",
      "Bash(test *)",
      "Bash([ *)",
      "Bash(for *)",
      "Bash(cut *)",
      "Bash(file *)"
    ]
  }
}
```

This avoids permission prompts without limiting agent capabilities.

**Why these are included**:
- `Write`, `Edit` - Background agents can't prompt; without these, file ops fail silently
- `WebFetch(domain:*)` - Allow fetching from any domain without prompts
- `Bash(...)` - Safe read-only and file management commands

**Note**: `WebSearch` doesn't support wildcards - it requires exact search terms, so can't be blanket-allowed.

**Note**: Pattern matching is based on the **first token** - `for file in...` needs `Bash(for *)`, not just the commands inside the loop.

## Corrections

| If agent says... | Use instead... |
|------------------|----------------|
| `grep -r "PLACEHOLDER:" build/*.html` | "Find any PLACEHOLDER comments in build/*.html" |
| `ls build/` | "Check build/ folder exists and list its contents" |
| `cat discovery/report.json \| jq '.abn'` | "Read ABN from discovery/report.json" |
| "Use the Grep tool to..." | "Search for X in Y" |
| "Run this bash command:" | "Verify that X exists/matches/contains" |

## Pattern

**Imperative (avoid)**:
```markdown
### Check for placeholders
```bash
grep -r "PLACEHOLDER:" build/*.html
grep -ri "TODO\|TBD" build/*.html
```
```

**Declarative (prefer)**:
```markdown
### Check for placeholders
Search all HTML files in build/ for:
- PLACEHOLDER: comments
- TODO or TBD markers
- Template brackets like [Client Name]

Any match = incomplete content.
```

## What to Include in Agent Instructions

| Include | Skip |
|---------|------|
| Task goal and context | Explicit bash/tool commands |
| Input file paths | "Use X tool to..." |
| Output file paths and format | Step-by-step tool invocations |
| Success/failure criteria | Shell pipeline syntax |
| Blocking checks (prerequisites) | Micromanaged workflows |
| Quality checklists | |

## Exception

Bash commands in instructions are appropriate when:
- Running external CLIs (`jezpress-cli`, `npx tsx`, `wrangler`)
- Complex file operations that tools don't cover
- The specific command syntax matters (rare)

## Summary

**Philosophy**: Trust the model, simplify config, use allowlists.

| Instead of... | Do this... |
|---------------|------------|
| Curating tools per agent | Give all tools to all agents |
| Prescribing how to use tools | Describe what to accomplish |
| Restricting Bash access | Allowlist safe commands |
| Micromanaging workflows | Define inputs, outputs, criteria |
