#!/usr/bin/env python3
"""Miniflux API helper.

Reads credentials from (in order):
1) Environment variables (override):
   - MINIFLUX_URL   e.g. https://reader.example.com
   - MINIFLUX_TOKEN your Miniflux API token
2) Config file (recommended):
   - ~/.config/clawdbot/miniflux-news.json  (keys: url, token)

Usage examples:
  python3 miniflux.py entries --limit 20
  python3 miniflux.py entries --limit 20 --json
  python3 miniflux.py categories
  python3 miniflux.py entries --category "Tech" --limit 20
  python3 miniflux.py entry 123
  python3 miniflux.py entry 123 --full --format text
  python3 miniflux.py entry 123 --full --format html
  python3 miniflux.py entry 123 --json
  python3 miniflux.py mark-read 123 124 --confirm
  python3 miniflux.py mark-read-category "Tech" --confirm

Notes:
- Uses only the Python standard library.
- Prints human-readable text by default; pass --json for machine-readable output.
"""

from __future__ import annotations

import argparse
import json
import os
import stat
import sys
import textwrap
import urllib.parse
import urllib.request
from html.parser import HTMLParser


def _config_path() -> str:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = xdg if xdg else os.path.join(os.path.expanduser("~"), ".config")
    return os.path.join(base, "clawdbot", "miniflux-news.json")


def _read_config() -> dict:
    path = _config_path()
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        raise SystemExit(f"Failed to read config at {path}: {e}")


def _require(name: str, env: str, cfg_key: str) -> str:
    v = os.environ.get(env)
    if v:
        return v
    cfg = _read_config()
    v = cfg.get(cfg_key)
    if v:
        return str(v)
    raise SystemExit(
        f"Missing {env} (or config value '{cfg_key}').\n\n"
        f"Set env vars:\n  export {env}=...\n\n"
        f"Or create config:\n  python3 miniflux.py configure --url ... --token ...\n"
        f"Config path: {_config_path()}\n"
    )


def _request(path: str, query: dict | None = None, *, method: str = "GET", body: dict | None = None):
    base = _require("MINIFLUX_URL", "MINIFLUX_URL", "url").rstrip("/")
    token = _require("MINIFLUX_TOKEN", "MINIFLUX_TOKEN", "token").strip()

    url = base + path
    if query:
        url = url + "?" + urllib.parse.urlencode({k: v for k, v in query.items() if v is not None})

    data_bytes = None
    if body is not None:
        data_bytes = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(url, data=data_bytes, method=method)
    req.add_header("X-Auth-Token", token)
    req.add_header("Accept", "application/json")
    if data_bytes is not None:
        req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace")
        raise SystemExit(f"HTTP {e.code} for {url}\n{err_body}")

    if not data:
        return {}

    try:
        return json.loads(data.decode("utf-8"))
    except Exception:
        raise SystemExit(f"Failed to parse JSON from {url}")


def _categories() -> list[dict]:
    data = _request("/v1/categories")
    if isinstance(data, list):
        return data
    return []


def _category_id_from_name(name: str) -> int:
    needle = name.strip().casefold()
    for c in _categories():
        title = (c.get("title") or "").strip().casefold()
        if title == needle:
            return int(c.get("id"))
    known = ", ".join((c.get("title") or "").strip() for c in _categories())
    raise SystemExit(f"Unknown category: {name}. Known: {known}")


def cmd_categories(args: argparse.Namespace) -> int:
    cats = _categories()
    if args.json:
        print(json.dumps(cats, ensure_ascii=False, indent=2))
        return 0
    if not cats:
        print("No categories.")
        return 0
    for c in cats:
        print(f"[{c.get('id')}] {(c.get('title') or '').strip()}")
    return 0


def cmd_entries(args: argparse.Namespace) -> int:
    # Miniflux supports /v1/entries with many filters.
    query = {
        "status": args.status,
        "limit": args.limit,
        "order": args.order,
        "direction": args.direction,
    }

    if args.category_id is not None:
        query["category_id"] = args.category_id
    elif args.category is not None:
        query["category_id"] = _category_id_from_name(args.category)

    data = _request("/v1/entries", query=query)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    entries = data.get("entries", []) if isinstance(data, dict) else []
    if not entries:
        print("No entries.")
        return 0

    for e in entries:
        eid = e.get("id")
        title = (e.get("title") or "").strip() or "(untitled)"
        url = (e.get("url") or "").strip()
        feed = (e.get("feed", {}) or {}).get("title")
        published = e.get("published_at") or e.get("created_at")

        line = f"[{eid}] {title}"
        if feed:
            line += f" — {feed}"
        if published:
            line += f" ({published})"
        print(line)
        if url:
            print(f"  {url}")

    return 0


class _HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self._parts: list[str] = []

    def handle_data(self, data: str) -> None:
        if data:
            self._parts.append(data)

    def text(self) -> str:
        return "".join(self._parts)


def _html_to_text(html: str) -> str:
    s = _HTMLStripper()
    s.feed(html)
    return s.text()


def cmd_entry(args: argparse.Namespace) -> int:
    data = _request(f"/v1/entries/{args.id}")

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return 0

    title = (data.get("title") or "").strip() or "(untitled)"
    url = (data.get("url") or "").strip()
    raw = (data.get("content") or data.get("content_text") or "").strip()

    print(f"[{data.get('id')}] {title}")
    if url:
        print(url)

    if not raw:
        return 0

    # Miniflux usually stores HTML in `content`.
    if args.format == "html":
        body = raw
    else:
        body = _html_to_text(raw)

    if args.full:
        print("\n" + body.strip() + "\n")
        return 0

    # Default: short preview so humans don't get flooded.
    preview = textwrap.shorten(" ".join(body.split()), width=600, placeholder=" …")
    print("\n" + preview)
    return 0


