---
name: entr
description: Run arbitrary commands when files change. Useful for watching files and triggering builds or tests.
---

# entr (Event Notify Test Runner)

A utility for running arbitrary commands when files change.

## Usage

`entr` takes a list of filenames from standard input and executes the utility specified as the first argument.

### Syntax
```bash
<file_listing_command> | entr <utility> [arguments]
```

### Options
- `-c`: Clear the screen before invoking the utility.
- `-r`: Reload a persistent child process (e.g., a server).
- `-s`: Evaluate the first argument using the interpreter specified by `SHELL`.

## Examples

**Rebuild project when sources change:**
```bash
find src/ -name "*.c" | entr make
```

**Run tests when JS files change:**
```bash
git ls-files | grep '\.js$' | entr npm test
```

**Auto-reload a Node server:**
```bash
ls *.js | entr -r node app.js
```

## Agent Notes
`entr` blocks the terminal. When using it as an agent:
1. Use `process` tool to run it in the background if you need to do other things.
2. Or use it for a quick "watch mode" session where you intend to monitor output for a while.
