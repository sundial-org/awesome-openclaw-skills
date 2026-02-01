#!/usr/bin/env python3
"""niri IPC helper.

This is a convenience wrapper around `niri msg --json ...`.

Why: JSON output is stable; human-readable output is not. This wrapper keeps calls consistent and
makes it easy to chain in scripts.

Examples:
  ./niri.py version
  ./niri.py outputs
  ./niri.py workspaces
  ./niri.py windows
  ./niri.py focused-window
  ./niri.py action focus-workspace 2
  ./niri.py action move-window-to-workspace 3
  ./niri.py action focus-window 123

Notes:
- Requires `niri` and a running compositor.
- Must run in an environment where `$NIRI_SOCKET` is set (typically inside the Niri session).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from typing import Any


def run_niri_msg(args: list[str]) -> tuple[int, str, str]:
    cmd = ["niri", "msg", "--json", *args]
    p = subprocess.run(cmd, text=True, capture_output=True)
    return p.returncode, p.stdout, p.stderr


def load_json_or_die(s: str) -> Any:
    s = s.strip()
    if not s:
        return None
    try:
        return json.loads(s)
    except json.JSONDecodeError as e:
        raise SystemExit(f"Failed to parse JSON from niri msg output: {e}\nOutput was:\n{s}")


def main() -> int:
    ap = argparse.ArgumentParser(prog="niri.py", description="Convenience wrapper for niri IPC")
    sub = ap.add_subparsers(dest="cmd", required=True)

    # Informational endpoints
    for name in [
        "version",
        "outputs",
        "workspaces",
        "windows",
        "layers",
        "keyboard-layouts",
        "focused-output",
        "focused-window",
        "overview-state",
    ]:
        sub.add_parser(name)

    # Generic passthrough
    p_action = sub.add_parser("action", help="Run `niri msg action ...`")
    p_action.add_argument("action_args", nargs=argparse.REMAINDER, help="Arguments after 'action'")

    p_output = sub.add_parser("output", help="Run `niri msg output ...`")
    p_output.add_argument("output_args", nargs=argparse.REMAINDER, help="Arguments after 'output'")

    p_event = sub.add_parser("event-stream", help="Run `niri msg --json event-stream`")
    p_event.add_argument(
        "--lines",
        type=int,
        default=0,
        help="If non-zero, stop after N event lines (useful for testing).",
    )

    p_raw = sub.add_parser("raw", help="Run `niri msg --json <args...>` directly")
    p_raw.add_argument("args", nargs=argparse.REMAINDER)

    ns = ap.parse_args()

    if ns.cmd == "event-stream":
        # Stream mode: do not attempt to parse; forward lines.
        cmd = ["niri", "msg", "--json", "event-stream"]
        p = subprocess.Popen(cmd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        assert p.stdout is not None
        count = 0
        try:
            for line in p.stdout:
                sys.stdout.write(line)
                sys.stdout.flush()
                count += 1
                if ns.lines and count >= ns.lines:
                    p.terminate()
                    break
        finally:
            try:
                p.terminate()
            except Exception:
                pass
        return 0

    if ns.cmd == "raw":
        args = [a for a in ns.args if a != "--"]
        code, out, err = run_niri_msg(args)
    elif ns.cmd == "action":
        # Preserve "--" because some niri actions use it to separate the action from command args.
        args = ns.action_args
        code, out, err = run_niri_msg(["action", *args])
    elif ns.cmd == "output":
        # Preserve "--" for parity with `niri msg`.
        args = ns.output_args
        code, out, err = run_niri_msg(["output", *args])
    else:
        code, out, err = run_niri_msg([ns.cmd])

    if err.strip():
        # Preserve stderr for debugging but keep stdout clean JSON for piping.
        print(err.rstrip(), file=sys.stderr)

    if code != 0:
        # If niri msg fails, its stderr is the useful output.
        return code

    # Ensure stdout is valid JSON and re-dump to normalized JSON (one line).
    data = load_json_or_die(out)
    sys.stdout.write(json.dumps(data, ensure_ascii=False))
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