def _mark_read(ids: list[int]) -> None:
    payload = {"entry_ids": ids, "status": "read"}
    _request("/v1/entries", method="PUT", body=payload)


def cmd_mark_read(args: argparse.Namespace) -> int:
    if not args.confirm:
        ids = " ".join(str(i) for i in args.ids)
        raise SystemExit(
            "Refusing to mark entries as read without --confirm.\n"
            f"Would mark as read: {ids}\n"
        )

    _mark_read(args.ids)

    for i in args.ids:
        print(f"✓ marked read: {i}")
    return 0


def _fetch_unread_ids_by_category(category_id: int, *, limit: int) -> list[int]:
    # Simple paging via offset. Stop when we hit limit or no more entries.
    ids: list[int] = []
    offset = 0
    page = 100
    while len(ids) < limit:
        data = _request(
            "/v1/entries",
            query={
                "status": "unread",
                "category_id": category_id,
                "limit": min(page, limit - len(ids)),
                "offset": offset,
                "order": "published_at",
                "direction": "desc",
            },
        )
        entries = data.get("entries", []) if isinstance(data, dict) else []
        if not entries:
            break
        for e in entries:
            if e.get("id") is not None:
                ids.append(int(e["id"]))
        offset += len(entries)
        if len(entries) == 0:
            break
    return ids


def cmd_mark_read_category(args: argparse.Namespace) -> int:
    if not args.confirm:
        raise SystemExit("Refusing to mark a whole category read without --confirm.")

    cid = args.category_id if args.category_id is not None else _category_id_from_name(args.category)
    ids = _fetch_unread_ids_by_category(cid, limit=args.limit)
    if not ids:
        print("No unread entries in category.")
        return 0

    _mark_read(ids)
    print(f"✓ marked read: {len(ids)} entries (category_id={cid})")
    return 0


def cmd_configure(args: argparse.Namespace) -> int:
    path = _config_path()
    os.makedirs(os.path.dirname(path), exist_ok=True)

    cfg = _read_config() if os.path.exists(path) else {}
    if args.url:
        cfg["url"] = args.url
    if args.token:
        cfg["token"] = args.token

    if not cfg.get("url") or not cfg.get("token"):
        raise SystemExit("Both --url and --token are required (at least once).")

    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # Best-effort restrictive perms.
    try:
        os.chmod(tmp, stat.S_IRUSR | stat.S_IWUSR)
    except Exception:
        pass

    os.replace(tmp, path)
    print(f"Wrote config: {path}")
    return 0


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(prog="miniflux.py", add_help=True)
    sub = p.add_subparsers(dest="cmd", required=True)

    p_cfg = sub.add_parser("configure", help="Write/update config file")
    p_cfg.add_argument("--url", help="Miniflux base URL, e.g. https://reader.example.com")
    p_cfg.add_argument("--token", help="Miniflux API token")
    p_cfg.set_defaults(func=cmd_configure)

    p_cat = sub.add_parser("categories", help="List categories")
    p_cat.add_argument("--json", action="store_true", help="Output raw JSON")
    p_cat.set_defaults(func=cmd_categories)

    p_entries = sub.add_parser("entries", help="List entries")
    p_entries.add_argument("--status", default="unread", choices=["unread", "read", "removed"], help="Entry status")
    p_entries.add_argument("--limit", type=int, default=20, help="Max entries")
    p_entries.add_argument("--order", default="published_at", help="Order field")
    p_entries.add_argument("--direction", default="desc", choices=["asc", "desc"], help="Sort direction")
    p_entries.add_argument("--category", help="Category title (exact match)")
    p_entries.add_argument("--category-id", type=int, help="Category id")
    p_entries.add_argument("--json", action="store_true", help="Output raw JSON")
    p_entries.set_defaults(func=cmd_entries)

    p_entry = sub.add_parser("entry", help="Fetch one entry")
    p_entry.add_argument("id", type=int, help="Entry id")
    p_entry.add_argument("--json", action="store_true", help="Output raw JSON")
    p_entry.add_argument("--full", action="store_true", help="Print full content (instead of preview)")
    p_entry.add_argument("--format", default="text", choices=["text", "html"], help="Content format when printing")
    p_entry.set_defaults(func=cmd_entry)

    p_mr = sub.add_parser("mark-read", help="Mark entries as read (explicit only)")
    p_mr.add_argument("ids", nargs="+", type=int, help="Entry id(s) to mark as read")
    p_mr.add_argument("--confirm", action="store_true", help="Required safety flag")
    p_mr.set_defaults(func=cmd_mark_read)

    p_mrc = sub.add_parser("mark-read-category", help="Mark ALL unread entries in a category as read (explicit only)")
    p_mrc.add_argument("category", nargs="?", help="Category title (exact match)")
    p_mrc.add_argument("--category-id", type=int, help="Category id")
    p_mrc.add_argument("--limit", type=int, default=500, help="Safety limit: max entries to mark read")
    p_mrc.add_argument("--confirm", action="store_true", help="Required safety flag")
    p_mrc.set_defaults(func=cmd_mark_read_category)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
