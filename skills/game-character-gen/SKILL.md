---
name: game-character-gen
description: Generate professional game character designs via OpenAI Images API. Create diverse characters for RPGs, video games, tabletop games, and interactive media. Use when user needs character concept art, character portraits, game sprites, or character sheets with specific attributes like race, class, profession, equipment, and visual style (e.g., "create an elven ranger", "design a cyberpunk hacker", "generate fantasy warrior character").
---

# Game Character Generator

Generate detailed character concepts for games with precise control over race, class, equipment, and visual style.

## Setup

- Needs env: `OPENAI_API_KEY`

## Quick Start

Generate a basic character:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "elf" \
  --class "ranger"
```

Generate with specific details:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "dragonborn" \
  --class "paladin" \
  --gender "female" \
  --equipment "plate armor, divine shield" \
  --style "epic fantasy painting"
```

Generate a batch of characters:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "human" "dwarf" "tiefling" \
  --class "warrior" "mage" "rogue" \
  --style "dark fantasy" "anime" "realistic"
```

## Character Parameters

### Race (Fantasy)
- `human` - Human (various ethnicities)
- `elf` - High elf, wood elf, dark elf (drow)
- `dwarf` - Mountain dwarf, hill dwarf
- `halfling` - Lightfoot, stout halfling
- `gnome` - Rock gnome, forest gnome
- `half-elf` - Half-elf heritage
- `half-orc` - Half-orc heritage
- `dragonborn` - Dragonborn (various draconic lineages)
- `tiefling` - Tiefling (infernal heritage)
- `goliath` - Goliath (giant heritage)
- `aasimar` - Aasimar (celestial heritage)
- `goblin` - Goblin
- `hobgoblin` - Hobgoblin
- `bugbear` - Bugbear
- `kenku` - Kenku (bird-like)
- `tabaxi` - Tabaxi (feline)
- `lizardfolk` - Lizardfolk
- `firbolg` - Firbolg
- `genasi` - Genasi (elemental: air, earth, fire, water)

### Class (Fantasy)
- `warrior` - Fighter, barbarian, knight
- `mage` - Wizard, sorcerer, warlock
- `cleric` - Cleric, priest, paladin
- `rogue` - Rogue, assassin, thief
- `ranger` - Ranger, hunter, scout
- `bard` - Bard, entertainer
- `monk` - Monk, martial artist
- `druid` - Druid, shaman
- `artificer` - Artificer, engineer
- `inquisitor` - Inquisitor, investigator

### Race (Sci-Fi / Cyberpunk)
- `human-augmented` - Cybernetically enhanced human
- `android` - Synthetic android
- `clone` - Clone soldier
- `alien-humanoid` - Various alien species
- `cyborg` - Heavily modified cyborg
- `bio-engineered` - Genetically modified

### Class (Sci-Fi / Cyberpunk)
- `hacker` - Netrunner, hacker
- `soldier` - Mercenary, corporate soldier
- `tech-specialist` - Engineer, technician
- `medic` - Combat medic
- `scout` - Reconnaissance specialist
- `pilot` - Starship pilot
- `assassin` - Corporate assassin
- `detective` - Investigator

### Equipment
Common equipment keywords (comma-separated):
- `leather armor` / `chainmail` / `plate armor` / `cybernetic implants`
- `sword and shield` / `greatsword` / `daggers` / `quarterstaff`
- `crossbow` / `longbow` / `pistol` / `plasma rifle` / `laser pistol`
- `spellbook` / `arcane focus` / `holy symbol` / `tech gauntlet`
- `cloak` / `hooded cape` / `tactical vest` / `exosuit`
- `backpack` / `tool belt` / `medical kit` / `hacking deck`

### Style
Artistic styles for character render:
- `epic fantasy painting` - Rich oil painting, cinematic
- `realistic portrait` - Photorealistic character portrait
- `anime studio` - Anime/manga style
- `concept art` - Game concept art quality
- `illustration` - Detailed illustration
- `comic book` - Bold comic style
- `pixel art` - Retro pixel character
- `dark fantasy` - Grim dark aesthetic
- `low poly` - Low poly 3D model look
- `cel shaded` - Cel shading anime style
- `watercolor` - Soft watercolor style
- `vintage fantasy` - Classic fantasy art

### Gender / Expression
- `male`, `female`, `non-binary`, `androgynous`
- `young`, `middle-aged`, `elderly`
- `stoic`, `determined`, `mysterious`, `playful`, `grim`, `noble`

## Advanced Options

Custom prompt for full control:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --prompt "A rugged dwarven warrior with braided red beard, wearing ornate mithral plate armor decorated with runic engravings. He wields a massive warhammer with lightning crackling along the head. Battle-hardened expression, scars visible on face. Epic fantasy oil painting style, cinematic lighting, detailed textures."
```

Include character sheet:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "human" \
  --class "mage" \
  --style "concept art" \
  --sheet
```

## Parameters

- `--race` - Character race/species (repeatable for batch)
- `--class` - Character class/profession (repeatable for batch)
- `--gender` - Gender identity
- `--equipment` - Equipment and gear description
- `--style` - Artistic style (repeatable for batch)
- `--prompt` - Full custom prompt (overrides other options)
- `--count` - Number of variants per character (default: 1)
- `--sheet` - Generate character sheet JSON with stats
- `--out-dir` - Output directory (default: ~/Projects/tmp/game-character-gen-*)
- `--size` - Image size: 1024x1024, 1792x1024, 1024x1792 (default: 1024x1024)
- `--quality` - high/standard (default: high)
- `--model` - OpenAI image model (default: gpt-image-1.5)
- `--api-key` - OpenAI API key (or use OPENAI_API_KEY env)

## Character Sheet Format

When using `--sheet`, generates `character_sheet.json` with:

```json
{
  "name": "Generated Character",
  "race": "human",
  "class": "mage",
  "gender": "male",
  "equipment": ["staff", "robes"],
  "stats": {
    "strength": 8,
    "dexterity": 14,
    "constitution": 10,
    "intelligence": 18,
    "wisdom": 12,
    "charisma": 10
  },
  "image_file": "01-mage.png"
}
```

## Output

- `*.png` - Character images
- `character_sheet.json` - Character data (if --sheet)
- `prompts.json` - All prompts used
- `index.html` - Character gallery

## Examples

D&D party:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "human" "elf" "dwarf" "half-orc" \
  --class "paladin" "ranger" "cleric" "barbarian" \
  --style "epic fantasy painting"
```

Cyberpunk crew:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "human-augmented" "android" "clone" "cyborg" \
  --class "hacker" "soldier" "tech-specialist" "assassin" \
  --style "cyberpunk neon" \
  --equipment "hacking deck" "plasma rifle" "tool belt" "monowire"
```

Children's book characters:

```bash
python3 ~/Projects/agent-scripts/skills/game-character-gen/scripts/generate.py \
  --race "human" "elf" "gnome" "fairy" \
  --class "adventurer" "wizard" "explorer" "healer" \
  --style "whimsical illustration" "watercolor"
```
