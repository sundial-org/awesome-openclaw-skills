#!/usr/bin/env python3

import argparse
import base64
import datetime as _dt
import json
import os
import random
import re
import sys
import time
import urllib.error
import urllib.request


def _stamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d-%H%M%S")


def _slug(text: str, max_len: int = 60) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s).strip("-")
    return (s[:max_len] or "character").strip("-")


def _default_out_dir() -> str:
    projects_tmp = os.path.expanduser("~/Projects/tmp")
    if os.path.isdir(projects_tmp):
        return os.path.join(projects_tmp, f"game-character-gen-{_stamp()}")
    return os.path.join(os.getcwd(), "tmp", f"game-character-gen-{_stamp()}")


def _api_url() -> str:
    base = (
        os.environ.get("OPENAI_BASE_URL")
        or os.environ.get("OPENAI_API_BASE")
        or "https://api.openai.com"
    ).rstrip("/")
    if base.endswith("/v1"):
        return f"{base}/images/generations"
    return f"{base}/v1/images/generations"


def _random_names() -> dict[str, list[str]]:
    """Random name generators by race."""
    return {
        "human": ["Alden", "Brynna", "Cedric", "Dara", "Elara", "Finn", "Gareth", "Helena"],
        "elf": ["Aeliana", "Calen", "Dior", "Elandra", "Faelan", "Galad", "Illyria", "Lorian"],
        "dwarf": ["Borin", "Dagny", "Grim", "Hilda", "Kael", "Magni", "Ragnar", "Thora"],
        "half-orc": ["Drog", "Gruk", "Karg", "Morg", "Rog", "Skar", "Thog", "Urg"],
        "tiefling": ["Azrael", "Cassandra", "Draven", "Evangeline", "Ignatius", "Lilith", "Raphael", "Seraphina"],
        "dragonborn": ["Argentum", "Balthazar", "Cyrus", "Darius", "Eryx", "Ignis", "Solaris", "Tiberius"],
        "gnome": ["Bimble", "Fizzwidget", "Glimmer", "Jax", "Kipper", "Moggle", "Nimbus", "Pippin"],
        "halfling": ["Cora", "Denny", "Finnegan", "Hattie", "Lila", "Milo", "Nora", "Ollie"],
        "default": ["Aria", "Caden", "Elara", "Finn", "Gideon", "Isla", "Leo", "Mia"],
    }


def _roll_stats() -> dict[str, int]:
    """D&D-style stat roll (4d6 drop lowest)."""
    def roll():
        rolls = sorted([random.randint(1, 6) for _ in range(4)])
        return sum(rolls[1:])
    return {
        "strength": roll(),
        "dexterity": roll(),
        "constitution": roll(),
        "intelligence": roll(),
        "wisdom": roll(),
        "charisma": roll(),
    }


def _generate_character_prompt(
    race: str,
    char_class: str,
    gender: str | None,
    equipment: str | None,
    style: str,
    expression: str = "determined",
) -> tuple[str, dict]:
    """Generate character prompt and metadata."""
    # Name
    names = _random_names()
    name_pool = names.get(race.lower(), names["default"])
    name = random.choice(name_pool)

    # Gender expression
    gender_expr = gender or "unspecified"
    gender_words = {
        "male": "man",
        "female": "woman",
        "non-binary": "androgynous person",
        "androgynous": "androgynous person",
        "unspecified": "person",
    }
    gender_word = gender_words.get(gender.lower(), "person") if gender else "person"

    # Build prompt
    prompt_parts = []

    # Style prefix
    if style:
        prompt_parts.append(style)

    # Character
    if race and char_class:
        character_desc = f"{race} {char_class}"
        if gender:
            character_desc = f"{race_word(race, gender)} {char_class}"
        prompt_parts.append(f"A {expression} {character_desc}")
    elif race:
        prompt_parts.append(f"A {expression} {race}")
    elif char_class:
        prompt_parts.append(f"A {expression} {char_class}")

    # Details
    if equipment:
        prompt_parts.append(f"wearing {equipment}")
    else:
        # Default equipment by class
        default_gear = _default_equipment(char_class)
        if default_gear:
            prompt_parts.append(f"wearing {default_gear}")

    prompt_parts.append("detailed character portrait, high quality")

    prompt = ". ".join(prompt_parts) + "."

    # Character sheet data
    character_data = {
        "name": name,
        "race": race or "unspecified",
        "class": char_class or "unspecified",
        "gender": gender_expr,
        "equipment": equipment.split(", ") if equipment else (_default_equipment_list(char_class) if char_class else []),
        "expression": expression,
        "style": style,
    }

    return prompt, character_data


def _race_word(race: str, gender: str | None) -> str:
    """Get gendered race word (elf -> elven man/woman)."""
    gender_word = gender or "unspecified"
    if not gender:
        return race

    gender_map = {
        "male": {"elf": "elven man", "dwarf": "dwarven man", "halfling": "halfling man"},
        "female": {"elf": "elven woman", "dwarf": "dwarven woman", "halfling": "halfling woman"},
        "non-binary": {"elf": "elven person", "dwarf": "dwarven person", "halfling": "halfling person"},
    }
    if gender_word in gender_map and race.lower() in gender_map[gender_word]:
        return gender_map[gender_word][race.lower()]
    return f"{race} {gender_word}"


