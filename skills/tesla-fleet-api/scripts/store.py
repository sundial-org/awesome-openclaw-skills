#!/usr/bin/env python3
"""Shared storage helpers for the Tesla Fleet API skill.

We keep state in the user's home dir (outside the skill folder):
  ~/.clawdbot/tesla-fleet-api/

Files:
  - .env          (provider creds + overrides)
  - config.json   (non-token configuration)
  - auth.json     (OAuth tokens)
  - vehicles.json (cached vehicle list)
  - places.json   (named lat/lon places)

We also support a legacy single-file layout:
  - tesla-fleet.json

This module is stdlib-only and safe to import from any of the scripts.
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional


def default_dir() -> str:
    return os.path.expanduser("~/.clawdbot/tesla-fleet-api")


def env_path(dir_path: str) -> str:
    return os.path.join(dir_path, ".env")


def config_path(dir_path: str) -> str:
    return os.path.join(dir_path, "config.json")


def auth_path(dir_path: str) -> str:
    return os.path.join(dir_path, "auth.json")


def vehicles_path(dir_path: str) -> str:
    return os.path.join(dir_path, "vehicles.json")


def places_path(dir_path: str) -> str:
    return os.path.join(dir_path, "places.json")


def legacy_path(dir_path: str) -> str:
    return os.path.join(dir_path, "tesla-fleet.json")


def _mkdirp(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def load_env_file(dir_path: str) -> None:
    """Load KEY=VALUE pairs from ~/.clawdbot/tesla-fleet-api/.env into os.environ.

    - comments (# ...) and blank lines ignored
    - surrounding single/double quotes stripped
    - existing env vars are NOT overwritten
    """

    p = env_path(dir_path)
    if not os.path.exists(p):
        return

    try:
        with open(p, "r", encoding="utf-8") as f:
            for line in f.read().splitlines():
                s = line.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                k = k.strip()
                v = v.strip().strip('"\'')
                if k and k not in os.environ:
                    os.environ[k] = v
    except Exception:
        # Don't hard-fail on env loading.
        return


def read_json(path: str) -> Dict[str, Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def write_json_private(path: str, obj: Dict[str, Any]) -> None:
    parent = os.path.dirname(path)
    if parent:
        _mkdirp(parent)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)
        f.write("\n")
    try:
        os.chmod(tmp, 0o600)
    except Exception:
        pass
    os.replace(tmp, path)


def ensure_migrated(dir_path: str) -> None:
    """If legacy tesla-fleet.json exists, split it into the new multi-file layout.

    This is best-effort and non-destructive:
    - creates missing new files
    - does NOT delete legacy file
    """

    legacy = legacy_path(dir_path)
    if not os.path.exists(legacy):
        return

    cfg_p = config_path(dir_path)
    auth_p = auth_path(dir_path)
    veh_p = vehicles_path(dir_path)
    plc_p = places_path(dir_path)

    raw = read_json(legacy)

    if not os.path.exists(cfg_p):
        cfg: Dict[str, Any] = {}
        for k in ("audience", "base_url", "ca_cert", "redirect_uri", "domain"):
            if raw.get(k) is not None:
                cfg[k] = raw.get(k)
        write_json_private(cfg_p, cfg)

    if not os.path.exists(auth_p):
        auth: Dict[str, Any] = {}
        for k in ("access_token", "refresh_token", "partner_access_token", "partner_refresh_token"):
            if raw.get(k) is not None:
                auth[k] = raw.get(k)
        write_json_private(auth_p, auth)

    if not os.path.exists(veh_p):
        if raw.get("vehicles_cache") is not None:
            # store vehicles cache directly in vehicles.json
            write_json_private(veh_p, raw.get("vehicles_cache"))

    if not os.path.exists(plc_p):
        home_lat = raw.get("home_lat")
        home_lon = raw.get("home_lon")
        if home_lat is not None and home_lon is not None:
            # store places as a name -> {lat, lon} mapping
            places = {"home": {"lat": float(home_lat), "lon": float(home_lon)}}
            write_json_private(plc_p, places)


def get_config(dir_path: str) -> Dict[str, Any]:
    return read_json(config_path(dir_path))


def save_config(dir_path: str, cfg: Dict[str, Any]) -> None:
    write_json_private(config_path(dir_path), cfg)


def get_auth(dir_path: str) -> Dict[str, Any]:
    return read_json(auth_path(dir_path))


def save_auth(dir_path: str, auth: Dict[str, Any]) -> None:
    write_json_private(auth_path(dir_path), auth)


def get_vehicles(dir_path: str) -> Dict[str, Any]:
    return read_json(vehicles_path(dir_path))


def save_vehicles(dir_path: str, data: Dict[str, Any]) -> None:
    write_json_private(vehicles_path(dir_path), data)


def get_places(dir_path: str) -> Dict[str, Any]:
    return read_json(places_path(dir_path))


def save_places(dir_path: str, data: Dict[str, Any]) -> None:
    write_json_private(places_path(dir_path), data)


def env(name: str) -> Optional[str]:
    v = os.environ.get(name)
    return v if v not in (None, "") else None
