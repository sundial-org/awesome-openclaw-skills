#!/usr/bin/env python3
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path
from shutil import which
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

DEFAULT_DISPLAY_NAME = "smartthings-clawdbot"
DEFAULT_APP_NAME = "smartthings-clawdbot"
DEFAULT_DESCRIPTION = "Clawdbot SmartThings integration"
DEFAULT_REDIRECT_URI = "https://httpbin.org/get"
DEFAULT_SCOPES = ["r:devices:*", "x:devices:*"]
DEFAULT_AUTH_BASE = "https://api.smartthings.com/oauth"

ENV_KEYS = {
    "SMARTTHINGS_APP_ID": "appId",
    "SMARTTHINGS_CLIENT_ID": "clientId",
    "SMARTTHINGS_CLIENT_SECRET": "clientSecret",
}

TOKEN_ENV_KEYS = {
    "SMARTTHINGS_ACCESS_TOKEN": "access_token",
    "SMARTTHINGS_REFRESH_TOKEN": "refresh_token",
    "SMARTTHINGS_TOKEN_EXPIRES_AT": "expires_at",
}


def resolve_state_dir() -> Path:
    state_dir = os.environ.get("CLAWDBOT_STATE_DIR")
    if state_dir:
        return Path(state_dir).expanduser()
    return Path.home() / ".clawdbot"


def resolve_env_path(state_dir: Path) -> Path:
    return state_dir / ".env"


def resolve_cli() -> list[str]:
    if which("smartthings"):
        return ["smartthings"]
    npx_path = which("npx")
    if npx_path:
        return [npx_path, "-y", "@smartthings/cli"]
    raise RuntimeError("Missing SmartThings CLI. Install node (npx) or smartthings.")


def resolve_pat() -> str | None:
    return os.environ.get("SMARTTHINGS_TOKEN") or os.environ.get("SMARTTHINGS_PAT")


def normalize_auth_base(value: str) -> str:
    base = value.rstrip("/")
    if "/oauth" in base:
        base = base.split("/oauth", 1)[0] + "/oauth"
    else:
        base = base + "/oauth"
    return base


def build_authorize_url(base: str, client_id: str, redirect_uri: str, scopes: str) -> str:
    query = urlencode(
        {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": scopes,
        }
    )
    authorize = base.rstrip("/") + "/authorize"
    parts = urlsplit(authorize)
    return urlunsplit((parts.scheme, parts.netloc, parts.path, query, ""))


def write_payload(payload: dict) -> Path:
    handle, path = tempfile.mkstemp(prefix="smartthings-app-", suffix=".json")
    with os.fdopen(handle, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)
    return Path(path)


def parse_json_output(output: str) -> dict | list | None:
    text = output.strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    start = min((i for i in (text.find("{"), text.find("[")) if i != -1), default=-1)
    if start == -1:
        return None
    end = max(text.rfind("}"), text.rfind("]"))
    if end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start : end + 1])
    except json.JSONDecodeError:
        return None


def run_create(cli: list[str], payload: dict, token: str | None) -> dict:
    payload_path = write_payload(payload)
    try:
        cmd = [*cli, "apps:create", "--input", str(payload_path), "--json"]
        if token:
            cmd.extend(["--token", token])
        result = subprocess.run(
            cmd,
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    finally:
        payload_path.unlink(missing_ok=True)

    if result.returncode != 0:
        raise RuntimeError(
            "SmartThings CLI failed.\n"
            f"Command: {' '.join(cmd)}\n"
            f"stdout: {result.stdout.strip()}\n"
            f"stderr: {result.stderr.strip()}"
        )

    data = parse_json_output(result.stdout)
    if data is None:
        raise RuntimeError(
            "SmartThings CLI did not return JSON.\n"
            f"stdout: {result.stdout.strip()}\n"
            f"stderr: {result.stderr.strip()}"
        )
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected JSON payload: {data}")
    return data


def exchange_auth_code(
    base: str,
    client_id: str,
    client_secret: str,
    redirect_uri: str,
    code: str,
) -> dict:
    token_url = base.rstrip("/") + "/token"
    auth_bytes = f"{client_id}:{client_secret}".encode("utf-8")
    auth_header = base64.b64encode(auth_bytes).decode("ascii")
    body = urlencode(
        {
            "grant_type": "authorization_code",
            "client_id": client_id,
            "redirect_uri": redirect_uri,
            "code": code,
        }
    ).encode("utf-8")
    request = Request(
        token_url,
        data=body,
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Basic {auth_header}",
        },
        method="POST",
    )
    with urlopen(request, timeout=30) as response:
        payload = response.read().decode("utf-8", errors="replace")
    data = parse_json_output(payload)
    if not isinstance(data, dict):
        raise RuntimeError(f"Unexpected token response: {payload}")
    return data


