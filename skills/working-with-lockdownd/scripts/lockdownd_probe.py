#!/usr/bin/env python3
# Lightweight Probe - Discovery & Health Check
# This script performs a quick, non-invasive scan of the device to verify connectivity and service health.
# It checks a small subset of high-signal domains (Battery, Wireless) and services to confirm the device
# is reachable and responding, without dumping sensitive secrets or overwhelming the connection.
"""lockdownd_probe.py

Quick, safe(ish) enumeration of an iOS device via WiFi lockdownd:
- Queries a small set of high-signal domains/keys
- Attempts StartService for a curated service list
- Outputs JSON (no disk writes unless --out is provided)

This is meant for reliability + triage, not full secret dumping.
"""

from __future__ import annotations

import argparse
import json
from typing import Any

from wifi_lockdown import LockdownClient, get_pairing_record


DOMAINS: list[str | None] = [
    None,  # default
    "com.apple.mobile.battery",
    "com.apple.disk_usage",
    "com.apple.disk_usage.factory",
    "com.apple.mobile.wireless_lockdown",
    "com.apple.mobile.debug",
    "com.apple.mobile.internal",
    "com.apple.mobile.restriction",
    "com.apple.international",
    "com.apple.fmip",
]

SERVICES: list[str] = [
    # Known-good over WiFi
    "com.apple.syslog_relay",
    "com.apple.os_trace_relay",
    "com.apple.mobile.heartbeat",
    "com.apple.mobile.notification_proxy",
    "com.apple.mobile.insecure_notification_proxy",
    "com.apple.mobile.diagnostics_relay",
    "com.apple.iosdiagnostics.relay",
    "com.apple.webinspector",

    # Commonly blocked by WiFi wall (still useful to confirm)
    "com.apple.afc",
    "com.apple.mobile.installation_proxy",
    "com.apple.debugserver",
    "com.apple.screenshot",
    "com.apple.instruments.remoteserver",
    "com.apple.mobile.house_arrest",
    "com.apple.mobilesync",
    "com.apple.mobilebackup2",
    "com.apple.mobile.file_relay",
    "com.apple.mobile.MCInstall",
    "com.apple.mobile.mobile_image_mounter",
    "com.apple.amfi.lockdown",
]


def redact(v: Any, *, bytes_mode: str = "len", depth: int = 0) -> Any:
    if depth > 12:
        return "<max depth>"
    if isinstance(v, bytes):
        if bytes_mode == "hex":
            return v.hex()
        if bytes_mode == "b64":
            import base64

            return base64.b64encode(v).decode("ascii")
        return f"<{len(v)} bytes>"
    if isinstance(v, dict):
        return {k: redact(val, bytes_mode=bytes_mode, depth=depth + 1) for k, val in v.items()}
    if isinstance(v, list):
        return [redact(x, bytes_mode=bytes_mode, depth=depth + 1) for x in v]
    return v


def main() -> int:
    ap = argparse.ArgumentParser(description="Safe lockdownd probe (Orchard)")
    ap.add_argument("--host", required=True, help="iOS device IP")
    ap.add_argument("--udid", help="pairing record UDID (optional)")
    ap.add_argument(
        "--bytes",
        choices=["len", "hex", "b64"],
        default="len",
        help="How to represent bytes in output (default: len)",
    )
    ap.add_argument("--out", help="Write JSON output to this file path (optional)")
    args = ap.parse_args()

    pairing = get_pairing_record(args.udid) if args.udid else None
    c = LockdownClient(args.host, pairing=pairing)

    out: dict[str, Any] = {"host": args.host, "domains": {}, "services": {}}

    try:
        c.connect()
        sess = c.start_session()
        out["session"] = redact(sess, bytes_mode=args.bytes)

        if isinstance(sess, dict) and sess.get("EnableSessionSSL"):
            c.start_ssl()

        # Domains
        for d in DOMAINS:
            try:
                resp = c.query(domain=d)
                key = d or "default"
                out["domains"][key] = redact(resp, bytes_mode=args.bytes)
            except Exception as e:
                out["domains"][d or "default"] = {"error": str(e)}

        # Services
        for s in SERVICES:
            try:
                resp = c.start_service(s)
                out["services"][s] = redact(resp, bytes_mode=args.bytes)
            except Exception as e:
                out["services"][s] = {"error": str(e)}

    finally:
        c.close()

    text = json.dumps(out, indent=2, ensure_ascii=False)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
    else:
        print(text)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
