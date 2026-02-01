#!/usr/bin/env python3
"""List Tesla vehicles and refresh local cache.

State layout (default dir: ~/.clawdbot/tesla-fleet-api):
  - config.json   non-token configuration
  - auth.json     OAuth tokens
  - vehicles.json cached vehicle list

Usage:
  vehicles.py [--dir DIR] [--json]
"""

from __future__ import annotations

import argparse
import json
import ssl
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

from store import default_dir, ensure_migrated, get_auth, get_config, load_env_file, save_auth, save_vehicles, env as _env

FLEET_AUTH_TOKEN_URL = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"


def _form_post(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
    body = urllib.parse.urlencode(fields).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        method="POST",
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
    )
    ctx = ssl.create_default_context()
    with urllib.request.urlopen(req, context=ctx) as resp:
        data = resp.read().decode("utf-8", errors="replace")
        return json.loads(data) if data else {}


def _refresh_access_token(dir_path: str) -> bool:
    auth = get_auth(dir_path)
    refresh_token = auth.get("refresh_token")
    client_id = _env("TESLA_CLIENT_ID")
    if not client_id or not refresh_token:
        return False

    payload = _form_post(
        FLEET_AUTH_TOKEN_URL,
        {
            "grant_type": "refresh_token",
            "client_id": client_id,
            "refresh_token": refresh_token,
        },
    )

    if payload.get("access_token"):
        auth["access_token"] = payload.get("access_token")
    if payload.get("refresh_token"):
        auth["refresh_token"] = payload.get("refresh_token")
    save_auth(dir_path, {k: v for k, v in auth.items() if v is not None})
    return True


def http_json(method: str, url: str, token: str, ca_cert: Optional[str] = None) -> Any:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    req = urllib.request.Request(url=url, method=method, headers=headers)

    ctx = ssl.create_default_context(cafile=ca_cert) if ca_cert else ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace") if hasattr(e, "read") else ""
        raise RuntimeError(f"HTTP {e.code}: {text}")


def main() -> int:
    ap = argparse.ArgumentParser(description="List Tesla vehicles")
    ap.add_argument("--dir", default=default_dir(), help="Config directory (default: ~/.clawdbot/tesla-fleet-api)")
    ap.add_argument("--json", action="store_true", dest="raw_json", help="Output raw JSON")
    args = ap.parse_args()

    load_env_file(args.dir)
    ensure_migrated(args.dir)

    cfg = get_config(args.dir)
    auth = get_auth(args.dir)

    token = auth.get("access_token")
    if not token:
        print("No access token. Run auth.py to authenticate.", file=sys.stderr)
        return 1

    base_url = (cfg.get("base_url") or cfg.get("audience") or "https://fleet-api.prd.eu.vn.cloud.tesla.com").rstrip("/")
    ca_cert = cfg.get("ca_cert")

    try:
        data = http_json("GET", f"{base_url}/api/1/vehicles", token, ca_cert=ca_cert)
    except RuntimeError as e:
        # common case: token expired
        if "401" in str(e) and _refresh_access_token(args.dir):
            auth = get_auth(args.dir)
            token = auth.get("access_token")
            data = http_json("GET", f"{base_url}/api/1/vehicles", token, ca_cert=ca_cert)
        else:
            raise

    if args.raw_json:
        print(json.dumps(data, indent=2))
    else:
        vehicles = data.get("response", [])
        if not vehicles:
            print("(no vehicles)")
        else:
            for v in vehicles:
                name = v.get("display_name") or "Tesla"
                vin = v.get("vin") or "?"
                state = v.get("state") or "unknown"
                print(f"{name} ({vin}) — {state}")

    # refresh cache
    cache = {
        "cached_at": int(time.time()),
        "vehicles": [{"vin": v.get("vin"), "display_name": v.get("display_name")} for v in data.get("response", [])],
    }
    save_vehicles(args.dir, cache)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
