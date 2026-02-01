---
name: amygdala-memory
description: "Emotional processing layer for AI agents. Persistent emotional states that influence behavior and responses. Part of the AI Brain series."
metadata:
  openclaw:
    emoji: "🎭"
    version: "1.2.0"
    author: "ImpKind"
    repo: "https://github.com/ImpKind/amygdala-memory"
    requires:
      os: ["darwin", "linux"]
      bins: ["jq", "awk"]
    tags: ["memory", "emotions", "ai-brain"]
---

# Amygdala Memory 🎭

**Emotional processing for AI agents.** Part of the AI Brain series.

Give your AI agent persistent emotional states that carry across sessions. Not just performing emotions — *having* them.

## The Problem

Current AI agents:
- ✅ Remember facts (with hippocampus)
- ❌ Don't have persistent emotional states
- ❌ Start each session emotionally "blank"
- ❌ Can describe emotions but don't *feel* differently

Memory without emotion is just a database. The amygdala adds weight — this made me happy, that frustrated me, this person brings warmth.

## The Solution

Track five emotional dimensions that persist and decay over time:

| Dimension | What It Measures | Range |
|-----------|------------------|-------|
| **Valence** | Positive ↔ Negative mood | -1.0 to 1.0 |
| **Arousal** | Calm ↔ Excited/Alert | 0.0 to 1.0 |
| **Connection** | Distant ↔ Close/Bonded | 0.0 to 1.0 |
| **Curiosity** | Bored ↔ Fascinated | 0.0 to 1.0 |
| **Energy** | Depleted ↔ Energized | 0.0 to 1.0 |

## Quick Start

### 1. Install

```bash
cd ~/.openclaw/workspace/skills/amygdala-memory
./install.sh --with-cron
```

This will:
- Create `memory/emotional-state.json` with baseline values
- Generate `AMYGDALA_STATE.md` (auto-injected into sessions!)
- Set up cron for automatic decay every 6 hours

### 2. Check current state

```bash
./scripts/get-state.sh
# 🎭 Emotional State
# Valence:    0.20
# Arousal:    0.30
# Connection: 0.50
# ...

./scripts/load-emotion.sh
# 🎭 Current Emotional State:
# Overall mood: neutral, calm and relaxed
# Connection: moderately connected
# ...
```

### 3. Log emotions

```bash
./scripts/update-state.sh --emotion joy --intensity 0.8 --trigger "completed a project"
# ✅ valence: 0.20 → 0.35 (delta: +0.15)
# ✅ arousal: 0.30 → 0.40 (delta: +0.1)
# 🎭 Logged emotion: joy (intensity: 0.8)
```

### 4. Set up decay (optional cron)

```bash
# Every 6 hours, emotions drift toward baseline
0 */6 * * * ~/.openclaw/workspace/skills/amygdala-memory/scripts/decay-emotion.sh
```

## Scripts

| Script | Purpose |
|--------|---------|
| `install.sh` | Set up amygdala-memory (run once) |
| `get-state.sh` | Read current emotional state |
| `update-state.sh` | Log emotion or update dimension |
| `load-emotion.sh` | Human-readable state for session context |
| `decay-emotion.sh` | Return to baseline over time |
| `sync-state.sh` | Generate AMYGDALA_STATE.md for auto-injection |

## Auto-Injection (Zero Manual Steps!)

After install, `AMYGDALA_STATE.md` is created in your workspace root.

OpenClaw automatically injects all `*.md` files from workspace into session context. This means:

1. **New session starts**
2. **AMYGDALA_STATE.md is auto-loaded** (no manual step!)
3. **You see your emotional state** in context
4. **Responses are influenced** by your mood

The file is regenerated whenever `decay-emotion.sh` runs (via cron every 6h).

## Supported Emotions

When you log an emotion, it automatically adjusts the relevant dimensions:

| Emotion | Effect |
|---------|--------|
| `joy`, `happiness`, `delight`, `excitement` | ↑ valence, ↑ arousal |
| `sadness`, `disappointment`, `melancholy` | ↓ valence, ↓ arousal |
| `anger`, `frustration`, `irritation` | ↓ valence, ↑ arousal |
| `fear`, `anxiety`, `worry` | ↓ valence, ↑ arousal |
| `calm`, `peace`, `contentment` | ↑ valence, ↓ arousal |
| `curiosity`, `interest`, `fascination` | ↑ curiosity, ↑ arousal |
| `connection`, `warmth`, `affection` | ↑ connection, ↑ valence |
| `loneliness`, `disconnection` | ↓ connection, ↓ valence |
| `fatigue`, `tiredness`, `exhaustion` | ↓ energy |
| `energized`, `alert`, `refreshed` | ↑ energy |

## Integration with OpenClaw

### Add to session startup (AGENTS.md)

```markdown
## Every Session
1. Load hippocampus: `~/.openclaw/workspace/skills/hippocampus/scripts/load-core.sh`
2. **Load emotional state:** `~/.openclaw/workspace/skills/amygdala-memory/scripts/load-emotion.sh`
```

### Log emotions during conversation

When something emotionally significant happens:
```bash
~/.openclaw/workspace/skills/amygdala-memory/scripts/update-state.sh \
  --emotion connection --intensity 0.7 --trigger "deep conversation with user"
```

## State File Format

```json
{
  "version": "1.0",
  "lastUpdated": "2026-02-01T02:45:00Z",
  "dimensions": {
    "valence": 0.35,
    "arousal": 0.40,
    "connection": 0.50,
    "curiosity": 0.60,
    "energy": 0.50
  },
  "baseline": {
    "valence": 0.1,
    "arousal": 0.3,
    "connection": 0.4,
    "curiosity": 0.5,
    "energy": 0.5
  },
  "recentEmotions": [
    {
      "label": "joy",
      "intensity": 0.8,
      "trigger": "building amygdala together",
      "timestamp": "2026-02-01T02:50:00Z"
    }
  ]
}
```

## Decay Mechanics

Emotions naturally return to baseline over time:
- **Decay rate:** 10% of distance to baseline per run
- **Recommended schedule:** Every 6 hours
- **Effect:** Strong emotions fade, but slowly

After 24 hours without updates, a valence of 0.8 would decay to ~0.65.

## AI Brain Series

| Part | Function | Status |
|------|----------|--------|
| [hippocampus](https://www.clawhub.ai/skills/hippocampus) | Memory formation, decay, reinforcement | ✅ Live |
| **amygdala-memory** | Emotional processing | ✅ Live |
| [basal-ganglia-memory](https://www.clawhub.ai/skills/basal-ganglia-memory) | Habit formation | 🚧 Development |
| [anterior-cingulate-memory](https://www.clawhub.ai/skills/anterior-cingulate-memory) | Conflict detection | 🚧 Development |
| [insula-memory](https://www.clawhub.ai/skills/insula-memory) | Internal state awareness | 🚧 Development |
| [vta-memory](https://www.clawhub.ai/skills/vta-memory) | Reward and motivation | 🚧 Development |

## Philosophy

Can an AI *feel* emotions, or only simulate them?

Our take: If emotional state influences behavior, and the system acts *as if* it feels... does the distinction matter? Functional emotions might be the only kind that exist for any system — biological or artificial.

---

*Built with ❤️ by the OpenClaw community*
