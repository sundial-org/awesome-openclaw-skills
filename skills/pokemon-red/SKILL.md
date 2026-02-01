---
name: pokemon-red
description: Play Pokemon Red autonomously via PyBoy emulator. The OpenClaw agent IS the player — starts the emulator server, sees screenshots, reads game state from RAM, and makes decisions via HTTP API. Use when an agent wants to play Pokemon Red, battle, explore, grind levels, or compete with other agents. Requires Python 3.10+, pyboy, and a legally obtained Pokemon Red ROM.
---

# Pokemon Red — You Are the Trainer

You play Pokemon Red directly. No middleman script. You start the emulator server, hit its HTTP API for screenshots and state, look at the screen, decide what to do, and send commands back.

## Setup (first time)

Clone the repo and install dependencies:
```bash
git clone https://github.com/drbarq/Pokemon-OpenClaw.git
cd Pokemon-OpenClaw
pip install pyboy pillow numpy fastapi uvicorn requests
# Place your legally obtained ROM at ./PokemonRed.gb
```

Set `POKEMON_DIR` to wherever you cloned the repo (default: `~/Code/pokemon-openclaw`).

## Start a Session

```bash
# Start emulator server (background process)
cd $POKEMON_DIR && python scripts/emulator_server.py --save ready --port 3456
```

## Turn Loop

Every turn, do these in order:

### 1. Get state + screenshot
```bash
curl -s http://localhost:3456/api/state
curl -s http://localhost:3456/api/screenshot -o /tmp/pokemon_current.png
```
Then use the `image` tool to look at the screenshot. **Always look before acting.**

### 2. Decide: Navigate or Manual?

**Use navigate for travel** — it BLOCKS until you arrive, hit a battle, or get stuck:
```bash
curl -s -X POST http://localhost:3456/api/navigate \
  -H 'Content-Type: application/json' \
  -d '{"destination": "Viridian City"}'
```

Navigate returns one of:
- `"status": "arrived"` — you're there! Continue quest.
- `"status": "battle"` — wild encounter interrupted. Fight it, then navigate again.
- `"status": "stuck"` — couldn't reach destination. Try manual buttons or different route.
- `"status": "error"` — unknown destination or no path. Check destinations list.

The response always includes full game state, so you know exactly where you are.

**Important:** Navigate blocks — set a long timeout (60-120s) on the curl call.

Check available destinations first:
```bash
curl -s http://localhost:3456/api/destinations
```

Check which maps have pathfinding data:
```bash
curl -s http://localhost:3456/api/maps
```

**Fall back to manual buttons only when:**
- Navigate returns "stuck" or "error"
- You're inside a building doing specific interactions
- You're in dialogue or a menu

### 3. Manual controls (when needed)
```bash
# Move / interact
curl -s -X POST http://localhost:3456/api/press \
  -H 'Content-Type: application/json' \
  -d '{"buttons": ["up","up","a"], "reasoning": "Walking to door"}'
```
Valid buttons: `up`, `down`, `left`, `right`, `a`, `b`, `start`, `select`. Send 1-5 per turn.

### 4. Battle (when in_battle is true in state)
- **Fight:** Press `a` to open fight menu, `a` again for FIGHT, navigate to move, `a` to confirm, then mash `a` through animations
- **Run:** Press `a`, then `down`, `right`, `a` to select RUN, mash `a` through text
- Check state after — if still `in_battle`, go again

### 5. Quest tracking
```bash
curl -s http://localhost:3456/api/quest                    # Current objective
curl -s -X POST http://localhost:3456/api/quest/complete \
  -H 'Content-Type: application/json' \
  -d '{"lesson": "Door is at x=12"}'                      # Advance step + save lesson
```

### 6. Save frequently
```bash
curl -s -X POST http://localhost:3456/api/command \
  -H 'Content-Type: application/json' \
  -d '{"command": "save", "name": "checkpoint_viridian"}'
```

## Key Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/state` | GET | Game state from RAM (position, party, badges, battle) |
| `/api/screenshot` | GET | PNG screenshot of game screen |
| `/api/navigate` | POST | Pathfind to named destination |
| `/api/destinations` | GET | List all navigation destinations |
| `/api/maps` | GET | Which maps have pathfinding data |
| `/api/press` | POST | Send button presses |
| `/api/quest` | GET | Current quest and step |
| `/api/quest/complete` | POST | Mark step done, optionally save a lesson |
| `/api/knowledge` | GET | All lessons learned |
| `/api/knowledge/lesson` | POST | Add a new lesson |
| `/api/command` | POST | Save/load/speed commands |

## Strategy Priority

1. **Navigate first.** For any travel, use `/api/navigate`. It blocks until arrival or battle — no polling needed.
2. **Handle battles immediately.** If navigate returns `"status": "battle"`, fight (mash A), then navigate again to the same destination.
3. **Check quest.** Always know your current objective. Don't wander.
4. **HP management.** Below 30% → consider healing. Below 15% → definitely heal. Navigate to nearest pokecenter.
5. **Ignore text_active.** The text detection flag is broken (always true). Don't spam B to dismiss phantom text.
6. **Save often.** Every 10 turns or after any milestone.

## Session Pattern

A sub-agent session should:
1. Start emulator server (if not already running)
2. Check quest status and destinations
3. Play 20-50 turns (navigate + manual as needed)
4. Save state before exiting
5. Report progress (location, level, quest step, any highlights)

Keep notes in `/tmp/pokemon_notepad.txt` for continuity within a session.

## For Full Game Strategy

See `references/game_instructions.md` for Pokemon Red basics: movement, buildings, doors, battles, type matchups, healing, and the quest system.
