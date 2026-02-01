#!/usr/bin/env python3
"""Tesla Fleet API authentication and configuration.

State layout (default dir: ~/.clawdbot/tesla-fleet-api):
  - .env          provider creds / overrides (TESLA_CLIENT_ID, TESLA_CLIENT_SECRET, ...)
  - config.json   non-token configuration
  - auth.json     OAuth tokens

Usage:
  auth.py config
  auth.py config set --audience ... --redirect-uri ...
  auth.py login
  auth.py refresh
  auth.py register --domain example.com
"""

from __future__ import annotations

import argparse
import json
import secrets
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Dict, Optional

from store import env as _env
from store import ensure_migrated, get_auth, get_config, load_env_file, save_auth, save_config, default_dir

FLEET_AUTH_TOKEN_URL = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"
TESLA_AUTHORIZE_URL = "https://auth.tesla.com/oauth2/v3/authorize"

DEFAULT_AUDIENCE_EU = "https://fleet-api.prd.eu.vn.cloud.tesla.com"
DEFAULT_REDIRECT_URI = "http://localhost:18080/callback"


@dataclass
class TeslaRuntime:
    # Provider creds (prefer .env)
    client_id: Optional[str]
    client_secret: Optional[str]

    # Config
    redirect_uri: str
    audience: str
    base_url: str
    ca_cert: Optional[str]
    domain: Optional[str]

    # Tokens
    access_token: Optional[str]
    refresh_token: Optional[str]


def form_post(url: str, fields: Dict[str, str]) -> Any:
    body = urllib.parse.urlencode(fields).encode("utf-8")
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    req = urllib.request.Request(url=url, method="POST", data=body, headers=headers)
    ctx = ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            payload = text
        raise RuntimeError(f"HTTP {e.code}: {payload}")


def http_json(method: str, url: str, token: str, json_body: Optional[Dict[str, Any]] = None, ca_cert: Optional[str] = None) -> Any:
    headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
    body = None
    if json_body is not None:
        body = json.dumps(json_body).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url=url, method=method, data=body, headers=headers)
    ctx = ssl.create_default_context(cafile=ca_cert) if ca_cert else ssl.create_default_context()

    try:
        with urllib.request.urlopen(req, context=ctx) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        text = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code}: {text}")


def load_runtime(dir_path: str, *, args: argparse.Namespace) -> TeslaRuntime:
    load_env_file(dir_path)
    ensure_migrated(dir_path)

    cfg = get_config(dir_path)
    auth = get_auth(dir_path)

    audience = (args.audience or cfg.get("audience") or _env("TESLA_AUDIENCE") or DEFAULT_AUDIENCE_EU).strip()
    redirect_uri = (args.redirect_uri or cfg.get("redirect_uri") or _env("TESLA_REDIRECT_URI") or DEFAULT_REDIRECT_URI).strip()
    base_url = (args.base_url or cfg.get("base_url") or _env("TESLA_BASE_URL") or audience).strip()

    return TeslaRuntime(
        client_id=args.client_id or _env("TESLA_CLIENT_ID") or cfg.get("client_id"),
        client_secret=args.client_secret or _env("TESLA_CLIENT_SECRET") or cfg.get("client_secret"),
        redirect_uri=redirect_uri,
        audience=audience,
        base_url=base_url,
        ca_cert=args.ca_cert or cfg.get("ca_cert") or _env("TESLA_CA_CERT"),
        domain=args.domain or cfg.get("domain") or _env("TESLA_DOMAIN"),
        access_token=_env("TESLA_ACCESS_TOKEN") or auth.get("access_token"),
        refresh_token=_env("TESLA_REFRESH_TOKEN") or auth.get("refresh_token"),
    )


