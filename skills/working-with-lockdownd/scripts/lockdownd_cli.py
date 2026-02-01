#!/usr/bin/env python3
# Lockdownd CLI - Primary User Interface
# This script serves as the main entry point for interacting with the skill. It provides a safe,
# structured command-line interface for common tasks like querying battery status, streaming logs,
# or checking connection health. It intentionally isolates "safe" commands from dangerous ones.
"""lockdownd_cli.py

Opinionated CLI wrapper around the Orchard WiFi lockdown research scripts (by woflo).
Goal: reliable day-to-day use (query keys, start safe services, stream logs).

This intentionally avoids running dangerous requests by default.

Examples:
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py ping --host 10.0.0.33
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py get --host 10.0.0.33 --key DeviceName
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py get --host 10.0.0.33 --domain com.apple.mobile.battery
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py syslog --host 10.0.0.33
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py trace --host 10.0.0.33 --seconds 10
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py status --host 10.0.0.33
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py probe --host 10.0.0.33
  python skills/working-with-lockdownd/scripts/lockdownd_cli.py discover --prefix 10.0.0.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from typing import Any

# Local import (bundled)
from wifi_lockdown import LockdownClient, LOCKDOWN_PORT, get_pairing_record, list_pairing_records

SAFE_SERVICES = {
    "com.apple.syslog_relay",
    "com.apple.os_trace_relay",
    "com.apple.mobile.heartbeat",
    "com.apple.notification_proxy",
    "com.apple.mobile.insecure_notification_proxy",
}

DANGEROUS_REQUESTS = {
    "EnterRecovery",  # Remote DoS
}


def jdump(obj: Any) -> None:
    print(json.dumps(obj, indent=2, default=str, ensure_ascii=False))


def connect_client(host: str, udid: str | None = None) -> LockdownClient:
    pairing = get_pairing_record(udid) if udid else None
    c = LockdownClient(host, pairing=pairing)
    c.connect()
    # Start authenticated session; some calls work without SSL, but session makes behavior consistent.
    sess = c.start_session()
    if not isinstance(sess, dict):
        raise RuntimeError("StartSession failed (no response)")
    if sess.get("EnableSessionSSL"):
        c.start_ssl()
    return c


def cmd_ping(args: argparse.Namespace) -> int:
    import socket

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(args.timeout)
    try:
        s.connect((args.host, LOCKDOWN_PORT))
        print(f"OK {args.host}:{LOCKDOWN_PORT}")
        return 0
    except Exception as e:
        print(f"DOWN {args.host}:{LOCKDOWN_PORT} ({e})")
        return 2
    finally:
        try:
            s.close()
        except Exception:
            pass


def cmd_get(args: argparse.Namespace) -> int:
    c = connect_client(args.host, args.udid)
    try:
        resp = c.query(domain=args.domain, key=args.key)
        jdump(resp)
        return 0
    finally:
        c.close()


def cmd_start_service(args: argparse.Namespace) -> int:
    if args.service in SAFE_SERVICES or args.force:
        pass
    else:
        raise SystemExit(
            f"Refusing to start non-safe service '{args.service}'. Use --force if you know what you're doing."
        )

    c = connect_client(args.host, args.udid)
    try:
        resp = c.start_service(args.service)
        jdump(resp)
        return 0
    finally:
        c.close()


def cmd_syslog(args: argparse.Namespace) -> int:
    # Delegates to orchard script for streaming behavior.
    import subprocess

    from pathlib import Path
    here = Path(__file__).resolve().parent
    cmd = [sys.executable, str(here / "syslog_stream.py"), args.host]
    if getattr(args, "udid", None):
        cmd += ["--udid", args.udid]
    return subprocess.call(cmd)


def cmd_trace(args: argparse.Namespace) -> int:
    import subprocess

    from pathlib import Path
    here = Path(__file__).resolve().parent
    cmd = [sys.executable, str(here / "os_trace_v2.py"), args.host, "--seconds", str(args.seconds)]
    if getattr(args, "udid", None):
        cmd += ["--udid", args.udid]
    return subprocess.call(cmd)


def cmd_probe(args: argparse.Namespace) -> int:
    import subprocess

    from pathlib import Path
    here = Path(__file__).resolve().parent
    cmd = [sys.executable, str(here / "lockdownd_probe.py"), "--host", args.host, "--bytes", args.bytes]
    if getattr(args, "udid", None):
        cmd += ["--udid", args.udid]
    if getattr(args, "out", None):
        cmd += ["--out", args.out]
    return subprocess.call(cmd)


def cmd_discover(args: argparse.Namespace) -> int:
    import socket
    import struct
    import plistlib

    def query_name(ip: str) -> str | None:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(args.timeout)
            if s.connect_ex((ip, LOCKDOWN_PORT)) != 0:
                return None

            req = {"Request": "GetValue", "Label": "foxprobe", "Key": "DeviceName"}
            payload = plistlib.dumps(req)
            s.sendall(struct.pack(">I", len(payload)) + payload)

            hdr = s.recv(4)
            if not hdr or len(hdr) < 4:
                return None
            ln = struct.unpack(">I", hdr)[0]
            body = b""
            while len(body) < ln:
                chunk = s.recv(ln - len(body))
                if not chunk:
                    break
                body += chunk
            if len(body) != ln:
                return None
            resp = plistlib.loads(body)
            return resp.get("Value")
        except Exception:
            return None
        finally:
            try:
                s.close()
            except Exception:
                pass

    found: list[dict] = []
    for i in range(args.start, args.end + 1):
        ip = f"{args.prefix}{i}"
        name = query_name(ip)
        if name:
            found.append({"ip": ip, "DeviceName": name})
            if not args.all:
                break

    jdump({"found": found})
    return 0


def cmd_pairings(args: argparse.Namespace) -> int:
    recs = list_pairing_records()
    if not recs:
        print("No pairing records found in C:/ProgramData/Apple/Lockdown")
        return 2
    jdump(recs)
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    # Minimal, human-friendly overview for quick checks.
    c = connect_client(args.host, args.udid)
    try:
        name = c.query(key="DeviceName")
        ver = c.query(key="ProductVersion")
        build = c.query(key="BuildVersion")
        batt = c.query(domain="com.apple.mobile.battery")
        wl = c.query(domain="com.apple.mobile.wireless_lockdown")

        out = {
            "host": args.host,
            "DeviceName": (name or {}).get("Value"),
            "ProductVersion": (ver or {}).get("Value"),
            "BuildVersion": (build or {}).get("Value"),
            "battery": (batt or {}).get("Value"),
            "wireless_lockdown": (wl or {}).get("Value"),
            "note": "If many services EOF/0 bytes, you are hitting the iOS 17+ WiFi wall (RemoteXPC trusted tunnel required).",
        }
        jdump(out)
        return 0
    finally:
        c.close()


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Lockdownd WiFi CLI (Orchard)")
    p.add_argument("--host", help="iOS device IP address")
    p.add_argument("--udid", help="pairing record UDID (optional)")

    sp = p.add_subparsers(dest="cmd", required=True)

    ppairs = sp.add_parser("pairings", help="List local Windows pairing records")
    ppairs.set_defaults(func=cmd_pairings)

    pstat = sp.add_parser("status", help="Quick JSON status (name/version/battery/wireless_lockdown)")
    pstat.add_argument("--host", required=True)
    pstat.add_argument("--udid")
    pstat.set_defaults(func=cmd_status)

    pp = sp.add_parser("ping", help="TCP connect test to 62078")
    pp.add_argument("--host", required=True)
    pp.add_argument("--timeout", type=float, default=1.0)
    pp.set_defaults(func=cmd_ping)

    pg = sp.add_parser("get", help="Lockdown GetValue")
    pg.add_argument("--host", required=True)
    pg.add_argument("--domain", help="Lockdown domain")
    pg.add_argument("--key", help="Lockdown key")
    pg.add_argument("--udid")
    pg.set_defaults(func=cmd_get)

    ps = sp.add_parser("start-service", help="StartService (safe allowlist by default)")
    ps.add_argument("--host", required=True)
    ps.add_argument("--service", required=True)
    ps.add_argument("--udid")
    ps.add_argument("--force", action="store_true", help="Allow non-safe services")
    ps.set_defaults(func=cmd_start_service)

    pl = sp.add_parser("syslog", help="Stream syslog via com.apple.syslog_relay")
    pl.add_argument("--host", required=True)
    pl.add_argument("--udid")
    pl.set_defaults(func=cmd_syslog)

    pt = sp.add_parser("trace", help="Stream os_trace for N seconds")
    pt.add_argument("--host", required=True)
    pt.add_argument("--seconds", type=int, default=10)
    pt.add_argument("--udid")
    pt.set_defaults(func=cmd_trace)

    pprobe = sp.add_parser("probe", help="Enumerate domains/services (safe JSON)")
    pprobe.add_argument("--host", required=True)
    pprobe.add_argument("--udid")
    pprobe.add_argument("--bytes", choices=["len", "hex", "b64"], default="len")
    pprobe.add_argument("--out", help="Write JSON to file")
    pprobe.set_defaults(func=cmd_probe)

    pdisc = sp.add_parser("discover", help="Scan a /24 prefix for devices on port 62078")
    pdisc.add_argument("--prefix", default="10.0.0.")
    pdisc.add_argument("--start", type=int, default=2)
    pdisc.add_argument("--end", type=int, default=254)
    pdisc.add_argument("--timeout", type=float, default=0.15)
    pdisc.add_argument("--all", action="store_true", help="Return all matches (default: stop at first)")
    pdisc.set_defaults(func=cmd_discover)

    return p


def main() -> int:
    p = build_parser()
    args = p.parse_args()

    # Safety tripwire: refuse explicit dangerous request names if someone passes them in the future.
    if getattr(args, "request", None) in DANGEROUS_REQUESTS:
        raise SystemExit(f"Refusing dangerous request: {args.request}")

    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
