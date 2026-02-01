#!/usr/bin/env python3
"""Meshy API helper.

Environment:
- MESHY_API_KEY (required)
- MESHY_BASE_URL (optional) default: https://api.meshy.ai

Implements:
- create_task(path, payload)
- get_task(path_with_id)
- poll_task(get_path, *, timeout_s, interval_s)
- download(url, out_path)

API docs: https://docs.meshy.ai/en
"""

from __future__ import annotations

import base64
import json
import os
import time
import urllib.error
import urllib.request
from typing import Any, Dict, Optional

DEFAULT_BASE_URL = "https://api.meshy.ai"


class MeshyError(RuntimeError):
    pass


def _get_env(name: str) -> str:
    v = os.environ.get(name, "").strip()
    if not v:
        raise MeshyError(f"Missing env var: {name}")
    return v


def _headers_json() -> Dict[str, str]:
    api_key = _get_env("MESHY_API_KEY")
    return {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


def _base_url() -> str:
    return os.environ.get("MESHY_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def _request(method: str, path: str, *, body: Optional[dict] = None) -> Any:
    url = f"{_base_url()}{path}"
    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, method=method, headers=_headers_json(), data=data)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read()
            if not raw:
                return None
            # Meshy returns JSON for API endpoints.
            return json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise MeshyError(f"HTTP {e.code} calling {method} {path}: {raw}") from e
    except urllib.error.URLError as e:
        raise MeshyError(f"Network error calling {method} {path}: {e}") from e


def create_task(path: str, payload: dict) -> str:
    """POST and return task id (response.result)."""
    data = _request("POST", path, body=payload)
    if not isinstance(data, dict) or "result" not in data:
        raise MeshyError(f"Unexpected create response: {data!r}")
    return str(data["result"])


def get_task(path: str) -> dict:
    data = _request("GET", path)
    if not isinstance(data, dict):
        raise MeshyError(f"Unexpected task response: {data!r}")
    return data


def poll_task(get_path: str, *, timeout_s: int = 900, interval_s: float = 3.0) -> dict:
    """Poll until status is SUCCEEDED/FAILED/CANCELED or timeout."""
    deadline = time.time() + timeout_s
    last = None
    while time.time() < deadline:
        last = get_task(get_path)
        status = str(last.get("status", "")).upper()
        if status in {"SUCCEEDED", "FAILED", "CANCELED"}:
            return last
        time.sleep(interval_s)
    raise MeshyError(f"Timed out after {timeout_s}s polling {get_path}. Last: {last}")


def download(url: str, out_path: str) -> None:
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    req = urllib.request.Request(url, method="GET")
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = resp.read()
        with open(out_path, "wb") as f:
            f.write(data)
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace")
        raise MeshyError(f"HTTP {e.code} downloading {url}: {raw}") from e


def file_to_data_uri(path: str) -> str:
    """Convert a local .png/.jpg/.jpeg file to a data: URI for Meshy inputs."""
    ext = os.path.splitext(path)[1].lower()
    if ext not in {".png", ".jpg", ".jpeg"}:
        raise MeshyError("Only .png/.jpg/.jpeg supported for data URI upload")
    mime = "image/png" if ext == ".png" else "image/jpeg"
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("ascii")
    return f"data:{mime};base64,{b64}"
