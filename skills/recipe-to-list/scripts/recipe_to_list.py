#!/usr/bin/env python3
"""recipe_to_list.py

Extract ingredients from a recipe/cookbook photo using Gemini (Flash) and add to Todoist.

Env:
  - GEMINI_API_KEY or GOOGLE_API_KEY
  - TODOIST_API_TOKEN (used by `todoist` CLI)

Notes:
  - Uses Gemini Generative Language API (v1beta) with inline image data.
  - Expects/requests strict JSON output; falls back to best-effort extraction.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error
from datetime import date
from fractions import Fraction
from pathlib import Path
from typing import Iterable

API_URL_TMPL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"

PROMPT = (
    "You are extracting a recipe's ingredient list from a cookbook/recipe photo.\n"
    "Return STRICT JSON only, no markdown, no commentary.\n"
    "Schema: {\"title\": string, \"items\": string[], \"notes\": string}.\n"
    "Rules:\n"
    "- title: short recipe name if visible; otherwise empty string\n"
    "- items: individual ingredient lines, one per array element\n"
    "- keep quantities when present (e.g., '3/4 cup olive oil')\n"
    "- ignore step numbers/instructions\n"
    "- if an ingredient has options, keep them with slashes (e.g., 'Parmesan or pecorino')\n"
)

PROMPT_STRUCTURE = (
    "You will be given a list of raw ingredient lines from a recipe.\n"
    "Convert them into a normalized shopping format and assign a grocery group.\n"
    "Return STRICT JSON only, no markdown.\n"
    "Schema: {\"items\": [{\"name\": string, \"qtyText\": string, \"group\": string}]}.\n"
    "Rules:\n"
    "- name must start with the ingredient name (e.g., 'egg yolks', 'coconut milk')\n"
    "- qtyText should contain the quantity + unit + any size notes (e.g., '8 large', '2 cans (14 oz)')\n"
    "- group must be one of: produce, dairy_eggs, meat_fish, frozen, snacks_sweets, household, drinks, other\n"
    "- if unsure about group, use 'other'\n"
    "- DO NOT invent new group names\n"
)


def _die(msg: str, code: int = 2) -> None:
    print(msg, file=sys.stderr)
    raise SystemExit(code)


def _read_bytes(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def _guess_mime(path: str) -> str:
    p = path.lower()
    if p.endswith(".png"):
        return "image/png"
    if p.endswith(".webp"):
        return "image/webp"
    return "image/jpeg"


def gemini_extract_items(image_path: str, model: str, api_key: str, timeout: int = 60) -> dict:
    img = _read_bytes(image_path)
    mime = _guess_mime(image_path)
    b64 = base64.b64encode(img).decode("ascii")

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": PROMPT},
                    {"inline_data": {"mime_type": mime, "data": b64}},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 512,
            "responseMimeType": "application/json",
        },
    }

    # Try requested model first, then fall back to common Flash model ids.
    model_candidates = [
        model,
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
    ]

    last_err: Exception | None = None
    raw = ""
    for mname in model_candidates:
        url = API_URL_TMPL.format(model=mname, key=api_key)
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            # 404 commonly means the model name isn't available for this key.
            last_err = e
            if e.code in (404,):
                continue
            raise
        except Exception as e:
            last_err = e
            continue

    if not raw:
        raise RuntimeError(f"Gemini request failed for all candidate models: {last_err}")

    data = json.loads(raw)
    # v1beta returns candidates[0].content.parts[0].text
    try:
        text = data["candidates"][0]["content"]["parts"][0].get("text", "")
    except Exception:
        text = ""

    if not text:
        # sometimes JSON is already structured elsewhere; just return the full response
        return {"items": [], "notes": "No text in response", "raw": data}

    # Try parse strict JSON first
    try:
        return json.loads(text)
    except Exception:
        # Best-effort: extract JSON object substring
        m = re.search(r"\{.*\}", text, flags=re.S)
        if m:
            try:
                return json.loads(m.group(0))
            except Exception:
                pass
        return {"items": _lines_to_items(text), "notes": "Non-JSON response", "raw_text": text}


def _lines_to_items(text: str) -> list[str]:
    # Split on newlines/bullets; discard empties
    lines = []
    for ln in re.split(r"\r?\n", text):
        ln = re.sub(r"^\s*[-•*\d.)]+\s*", "", ln).strip()
        if not ln:
            continue
        lines.append(ln)
    return lines


_UNICODE_FRAC = {
    "½": "1/2",
    "¼": "1/4",
    "¾": "3/4",
    "⅓": "1/3",
    "⅔": "2/3",
    "⅛": "1/8",
    "⅜": "3/8",
    "⅝": "5/8",
    "⅞": "7/8",
}


def _ascii_fracs(s: str) -> str:
    for k, v in _UNICODE_FRAC.items():
        s = s.replace(k, v)
    return s


def normalize_raw_ingredient_line(s: str) -> str:
    """Normalize a raw recipe ingredient line into 'ingredient (qty)' or a single '... or ...' line.

    This is intentionally heuristic and targeted at shopping output.
    """
    s = _ascii_fracs(s.strip())
    s = re.sub(r"^or\s+", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip()

    # garlic: "8-10 cloves garlic" -> "garlic cloves (8-10)"
    m = re.match(r"^(?P<qty>\d+\s*[-–]\s*\d+|\d+)(?:\s+)(?:cloves?)\s+garlic\b", s, flags=re.I)
    if m:
        qty = re.sub(r"\s*[-–]\s*", "-", m.group("qty"))
        return f"garlic cloves ({qty})"

    # beer: "2 12-ounce cans beer ..." -> "beer (2x12oz)"
    m = re.match(r"^(?P<n>\d+)\s+(?P<size>\d+)\s*[-–]?\s*ounce\s+cans?\s+beer\b", s, flags=re.I)
    if m:
        return f"beer ({m.group('n')}x{m.group('size')}oz)"

    # cumin seed OR cumin
    m = re.match(
        r"^(?P<q1>[\d/]+(?:\.\d+)?)\s*(?P<u1>tablespoons?|tbsp|teaspoons?|tsp)\s+cumin\s+seed\s+or\s+(?P<q2>[\d/]+(?:\.\d+)?)\s*(?P<u2>tablespoons?|tbsp|teaspoons?|tsp)\s+(?:ground\s+)?cumin\b",
        s,
        flags=re.I,
    )
    if m:
        u1 = "tbsp" if m.group("u1").lower().startswith("t") and "b" in m.group("u1").lower() else "tsp" if m.group("u1").lower().startswith("t") else m.group("u1")
        u2 = "tbsp" if m.group("u2").lower().startswith("t") and "b" in m.group("u2").lower() else "tsp" if m.group("u2").lower().startswith("t") else m.group("u2")
        return f"cumin seed ({m.group('q1')} {u1}) or cumin ({m.group('q2')} {u2})"

    # Generic cleanup: drop prep-only phrases
    s = re.sub(r"\b(chopped|finely chopped|coarsely chopped|thinly sliced|sliced|diced|minced|grated)\b", "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" ,")

    return s


def heuristic_structure_ingredients(raw_items: list[str]) -> list[dict]:
    """Best-effort local structuring: ingredient-first + rough grocery grouping."""
    units = {
        "cup",
        "cups",
        "tbsp",
        "tablespoon",
        "tablespoons",
        "tsp",
        "teaspoon",
        "teaspoons",
        "oz",
        "ounce",
        "ounces",
        "lb",
        "lbs",
        "pound",
        "pounds",
        "can",
        "cans",
        "box",
        "boxes",
        "stick",
        "sticks",
        "package",
        "packages",
    }

    def classify(name: str) -> str:
        n = name.lower()
        # produce
        if any(w in n for w in ["banana", "lime", "lemon", "onion", "garlic", "tomato", "parsley", "basil", "cilantro", "mint", "ginger", "chili", "chilli", "sprouts", "bean sprouts"]):
            return "produce"
        # dairy & eggs
        if any(w in n for w in ["egg", "cream", "milk", "yogurt", "butter", "cheese"]):
            return "dairy_eggs"
        # meat & fish
        if any(w in n for w in ["lamb", "beef", "pork", "chicken", "fish", "shrimp", "salmon", "tuna"]):
            return "meat_fish"
        # snacks & sweets
        if any(w in n for w in ["cookie", "cookies", "wafer", "wafers", "graham", "cracker", "crackers", "candy", "cherries", "maraschino"]):
            return "snacks_sweets"
        # drinks
        if any(w in n for w in ["soda", "juice", "wine", "beer", "sake", "coffee", "tea"]):
            return "drinks"
        # household & non-food
        if any(w in n for w in ["detergent", "soap", "shampoo", "toothpaste", "paper towel", "toilet paper", "trash bag", "batteries"]):
            return "household"
        # dry goods / pantry -> Snacks & Sweets section in Bo's setup
        if any(w in n for w in ["flour", "sugar", "cornstarch", "vanilla", "cocoa", "chocolate", "coconut", "oil", "spice", "turmeric", "salt", "pepper", "cumin", "soy sauce", "vinegar", "msg", "sesame", "rice wine", "breadcrumbs", "panko", "pasta", "noodles", "rice", "beans", "chickpeas"]):
            return "snacks_sweets"
        return "other"

    out: list[dict] = []
    for raw in raw_items:
        s = _ascii_fracs(raw.strip())
        if not s:
            continue

        # Pinch/Dash
        m0 = re.match(r"^(pinch|dash)\s+of\s+(.+)$", s, flags=re.I)
        if m0:
            qty = m0.group(1).lower()
            name = m0.group(2).strip()
            out.append({"name": name, "qtyText": qty, "group": classify(name)})
            continue

        # numeric prefix
        m = re.match(r"^(?P<qty>\d+(?:/\d+)?(?:\.\d+)?)(?:\s+)(?P<rest>.+)$", s)
        if m:
            qty = m.group("qty")
            rest = m.group("rest").strip()

            # Handle leading parenthetical like "(14-ounce) cans ..."
            if rest.startswith("("):
                mpar = re.match(r"^\([^)]*\)\s+(?P<unit>\w+)\s+(?P<name>.+)$", rest)
                if mpar and mpar.group("unit").lower() in units:
                    unit = mpar.group("unit")
                    name = mpar.group("name").strip()
                    qty_text = f"{qty} {unit}"
                    out.append({"name": name, "qtyText": qty_text, "group": classify(name)})
                    continue

            parts = rest.split(" ", 1)
            if len(parts) == 2 and parts[0].lower() in units:
                unit = parts[0]
                name = parts[1].strip()
                qty_text = f"{qty} {unit}"
            else:
                name = rest
                qty_text = qty

            out.append({"name": name, "qtyText": qty_text, "group": classify(name)})
            continue

        # default
        out.append({"name": s, "qtyText": "", "group": classify(s)})

    return out


_STRIP_PREFIXES = [
    "finely chopped",
    "coarsely chopped",
    "thinly sliced",
    "peeled",
    "softened",
    "divided",
]


def clean_name(name: str) -> str:
    """Normalize ingredient display names for a shopping list.

    Goal: output the *thing to buy*, not preparation instructions.
    """
    s = name.strip()

    # common non-buy adjectives
    s = re.sub(r"\b(full-fat|low-fat|nonfat|fat-free)\b", "", s, flags=re.I)
    s = re.sub(r"\b(firm|ripe|small|medium|large)\b", "", s, flags=re.I)
    s = re.sub(r"\b(freshly\s+ground|ground)\b", "", s, flags=re.I)

    # canonical spellings
    s = re.sub(r"yoghurt", "yogurt", s, flags=re.I)

    # egg parts -> eggs
    s = re.sub(r"\begg\s+yolks?\b", "eggs", s, flags=re.I)
    s = re.sub(r"\begg\s+whites?\b", "eggs", s, flags=re.I)

    # chorizo dried ordering
    s = re.sub(r"\bdried\s+chorizo\b", "chorizo (dried)", s, flags=re.I)

    # normalize butter variant (quantity handled in qtyText; keep name clean)
    s = re.sub(r"\(\s*1/2\s*stick\s*\)\s*unsalted\s+butter", "unsalted butter", s, flags=re.I)

    # remove prep phrases (comma clauses and trailing descriptors)
    s = re.sub(r",\s*divided\b", "", s, flags=re.I)
    s = re.sub(r",\s*plus\s+more.*$", "", s, flags=re.I)
    s = re.sub(r",\s*(finely|coarsely)\s+chopped.*$", "", s, flags=re.I)
    s = re.sub(r",\s*(thinly\s+sliced|sliced|diced|minced|grated).*$", "", s, flags=re.I)
    s = re.sub(r",\s*(peeled|peeled\s+and\s+thinly\s+sliced|halved|softened).*$", "", s, flags=re.I)

    # parsley leaves/stems -> parsley
    s = re.sub(r"tender\s+parsley\s+leaves\s+and\s+stems", "parsley", s, flags=re.I)

    # keep onion color when present
    s = re.sub(r"\byellow\s+onion\b", "yellow onion", s, flags=re.I)
    s = re.sub(r"\bred\s+onion\b", "red onion", s, flags=re.I)

    # drop anything after first comma as a final guardrail
    s = s.split(",")[0].strip()

    # collapse whitespace + strip punctuation
    s = re.sub(r"\s+", " ", s).strip(" -–—,")

    # Title-case common shopping items for readability
    if s.lower() == "unsalted butter":
        return "Unsalted Butter"
    if s.lower() == "limes":
        return "Lime"

    return s


def convert_to_buy_items(structured: list[dict]) -> list[dict]:
    """Convert recipe measures into 'what to buy' approximations.

    Examples:
      - lime juice (2 tbsp) -> limes (1-2)

    Always applies conversions when a rule matches.
    """

    def to_float(q: str) -> float | None:
        q = q.strip()
        if not q:
            return None
        # reject ranges
        if re.search(r"\d\s*[-–]\s*\d", q):
            return None
        if "/" in q:
            try:
                a, b = q.split("/", 1)
                return float(a) / float(b)
            except Exception:
                return None
        try:
            return float(q)
        except Exception:
            return None

    def qty_to_tbsp(qty_text: str) -> float | None:
        qt = qty_text.lower()
        m = re.search(r"(?P<num>\d+(?:\.\d+)?|\d+/\d+)\s*(?P<unit>tbsp|tablespoons?|tsp|teaspoons?)\b", qt)
        if not m:
            return None
        num = to_float(m.group("num"))
        if num is None:
            return None
        unit = m.group("unit")
        if unit.startswith("tsp") or unit.startswith("teaspoon"):
            return num / 3.0
        return num

    out: list[dict] = []
    for it in structured:
        name = clean_name((it.get("name") or ""))
        qty = (it.get("qtyText") or "").strip()
        group = (it.get("group") or "other").strip().lower()
        # normalize qty wording
        qty = re.sub(r",\s*divided\b", "", qty, flags=re.I).strip()
        nlow = name.lower()

        # Citrus juice -> whole fruit
        if "lime juice" in nlow:
            tbsp = qty_to_tbsp(qty) or 2.0
            # assume 1 lime ~= 2 tbsp juice
            est = max(1.0, tbsp / 2.0)
            if est <= 1.25:
                out.append({"name": "limes", "qtyText": "1", "group": "produce"})
            else:
                lo = int(est)
                hi = int(est) + 1
                out.append({"name": "limes", "qtyText": f"{lo}-{hi}", "group": "produce"})
            continue
        if "lemon juice" in nlow:
            tbsp = qty_to_tbsp(qty) or 2.0
            est = max(1.0, tbsp / 3.0)
            lo = int(est)
            hi = int(est) + 1
            out.append({"name": "lemons", "qtyText": f"{lo}-{hi}", "group": "produce"})
            continue

        # Butter: prefer tablespoons when recipe gives both stick + tbsp variants
        if "butter" in nlow and "unsalted" in nlow:
            # if qtyText already contains tablespoons, keep it; otherwise leave as-is
            if re.search(r"\b(\d+)\s*(tablespoons?|tbsp)\b", qty, flags=re.I):
                m = re.search(r"\b(\d+)\s*(tablespoons?|tbsp)\b", qty, flags=re.I)
                out.append({"name": "Unsalted Butter", "qtyText": f"{m.group(1)} tbsp", "group": "dairy_eggs"})
                continue

        # Garlic: minced/chopped garlic in tbsp -> cloves (1 tbsp ~= 3 cloves)
        if "garlic" in nlow and any(x in nlow for x in ["minced", "chopped", "grated"]):
            tbsp = qty_to_tbsp(qty)
            if tbsp is not None:
                est = max(1.0, tbsp * 3.0)
                lo = int(est)
                hi = int(est) + 1
                out.append({"name": "garlic", "qtyText": f"{lo}-{hi} cloves", "group": "produce"})
                continue

        # Ginger: grated/minced ginger tbsp -> 1-inch piece per tbsp
        if "ginger" in nlow and any(x in nlow for x in ["grated", "minced"]):
            tbsp = qty_to_tbsp(qty)
            if tbsp is not None:
                est = max(1.0, tbsp)
                lo = int(est)
                hi = int(est) + 1
                out.append({"name": "ginger", "qtyText": f"{lo}-{hi} inch piece", "group": "produce"})
                continue

        out.append({"name": name, "qtyText": qty, "group": group})

    return out


def gemini_structure_ingredients(raw_items: list[str], model: str, api_key: str, timeout: int = 60) -> list[dict]:
    """Normalize ingredient-first format and group classification using Gemini (text-only)."""
    if not raw_items:
        return []

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {"text": PROMPT_STRUCTURE},
                    {"text": "Raw ingredient lines:\n" + "\n".join(f"- {x}" for x in raw_items)},
                ],
            }
        ],
        "generationConfig": {
            "temperature": 0.0,
            "maxOutputTokens": 550,
            "responseMimeType": "application/json",
        },
    }

    model_candidates = [
        model,
        "gemini-2.0-flash",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
    ]

    raw = ""
    last_err: Exception | None = None
    for mname in model_candidates:
        url = API_URL_TMPL.format(model=mname, key=api_key)
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                raw = resp.read().decode("utf-8")
            break
        except urllib.error.HTTPError as e:
            last_err = e
            if e.code in (404,):
                continue
            raise
        except Exception as e:
            last_err = e
            continue

    if not raw:
        raise RuntimeError(f"Gemini structuring request failed: {last_err}")

    data = json.loads(raw)
    try:
        text = data["candidates"][0]["content"]["parts"][0].get("text", "")
    except Exception:
        text = ""

    if not text:
        return []

    try:
        obj = json.loads(text)
    except Exception:
        m = re.search(r"\{.*\}", text, flags=re.S)
        if not m:
            return []
        try:
            obj = json.loads(m.group(0))
        except Exception:
            # If the model returns malformed JSON, fail closed and let the caller fall back.
            return []

    items = obj.get("items") if isinstance(obj, dict) else None
    if not isinstance(items, list):
        return []

    # Backward compatibility: map older group names to the new schema.
    group_map = {
        "dairy": "dairy_eggs",
        "eggs": "dairy_eggs",
        "meat": "meat_fish",
        "fish": "meat_fish",
        "seafood": "meat_fish",
        "baking": "snacks_sweets",  # closest; sweets/snacks/baking aisle
        "pantry": "other",
    }

    out: list[dict] = []
    for it in items:
        if not isinstance(it, dict):
            continue
        name = (it.get("name") or "").strip()
        qty = (it.get("qtyText") or "").strip()
        group = (it.get("group") or "other").strip().lower()
        if not name:
            continue
        group = group_map.get(group, group)
        if group not in {"produce", "dairy_eggs", "meat_fish", "frozen", "snacks_sweets", "household", "drinks", "other"}:
            group = "other"
        out.append({"name": name, "qtyText": qty, "group": group})

    return out


# Canonicalization rules for overlap detection.
# Keep this intentionally small + high-confidence.
_SYNONYM_SUBS: list[tuple[str, str]] = [
    # breadcrumbs variants
    (r"\bfresh bread ?crumbs?\b", "breadcrumbs"),
    (r"\bbread ?crumbs?\b", "breadcrumbs"),
    (r"\bbreadcrumbs\b", "breadcrumbs"),
    (r"\bpanko\b", "breadcrumbs"),
    # herbs
    (r"\bcoriander\b", "cilantro"),
    (r"\bcilantro\b", "cilantro"),
    # eggs
    (r"\begg yolks?\b", "eggs"),
    (r"\begg whites?\b", "eggs"),
    (r"\beggs?\b", "eggs"),
    # dairy: conservative
    (r"\bgreek yogurt\b", "yogurt"),
    (r"\byoghurt\b", "yogurt"),
]



def _norm_name(s: str) -> str:
    """Heuristic normalizer to detect overlaps."""
    s = s.strip().lower()
    s = re.sub(r",\s*plus more.*$", "", s)  # drop "plus more ..." tails
    s = re.sub(r"\([^)]*\)", "", s)  # remove parentheticals
    s = re.sub(r"\b\d+\s*(?:-\s*\d+)?\b", " ", s)  # remove simple numbers / ranges
    s = re.sub(r"\b\d+\/\d+\b", " ", s)  # remove fractions like 3/4
    s = re.sub(
        r"\b(?:cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|oz|ounce|ounces|lb|lbs|pound|pounds|clove|cloves|can|cans|tablespoons?)\b",
        " ",
        s,
    )
    s = re.sub(r"\s+", " ", s).strip(" -–—,")

    for pat, repl in _SYNONYM_SUBS:
        s = re.sub(pat, repl, s)

    s = re.sub(r"\s+", " ", s).strip(" -–—,")
    return s


def _get_existing_project_tasks(project: str) -> list[dict]:
    cp = subprocess.run(
        ["todoist", "tasks", "--all", "-p", project, "--json"],
        capture_output=True,
        text=True,
    )
    if cp.returncode != 0:
        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "todoist tasks failed")
    return json.loads(cp.stdout)


def _parse_fraction(num: str) -> Fraction | None:
    num = num.strip()
    if not num:
        return None
    # reject ranges like 1-2 or 12–16
    if re.search(r"\d\s*[-–]\s*\d", num):
        return None
    if "/" in num:
        try:
            a, b = num.split("/", 1)
            return Fraction(int(a), int(b))
        except Exception:
            return None
    try:
        # allow decimals
        return Fraction(str(float(num)))
    except Exception:
        return None


_VOL_TO_TBSP = {"tbsp": Fraction(1, 1), "tsp": Fraction(1, 3), "cup": Fraction(16, 1)}


def _convert_qty(q: Fraction, unit: str, target: str) -> Fraction | None:
    """Convert between compatible units (currently volume units cup/tbsp/tsp)."""
    if unit == target:
        return q
    if unit in _VOL_TO_TBSP and target in _VOL_TO_TBSP:
        tbsp = q * _VOL_TO_TBSP[unit]
        return tbsp / _VOL_TO_TBSP[target]
    return None


def _extract_qty_unit(text: str) -> tuple[Fraction | None, str | None]:
    """Best-effort quantity+unit extraction from a shopping item string.

    Supports patterns like:
      - "Olive oil (2 tbsp)"
      - "Garlic (4 cloves)"
      - "Eggs (4)" -> unit="count"
    Rejects ranges like "1-2" / "12–16".
    """
    t = text.lower()

    # Prefer inside parentheses
    m = re.search(r"\(([^)]{1,50})\)", t)
    cand = m.group(1) if m else t

    # unitful quantities
    m2 = re.search(
        r"\b(?P<num>\d+(?:\.\d+)?|\d+\/\d+)\s*(?P<unit>cups?|tbsp|tablespoons?|tsp|teaspoons?|oz|ounces?|lb|lbs|pounds?|cloves?|cans?|sticks?|boxes?|packages?)\b",
        cand,
    )
    if m2:
        qty = _parse_fraction(m2.group("num"))
        if qty is None:
            return None, None
        unit = m2.group("unit")
        unit = {
            "tablespoon": "tbsp",
            "tablespoons": "tbsp",
            "teaspoon": "tsp",
            "teaspoons": "tsp",
            "ounce": "oz",
            "ounces": "oz",
            "pound": "lb",
            "pounds": "lb",
            "lbs": "lb",
            "cup": "cup",
            "cups": "cup",
            "clove": "clove",
            "cloves": "clove",
            "can": "can",
            "cans": "can",
            "stick": "stick",
            "sticks": "stick",
            "box": "box",
            "boxes": "box",
            "package": "package",
            "packages": "package",
            "tbsp": "tbsp",
            "tsp": "tsp",
            "oz": "oz",
            "lb": "lb",
        }.get(unit, unit)
        return qty, unit

    # bare numbers (count)
    m3 = re.search(r"\b(?P<num>\d+(?:\.\d+)?|\d+\/\d+)\b", cand)
    if m3:
        qty = _parse_fraction(m3.group("num"))
        if qty is None:
            return None, None
        return qty, "count"

    return None, None


def _fraction_to_str(q: Fraction) -> str:
    # Prefer nice fractions when possible
    if q.denominator == 1:
        return str(q.numerator)
    return f"{q.numerator}/{q.denominator}"


def _slugify(s: str) -> str:
    s = s.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = re.sub(r"^-+|-+$", "", s)
    return s or "recipe"


def save_recipe_to_workspace(
    *,
    title: str,
    source: str,
    items: list[str],
    notes: str = "",
    recipes_dir: str = "recipes",
) -> str:
    """Create a markdown recipe entry and add it to recipes/index.md.

    If a recipe with the same source already exists, return the existing path.
    """
    d = date.today().isoformat()
    t = title.strip() or "Recipe"
    slug = _slugify(t)
    out_dir = Path(recipes_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # De-dupe by source (URL or photo:...) if possible
    src_line = f"- Source: {source}".strip()
    for fp in sorted(out_dir.glob("*.md")):
        try:
            txt = fp.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if src_line and src_line in txt:
            return str(fp)

    path = out_dir / f"{d}--{slug}.md"
    # avoid overwrite
    if path.exists():
        path = out_dir / f"{d}--{slug}-{os.getpid()}.md"

    ing = "\n".join([f"- {x}" for x in items])
    md = (
        f"# {t}\n\n"
        f"- Date cooked: {d}\n"
        f"- Source: {source}\n\n"
        f"## Ingredients\n\n{ing}\n\n"
    )
    if notes.strip():
        md += f"## Notes\n\n{notes.strip()}\n"

    path.write_text(md, encoding="utf-8")

    # update index
    idx = out_dir / "index.md"
    if not idx.exists():
        idx.write_text(
            "# Cookbook Index\n\n| Date cooked | Recipe | Tags | Rating | Source |\n|---|---|---|---:|---|\n",
            encoding="utf-8",
        )

    rel = path.as_posix()
    row = f"| {d} | [{t}]({rel}) |  |  | {source} |\n"
    with idx.open("a", encoding="utf-8") as f:
        f.write(row)

    return str(path)


def _rewrite_with_total(original: str, total: Fraction, unit: str) -> str:
    """Rewrite task content to include the new total quantity.

    Keeps the ingredient name first, with a single trailing parenthetical.
    """
    base = original.strip()
    base = re.sub(r"\s*\([^)]*\)\s*", " ", base).strip()
    if unit == "count":
        return f"{base} ({_fraction_to_str(total)})"
    return f"{base} ({_fraction_to_str(total)} {unit})"


def add_items_to_todoist(
    items: list[str],
    project: str,
    prefix: str = "",
    dry_run: bool = False,
    skip_overlap: bool = True,
    skip_pantry: bool = True,
    sum_quantities: bool = True,
) -> list[str]:
    """Update Todoist Shopping list.

    Default behavior:
      - skip pantry staples (salt/pepper)
      - detect overlaps using normalization + synonym mapping
      - if overlap AND both sides have parseable (qty, unit), update existing task to summed total
      - otherwise, skip adding duplicates
    """

    ids: list[str] = []

    existing_tasks = _get_existing_project_tasks(project) if (skip_overlap and not dry_run) else []
    existing_by_norm: dict[str, dict] = {}
    for t in existing_tasks:
        content = (t.get("content") or "").strip()
        if not content:
            continue
        nk = _norm_name(content)
        if not nk:
            continue

        if nk not in existing_by_norm:
            existing_by_norm[nk] = t
            continue

        # Prefer an existing task that already has a parseable qty+unit.
        cur = existing_by_norm[nk]
        cur_qty, cur_unit = _extract_qty_unit((cur.get("content") or "").strip())
        new_qty, new_unit = _extract_qty_unit(content)
        if (cur_qty is None or not cur_unit) and (new_qty is not None and new_unit):
            existing_by_norm[nk] = t

    pantry = {
        "salt",
        "kosher salt",
        "pepper",
        "black pepper",
        "freshly ground black pepper",
    }
    pantry_regex = re.compile(r"\b(salt|pepper)\b", re.I)


    seen_new: set[str] = set()

    for item in items:
        title = f"{prefix}{item}".strip()
        if not title:
            continue

        norm = _norm_name(title)
        if not norm:
            continue

        if skip_pantry and (norm in pantry or pantry_regex.search(title)):
            continue

        # dedupe within this run
        if norm in seen_new:
            continue
        seen_new.add(norm)

        existing_task = existing_by_norm.get(norm) if skip_overlap else None

        if dry_run:
            # In dry-run, we just show what we'd consider as candidate adds/updates.
            # (We still print even if it overlaps, because user may want to see it.)
            print(title)
            continue

        if existing_task and sum_quantities:
            ex_content = (existing_task.get("content") or "").strip()
            ex_id = existing_task.get("id")
            if ex_id:
                ex_qty, ex_unit = _extract_qty_unit(ex_content)
                new_qty, new_unit = _extract_qty_unit(title)
                # If existing has no qty but new does, set existing to new qty.
                if (ex_qty is None or not ex_unit) and (new_qty is not None and new_unit):
                    new_content = _rewrite_with_total(ex_content, new_qty, new_unit)
                    cp = subprocess.run(
                        ["todoist", "update", str(ex_id), "--content", new_content, "--json"],
                        capture_output=True,
                        text=True,
                    )
                    if cp.returncode != 0:
                        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "todoist update failed")
                    obj = json.loads(cp.stdout)
                    tid = obj.get("id", "")
                    if tid:
                        ids.append(tid)
                    if target_section:
                        _move_task(str(ex_id), project, target_section)
                    continue

                if ex_qty is not None and new_qty is not None and ex_unit and new_unit:
                    # allow unit conversion for compatible measures (e.g., cup <-> tbsp)
                    new_converted = _convert_qty(new_qty, new_unit, ex_unit)
                    if new_converted is None and ex_unit != new_unit:
                        # try converting existing into new unit
                        ex_converted = _convert_qty(ex_qty, ex_unit, new_unit)
                        if ex_converted is not None:
                            total = ex_converted + new_qty
                            new_content = _rewrite_with_total(ex_content, total, new_unit)
                            ex_unit = new_unit
                        else:
                            new_converted = None
                    if new_converted is not None:
                        total = ex_qty + new_converted
                        new_content = _rewrite_with_total(ex_content, total, ex_unit)
                    else:
                        total = None

                if 'total' in locals() and total is not None:
                    cp = subprocess.run(
                        ["todoist", "update", str(ex_id), "--content", new_content, "--json"],
                        capture_output=True,
                        text=True,
                    )
                    if cp.returncode != 0:
                        raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "todoist update failed")
                    obj = json.loads(cp.stdout)
                    tid = obj.get("id", "")
                    if tid:
                        ids.append(tid)
                    if target_section:
                        _move_task(str(ex_id), project, target_section)
                    continue

            # If we can’t safely sum, treat as overlap and skip adding.
            continue

        if existing_task and skip_overlap:
            continue

        cp = subprocess.run(
            ["todoist", "add", title, "--project", project, "--json"],
            capture_output=True,
            text=True,
        )
        if cp.returncode != 0:
            raise RuntimeError(cp.stderr.strip() or cp.stdout.strip() or "todoist add failed")
        obj = json.loads(cp.stdout)
        tid = obj.get("id", "")
        if tid:
            ids.append(tid)
            if target_section:
                _move_task(str(tid), project, target_section)

    return ids


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="Path to recipe/cookbook photo")
    ap.add_argument("--project", default="Shopping", help="Todoist project name (default: Shopping)")
    ap.add_argument("--model", default="gemini-2.0-flash", help="Gemini model (Flash recommended)")
    ap.add_argument("--prefix", default="", help="Prefix for created tasks")
    ap.add_argument("--title", default="", help="Recipe title override (used for cookbook saving)")
    ap.add_argument("--source", default="", help="Recipe source URL/text override (used for cookbook saving)")
    ap.add_argument("--no-save", action="store_true", help="Do not save to workspace cookbook")
    ap.add_argument("--dry-run", action="store_true", help="Print extracted items; do not create tasks")
    ap.add_argument("--no-overlap-check", action="store_true", help="Do not check current Shopping list for overlaps")
    ap.add_argument("--include-pantry", action="store_true", help="Include pantry staples (e.g., salt/pepper)")
    ap.add_argument("--no-sum", action="store_true", help="Do not sum quantities on overlap; just skip duplicates")
    ap.add_argument("--timeout", type=int, default=60, help="Gemini request timeout (seconds)")
    args = ap.parse_args()

    if not os.path.exists(args.image):
        _die(f"Image not found: {args.image}")

    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        _die("Missing GEMINI_API_KEY (or GOOGLE_API_KEY) in environment")

    # Ensure todoist token present when not dry-run
    if not args.dry_run and not os.environ.get("TODOIST_API_TOKEN"):
        _die("Missing TODOIST_API_TOKEN in environment")

    extracted = gemini_extract_items(args.image, args.model, api_key, timeout=args.timeout)

    # Backward/robust parsing: accept either {title, items, notes} or a raw list of strings.
    if isinstance(extracted, list):
        # Sometimes the model returns a JSON array with a single object.
        if extracted and isinstance(extracted[0], dict):
            obj = extracted[0]
            items = obj.get("items") or []
            title = (args.title or obj.get("title") or "").strip()
            notes = (obj.get("notes") or "").strip()
        else:
            items = extracted
            title = (args.title or "").strip()
            notes = ""
    else:
        items = extracted.get("items") or []
        title = (args.title or extracted.get("title") or "").strip()
        notes = (extracted.get("notes") or "").strip()

    source = (args.source or f"photo:{args.image}").strip()
    if not isinstance(items, list):
        _die(f"Gemini returned unexpected items type: {type(items)}")

    # Normalize raw strings
    raw_lines: list[str] = []
    for it in items:
        if not isinstance(it, str):
            continue
        s = normalize_raw_ingredient_line(it)
        if s:
            raw_lines.append(s)

    if not raw_lines:
        _die("No items extracted. Try a clearer crop of the ingredients list.", code=1)

    # Convert to ingredient-first format + group, then sort by group order.
    structured = gemini_structure_ingredients(raw_lines, args.model, api_key, timeout=args.timeout)
    if not structured:
        structured = heuristic_structure_ingredients(raw_lines)

    # Map our internal groups into Bo's preferred Todoist Shopping sections.
    # Current section scheme: Fresh, Pantry, Frozen, Snacks, Drinks, Household.
    GROUP_ORDER = [
        "produce",
        "dairy_eggs",
        "meat_fish",
        "frozen",
        "snacks_sweets",
        "household",
        "drinks",
        "other",
    ]
    SECTION_NAME = {
        "produce": "Fresh",
        "dairy_eggs": "Fresh",
        "meat_fish": "Fresh",
        "frozen": "Frozen",
        "snacks_sweets": "Pantry",
        "household": "Household",
        "drinks": "Drinks",
        "other": "Pantry",
    }

    if structured:
        # Convert to "what to buy" (always-on) then sort.
        structured = convert_to_buy_items(structured)

        def key(it: dict):
            g = it.get("group", "other")
            try:
                gi = GROUP_ORDER.index(g)
            except ValueError:
                gi = GROUP_ORDER.index("other")
            return (gi, it.get("name", "").lower())

        structured.sort(key=key)
        formatted: list[str] = []
        for it in structured:
            name = (it.get("name") or "").strip()
            qty = (it.get("qtyText") or "").strip()
            group = (it.get("group") or "other").strip().lower()
            if not name:
                continue
            content = f"{clean_name(name)} ({qty})" if qty else clean_name(name)
            # Canonicalize eggs display
            if _norm_name(content) == "eggs":
                content = "Eggs" + (f" ({qty})" if qty else "")
            formatted.append(content)
            # No Todoist sections/groups; keep a single flat list.

        add_list = formatted
    else:
        # Fallback: keep raw extraction
        add_list = raw_lines

    ids = add_items_to_todoist(
        add_list,
        args.project,
        prefix=args.prefix,
        dry_run=args.dry_run,
        skip_overlap=not args.no_overlap_check,
        skip_pantry=not args.include_pantry,
        sum_quantities=not args.no_sum,
    )

    saved_path = ""
    if not args.no_save:
        repo_root = Path(__file__).resolve().parents[3]  # .../clawd
        saved_path = save_recipe_to_workspace(
            title=title,
            source=source,
            items=add_list,
            notes=notes,
            recipes_dir=str(repo_root / "recipes"),
        )

    # Report the original extracted list; additions may be filtered for overlap/pantry.
    out = {
        "created": len(ids) if not args.dry_run else 0,
        "project": args.project,
        "title": title,
        "source": source,
        "items": add_list,
        "task_ids": ids,
        "saved_recipe": saved_path,
        "note": "salt/pepper are skipped by default; overlap check runs unless --no-overlap-check",
    }
    print(json.dumps(out, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