def extract_oauth_fields(payload: dict) -> dict[str, str]:
    oauth = payload.get("oauth") or {}
    candidates = {
        "clientId": oauth.get("clientId") or oauth.get("client_id") or payload.get("clientId"),
        "clientSecret": oauth.get("clientSecret")
        or oauth.get("client_secret")
        or payload.get("clientSecret"),
        "appId": payload.get("appId") or payload.get("id"),
    }
    missing = [key for key, value in candidates.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing OAuth fields from SmartThings response: " + ", ".join(missing)
        )
    return {
        "SMARTTHINGS_APP_ID": str(candidates["appId"]),
        "SMARTTHINGS_CLIENT_ID": str(candidates["clientId"]),
        "SMARTTHINGS_CLIENT_SECRET": str(candidates["clientSecret"]),
    }


def upsert_env(env_path: Path, updates: dict[str, str]) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if env_path.exists():
        existing = env_path.read_text(encoding="utf-8").splitlines()

    updated_lines: list[str] = []
    seen: set[str] = set()
    key_pattern = re.compile(r"^([A-Z0-9_]+)=(.*)$")

    for line in existing:
        match = key_pattern.match(line)
        if match and match.group(1) in updates:
            key = match.group(1)
            updated_lines.append(f"{key}={updates[key]}")
            seen.add(key)
        else:
            updated_lines.append(line)

    for key, value in updates.items():
        if key not in seen:
            updated_lines.append(f"{key}={value}")

    env_path.write_text("\n".join(updated_lines).rstrip() + "\n", encoding="utf-8")
    try:
        os.chmod(env_path, 0o600)
    except PermissionError:
        pass


