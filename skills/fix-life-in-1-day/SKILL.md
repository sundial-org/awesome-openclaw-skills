---
name: fix-life-in-1-day
version: 1.0.0
description: "Fix your entire life in 1 day. 10 psychological sessions based on Dan Koe's viral article."
author: chip1cr
license: MIT
repository: https://github.com/pinkpixel/fix-life-in-1-day
metadata:
  clawdbot:
    emoji: "🧠"
    triggers: ["/life", "/architect"]
  tags: ["psychology", "self-improvement", "coaching", "life-design", "dan-koe"]
---

# Fix Your Entire Life in 1 Day 🧠

10 psychological sessions based on Dan Koe's viral article.

Based on:
- 📝 [@thedankoe](https://x.com/thedankoe) — "How to fix your entire life in 1 day"
- 🔧 [@alex_prompter](https://x.com/alex_prompter) — 10 AI prompts reverse-engineered from Dan's article
- ⚡ [@chip1cr](https://x.com/chip1cr) — Clawdbot skill implementation

## What It Does

Guides users through 10 structured sessions:

1. **The Anti-Vision Architect** — Build a visceral image of the life you're drifting toward
2. **The Hidden Goal Decoder** — Expose what you're actually optimizing for
3. **The Identity Construction Tracer** — Trace limiting beliefs to their origins
4. **The Lifestyle-Outcome Alignment Auditor** — Compare required vs actual lifestyle
5. **The Dissonance Engine** — Move from comfort to productive tension
6. **The Cybernetic Debugger** — Fix your goal-pursuit feedback loop
7. **The Ego Stage Navigator** — Assess developmental stage and transition
8. **The Game Architecture Engineer** — Design life as a game with stakes
9. **The Conditioning Excavator** — Separate inherited beliefs from chosen ones
10. **The One-Day Reset Architect** — Generate a complete 1-day transformation protocol

## Commands

| Command | Action |
|---------|--------|
| `/life` | Start or continue (shows intro for new users) |
| `/life ru` | Start in Russian |
| `/life status` | Show progress |
| `/life session N` | Jump to session N |
| `/life reset` | Start over |

## Usage Flow

### When User Says `/life`

**Step 1:** Check if intro needed
```bash
bash scripts/handler.sh intro en $WORKSPACE
```

If `showIntro: true` → Send intro message with image and "🐇 Jump into the rabbit hole" button (`life:begin`)

If `showIntro: false` → Run `start` and show current phase

**Step 2:** Get current state
```bash
bash scripts/handler.sh start en $WORKSPACE
```

**Step 3:** Format and show to user:
```
🧠 **Life Architect** — Session {session}/10
**{title}**
Phase {phase}/{totalPhases}
━━━━━━━━━━━━━━━━━━━━━━━━━━━

{content}

━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Step 4:** When user responds, save and advance:
```bash
bash scripts/handler.sh save "USER_RESPONSE" $WORKSPACE
```

## Handler Commands

```bash
handler.sh intro [en|ru]     # Check if should show intro
handler.sh start [en|ru]     # Start/continue session
handler.sh status            # Progress JSON
handler.sh session N         # Jump to session N
handler.sh save "text"       # Save response & advance
handler.sh skip              # Skip current phase
handler.sh reset             # Clear all progress
handler.sh callback <cb>     # Handle button callbacks
handler.sh lang en|ru        # Switch language
handler.sh reminders "07:00" "2026-01-27"  # Create Session 10 reminders
handler.sh insights          # Get accumulated insights
```

## Callbacks

- `life:begin` / `life:begin:ru` — Start sessions
- `life:prev` — Previous phase
- `life:skip` — Skip phase
- `life:save` — Save and exit
- `life:continue` — Continue
- `life:lang:en` / `life:lang:ru` — Switch language
- `life:session:N` — Jump to session N

## Files

```
life-architect/
├── SKILL.md              # This file
├── assets/
│   └── intro.jpg         # Intro image
├── references/
│   ├── sessions.md       # Session overview
│   ├── sources.md        # Original sources
│   └── sessions/
│       ├── en/           # English sessions (1-10)
│       └── ru/           # Russian sessions (1-10)
└── scripts/
    ├── handler.sh        # Main command handler
    └── export.sh         # Export final document
```

## User Data

Stored in `$WORKSPACE/memory/life-architect/`:
- `state.json` — Progress tracking
- `session-NN.md` — User responses
- `insights.md` — Key insights from completed sessions
- `final-document.md` — Exported complete document

## Languages

- English (default)
- Russian (full translation)

## Requirements

- `jq` (JSON processor)
- `bash` 4.0+

## License

MIT