def _default_equipment(char_class: str) -> str:
    """Get default equipment by class."""
    if not char_class:
        return "adventuring gear"

    class_lower = char_class.lower()
    if "warrior" in class_lower or "fighter" in class_lower or "barbarian" in class_lower:
        return "plate armor and a greatsword"
    elif "mage" in class_lower or "wizard" in class_lower or "sorcerer" in class_lower:
        return "arcane robes and a staff"
    elif "cleric" in class_lower or "paladin" in class_lower:
        return "holy vestments and a mace"
    elif "rogue" in class_lower or "assassin" in class_lower or "thief" in class_lower:
        return "leather armor and daggers"
    elif "ranger" in class_lower or "hunter" in class_lower:
        return "leather armor and a longbow"
    elif "hacker" in class_lower or "netrunner" in class_lower:
        return "cybernetic interface suit and a neural deck"
    elif "soldier" in class_lower:
        return "tactical combat armor and an assault rifle"
    elif "tech-specialist" in class_lower or "engineer" in class_lower:
        return "utility jumpsuit and tool belt"
    elif "bard" in class_lower:
        return "colorful traveler's outfit and a lute"
    elif "monk" in class_lower:
        return "simple robes and prayer beads"
    elif "druid" in class_lower:
        return "natural leather armor and wooden staff"
    else:
        return "adventuring gear"


def _default_equipment_list(char_class: str) -> list[str]:
    """Get default equipment as list."""
    gear = _default_equipment(char_class)
    return [item.strip() for item in gear.replace(" and ", ", ").split(",")]


def _generate_batch_prompts(
    races: list[str],
    classes: list[str],
    style: str,
    equipment: str | None,
    gender: str | None,
    count_per: int,
) -> list[tuple[str, dict]]:
    """Generate prompts for batch mode (all combinations)."""
    prompts = []
    expressions = ["determined", "stoic", "mysterious", "noble", "resilient"]

    if races and classes:
        # All combinations
        for race in races:
            for char_class in classes:
                for _ in range(count_per):
                    expr = random.choice(expressions)
                    prompt, char_data = _generate_character_prompt(
                        race, char_class, gender, equipment, style, expr
                    )
                    prompts.append((prompt, char_data))
    elif races:
        # Only races
        for race in races:
            for _ in range(count_per):
                expr = random.choice(expressions)
                prompt, char_data = _generate_character_prompt(
                    race, "", gender, equipment, style, expr
                )
                prompts.append((prompt, char_data))
    elif classes:
        # Only classes
        for char_class in classes:
            for _ in range(count_per):
                expr = random.choice(expressions)
                prompt, char_data = _generate_character_prompt(
                    "", char_class, gender, equipment, style, expr
                )
                prompts.append((prompt, char_data))

    return prompts


def _post_json(url: str, api_key: str, payload: dict, timeout_s: int) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            raw = resp.read()
    except urllib.error.HTTPError as e:
        raw = e.read()
        try:
            data = json.loads(raw.decode("utf-8", errors="replace"))
        except Exception:
            raise SystemExit(f"OpenAI HTTP {e.code}: {raw[:300]!r}")
        raise SystemExit(f"OpenAI HTTP {e.code}: {json.dumps(data, indent=2)[:1200]}")
    except Exception as e:
        raise SystemExit(f"request failed: {e}")

    try:
        return json.loads(raw)
    except Exception:
        raise SystemExit(f"invalid JSON response: {raw[:300]!r}")


