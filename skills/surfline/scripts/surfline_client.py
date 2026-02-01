#!/usr/bin/env python3
"""Minimal Surfline public client (no login).

We intentionally avoid private/account endpoints and avoid non-stdlib deps.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional

BASE = "https://services.surfline.com"

CACHE_DIR = Path(os.environ.get("SURFLINE_CACHE_DIR", str(Path.home() / ".cache" / "surfline")))
CACHE_TTL_SEC = int(os.environ.get("SURFLINE_CACHE_TTL_SEC", "600"))


class SurflineError(RuntimeError):
    pass


def _http_get_json(url: str, timeout: int = 20) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "clawdbot-surfline-skill/0.1"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        data = resp.read().decode("utf-8", errors="replace")
    try:
        return json.loads(data)
    except Exception as e:
        raise SurflineError(f"Failed to parse JSON from {url}: {e}")


def _cache_path(key: str) -> Path:
    safe = "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in key)
    return CACHE_DIR / f"{safe}.json"


def get_json_cached(url: str, cache_key: str, ttl_sec: int = CACHE_TTL_SEC) -> Any:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    p = _cache_path(cache_key)
    if p.exists():
        age = time.time() - p.stat().st_mtime
        if age < ttl_sec:
            return json.loads(p.read_text("utf-8"))
    data = _http_get_json(url)
    p.write_text(json.dumps(data), encoding="utf-8")
    return data


@dataclass
class SearchHit:
    spot_id: str
    name: str
    url: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


def search_spots(query: str, limit: int = 8) -> list[SearchHit]:
    """Search Surfline for spot IDs.

    Surfline's `/search/site` often returns a **list** of result buckets (multiple
    indices). Each element contains `hits.hits[]. _source`.

    We keep this defensive because Surfline changes this payload periodically.
    """

    q = urllib.parse.quote(query)
    url = f"{BASE}/search/site?q={q}"
    data = get_json_cached(url, cache_key=f"search_{q}")

    hits: list[SearchHit] = []

    buckets = data if isinstance(data, list) else [data]

    for bucket in buckets:
        if not isinstance(bucket, dict):
            continue
        raw_hits = (((bucket.get("hits") or {}).get("hits")) or [])
        for item in raw_hits:
            src: Dict[str, Any] = item.get("_source") or {}
            # Spot documents usually come from the "spots" index and have _type "spot".
            # Some payloads also include src.type.
            if src.get("type") not in (None, "spot"):
                continue
            spot_id = src.get("spotId") or src.get("id") or item.get("_id")
            name = src.get("name") or "(unknown)"
            if not spot_id:
                continue
            loc = src.get("location") or {}
            hits.append(
                SearchHit(
                    spot_id=str(spot_id),
                    name=str(name),
                    url=src.get("href") or src.get("url"),
                    latitude=loc.get("lat"),
                    longitude=loc.get("lon"),
                )
            )
            if len(hits) >= limit:
                return hits

    return hits


def kbyg_spot(spot_id: str) -> Dict[str, Any]:
    # Some kbyg endpoints accept spotId as query param (more consistent).
    params = urllib.parse.urlencode({"spotId": spot_id})
    url = f"{BASE}/kbyg/spots/forecasts/spot?{params}"
    return get_json_cached(url, cache_key=f"spot_{spot_id}")


def kbyg_conditions(spot_id: str) -> Dict[str, Any]:
    params = urllib.parse.urlencode({"spotId": spot_id})
    url = f"{BASE}/kbyg/spots/forecasts/conditions?{params}"
    return get_json_cached(url, cache_key=f"conditions_{spot_id}")


def kbyg_wave(spot_id: str, days: int = 2, interval_hours: int = 1) -> Dict[str, Any]:
    params = urllib.parse.urlencode({"spotId": spot_id, "days": str(days), "intervalHours": str(interval_hours)})
    url = f"{BASE}/kbyg/spots/forecasts/wave?{params}"
    return get_json_cached(url, cache_key=f"wave_{spot_id}_{days}_{interval_hours}")


def kbyg_wind(spot_id: str, days: int = 2, interval_hours: int = 1) -> Dict[str, Any]:
    params = urllib.parse.urlencode({"spotId": spot_id, "days": str(days), "intervalHours": str(interval_hours)})
    url = f"{BASE}/kbyg/spots/forecasts/wind?{params}"
    return get_json_cached(url, cache_key=f"wind_{spot_id}_{days}_{interval_hours}")


def kbyg_tides(spot_id: str, days: int = 2) -> Dict[str, Any]:
    params = urllib.parse.urlencode({"spotId": spot_id, "days": str(days)})
    url = f"{BASE}/kbyg/spots/forecasts/tides?{params}"
    return get_json_cached(url, cache_key=f"tides_{spot_id}_{days}")
