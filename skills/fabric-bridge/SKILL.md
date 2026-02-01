---
name: fabric-bridge
description: "Run Fabric AI patterns for text transformation, analysis, and content creation. Use when the user asks to use a Fabric pattern, extract wisdom, analyze claims, improve writing, summarize with Fabric, or mentions 'fabric' CLI. Supports 242+ patterns for tasks like content analysis, writing improvement, code review, threat modeling, and structured extraction."
homepage: https://github.com/danielmiessler/fabric
metadata: {"clawdbot":{"emoji":"🧶","requires":{"bins":["fabric-ai"]},"install":[{"id":"brew","kind":"brew","formula":"fabric-ai","bins":["fabric-ai"],"label":"Install Fabric AI (brew)"}]}}
---

# Fabric Bridge

Run Fabric AI patterns via the `fabric-ai` CLI. Each pattern is a reusable system prompt for a specific task.

> See `references/popular-patterns.md` for a curated list of high-quality patterns by category.

## Important Notes

- The command is **`fabric-ai`**, not `fabric`.
- First-time setup: run `fabric-ai -S` to configure API keys.
- If pattern list is empty: run `fabric-ai -U` to update patterns.
- Use `-s` (stream) for most calls to avoid long waits.

## Core Commands

### Basic usage

```bash
echo "input text" | fabric-ai -p <pattern>
```

### Stream output (recommended)

```bash
echo "input text" | fabric-ai -p <pattern> -s
```

### Process a YouTube video

```bash
fabric-ai -y "https://youtube.com/watch?v=..." -p extract_wisdom -s
```

### Process a web page

```bash
fabric-ai -u "https://example.com/article" -p summarize -s
```

### Specify model

```bash
echo "input" | fabric-ai -p <pattern> -m gpt-4o
```

### Chinese output

```bash
echo "input" | fabric-ai -p <pattern> -g zh -s
```

### Chain patterns (pipe output to next pattern)

```bash
echo "input" | fabric-ai -p extract_wisdom | fabric-ai -p summarize
```

### Reasoning strategy (requires setup)

```bash
echo "input" | fabric-ai -p <pattern> --strategy cot -s
```

### Process an image (multimodal)

```bash
echo "describe this image" | fabric-ai -p <pattern> -a /path/to/image.png -s
```

### Use context

```bash
echo "input" | fabric-ai -p <pattern> -C my_context -s
```

### Session continuity

```bash
echo "input" | fabric-ai -p <pattern> --session my_session -s
```

### Save output to file

```bash
echo "input" | fabric-ai -p extract_wisdom -o output.md
```

### Copy output to clipboard

```bash
echo "input" | fabric-ai -p extract_wisdom -c
```

### Dry run (preview without calling API)

```bash
fabric-ai -p <pattern> --dry-run
```

### List all available patterns

```bash
fabric-ai -l
```

## Template Variables

Patterns can contain `{{variable}}` placeholders. Pass values with `-v`:

```bash
# Single variable
echo "input" | fabric-ai -p <pattern> -v="#role:expert"

# Multiple variables
echo "input" | fabric-ai -p <pattern> -v="#role:expert" -v="#points:30"
```

## Custom Patterns

Create custom patterns at `~/.config/fabric/patterns/<name>/system.md`.

Each pattern directory contains a `system.md` file with the system prompt.

## Feeding File Content

```bash
cat file.txt | fabric-ai -p <pattern> -s
cat file1.md file2.md | fabric-ai -p <pattern> -s
```

## Tips

- Prefer `-s` (stream) for interactive use — output appears incrementally.
- Chain patterns for multi-step processing (extract → summarize → translate).
- Use `-g zh` when the user wants Chinese output.
- Use `-o file.md` to save output, `-c` to copy to clipboard.
- Use `--dry-run` to inspect what will be sent before making API calls.
- Run `fabric-ai -U` periodically to get new community patterns.
