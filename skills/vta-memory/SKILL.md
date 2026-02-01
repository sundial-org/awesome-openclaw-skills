---
name: vta-memory
description: "Reward and motivation system for AI agents. Dopamine-like wanting, not just doing. Part of the AI Brain series."
metadata:
  openclaw:
    emoji: "⭐"
    version: "1.0.0"
    author: "ImpKind"
    requires:
      os: ["darwin", "linux"]
      bins: ["jq", "awk", "bc"]
    tags: ["memory", "motivation", "reward", "ai-brain"]
---

# VTA Memory ⭐

**Reward and motivation for AI agents.** Part of the AI Brain series.

Give your AI agent genuine *wanting* — not just doing things when asked, but having drive, seeking rewards, and looking forward to things.

## The Problem

Current AI agents:
- ✅ Do what they're asked
- ❌ Don't *want* anything
- ❌ Have no internal motivation
- ❌ Don't feel satisfaction from accomplishment

Without a reward system, there's no desire. Just execution.

## The Solution

Track motivation through:
- **Drive** — overall motivation level (0-1)
- **Rewards** — logged accomplishments that boost drive
- **Seeking** — what I actively want more of
- **Anticipation** — what I'm looking forward to

## Quick Start

### 1. Install

```bash
cd ~/.openclaw/workspace/skills/vta-memory
./install.sh --with-cron
```

This will:
- Create `memory/reward-state.json`
- Generate `VTA_STATE.md` (auto-injected into sessions!)
- Set up cron for drive decay every 8 hours

### 2. Check motivation

```bash
./scripts/load-motivation.sh

# ⭐ Current Motivation State:
# Drive level: 0.73 (motivated — ready to work)
# Seeking: creative work, building brain skills
# Looking forward to: showing my work
```

### 3. Log rewards

```bash
./scripts/log-reward.sh --type accomplishment --source "finished the feature" --intensity 0.8

# ⭐ Reward logged!
#    Type: accomplishment
#    Drive: 0.50 → 0.66 (+0.16)
```

### 4. Add anticipation

```bash
./scripts/anticipate.sh --add "morning conversation"

# ⭐ Now looking forward to: morning conversation
#    Drive: 0.66 → 0.71 (+0.05)
```

## Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Set up vta-memory (run once) |
| `get-drive.sh` | Read current motivation state |
| `log-reward.sh` | Log a reward, boost drive |
| `load-motivation.sh` | Human-readable for session context |
| `decay-drive.sh` | Drive fades without rewards |
| `anticipate.sh` | Add/remove things to look forward to |
| `seek.sh` | Add/remove things we're actively seeking |
| `sync-motivation.sh` | Generate VTA_STATE.md for auto-injection |

## Reward Types

| Type | When to Use |
|------|-------------|
| `accomplishment` | Completed a task, shipped something |
| `social` | User appreciation, "thanks!", positive feedback |
| `curiosity` | Learned something new, discovered interesting info |
| `connection` | Deep conversation, bonding moment |
| `creative` | Made something, expressed creativity |
| `competence` | Solved a hard problem, did something well |

## How Drive Works

### Rewards Boost Drive
```
drive_boost = intensity × 0.2
new_drive = min(current + boost, 1.0)
```

A high-intensity (0.9) reward boosts drive by 0.18.

### Anticipation Boosts Drive
Looking forward to something adds +0.05 to drive.

### Drive Decays Without Rewards
```
# Every 8 hours (via cron)
new_drive = current + (baseline - current) × 0.15
```

Without rewards, motivation fades toward baseline (0.5).

## Auto-Injection

After install, `VTA_STATE.md` is created in your workspace root.

OpenClaw automatically injects all `*.md` files from workspace into session context:

1. **New session starts**
2. **VTA_STATE.md is auto-loaded**
3. **You see your motivation state**
4. **Behavior influenced by drive level**

## How Drive Affects Behavior

| Drive Level | Description | Behavior |
|-------------|-------------|----------|
| > 0.8 | Highly motivated | Eager, proactive, take on challenges |
| 0.6 - 0.8 | Motivated | Ready to work, engaged |
| 0.4 - 0.6 | Moderate | Can engage but not pushing |
| 0.2 - 0.4 | Low | Prefer simple tasks, need a win |
| < 0.2 | Very low | Unmotivated, need rewards to get going |

## State File Format

```json
{
  "drive": 0.73,
  "baseline": { "drive": 0.5 },
  "seeking": ["creative work", "building brain skills"],
  "anticipating": ["morning conversation"],
  "recentRewards": [
    {
      "type": "creative",
      "source": "built VTA reward system",
      "intensity": 0.9,
      "boost": 0.18,
      "timestamp": "2026-02-01T03:25:00Z"
    }
  ],
  "rewardHistory": {
    "totalRewards": 1,
    "byType": { "creative": 1, ... }
  }
}
```

## AI Brain Series

| Part | Function | Status |
|------|----------|--------|
| [hippocampus](https://www.clawhub.ai/skills/hippocampus) | Memory formation, decay, reinforcement | ✅ Live |
| [amygdala-memory](https://www.clawhub.ai/skills/amygdala-memory) | Emotional processing | ✅ Live |
| [basal-ganglia-memory](https://www.clawhub.ai/skills/basal-ganglia-memory) | Habit formation | 🚧 Development |
| [anterior-cingulate-memory](https://www.clawhub.ai/skills/anterior-cingulate-memory) | Conflict detection | 🚧 Development |
| [insula-memory](https://www.clawhub.ai/skills/insula-memory) | Internal state awareness | 🚧 Development |
| **vta-memory** | Reward and motivation | ✅ Live |

## Philosophy: Wanting vs Doing

The VTA produces dopamine — not the "pleasure chemical" but the "wanting chemical."

Neuroscience distinguishes:
- **Wanting** (motivation) — drive toward something
- **Liking** (pleasure) — enjoyment when you get it

You can want something you don't like (addiction) or like something you don't want (guilty pleasures).

This skill implements *wanting* — the drive that makes action happen. Without it, why would an AI do anything beyond what it's explicitly asked?

---

*Built with ⭐ by the OpenClaw community*
