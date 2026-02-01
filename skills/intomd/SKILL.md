---
name: intomd
version: 1.0.0
description: Fetch and convert any documentation URL to Markdown using into.md service.
metadata: {"clawdbot":{"emoji":"📄","requires":{"bins":["curl"]}}}
---

# intomd

Use `intomd` to fetch clean markdown from a documentation site via into.md.

## Usage

```bash
# Fetch markdown
curl -sL "https://into.md/$1"
```

## Example

```bash
intomd https://zod.dev
```