def build_payload(app_name: str) -> dict:
    return {
        "appName": app_name,
        "displayName": DEFAULT_DISPLAY_NAME,
        "description": DEFAULT_DESCRIPTION,
        "appType": "API_ONLY",
        "oauth": {
            "clientName": DEFAULT_DISPLAY_NAME,
            "scope": DEFAULT_SCOPES,
            "redirectUris": [DEFAULT_REDIRECT_URI],
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Provision a SmartThings OAuth app for Clawdbot."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Recreate credentials even if they already exist in the env file.",
    )
    parser.add_argument(
        "--auth-code",
        help="Authorization code returned to the redirect URI.",
    )
    parser.add_argument(
        "--redirect-uri",
        default=DEFAULT_REDIRECT_URI,
        help=f"Redirect URI for OAuth (default: {DEFAULT_REDIRECT_URI}).",
    )
    parser.add_argument(
        "--auth-base",
        default=DEFAULT_AUTH_BASE,
        help=f"OAuth base URL (default: {DEFAULT_AUTH_BASE}).",
    )
    args = parser.parse_args()

    try:
        cli = resolve_cli()
    except RuntimeError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    state_dir = resolve_state_dir()
    env_path = resolve_env_path(state_dir)
    existing_env = {}
    if env_path.exists():
        for line in env_path.read_text(encoding="utf-8").splitlines():
            if "=" in line and not line.lstrip().startswith("#"):
                key, value = line.split("=", 1)
                existing_env[key.strip()] = value.strip()

    have_app_creds = all(existing_env.get(key) for key in ENV_KEYS.keys())
    have_tokens = all(existing_env.get(key) for key in TOKEN_ENV_KEYS.keys())
    if not args.force and have_app_creds and have_tokens:
        print("SmartThings credentials already present; skipping setup.")
        print(f"Env file: {env_path}")
        print("Use --force to recreate.")
        return 0

    auth_base = normalize_auth_base(args.auth_base)
    redirect_uri = args.redirect_uri
    scopes = existing_env.get("SMARTTHINGS_SCOPES") or " ".join(DEFAULT_SCOPES)

    app_updates: dict[str, str] = {}
    if have_app_creds and not args.force:
        app_updates = {
            key: existing_env.get(key, "")
            for key in ENV_KEYS.keys()
        }
    else:
        token = resolve_pat()
        if not token:
            print("SmartThings CLI login requires a browser.", file=sys.stderr)
            print("Provide a Personal Access Token (PAT) to run headless:", file=sys.stderr)
            print("1) Create a PAT: https://account.smartthings.com/tokens", file=sys.stderr)
            print("2) Export it: export SMARTTHINGS_TOKEN=your-token", file=sys.stderr)
            print("   (or set SMARTTHINGS_PAT)", file=sys.stderr)
            print("3) Re-run this script.", file=sys.stderr)
            return 2

        payload = build_payload(DEFAULT_APP_NAME)
        payload["oauth"]["redirectUris"] = [redirect_uri]
        payload["oauth"]["scope"] = scopes.split()

        try:
            data = run_create(cli, payload, token)
        except RuntimeError as exc:
            err = str(exc)
            if "appName" in err and "already" in err.lower():
                fallback_name = f"{DEFAULT_APP_NAME}-{uuid.uuid4().hex[:8]}"
                payload = build_payload(fallback_name)
                payload["oauth"]["redirectUris"] = [redirect_uri]
                payload["oauth"]["scope"] = scopes.split()
                data = run_create(cli, payload, token)
            else:
                print(f"Error: {exc}", file=sys.stderr)
                return 1

        try:
            app_updates = extract_oauth_fields(data)
        except RuntimeError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

        app_updates["SMARTTHINGS_SCOPES"] = scopes
        upsert_env(env_path, app_updates)

        print("SmartThings OAuth app created.")
        print(f"Display Name: {DEFAULT_DISPLAY_NAME}")
        print(f"Redirect URI: {redirect_uri}")
        print(f"App ID: {app_updates['SMARTTHINGS_APP_ID']}")
        print(f"Saved credentials to: {env_path}")

    client_id = app_updates.get("SMARTTHINGS_CLIENT_ID") or existing_env.get("SMARTTHINGS_CLIENT_ID")
    client_secret = app_updates.get("SMARTTHINGS_CLIENT_SECRET") or existing_env.get("SMARTTHINGS_CLIENT_SECRET")
    if not client_id or not client_secret:
        print("Missing SmartThings client credentials. Re-run with --force.", file=sys.stderr)
        return 1

    if not args.auth_code:
        auth_url = build_authorize_url(auth_base, client_id, redirect_uri, scopes)
        print("Open this URL on your phone and complete SmartThings login:")
        print(auth_url)
        print("")
        print("After login, copy the `code` query param from the redirect URL.")
        print("Then re-run with:")
        print(f"  SMARTTHINGS_TOKEN=... {Path(__file__).name} --auth-code YOUR_CODE")
        return 3

    try:
        token_payload = exchange_auth_code(
            auth_base, client_id, client_secret, redirect_uri, args.auth_code
        )
    except Exception as exc:
        print(f"Error exchanging auth code: {exc}", file=sys.stderr)
        return 1

    updates: dict[str, str] = {}
    if token_payload.get("access_token"):
        updates["SMARTTHINGS_ACCESS_TOKEN"] = str(token_payload["access_token"])
    if token_payload.get("refresh_token"):
        updates["SMARTTHINGS_REFRESH_TOKEN"] = str(token_payload["refresh_token"])
    if token_payload.get("expires_in"):
        try:
            expires_at = int(time.time()) + int(token_payload["expires_in"])
            updates["SMARTTHINGS_TOKEN_EXPIRES_AT"] = str(expires_at)
        except (TypeError, ValueError):
            pass
    if token_payload.get("scope"):
        updates["SMARTTHINGS_TOKEN_SCOPE"] = str(token_payload["scope"])

    if not updates:
        print("Token exchange succeeded but no tokens were returned.", file=sys.stderr)
        return 1

    upsert_env(env_path, updates)

    print("SmartThings OAuth tokens saved.")
    print(f"Env file: {env_path}")
    print("Next: set SMARTTHINGS_DEVICE_ID (use: smartthings devices --json)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
