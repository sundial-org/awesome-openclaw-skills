---
name: feishu-card
description: Send rich interactive cards to Feishu (Lark) users or groups. Supports Markdown (code blocks, tables), titles, color headers, and buttons.
tags: [feishu, lark, card, message, interactive, markdown]
---

# Feishu Card Skill

Send rich interactive cards via Feishu Open API.
Updated to use the `markdown` component tag for full Markdown support (Code blocks, Tables, etc.).

## Usage

```bash
# Via argument
node send.js --target "ou_..." --text "Hello **World**"

# Via file (Recommended for complex content)
node send.js --target "ou_..." --text-file message.md

# Via STDIN (New! Safe for shell scripts)
echo "Hello **World**" | node send.js --target "ou_..."
```

## Options
- `-t, --target`: User Open ID (`ou_...`) or Group Chat ID (`oc_...`).
- `-x, --text`: Markdown content.
- `-f, --text-file`: Read markdown from file.
- `STDIN`: If text/text-file is missing, content is read from STDIN.
- `--title`: Card header title.
- `--color`: Header color (blue, red, green, etc.).
- `--button-text`: Add a bottom button.
- `--button-url`: Button URL.
- `--text-size`: Text size (`normal`, `heading`, `heading-1`... `small`).
- `--text-align`: Alignment (`left`, `center`, `right`).
