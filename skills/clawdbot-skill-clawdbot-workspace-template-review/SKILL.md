---
name: clawdbot-workspace-template-review
description: Compare a Clawdbot workspace against the official templates installed with Clawdbot (npm or source) and list missing sections to pull in, especially after upgrades.
---

# Workspace Template Diff

Use this skill when the user wants to compare their workspace `.md` files (AGENTS, SOUL, USER, IDENTITY, TOOLS, HEARTBEAT, etc.) against the official Clawdbot templates, then review missing sections and decide what to add.

## Locate the official templates

Find the installed Clawdbot source root:

- If `clawdbot` is installed via npm/pnpm globally:
  - `command -v clawdbot`
  - If it points into `.../node_modules/.bin/`, resolve to the sibling `node_modules/clawdbot`
  - Or use `npm root -g` / `pnpm root -g` and look for `clawdbot/`
- If Clawdbot runs from source, use that checkout root (must contain `package.json`).

Templates live at:

```
<clawdbot-root>/docs/reference/templates/
```

If you can’t find the source root, ask the user where their Clawdbot is installed.

## Comparison workflow

1. Identify the workspace root (the user’s “our version” directory).
2. For each template file in `docs/reference/templates` (skip `*.dev.md`):
   - Open the official template and the workspace file with the same name.
   - Ignore template frontmatter (`---` block) and any “First Run”/“Bootstrap” sections.
   - Compare the remaining sections and list any missing blocks.

Helpful commands (use ad‑hoc CLI tools like `diff`):

```
ls <clawdbot-root>/docs/reference/templates
sed -n '1,200p' <clawdbot-root>/docs/reference/templates/AGENTS.md
sed -n '1,200p' <workspace>/AGENTS.md
diff -u <clawdbot-root>/docs/reference/templates/AGENTS.md <workspace>/AGENTS.md
```

When reporting diffs:
- Show the missing sections verbatim from the official template.
- Explain briefly why they matter, then ask whether to add them.
- Move file by file; skip files that only differ by frontmatter or bootstrap content.

## Output format

Use the “missing section” format we used previously:
- File path
- Missing block(s)
- Suggestion + question to proceed