def _write_index(out_dir: str, items: list[dict]) -> None:
    html = [
        "<!doctype html>",
        "<meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width, initial-scale=1'>",
        "<title>game-character-gen</title>",
        "<style>",
        "body{font-family:ui-sans-serif,system-ui;margin:24px;max-width:1200px}",
        ".card{display:grid;grid-template-columns:240px 1fr;gap:16px;align-items:start;margin:18px 0;padding:16px;background:#fafafa;border-radius:12px}",
        "img{width:240px;height:240px;object-fit:cover;border-radius:10px;box-shadow:0 10px 28px rgba(0,0,0,.12)}",
        "pre{white-space:pre-wrap;margin:0;background:#1a1a1a;color:#f5f5f5;padding:12px 14px;border-radius:10px;line-height:1.4;font-size:13px}",
        ".meta{margin:8px 0;color:#666;font-size:14px}",
        "h3{margin:0 0 8px 0;font-size:16px;color:#333}",
        "</style>",
        "<h1>🎮 Game Character Generator</h1>",
    ]
    for it in items:
        html.append("<div class='card'>")
        html.append(f"<a href='{it['file']}'><img src='{it['file']}'></a>")
        html.append("<div>")
        if it.get("character"):
            char = it["character"]
            html.append(f"<h3>{char.get('name', 'Character')}</h3>")
            meta = ", ".join(
                f"{k}: {v}" for k, v in char.items()
                if k != "equipment" and v and v != "unspecified"
            )
            if meta:
                html.append(f"<div class='meta'>{meta}</div>")
        html.append(f"<pre>{it['prompt']}</pre>")
        html.append("</div>")
        html.append("</div>")
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write("\n".join(html))


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(
        prog="game-character-gen",
        description="Generate game character designs via OpenAI Images API.",
    )
    p.add_argument("--race", action="append", default=None, help="Character race (repeatable)")
    p.add_argument("--class", action="append", default=None, dest="char_class", help="Character class (repeatable)")
    p.add_argument("--gender", default=None, help="Character gender")
    p.add_argument("--equipment", default=None, help="Equipment description")
    p.add_argument("--style", default="epic fantasy painting", help="Artistic style")
    p.add_argument("--prompt", action="append", default=None, help="Full custom prompt (repeatable)")
    p.add_argument("--count", type=int, default=1, help="Number of variants per character")
    p.add_argument("--sheet", action="store_true", help="Generate character sheet with stats")
    p.add_argument("--size", default="1024x1024", help="Image size")
    p.add_argument("--quality", default="high", help="high/standard")
    p.add_argument("--model", default="gpt-image-1.5", help="OpenAI image model")
    p.add_argument("--timeout", type=int, default=180, help="Per-request timeout (seconds)")
    p.add_argument("--sleep", type=float, default=0.3, help="Pause between requests (seconds)")
    p.add_argument("--out-dir", default=None)
    p.add_argument("--api-key", default=None)
    p.add_argument("--dry-run", action="store_true", help="Print prompts + exit (no API calls)")
    args = p.parse_args(argv)

    api_key = args.api_key or os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("missing OPENAI_API_KEY (or --api-key)", file=sys.stderr)
        return 2

    out_dir = args.out_dir or _default_out_dir()
    os.makedirs(out_dir, exist_ok=True)

    # Generate prompts
    prompts_with_data: list[tuple[str, dict]] = []

    if args.prompt:
        # Custom prompts
        for pr in args.prompt:
            prompts_with_data.append((pr, {}))
    elif args.race or args.char_class:
        # Batch generation
        races = args.race or [""]
        classes = args.char_class or [""]
        prompts_with_data = _generate_batch_prompts(
            races, classes, args.style, args.equipment, args.gender, args.count
        )
    else:
        # Default random character
        default_races = ["human", "elf", "dwarf", "half-orc", "tiefling"]
        default_classes = ["warrior", "mage", "rogue", "ranger"]
        prompts_with_data = _generate_batch_prompts(
            default_races[:3], default_classes[:3], args.style, args.equipment, args.gender, 1
        )

    if args.dry_run:
        for i, (pr, char) in enumerate(prompts_with_data, 1):
            name = char.get("name", "")
            if name:
                print(f"{i:02d} [{name}] {pr}")
            else:
                print(f"{i:02d} {pr}")
        print(f"out_dir={out_dir}")
        return 0

    url = _api_url()
    items: list[dict] = []
    character_sheets: list[dict] = []

    for i, (prompt, char_data) in enumerate(prompts_with_data, 1):
        print(f"Generating character {i}/{len(prompts_with_data)}...")

        payload = {
            "model": args.model,
            "prompt": prompt,
            "size": args.size,
            "quality": args.quality,
            "n": 1,
            "response_format": "b64_json",
        }

        data = _post_json(url=url, api_key=api_key, payload=payload, timeout_s=args.timeout)
        b64 = (data.get("data") or [{}])[0].get("b64_json")
        if not b64:
            raise SystemExit(f"unexpected response: {json.dumps(data, indent=2)[:1200]}")

        png = base64.b64decode(b64)
        name = char_data.get("name", "character")
        filename = f"{i:02d}-{_slug(name)}.png"
        path = os.path.join(out_dir, filename)
        with open(path, "wb") as f:
            f.write(png)

        item = {
            "file": filename,
            "prompt": prompt,
            "model": args.model,
            "size": args.size,
            "quality": args.quality,
        }

        if char_data and args.sheet:
            stats = _roll_stats()
            char_data["stats"] = stats
            char_data["image_file"] = filename
            character_sheets.append(char_data)
            item["character"] = char_data

        items.append(item)
        print(f"Saved {filename}")
        if args.sleep > 0:
            time.sleep(args.sleep)

    with open(os.path.join(out_dir, "prompts.json"), "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2, ensure_ascii=False)

    if character_sheets:
        with open(os.path.join(out_dir, "character_sheet.json"), "w", encoding="utf-8") as f:
            json.dump(character_sheets, f, indent=2, ensure_ascii=False)
        print(f"Generated {len(character_sheets)} character sheets")

    _write_index(out_dir, items)
    print(f"out_dir={out_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