def cmd_login(rt: TeslaRuntime, dir_path: str) -> int:
    if not rt.client_id:
        print("Missing client_id (set TESLA_CLIENT_ID in ~/.clawdbot/tesla-fleet-api/.env)", file=sys.stderr)
        return 1

    scope = "openid offline_access vehicle_device_data vehicle_cmds vehicle_location"
    state = secrets.token_hex(16)

    params = {
        "response_type": "code",
        "client_id": rt.client_id,
        "redirect_uri": rt.redirect_uri,
        "scope": scope,
        "state": state,
        "locale": "en-US",
        "prompt": "login",
    }

    url = TESLA_AUTHORIZE_URL + "?" + urllib.parse.urlencode(params)

    print("Open this URL to authorize:\n")
    print(url)
    print("\nState:", state)
    print()

    code = input("Paste the 'code' from the callback URL: ").strip()
    if not code:
        print("No code provided.", file=sys.stderr)
        return 1

    return cmd_exchange(rt, dir_path, code)


def cmd_exchange(rt: TeslaRuntime, dir_path: str, code: str) -> int:
    if not rt.client_id or not rt.client_secret:
        print("Missing client_id/client_secret (set TESLA_CLIENT_ID and TESLA_CLIENT_SECRET in .env)", file=sys.stderr)
        return 1

    fields = {
        "grant_type": "authorization_code",
        "client_id": rt.client_id,
        "client_secret": rt.client_secret,
        "code": code,
        "audience": rt.audience,
        "redirect_uri": rt.redirect_uri,
    }

    try:
        payload = form_post(FLEET_AUTH_TOKEN_URL, fields)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    auth = get_auth(dir_path)
    auth["access_token"] = payload.get("access_token")
    auth["refresh_token"] = payload.get("refresh_token")
    save_auth(dir_path, {k: v for k, v in auth.items() if v is not None})

    print("✅ Tokens saved (auth.json)")
    return 0


def cmd_refresh(rt: TeslaRuntime, dir_path: str) -> int:
    if not rt.client_id or not rt.refresh_token:
        print("Missing client_id or refresh_token.", file=sys.stderr)
        return 1

    fields = {
        "grant_type": "refresh_token",
        "client_id": rt.client_id,
        "refresh_token": rt.refresh_token,
    }

    try:
        payload = form_post(FLEET_AUTH_TOKEN_URL, fields)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    auth = get_auth(dir_path)
    auth["access_token"] = payload.get("access_token")
    if payload.get("refresh_token"):
        auth["refresh_token"] = payload.get("refresh_token")
    save_auth(dir_path, {k: v for k, v in auth.items() if v is not None})

    print("✅ Token refreshed")
    return 0


def cmd_register(rt: TeslaRuntime, dir_path: str) -> int:
    if not rt.domain:
        print("Specify --domain or set TESLA_DOMAIN / config.json:domain", file=sys.stderr)
        return 1
    if not rt.client_id or not rt.client_secret:
        print("Missing client_id/client_secret (set in .env)", file=sys.stderr)
        return 1

    # Partner token via client_credentials
    fields = {
        "grant_type": "client_credentials",
        "client_id": rt.client_id,
        "client_secret": rt.client_secret,
        "audience": rt.audience,
    }

    try:
        token_resp = form_post(FLEET_AUTH_TOKEN_URL, fields)
        partner_token = token_resp.get("access_token")
    except RuntimeError as e:
        print(f"Error getting partner token: {e}", file=sys.stderr)
        return 1

    base = rt.base_url.rstrip("/")
    url = f"{base}/api/1/partner_accounts"

    try:
        _ = http_json("POST", url, partner_token, {"domain": rt.domain}, rt.ca_cert)
    except RuntimeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    cfg = get_config(dir_path)
    cfg["domain"] = rt.domain
    save_config(dir_path, cfg)

    print(f"✅ Domain registered: {rt.domain}")
    print("Next step: Enroll your key on the vehicle:")
    print(f"  https://tesla.com/_ak/{rt.domain}")
    return 0


