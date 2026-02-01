#!/usr/bin/env python3
"""Low-level Niri IPC client (direct `$NIRI_SOCKET` access).

Protocol (newline-delimited JSON):
- connect to UNIX socket at `$NIRI_SOCKET`
- send JSON request on a single line + newline
- read JSON reply as a single line

This script supports:
- sending a single request JSON (raw)
- sending a batch of requests (one per line)
- printing replies (normalized JSON)
- event stream (prints events until interrupted)

Why not only `niri msg`?
- `niri msg --json` is great and should be preferred for most tasks.
- Direct socket access enables complete coverage, custom batching, and behavior identical to the
  underlying IPC protocol.

Safety:
- This script can trigger destructive actions (quit compositor, power off monitors, etc.) if you
  send those requests. Use with care.
"""

from __future__ import annotations

import argparse
import json
import os
import socket
import sys
from typing import Any, Iterable, Iterator


def socket_path() -> str:
    p = os.environ.get("NIRI_SOCKET")
    if not p:
        raise SystemExit("NIRI_SOCKET is not set. Run inside your Niri session or export it.")
    return p


def connect() -> socket.socket:
    s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    s.connect(socket_path())
    return s


def _send_line(sock: socket.socket, line: str) -> None:
    if not line.endswith("\n"):
        line += "\n"
    sock.sendall(line.encode("utf-8"))


def _read_line(fileobj) -> str:
    line = fileobj.readline()
    if not line:
        raise EOFError("socket closed")
    return line


def iter_json_lines_from_stdin() -> Iterator[Any]:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        yield json.loads(raw)


def normalize(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


def send_one(req: Any) -> Any:
    with connect() as s:
        f = s.makefile("r", encoding="utf-8", newline="\n")
        _send_line(s, normalize(req))
        reply_line = _read_line(f)
        return json.loads(reply_line)


def send_many(reqs: Iterable[Any]) -> list[Any]:
    with connect() as s:
        f = s.makefile("r", encoding="utf-8", newline="\n")
        out: list[Any] = []
        for req in reqs:
            _send_line(s, normalize(req))
            reply_line = _read_line(f)
            out.append(json.loads(reply_line))
        return out


def event_stream() -> None:
    # You must send EventStream request first.
    # After that, niri writes events continuously and stops reading further requests.
    with connect() as s:
        f = s.makefile("r", encoding="utf-8", newline="\n")
        _send_line(s, normalize("EventStream"))
        first = json.loads(_read_line(f))
        print(normalize(first))
        while True:
            line = _read_line(f)
            evt = json.loads(line)
            print(normalize(evt))
            sys.stdout.flush()


def main() -> int:
    ap = argparse.ArgumentParser(prog="niri_socket.py", description="Direct Niri IPC socket client")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p_raw = sub.add_parser("raw", help="Send a single request JSON from args")
    p_raw.add_argument(
        "json",
        help='Request JSON. Examples: ' '"\\\"FocusedWindow\\\"" or "{\\\"Request\\\":...}"',
    )

    p_stdin = sub.add_parser("stdin", help="Send one request per stdin line (each line is JSON)")

    sub.add_parser("event-stream", help="Request event stream and print JSON lines until interrupted")

    ns = ap.parse_args()

    if ns.cmd == "raw":
        req = json.loads(ns.json)
        reply = send_one(req)
        print(normalize(reply))
        return 0

    if ns.cmd == "stdin":
        replies = send_many(iter_json_lines_from_stdin())
        for r in replies:
            print(normalize(r))
        return 0

    if ns.cmd == "event-stream":
        event_stream()
        return 0

    raise SystemExit("unreachable")


if __name__ == "__main__":
    raise SystemExit(main())
