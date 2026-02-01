#!/usr/bin/env python3
"""Tesla Fleet API OAuth helper that runs a local callback server.

Stdlib-only.

State layout (default dir: ~/.clawdbot/tesla-fleet-api):
  - .env          provider creds / overrides (TESLA_CLIENT_ID, TESLA_CLIENT_SECRET, ...)
  - config.json   non-token configuration
  - auth.json     OAuth tokens

Typical flow:
  1) put TESLA_CLIENT_ID / TESLA_CLIENT_SECRET into ~/.clawdbot/tesla-fleet-api/.env
  2) run this script; it prints an /authorize URL
  3) approve in browser; Tesla redirects to http://localhost:18080/callback?code=...
  4) the script exchanges the code for tokens and saves them to auth.json

Security:
- Writes auth.json with mode 600.
- Avoid pasting secrets into chat; prefer local .env.
"""

from __future__ import annotations

import argparse
import json
import secrets
import ssl
import sys
import time
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict, Optional, Tuple

from store import (
    default_dir,
    ensure_migrated,
    env as _env,
    get_auth,
    get_config,
    load_env_file,
    save_auth,
    save_config,
)

TESLA_AUTHORIZE_URL = "https://auth.tesla.com/oauth2/v3/authorize"
FLEET_AUTH_TOKEN_URL = "https://fleet-auth.prd.vn.cloud.tesla.com/oauth2/v3/token"

DEFAULT_AUDIENCE_EU = "https://fleet-api.prd.eu.vn.cloud.tesla.com"
DEFAULT_REDIRECT_URI = "http://localhost:18080/callback"


def form_post(url: str, fields: Dict[str, str]) -> Dict[str, Any]:
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


def parse_redirect_uri(uri: str) -> Tuple[str, int, str]:
    p = urllib.parse.urlparse(uri)
    if p.scheme not in ("http", "https"):
        raise ValueError("redirect_uri must be http(s)")
    host = p.hostname or "localhost"
    port = p.port
    if port is None:
        port = 443 if p.scheme == "https" else 80
    path = p.path or "/"
    return host, port, path


def build_authorize_url(*, client_id: str, redirect_uri: str, scope: str, state: str, locale: str, prompt_missing_scopes: bool = False) -> str:
    q = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
        "locale": locale,
        "prompt": "login",
    }
    if prompt_missing_scopes:
        q["prompt_missing_scopes"] = "true"
    return TESLA_AUTHORIZE_URL + "?" + urllib.parse.urlencode(q)


class _CallbackHandler(BaseHTTPRequestHandler):
    server_version = "tesla-oauth-local/1.0"

    def do_GET(self) -> None:  # noqa: N802
        parsed = urllib.parse.urlparse(self.path)
        qs = urllib.parse.parse_qs(parsed.query)

        self.server._last_path = parsed.path  # type: ignore[attr-defined]
        self.server._last_qs = qs  # type: ignore[attr-defined]

        code = (qs.get("code") or [None])[0]
        err = (qs.get("error") or [None])[0]

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()

        if err:
            self.wfile.write(f"OAuth error: {err}\n".encode("utf-8"))
        elif code:
            self.wfile.write(b"OK. You can close this tab.\n")
        else:
            self.wfile.write(b"No code received.\n")

        self.server._done = True  # type: ignore[attr-defined]

    def log_message(self, fmt: str, *args: Any) -> None:
        return


def run_callback_server(host: str, port: int, expect_path: str, timeout_s: int) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    httpd = HTTPServer((host, port), _CallbackHandler)
    httpd._done = False  # type: ignore[attr-defined]
    httpd._last_path = None  # type: ignore[attr-defined]
    httpd._last_qs = None  # type: ignore[attr-defined]

    started = time.time()
    while True:
        httpd.handle_request()
        if getattr(httpd, "_done", False):
            qs = getattr(httpd, "_last_qs", {}) or {}
            path = getattr(httpd, "_last_path", "") or ""
            code = (qs.get("code") or [None])[0]
            state = (qs.get("state") or [None])[0]
            err = (qs.get("error") or [None])[0]
            if expect_path and path != expect_path:
                print(f"Warning: callback path was {path}, expected {expect_path}", file=sys.stderr)
            return code, state, err

        if time.time() - started > timeout_s:
            return None, None, "timeout"


