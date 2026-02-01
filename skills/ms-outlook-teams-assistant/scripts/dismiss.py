"""Dismiss an item key from reminders.

We dismiss by index from the last reminder run. We store the mapping in state/last_batch.json.

Usage:
  python scripts/dismiss.py --config references/config.json --number 1
"""

from __future__ import annotations

import argparse
import json
import os
import time


def _load(path: str) -> dict:
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(path: str, data: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("references", "config.json"))
    ap.add_argument("--number", type=int, required=True)
    args = ap.parse_args()

    cfg_path = os.path.abspath(args.config)
    skill_dir = os.path.dirname(os.path.dirname(cfg_path))

    state_path = os.path.join(skill_dir, "state", "reminders.json")
    batch_path = os.path.join(skill_dir, "state", "last_batch.json")

    st = _load(state_path)
    batch = _load(batch_path)
    keys = batch.get("keys", [])

    idx = args.number - 1
    if idx < 0 or idx >= len(keys):
        raise SystemExit(f"Invalid number {args.number}. Last batch had {len(keys)} items.")

    key = keys[idx]
    st.setdefault("dismissed", {})[key] = time.time()

    _save(state_path, st)
    print(f"DISMISSED {args.number}: {key}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
