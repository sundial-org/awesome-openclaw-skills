#!/usr/bin/env python3
"""One-spot report (human summary + JSON).

Usage:
  surfline_report.py <spotId> [--json] [--text] [--both]

Default: --both
"""

import json
import sys
from datetime import datetime

from surfline_client import kbyg_conditions, kbyg_tides, kbyg_wave, kbyg_wind


def _pick_flag(argv: list[str]) -> str:
    if "--json" in argv:
        return "json"
    if "--text" in argv:
        return "text"
    return "both"


def _fmt_local_day(ts: int, tz_offset_hours: int) -> str:
    # ts is UTC seconds. tz_offset_hours is e.g. -8.
    dt = datetime.utcfromtimestamp(ts)
    dt = dt.replace()  # naive utc
    # just show the provided forecastDay when available, else date from timestamp
    return dt.strftime("%Y-%m-%d")


def _headline_from_conditions(payload: dict) -> str:
    d = (payload.get("data") or {})
    conds = d.get("conditions") or []
    if conds and isinstance(conds, list):
        h = (conds[0].get("headline") or "").strip()
        if h:
            return h
    return "(no headline)"


# (score removed)

def main() -> int:
    if len(sys.argv) < 2:
        print("Usage: surfline_report.py <spotId> [--json|--text|--both]")
        return 2

    spot_id = sys.argv[1]
    mode = _pick_flag(sys.argv[2:])

    conditions = kbyg_conditions(spot_id)
    wave = kbyg_wave(spot_id, days=2, interval_hours=1)
    wind = kbyg_wind(spot_id, days=2, interval_hours=1)
    tides = kbyg_tides(spot_id, days=2)

    headline = _headline_from_conditions(conditions)

    out = {
        "spotId": spot_id,
        "headline": headline,
        "raw": {
            "conditions": conditions,
            "wave": wave,
            "wind": wind,
            "tides": tides,
        },
    }

    if mode in ("text", "both"):
        # Keep short and stable.
        print(f"Spot {spot_id}: {headline}")

    if mode in ("json", "both"):
        print(json.dumps(out, ensure_ascii=False))

    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        # allow piping to head
        raise SystemExit(0)
