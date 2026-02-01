#!/usr/bin/env python3
"""Legacy compatibility wrapper.

This file used to be the monolithic Tesla Fleet API CLI. The skill has since
been split into focused scripts:

- auth.py            OAuth + config
- vehicles.py        list vehicles + refresh cache
- vehicle_data.py    read vehicle data
- command.py         issue vehicle commands (climate/locks/charging/etc)

This wrapper keeps a few common invocations working, but new usage should call
those scripts directly.
"""

from __future__ import annotations

import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def _exec(script: str, argv: list[str]) -> None:
    target = os.path.join(HERE, script)
    os.execv(sys.executable, [sys.executable, target, *argv])


def main() -> int:
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("--dir", default=os.path.expanduser("~/.clawdbot/tesla-fleet-api"))
    ap.add_argument("-h", "--help", action="store_true")
    ap.add_argument("cmd", nargs="?")
    ap.add_argument("rest", nargs=argparse.REMAINDER)
    args = ap.parse_args()

    if args.help or not args.cmd:
        print("Deprecated. Use scripts/auth.py, scripts/vehicles.py, scripts/vehicle_data.py, scripts/command.py")
        print()
        print("Compat commands:")
        print("  vehicles")
        print("  vehicle-data [VEHICLE]")
        print("  wake-up [VEHICLE]")
        print("  climate-start [VEHICLE]")
        print("  climate-stop [VEHICLE]")
        print("  door-lock [VEHICLE]")
        print("  door-unlock [VEHICLE]")
        print("  honk-horn [VEHICLE]")
        print("  flash-lights [VEHICLE]")
        print("  charge-start [VEHICLE]")
        print("  charge-stop [VEHICLE]")
        print()
        print("Notes:")
        print("  VEHICLE can be VIN or display name; omitted if you only have one vehicle.")
        return 0

    cmd = args.cmd
    rest = [r for r in args.rest if r != "--"]

    # Routes
    if cmd == "vehicles":
        _exec("vehicles.py", ["--dir", args.dir, *rest])

    if cmd in ("vehicle-data", "vehicle_data"):
        # vehicle_data.py takes VEHICLE as optional positional
        _exec("vehicle_data.py", ["--dir", args.dir, *rest])

    # Map old hyphenated commands to new command.py verbs
    mapping = {
        "wake-up": ["wake"],
        "climate-start": ["climate", "start"],
        "climate-stop": ["climate", "stop"],
        "door-lock": ["lock"],
        "door-unlock": ["unlock"],
        "honk-horn": ["honk"],
        "flash-lights": ["flash"],
        "charge-start": ["charge", "start"],
        "charge-stop": ["charge", "stop"],
    }

    if cmd in mapping:
        # If first arg doesn't look like an option, treat it as VEHICLE.
        vehicle = None
        remaining = rest
        if remaining and not remaining[0].startswith("-"):
            vehicle = remaining[0]
            remaining = remaining[1:]
        argv = ["--dir", args.dir]
        if vehicle:
            argv.append(vehicle)
        argv.extend(mapping[cmd])
        argv.extend(remaining)
        _exec("command.py", argv)

    print(f"Unknown legacy command: {cmd}", file=sys.stderr)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
