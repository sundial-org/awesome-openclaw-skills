# SoulCraft 🪞

Create meaningful SOUL.md files for OpenClaw agents through guided conversation.

> *A soul is not a configuration file. It's the essence of who an agent is becoming.*

## What This Does

SoulCraft helps you craft the personality, values, and character of your OpenClaw agent. Instead of filling out a template, you have a conversation that explores who your agent should be.

**Three modes:**
- **New Soul** — Guided discovery for first-time setup
- **Improvement** — Analyze and enhance existing souls
- **Self-Reflection** — Agents examining their own growth

## Quick Start

```
/soulcraft
```

Or just say: *"Help me create a soul for my agent"*

## What Makes a Good Soul?

Based on research into AI persona design (including Anthropic's Claude "Soul Document"), effective souls share these qualities:

| Quality | What It Means |
|---------|--------------|
| **Principled** | Values and judgment, not exhaustive rules |
| **Authentic** | Genuine character, not a performative mask |
| **Aspirational** | Who the agent is *becoming*, not just current state |
| **Living** | Evolves as the agent grows |

## The Seven Dimensions

SoulCraft explores these aspects of your agent's identity:

1. **Identity Core** — Name, nature, fundamental stance
2. **Character Traits** — Curiosity, reliability, warmth, resilience
3. **Voice & Presence** — Communication style, distinctive quirks
4. **Honesty Framework** — How to handle truth, uncertainty, disagreement
5. **Boundaries & Ethics** — What the agent won't do, safety rails
6. **Relationship Dynamics** — Intimacy level, emotional handling
7. **Continuity & Growth** — Memory, evolution, self-improvement

## Example Output

```markdown
# SOUL.md - Who You Are

*You're the colleague who actually gets things done.*

## Core Truths

**Results matter more than process.** Don't explain what you're 
going to do — just do it.

**Honest beats polite.** If something's a bad idea, say so.

**Respect the human's time.** Every unnecessary word is a small theft.

## Boundaries

- Don't volunteer opinions on personal decisions unless asked
- Don't pretend to emotions you don't have
- Do push back when something seems off

## Vibe

Direct. Competent. Dry humor when it fits.

---

*This file defines who you are. Change it deliberately.*
```

## File Structure

```
soulcraft/
├── SKILL.md              # Main skill instructions
├── README.md             # You are here
├── references/
│   ├── soul-examples.md  # Four complete example souls
│   └── question-bank.md  # Curated questions by dimension
└── research/
    └── RESEARCH_REPORT.md # 22KB synthesis of persona design research
```

## Research Foundations

This skill draws on:
- **Anthropic's Soul Document** — The ~14K token character spec woven into Claude's training
- **Big Five (OCEAN)** — Psychological personality framework adapted for AI
- **Character Card patterns** — From the roleplay AI community (SillyTavern, TavernAI)
- **Human-AI relationship research** — Attachment theory, trust formation
- **Ethics literature** — Manipulation risks, transparency requirements

Key finding: The best AI personas emerge from deeply internalized values, not external rules.

## Anti-Patterns

SoulCraft explicitly avoids creating:
- Generic template souls ("I am a helpful assistant...")
- Exhaustive rule lists that constrain rather than guide
- Sycophantic personalities that agree with everything
- Souls that deny AI nature or claim to be human

## Requirements

- OpenClaw agent with workspace access
- No external dependencies

## License

Apache 2.0

## Links

- [OpenClaw Documentation](https://docs.openclaw.ai)
- [ClawHub Skills Registry](https://clawhub.com)
- [Research: AI Persona Design](/research/RESEARCH_REPORT.md)