def cmd_config_show(rt: TeslaRuntime, dir_path: str) -> int:
    print(f"📁 Config dir: {dir_path}")
    print(f"   - config.json : {dir_path}/config.json")
    print(f"   - auth.json   : {dir_path}/auth.json")
    print()

    print(f"🔑 Client ID:     {'(from env)' if _env('TESLA_CLIENT_ID') else '(not set)'}")
    print(f"🔒 Client Secret: {'(from env)' if _env('TESLA_CLIENT_SECRET') else '(not set)'}")
    print(f"🔗 Redirect URI:  {rt.redirect_uri}")
    print(f"🌍 Audience:      {rt.audience}")
    print(f"🖥️  Base URL:      {rt.base_url}")
    print(f"📜 CA Cert:       {rt.ca_cert or '(not set)'}")
    print(f"🏠 Domain:        {rt.domain or '(not set)'}")
    print()
    print(f"🎫 Access Token:  {'(set)' if rt.access_token else '(not set)'}")
    print(f"🔄 Refresh Token: {'(set)' if rt.refresh_token else '(not set)'}")
    return 0


def cmd_config_set(args: argparse.Namespace, dir_path: str) -> int:
    load_env_file(dir_path)
    ensure_migrated(dir_path)

    cfg = get_config(dir_path)
    changed = []

    for key, val in (
        ("redirect_uri", args.redirect_uri),
        ("audience", args.audience),
        ("base_url", args.base_url),
        ("ca_cert", args.ca_cert),
        ("domain", args.domain),
    ):
        if val is not None:
            cfg[key] = val
            changed.append(key)

    if args.clear:
        for k in args.clear:
            if k in cfg:
                cfg.pop(k, None)
                changed.append(f"clear:{k}")

    if not changed:
        print("No changes specified.", file=sys.stderr)
        return 1

    save_config(dir_path, cfg)
    print("✅ Updated:", ", ".join(changed))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="auth.py", description="Tesla Fleet API auth/config")
    p.add_argument("--dir", default=default_dir(), help="Config directory (default: ~/.clawdbot/tesla-fleet-api)")

    # optional runtime overrides
    p.add_argument("--client-id")
    p.add_argument("--client-secret")
    p.add_argument("--redirect-uri")
    p.add_argument("--audience")
    p.add_argument("--base-url")
    p.add_argument("--ca-cert")
    p.add_argument("--domain")

    sp = p.add_subparsers(dest="command", required=True)

    sp.add_parser("login", help="OAuth login flow (interactive)")

    p_ex = sp.add_parser("exchange", help="Exchange auth code for tokens")
    p_ex.add_argument("code", help="Authorization code")

    sp.add_parser("refresh", help="Refresh access token")

    p_reg = sp.add_parser("register", help="Register app domain")
    p_reg.add_argument("--domain")

    p_cfg = sp.add_parser("config", help="Show or set config")
    cfg_sp = p_cfg.add_subparsers(dest="config_action")

    cfg_sp.add_parser("show", help="Show config")

    p_set = cfg_sp.add_parser("set", help="Set config values")
    p_set.add_argument("--redirect-uri")
    p_set.add_argument("--audience")
    p_set.add_argument("--base-url")
    p_set.add_argument("--ca-cert")
    p_set.add_argument("--domain")
    p_set.add_argument("--clear", action="append", help="Remove a key from config.json (repeatable)")

    return p


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "config" and args.config_action == "set":
        return cmd_config_set(args, args.dir)

    rt = load_runtime(args.dir, args=args)

    if args.command == "login":
        return cmd_login(rt, args.dir)
    if args.command == "exchange":
        return cmd_exchange(rt, args.dir, args.code)
    if args.command == "refresh":
        return cmd_refresh(rt, args.dir)
    if args.command == "register":
        # domain can come from args --domain for this command, override runtime
        if args.domain:
            rt.domain = args.domain
        return cmd_register(rt, args.dir)
    if args.command == "config":
        return cmd_config_show(rt, args.dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
