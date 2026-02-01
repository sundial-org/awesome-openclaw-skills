#!/usr/bin/env python3
"""Higher-level Niri control helpers.

This tool sits on top of `niri msg --json` (preferred for stability) and offers convenience
operations like:
- focus a window by title/app_id substring
- close a window by match
- move a window to a workspace by name/index
- focus a workspace by name

For anything not covered, use:
- `./niri.py raw ...` (thin wrapper over `niri msg --json`)
- or `./niri_socket.py raw ...` (direct socket requests)

Selection rules:
- If multiple windows match, we fail unless `--pick first` is used.
- Matching is case-insensitive substring against title and app_id.

Note: This script depends only on `niri msg --json` and standard Python.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


def run_json(cmd: list[str]) -> Any:
    p = subprocess.run(cmd, text=True, capture_output=True)
    if p.stderr.strip():
        print(p.stderr.rstrip(), file=sys.stderr)
    if p.returncode != 0:
        raise SystemExit(p.returncode)
    out = p.stdout.strip()
    if not out:
        return None
    return json.loads(out)


def niri(args: list[str]) -> Any:
    return run_json(["niri", "msg", "--json", *args])


def get_windows() -> list[dict[str, Any]]:
    data = niri(["windows"])
    # Current niri msg --json format is Reply-like; handle both shapes.
    # Often: {"Ok": {"Windows": [ ... ]}}
    if isinstance(data, dict) and "Ok" in data:
        ok = data["Ok"]
        # Find the first list nested under ok
        if isinstance(ok, dict):
            for v in ok.values():
                if isinstance(v, list):
                    return v
    if isinstance(data, list):
        return data
    raise SystemExit(f"Unexpected windows JSON shape: {type(data)}")


def get_workspaces() -> list[dict[str, Any]]:
    data = niri(["workspaces"])
    if isinstance(data, dict) and "Ok" in data:
        ok = data["Ok"]
        if isinstance(ok, dict):
            for v in ok.values():
                if isinstance(v, list):
                    return v
    if isinstance(data, list):
        return data
    raise SystemExit(f"Unexpected workspaces JSON shape: {type(data)}")


def match_window(w: dict[str, Any], q: str) -> bool:
    ql = q.lower()
    title = str(w.get("title", "")).lower()
    app_id = str(w.get("app_id", "")).lower()
    return ql in title or ql in app_id


def pick_one(matches: list[dict[str, Any]], pick: str) -> dict[str, Any]:
    if not matches:
        raise SystemExit("No windows matched.")
    if len(matches) == 1:
        return matches[0]
    if pick == "first":
        return matches[0]
    # Print a helpful list.
    lines = []
    for w in matches:
        lines.append(
            f"id={w.get('id')} app_id={w.get('app_id')} title={w.get('title')} workspace_id={w.get('workspace_id')}"
        )
    raise SystemExit(
        "Multiple windows matched. Be more specific, or use --pick first.\n" + "\n".join(lines)
    )


def find_workspace_by_name(name: str) -> dict[str, Any]:
    for ws in get_workspaces():
        if str(ws.get("name", "")) == name:
            return ws
    raise SystemExit(f"Workspace name not found: {name}")


def main() -> int:
    ap = argparse.ArgumentParser(prog="niri_ctl.py", description="High-level Niri control")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_listw = sub.add_parser("list-windows")
    p_listw.add_argument("--query", default="", help="Optional substring filter")

    p_focus = sub.add_parser("focus")
    p_focus.add_argument("query", help="Substring to match title/app_id")
    p_focus.add_argument("--pick", choices=["fail", "first"], default="fail")

    p_close = sub.add_parser("close")
    p_close.add_argument("query", help="Substring to match title/app_id")
    p_close.add_argument("--pick", choices=["fail", "first"], default="fail")

    p_move = sub.add_parser("move-to-workspace")
    p_move.add_argument("query", help="Substring to match title/app_id")
    p_move.add_argument("workspace", help="Workspace name or index")
    p_move.add_argument("--pick", choices=["fail", "first"], default="fail")

    p_fws = sub.add_parser("focus-workspace")
    p_fws.add_argument("workspace", help="Workspace name or index")

    ns = ap.parse_args()

    if ns.cmd == "list-windows":
        wins = get_windows()
        if ns.query:
            wins = [w for w in wins if match_window(w, ns.query)]
        for w in wins:
            print(
                json.dumps(
                    {
                        "id": w.get("id"),
                        "app_id": w.get("app_id"),
                        "title": w.get("title"),
                        "workspace_id": w.get("workspace_id"),
                        "is_focused": w.get("is_focused"),
                    },
                    ensure_ascii=False,
                )
            )
        return 0

    if ns.cmd in {"focus", "close", "move-to-workspace"}:
        wins = [w for w in get_windows() if match_window(w, ns.query)]
        w = pick_one(wins, ns.pick)
        wid = w.get("id")
        if wid is None:
            raise SystemExit("Matched window missing id")

        if ns.cmd == "focus":
            niri(["action", "focus-window", "--id", str(wid)])
            return 0

        if ns.cmd == "close":
            # focus then close focused (safer than close by id, since close-window supports focused)
            niri(["action", "focus-window", "--id", str(wid)])
            niri(["action", "close-window"])
            return 0

        if ns.cmd == "move-to-workspace":
            # niri action supports workspace by reference (index or name)
            # We'll focus the window first, then move focused window.
            niri(["action", "focus-window", "--id", str(wid)])
            # Decide if index (int) or name.
            try:
                idx = int(ns.workspace)
                niri(["action", "move-window-to-workspace", str(idx)])
            except ValueError:
                ws = find_workspace_by_name(ns.workspace)
                name = ws.get("name")
                if not name:
                    raise SystemExit("Workspace has no name")
                niri(["action", "move-window-to-workspace", str(name)])
            return 0

    if ns.cmd == "focus-workspace":
        try:
            idx = int(ns.workspace)
            niri(["action", "focus-workspace", str(idx)])
        except ValueError:
            ws = find_workspace_by_name(ns.workspace)
            name = ws.get("name")
            if not name:
                raise SystemExit("Workspace has no name")
            niri(["action", "focus-workspace", str(name)])
        return 0

    raise SystemExit("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
