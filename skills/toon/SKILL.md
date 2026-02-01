---
name: toon
description: Compress JSON data to TOON format for ~40% context savings. Use when fetching APIs, reading JSON files, or any task outputting structured data. Pipe any output through `toon` - JSON gets compressed, non-JSON passes through unchanged.
---

# TOON Context Compression

Pipe any command output through `toon` to compress JSON and save ~40% tokens.

## Usage

```bash
# API responses
curl -s "https://api.example.com/data" | toon

# JSON files  
cat data.json | toon

# Any command - safe on non-JSON (passes through unchanged)
some_command | toon
```

## Install

```bash
# Copy script to PATH
cp scripts/toon ~/.local/bin/
chmod +x ~/.local/bin/toon
```

Requires: `npx` (Node.js)

## Example

```json
[{"id":1,"name":"Alice"},{"id":2,"name":"Bob"}]
```
→
```toon
[2]{id,name}:
  1,Alice
  2,Bob
```

## When to Use

- **Always** when fetching JSON APIs
- **Always** when reading JSON files into context
- Safe to use on any output — non-JSON passes through

## Reference

- Format spec: https://toonformat.dev
- CLI: `@toon-format/cli`
