---
name: steel-browser
description: Use Steel cloud browsers and CLI commands for session-backed web automation, scraping, screenshots, PDFs, and multi-step browser flows.
metadata: {"clawdbot":{"emoji":"🌐","requires":{"bins":["node","npm"]}}}
allowed-tools: Bash(steel:*), Bash(npx @steel-dev/cli:*)
---

# Steel Browser

Use this skill when the task needs a real browser instead of plain HTTP fetches.
Steel gives you cloud browser sessions, explicit session lifecycle control, and API tools for scraping and artifact capture.

## Setup

Install and authenticate first:

```bash
npm i -g @steel-dev/cli
steel login
```

For CI or non-interactive environments, set `STEEL_API_KEY`.

## When to use

Use this skill for:

- website navigation and interaction
- login flows and multi-step forms
- scraping dynamic pages
- screenshots and PDFs
- anti-bot-sensitive automation
- workflows that need persistent browser state across steps

Skip this skill when the task must run only against localhost or a private network target that Steel cloud sessions cannot reach.

## Core workflow

1. Decide between fast extraction and interactive browsing.
2. For extraction, use `steel scrape`.
3. For interaction, start a named browser session.
4. Open the page, inspect with `snapshot -i`, then interact in small steps.
5. Re-snapshot after major page changes.
6. Stop the session when done.

## Fast extraction

```bash
steel scrape https://example.com --format markdown
steel screenshot https://example.com
steel pdf https://example.com
```

Use `steel scrape` first when the user mainly needs page content, not click-by-click automation.

## Interactive flow

```bash
SESSION="job-$(date +%s)"
steel browser start --session "$SESSION"
steel browser open https://example.com --session "$SESSION"
steel browser snapshot -i --session "$SESSION"
steel browser click @e1 --session "$SESSION"
steel browser fill @e2 "text" --session "$SESSION"
steel browser wait --load networkidle --session "$SESSION"
steel browser stop --session "$SESSION"
```

## Key commands

### Session lifecycle

```bash
steel browser start --session <name>
steel browser sessions
steel browser live --session <name>
steel browser stop --session <name>
steel browser stop --all
```

### Navigation and inspection

```bash
steel browser open <url> --session <name>
steel browser snapshot -i --session <name>
steel browser snapshot -c --session <name>
steel browser get title --session <name>
steel browser get url --session <name>
steel browser get text @e1 --session <name>
```

### Interaction

```bash
steel browser click @e1 --session <name>
steel browser fill @e2 "text" --session <name>
steel browser type @e2 "text" --session <name>
steel browser press Enter --session <name>
steel browser select @e1 "value" --session <name>
steel browser wait @e1 --session <name>
steel browser wait --text "Success" --session <name>
```

### Artifacts

```bash
steel browser screenshot ./page.png --session <name>
steel browser pdf ./page.pdf --session <name>
steel scrape <url> --format markdown,html
```

## CAPTCHA and anti-bot

For harder sites:

```bash
steel browser start --session <name> --stealth
steel browser captcha status --wait --session <name>
```

If the session is configured for manual solving:

```bash
steel browser captcha solve --session <name>
steel browser captcha status --wait --session <name>
```

## Migration from `agent-browser`

For most existing scripts, replace:

```bash
agent-browser <command>
```

with:

```bash
steel browser <command>
```

Steel keeps the familiar browser command shape and adds explicit lifecycle commands like `start`, `stop`, `sessions`, and `live`.

## Troubleshooting

If the workflow fails:

1. Check auth with `steel login` or `STEEL_API_KEY`.
2. Make sure every command uses the same `--session <name>`.
3. Do not mix cloud and local modes within one run.
4. Inspect active sessions with `steel browser sessions`.
5. If state is bad, stop the session and start a fresh one.

Useful diagnostics:

```bash
steel browser sessions
steel browser live --session <name>
steel browser stop --all
```

## References

- Skill source: <https://github.com/steel-dev/cli/tree/main/skills/steel-browser>
- Docs index: <https://docs.steel.dev/llms-full.txt>
- Browser repo: <https://github.com/steel-dev/steel-browser>
