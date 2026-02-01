#!/usr/bin/env python3
"""Favorites summary (human summary + JSON).

Reads ~/.config/surfline/favorites.json.

Usage:
  surfline_favorites.py [--json] [--text] [--both]

Default: --both
"""

import json
import sys
from pathlib import Path

from surfline_client import kbyg_conditions

CONFIG = Path.home() / ".config" / "surfline" / "favorites.json"


def _pick_flag(argv: list[str]) -> str:
    if "--json" in argv:
        return "json"
    if "--text" in argv:
        return "text"
    return "both"


def _headline(payload: dict) -> str:
    try:
        d = (payload.get("data") or {})
        conds = d.get("conditions") or []
        if conds and isinstance(conds, list):
            h = (conds[0].get("headline") or "").strip()
            if h:
                return h
    except Exception:
        pass
    return "(no headline)"


def _score(headline: str) -> int:
    h = headline.lower()
    score = 0
    if "flat" in h or "lake" in h:
        score -= 3
    if "small" in h:
        score += 1
    if "fun" in h:
        score += 2
    if "good" in h:
        score += 3
    if "great" in h or "firing" in h:
        score += 5
    if "clean" in h:
        score += 2
    if "offshore" in h:
        score += 2
    if "onshore" in h:
        score -= 1
    return score


def main() -> int:
    mode = _pick_flag(sys.argv[1:])

    if not CONFIG.exists():
        msg = f"Missing {CONFIG}. Create it from references/favorites.json.example"
        if mode in ("text", "both"):
            print(msg)
        if mode in ("json", "both"):
            print(json.dumps({"error": msg}))
        return 2

    cfg = json.loads(CONFIG.read_text("utf-8"))
    spots = cfg.get("spots") or []
    if not spots:
        msg = "No spots in favorites.json"
        if mode in ("text", "both"):
            print(msg)
        if mode in ("json", "both"):
            print(json.dumps({"error": msg}))
        return 2

    rows = []
    for s in spots:
        spot_id = str(s.get("spotId") or "").strip()
        name = (s.get("name") or spot_id).strip()
        if not spot_id:
            continue
        c = kbyg_conditions(spot_id)
        h = _headline(c)
        rows.append({"spotId": spot_id, "name": name, "headline": h})

    # Preserve config order.
    if mode in ("text", "both"):
        lines = ["Surfline favorites:"]
        for r in rows:
            lines.append(f"- {r['name']}: {r['headline']}")
        print("\n".join(lines))

    if mode in ("json", "both"):
        print(json.dumps({"favorites": rows}, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        raise SystemExit(0)
