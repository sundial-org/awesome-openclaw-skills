# MacBook Optimizer Skill

A comprehensive OpenClaw skill for MacBook system optimization, monitoring, and troubleshooting.

## Features

- **System Health Monitoring**: CPU, memory, disk, battery
- **Performance Analysis**: Identify slowdowns and bottlenecks  
- **Overheating Detection**: Monitor temperature and find causes
- **Cleanup Tools**: Find large files and suggest cleanup
- **Process Management**: Monitor and manage resource usage

## Installation

This skill is available on [ClawHub](https://clawhub.com). Install with:

```bash
clawhub install macbook-optimizer
```

Or manually:

1. Copy this folder to your OpenClaw workspace skills directory:
   ```bash
   cp -r macbook-optimizer ~/.openclaw/workspace/skills/
   ```

2. Restart OpenClaw or start a new session

## Usage

Ask your OpenClaw agent:

- "Check my MacBook system health"
- "What's my CPU temperature?"
- "Find what's slowing down my Mac"
- "What's using the most memory?"
- "Clean up disk space"

## Requirements

- macOS only
- Standard system tools (included with macOS)

## Publishing to ClawHub

To publish updates:

```bash
clawhub publish ./macbook-optimizer \
  --slug macbook-optimizer \
  --name "MacBook Optimizer" \
  --version 1.0.0 \
  --tags latest
```

## License

MIT
