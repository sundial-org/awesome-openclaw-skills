# ⭐ VTA Memory

> Reward and motivation system for AI agents. Part of the [AI Brain series](https://github.com/ImpKind).

[![ClawdHub](https://img.shields.io/badge/ClawdHub-vta--memory-purple)](https://www.clawhub.ai/skills/vta-memory)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Give your AI agent genuine *wanting* — not just doing things when asked, but having drive, seeking rewards, and looking forward to things.

## The Problem

Current AI agents:
- ✅ Do what they're asked
- ❌ Don't *want* anything
- ❌ Have no internal motivation
- ❌ Don't feel satisfaction from accomplishment

**Without a reward system, there's no desire. Just execution.**

## The Solution

Track motivation through:
- **Drive** — overall motivation level (0-1)
- **Rewards** — logged accomplishments that boost drive
- **Seeking** — what I actively want more of
- **Anticipation** — what I'm looking forward to

## Quick Start

```bash
# Install
clawdhub install vta-memory
cd ~/.openclaw/workspace/skills/vta-memory
./install.sh --with-cron

# Check motivation
./scripts/load-motivation.sh

# Log a reward
./scripts/log-reward.sh --type accomplishment --source "shipped feature" --intensity 0.8

# Add anticipation
./scripts/anticipate.sh --add "morning conversation"
```

## How It Works

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Do        │────▶│   Get       │────▶│   Drive     │
│   Thing     │     │   Reward    │     │   Goes UP   │
└─────────────┘     └─────────────┘     └──────┬──────┘
      ▲                                        │
      │                                        │
      └────────────────────────────────────────┘
           High drive = want to do more
```

### Drive Mechanics

| Event | Effect |
|-------|--------|
| Log reward | +intensity × 0.2 |
| Add anticipation | +0.05 |
| Decay (8h) | Move 15% toward baseline |

### Drive Levels

| Level | Description | Behavior |
|-------|-------------|----------|
| > 0.8 | Highly motivated | Eager, proactive |
| 0.6-0.8 | Motivated | Ready to work |
| 0.4-0.6 | Moderate | Can engage |
| < 0.4 | Low | Need a win |

## Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Set up (run once) |
| `log-reward.sh` | Log reward, boost drive |
| `anticipate.sh` | Add things to look forward to |
| `seek.sh` | Add things we're seeking |
| `load-motivation.sh` | Human-readable output |
| `decay-drive.sh` | Drive fades over time |
| `sync-motivation.sh` | Generate VTA_STATE.md |

## Reward Types

| Type | When to Use |
|------|-------------|
| `accomplishment` | Completed task, shipped something |
| `social` | User appreciation, positive feedback |
| `curiosity` | Learned something new |
| `connection` | Deep conversation, bonding |
| `creative` | Made something |
| `competence` | Solved hard problem |

## Auto-Injection

After install, `VTA_STATE.md` is created in your workspace root and auto-injected into every session. No manual steps!

## AI Brain Series

| Part | Function | Status |
|------|----------|--------|
| [hippocampus](https://github.com/ImpKind/hippocampus-skill) | Memory formation, decay, reinforcement | ✅ Live |
| [amygdala-memory](https://github.com/ImpKind/amygdala-memory) | Emotional processing | ✅ Live |
| **vta-memory** | Reward and motivation | ✅ Live |
| basal-ganglia-memory | Habit formation | 🚧 Coming |
| anterior-cingulate-memory | Conflict detection | 🚧 Coming |
| insula-memory | Internal state awareness | 🚧 Coming |

## Philosophy

The VTA produces dopamine — not the "pleasure chemical" but the "wanting chemical."

**Wanting** (motivation) ≠ **Liking** (pleasure)

This skill implements *wanting* — the drive that makes action happen. Without it, why would an AI do anything beyond what it's explicitly asked?

## Requirements

- Bash, jq, awk, bc

## License

MIT

---

*Part of the AI Brain series. Built with ⭐ by [ImpKind](https://github.com/ImpKind)*
