"""Scan Microsoft Teams for recent items that likely need a reply.

This uses Microsoft Graph + MSAL device code flow (delegated permissions).

Improvements vs naive scans:
- Includes a short message preview so reminders are actionable.
- Best-effort "already replied" detection in 1:1 chats.
- If the user replied but clearly deferred ("I'll do it later"), keep nagging.

Usage:
  python scripts/teams_scan.py --config references/config.json --days 7

Output: JSON with items.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

import msal
import requests


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _strip_html(s: str) -> str:
    """Very small HTML-to-text helper for Graph message bodies.

    Graph returns HTML. We don't want to pull in heavy parsers here.
    Preserve emoji alt text when present.
    """

    s = s or ""

    # Newlines
    s = s.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    s = s.replace("&nbsp;", " ")

    # Preserve Teams emoji alt="😅" etc.
    s = re.sub(r"<emoji[^>]*\salt=\"([^\"]+)\"[^>]*></emoji>", r"\1", s, flags=re.IGNORECASE)

    # Replace <at ...>Name</at> with Name
    s = re.sub(r"<at[^>]*>(.*?)</at>", r"\1", s, flags=re.IGNORECASE | re.DOTALL)

    # Drop remaining tags
    s = re.sub(r"<[^>]+>", "", s)

    return s


def _preview(s: str, n: int = 240) -> str:
    s = re.sub(r"\s+", " ", (s or "").strip())
    if len(s) <= n:
        return s
    return s[: n - 1] + "…"


def iso_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def graph_get(token: str, url: str, params: dict | None = None) -> dict:
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, params=params, timeout=30)
    if r.status_code >= 400:
        raise RuntimeError(f"Graph GET failed {r.status_code}: {r.text}")
    return r.json()


def acquire_token(cfg: dict) -> str:
    tcfg = cfg.get("teams", {})
    tenant_id = tcfg.get("tenantId")
    client_id = tcfg.get("clientId")
    scopes = tcfg.get("scopes") or ["User.Read"]
    if not tenant_id or not client_id:
        raise RuntimeError("Missing teams.tenantId or teams.clientId in config")

    cache_path = tcfg.get("tokenCachePath") or os.path.join("state", "teams_token_cache.bin")
    cache = msal.SerializableTokenCache()
    if os.path.exists(cache_path):
        cache.deserialize(open(cache_path, "r", encoding="utf-8").read())

    app = msal.PublicClientApplication(
        client_id=client_id,
        authority=f"https://login.microsoftonline.com/{tenant_id}",
        token_cache=cache,
    )

    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(scopes, account=accounts[0])

    if not result:
        flow = app.initiate_device_flow(scopes=scopes)
        if "user_code" not in flow:
            raise RuntimeError(f"Failed to initiate device flow: {flow}")
        print(flow["message"], file=sys.stderr)
        result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(f"Token acquisition failed: {result}")

    if cache.has_state_changed:
        os.makedirs(os.path.dirname(cache_path), exist_ok=True)
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(cache.serialize())

    return result["access_token"]


def _parse_graph_dt(s: str) -> datetime:
    """Parse Graph timestamps reliably on Python 3.10.

    Graph may return fractional seconds with 1–7 digits.
    We normalize the fraction to 6 digits.
    """

    s = s.replace("Z", "+00:00")
    if "." in s:
        head, tail = s.split(".", 1)
        if "+" in tail:
            frac, tz = tail.split("+", 1)
            tz = "+" + tz
        elif "-" in tail[1:]:
            frac, tz = tail.split("-", 1)
            tz = "-" + tz
        else:
            frac, tz = tail, ""
        frac = (frac + "000000")[:6]
        s = f"{head}.{frac}{tz}"
    return datetime.fromisoformat(s)


def _is_deferral(text: str) -> bool:
    """Heuristic: user replied but explicitly deferred the action."""

    t = (text or "").lower()
    patterns = [
        "later",
        "tomorrow",
        "next week",
        "after some time",
        "in some time",
        "will do",
        "i'll do",
        "i will do",
        "will check",
        "i'll check",
        "i will check",
        "will get back",
        "i'll get back",
        "remind me",
        "ping me",
    ]
    return any(p in t for p in patterns)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("references", "config.json"))
    ap.add_argument("--days", type=int, default=7)
    args = ap.parse_args()

    cfg = load_config(args.config)
    token = acquire_token(cfg)

    since = datetime.now(timezone.utc) - timedelta(days=args.days)

    me = graph_get(token, "https://graph.microsoft.com/v1.0/me")
    my_id = me.get("id")

    tcfg = cfg.get("teams", {})
    action_keywords = [k.lower() for k in (tcfg.get("actionKeywords") or [])]
    monitor = tcfg.get("monitor", {}) or {}
    include_one_on_one = bool(monitor.get("includeOneOnOne", True))
    include_group = bool(monitor.get("includeGroup", True))

    items: list[dict] = []

    max_chats = int(monitor.get("maxChats", 20))
    max_msgs = int(monitor.get("maxMessagesPerChat", 20))

    chats = graph_get(token, "https://graph.microsoft.com/v1.0/me/chats", params={"$top": max_chats})
    for chat in chats.get("value", []):
        chat_id = chat.get("id")
        if not chat_id:
            continue

        chat_type = (chat.get("chatType") or "").lower()  # oneOnOne|group|meeting
        is_group = chat_type in ("group", "meeting")
        if is_group and not include_group:
            continue
        if (not is_group) and (not include_one_on_one):
            continue

        msgs = graph_get(
            token,
            f"https://graph.microsoft.com/v1.0/chats/{chat_id}/messages",
            params={"$top": max_msgs, "$orderby": "createdDateTime desc"},
        )

        latest_my_reply_dt: datetime | None = None
        latest_my_reply_text: str = ""

        for m in msgs.get("value", []):
            created = m.get("createdDateTime")
            if not created:
                continue
            created_dt = _parse_graph_dt(created)
            if created_dt < since:
                continue

            body_html = ((m.get("body") or {}).get("content")) or ""
            body_text = _strip_html(body_html)
            body_l = body_text.lower()

            frm = ((m.get("from") or {}).get("user") or {})
            from_name = frm.get("displayName", "")
            from_id = frm.get("id", "")

            if my_id and from_id and from_id == my_id:
                if latest_my_reply_dt is None:
                    latest_my_reply_dt = created_dt
                    latest_my_reply_text = body_text
                continue

            mentions = m.get("mentions") or []
            mentioned_me = (
                any((((x.get("mentioned") or {}).get("user") or {}).get("id")) == my_id for x in mentions)
                if my_id
                else False
            )

            mentioned_all = False
            for x in mentions:
                mentioned = (x.get("mentioned") or {})
                display = (mentioned.get("displayName") or "")
                if display and display.lower() in ("everyone", "all", "team"):
                    mentioned_all = True
            if "@everyone" in body_l or "@all" in body_l:
                mentioned_all = True

            is_question = "?" in body_text
            keyword_hits = [k for k in action_keywords if k and k in body_l]

            needs_reply = False
            reason: list[str] = []

            if (chat_type not in ("group", "meeting")):
                if is_question:
                    needs_reply = True
                    reason.append("question")
                if keyword_hits:
                    needs_reply = True
                    reason.append("keywords: " + ", ".join(sorted(set(keyword_hits))[:5]))

                replied_after = bool(latest_my_reply_dt and latest_my_reply_dt > created_dt)
                deferred = bool(replied_after and _is_deferral(latest_my_reply_text))
                if needs_reply and replied_after and not deferred:
                    needs_reply = False
                    reason.append("replied_after")
                elif needs_reply and replied_after and deferred:
                    reason.append("replied_after_deferral")

            else:
                if mentioned_me and bool(monitor.get("flagGroupIfMentionedMe", True)):
                    needs_reply = True
                    reason.append("mentioned_you")
                if mentioned_all and bool(monitor.get("flagGroupBroadcast", True)):
                    reason.append("broadcast")
                    if is_question or keyword_hits:
                        needs_reply = True

            items.append(
                {
                    "kind": "teams.chat.message",
                    "chatId": chat_id,
                    "chatType": chat.get("chatType"),
                    "topic": chat.get("topic"),
                    "messageId": m.get("id"),
                    "webUrl": m.get("webUrl"),
                    "created": created,
                    "from": from_name,
                    "fromId": from_id,
                    "preview": _preview(body_text, 240),
                    "mentionedMe": bool(mentioned_me),
                    "broadcast": bool(mentioned_all),
                    "question": bool(is_question),
                    "keywordHits": keyword_hits[:8],
                    "needsReply": bool(needs_reply),
                    "reason": "; ".join(reason) if reason else "",
                    "myReplyCreated": latest_my_reply_dt.isoformat(timespec="seconds") if latest_my_reply_dt else None,
                    "myReplyPreview": _preview(latest_my_reply_text, 120) if latest_my_reply_text else "",
                }
            )

    # Windows console may be cp1252; ensure we can print emojis/unicode.
    payload = json.dumps(
        {
            "generatedAt": iso_now(),
            "since": since.isoformat(timespec="seconds"),
            "count": len(items),
            "items": items[:50],
        },
        ensure_ascii=False,
        indent=2,
    )
    sys.stdout.buffer.write(payload.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
