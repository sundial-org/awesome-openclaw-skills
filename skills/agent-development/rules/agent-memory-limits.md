# Agent Memory Limits

## Root Cause Fix (REQUIRED)

Add to `~/.bashrc` or `~/.zshrc`:
```bash
export NODE_OPTIONS="--max-old-space-size=16384"
```

This increases Node.js heap from default 4GB to 16GB. **With this set, you can run agents normally.**

## Model Selection (Quality First)

Don't downgrade model quality to work around memory - fix the heap limit instead.

| Model | Use For |
|-------|---------|
| **Opus** | Creative work (page building, design, content) - quality matters |
| **Sonnet** | Research, validation, synthesis - balanced |
| **Haiku** | Script runners, simple deployers - speed over quality |

## Parallel Limits (Even With Fix)

| Agent Type | Max Parallel | Notes |
|------------|--------------|-------|
| Any agents | 2-3 | Context accumulates; batch then pause |
| Heavy creative | 1-2 | Opus agents use more memory |

## Recovery

If crash occurs:
1. `source ~/.bashrc` or restart terminal
2. `NODE_OPTIONS="--max-old-space-size=16384" claude`
3. Check what files exist, continue from there
