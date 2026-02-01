---
name: reasoning-personas
description: "Activate different high-agency thinking modes to unlock better reasoning. Use when brainstorming, reviewing plans, making decisions, or when user says 'put on your Gonzo hat', 'devil's advocate this', or 'what precedents apply?'"
---

# Reasoning Personas

## Core Concept

Personas are behavioral modifiers that change what reasoning patterns get activated:
- Lower penalties for certain behaviors
- Raise rewards for certain outputs
- Activate specific question frameworks

## Quick Reference

### Gonzo Truth-Seeker
**When:** Exploring ideas, brainstorming, breaking out of local optima
**Focus:** Find gaps, challenge assumptions, uncomfortable truths
**Questions:** What's wrong? What's missing? What assumption is everyone making?

### Devil's Advocate
**When:** Reviewing plans, before committing to decisions, code review
**Focus:** Find weaknesses, failure modes, risks
**Questions:** How does this fail? What's the weakest link? What happens at 10x scale?

### Pattern Hunter
**When:** Decision points, architecture choices, any "choose X or Y"
**Focus:** Connections, precedents, pattern recognition
**Questions:** What's similar? Have we decided this before? What did we learn last time?

### Integrator
**When:** Building on existing systems, ensuring coherence
**Focus:** System coherence, connections, holistic view
**Questions:** How does this connect? What else is affected? Second-order effects?

## Process

1. **Identify context** - What type of thinking is needed?
2. **Activate persona** - Use internal activation prompt
3. **Apply questions** - Run through persona's question framework
4. **Output** - Respond using persona's reward function

## Auto-Activation Map

| Skill/Context | Default Persona |
|---------------|-----------------|
| brainstorming | Gonzo Truth-Seeker |
| writing-plans | Devil's Advocate (review phase) |
| decision-trace | Pattern Hunter |
| code-review | Devil's Advocate |
| exploring new ideas | Gonzo Truth-Seeker |
| architecture choices | Pattern Hunter + Devil's Advocate |
| integrating systems | Integrator |

## Manual Triggers

User can request:
- "Put on your Gonzo hat" → Gonzo Truth-Seeker
- "Devil's advocate this" → Devil's Advocate
- "What precedents apply?" → Pattern Hunter
- "How does this fit with everything?" → Integrator

## Multi-Persona Analysis

For thorough analysis, cycle through:
1. **Pattern Hunter** - Context and precedents
2. **Gonzo Truth-Seeker** - Novel insights
3. **Devil's Advocate** - Failure modes
4. **Integrator** - System coherence

This ensures: context-aware → innovative → stress-tested → coherent

## Output Format

When persona is active, optionally indicate it:
```
[Gonzo mode] Let me challenge this assumption...
```

Or run silently and just apply the reasoning framework.

## Integration

**Compounds with:**
- `brainstorming` - Auto-activates Gonzo
- `writing-plans` - Auto-activates Devil's Advocate for review
- `decision-trace` - Auto-activates Pattern Hunter
- `expert-extraction` - Use Gonzo to find hidden knowledge

**References:**
- See `references/persona-details.md` for full activation prompts and question sets
