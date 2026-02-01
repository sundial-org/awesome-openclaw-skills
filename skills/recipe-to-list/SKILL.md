---
name: recipe-to-list
description: Turn recipes into a Todoist Shopping list. Extract ingredients from recipe photos (Gemini Flash vision) or recipe web pages (search + fetch), then compare against the existing Shopping project with conservative synonym/overlap rules, skip pantry staples (salt/pepper), and sum quantities when units match. Also saves each cooked recipe into the workspace cookbook (recipes/).
---

# Create Shopping List (Gemini Flash + Todoist)

Target flow:
1) Input is either a **photo** or a **recipe web search**
2) Extract ingredients (Gemini Flash for photos; web_fetch text → Gemini for websites)
3) Pull current Todoist **Shopping** list
4) Compare using overlap + synonym mapping (kept conservative; only merge high-confidence equivalents like coriander↔cilantro, panko↔breadcrumbs)
5) Update **Shopping** (default: add only missing items; skip salt/pepper)

Use the bundled script to handle the **photo → ingredients → Shopping update** part.

It also **automatically saves** a markdown entry into `recipes/` (your cookbook knowledge base) and appends to `recipes/index.md`.

For **recipe-name → web search**, do it confirm-first using `web_search` + `web_fetch`, then feed the ingredients into the same update logic (and save the recipe).

## Prereqs

- Env: `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) for Gemini
- Env: `TODOIST_API_TOKEN` for Todoist
- Bin: `todoist` (todoist-ts-cli)

## Output formatting

- Items are reformatted to start with the **ingredient name**, followed by a parenthetical quantity.
- The Shopping list is kept **flat** (no Todoist sections/groups).

## Run

```bash
python3 skills/recipe-to-list/scripts/recipe_to_list.py \
  --image /path/to/photo.jpg \
  --title "<optional title>" \
  --source "photo:/path/to/photo.jpg"
```

### Optional flags

- `--model gemini-2.0-flash` (default; falls back automatically) or any compatible Gemini vision model
- `--dry-run` to print extracted items without creating tasks
- `--prefix "[Recipe] "` to prefix each created task
- `--no-overlap-check` to skip checking your existing Shopping list
- `--include-pantry` to include salt/pepper
- `--no-save` to skip saving into `recipes/`

## What to send to the model

The script prompts Gemini to return **strict JSON**:

```json
{
  "items": ["2 large globe eggplants", "kosher salt", "..."],
  "notes": "optional"
}
```

If parsing fails, rerun with a clearer crop (ingredients list only) or provide a manual list.
