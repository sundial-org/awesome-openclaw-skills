---
name: bun-runtime
description: Bun runtime capabilities for filesystem, process, and network operations. Use when you need to execute Bun-specific operations like Bun.file(), Bun.write(), or Bun.glob() for optimized file handling, or when working with Bun's native process/network APIs. Triggered by requests for Bun runtime features, file operations with Bun, or high-performance I/O tasks.
---

# Bun Runtime

Native Bun runtime operations for filesystem, process, and network tasks.

## When to Use

Use this skill when:
- Working with Bun's native file APIs (`Bun.file()`, `Bun.write()`, `Bun.glob()`)
- Need optimized I/O operations in Bun environment
- Running Bun-specific process commands
- Making network requests with Bun's fetch

## Filesystem Operations

### Read File

```bash
scripts/bun-fs.sh read /path/to/file.txt
```

Returns JSON: `{"content": "file contents"}`

### Write File

```bash
scripts/bun-fs.sh write /path/to/file.txt "content here"
```

Creates parent directories automatically.
Returns JSON: `{"written": true, "path": "/path/to/file.txt"}`

### Glob Files

```bash
scripts/bun-glob.sh "/tmp/*.txt"
```

Returns JSON: `{"files": ["/tmp/file1.txt", "/tmp/file2.txt"], "count": 2}`

## Process Operations

### Execute Command

```bash
scripts/bun-process.sh "ls -la"
```

Runs shell command and returns output.

## Network Operations

### HTTP Request

```bash
scripts/bun-fetch.sh "https://api.example.com" "GET"
```

Makes HTTP request using Bun's native fetch.

## Notes

- All scripts use Bun's native APIs for better performance
- File operations automatically handle encoding
- Errors are returned with clear messages