def main() -> int:
    ap = argparse.ArgumentParser(description="Tesla OAuth local callback helper")
    ap.add_argument("--dir", default=default_dir(), help="Config directory (default: ~/.clawdbot/tesla-fleet-api)")

    ap.add_argument("--client-id", help="Tesla app client_id")
    ap.add_argument("--client-secret", help="Tesla app client_secret")
    ap.add_argument("--redirect-uri", default=None)
    ap.add_argument("--audience", default=None)
    ap.add_argument("--scope", default=None)
    ap.add_argument("--locale", default="en-US")

    ap.add_argument("--timeout", type=int, default=300, help="Seconds to wait for callback")
    ap.add_argument("--no-exchange", action="store_true", help="Only capture code; do not exchange for tokens")
    ap.add_argument("--prompt-missing-scopes", action="store_true", help="Prompt user to grant any missing scopes")

    args = ap.parse_args()

    load_env_file(args.dir)
    ensure_migrated(args.dir)

    cfg = get_config(args.dir)

    client_id = args.client_id or _env("TESLA_CLIENT_ID") or cfg.get("client_id")
    client_secret = args.client_secret or _env("TESLA_CLIENT_SECRET") or cfg.get("client_secret")

    redirect_uri = args.redirect_uri or cfg.get("redirect_uri") or _env("TESLA_REDIRECT_URI") or DEFAULT_REDIRECT_URI
    audience = args.audience or cfg.get("audience") or _env("TESLA_AUDIENCE") or DEFAULT_AUDIENCE_EU
    scope = args.scope or _env("TESLA_SCOPE") or cfg.get("scope") or "openid offline_access vehicle_device_data vehicle_cmds vehicle_location"

    if not client_id:
        print("Missing client_id (set TESLA_CLIENT_ID in .env or pass --client-id)", file=sys.stderr)
        return 2
    if not args.no_exchange and not client_secret:
        print("Missing client_secret (set TESLA_CLIENT_SECRET in .env or pass --client-secret), or use --no-exchange.", file=sys.stderr)
        return 2

    # Persist non-sensitive defaults.
    cfg["redirect_uri"] = redirect_uri
    cfg["audience"] = audience
    cfg["scope"] = scope
    save_config(args.dir, cfg)

    state = secrets.token_hex(16)
    url = build_authorize_url(
        client_id=client_id,
        redirect_uri=redirect_uri,
        scope=scope,
        state=state,
        locale=args.locale,
        prompt_missing_scopes=args.prompt_missing_scopes,
    )

    host, port, path = parse_redirect_uri(redirect_uri)

    print("Open this URL in your browser:")
    print(url)
    print("\nWaiting for redirect on:")
    print(f"  {host}:{port}{path}")

    code, got_state, err = run_callback_server(host, port, path, args.timeout)

    if err and err != "timeout":
        print(f"OAuth error: {err}", file=sys.stderr)
        return 3
    if err == "timeout":
        print("Timed out waiting for callback.", file=sys.stderr)
        return 4
    if not code:
        print("No code received.", file=sys.stderr)
        return 5
    if got_state != state:
        print("State mismatch (possible CSRF / wrong browser session). Aborting.", file=sys.stderr)
        return 6

    print("\nReceived authorization code.")

    if args.no_exchange:
        print(f"code={code}")
        return 0

    payload = form_post(
        FLEET_AUTH_TOKEN_URL,
        {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "audience": audience,
            "redirect_uri": redirect_uri,
        },
    )

    auth = get_auth(args.dir)
    auth["access_token"] = payload.get("access_token")
    if payload.get("refresh_token"):
        auth["refresh_token"] = payload.get("refresh_token")
    save_auth(args.dir, {k: v for k, v in auth.items() if v is not None})

    print("✅ Tokens saved (auth.json)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
