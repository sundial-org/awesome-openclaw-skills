"""Scan Outlook Desktop inbox for recent messages that likely need a reply.

Requires: pywin32 (win32com)

This is intentionally best-effort. Outlook/MAPI threading and "already replied" detection
is imperfect, so we combine a few weak signals.

Usage:
  python scripts/scan_outlook.py --days 7 --max-items 200 --mode report
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import time
from datetime import datetime, timedelta

try:
    import win32com.client  # type: ignore
except Exception as e:
    print("Missing dependency: pywin32. Install with: pip install pywin32", file=sys.stderr)
    raise

from state import load_state, is_snoozed


def load_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def normalize(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").strip())


def message_key(msg) -> str:
    # Prefer stable IDs when available
    try:
        imid = getattr(msg, "InternetMessageID", None)
        if imid:
            return f"imid:{imid}"
    except Exception:
        pass
    # Fallback
    try:
        subj = normalize(getattr(msg, "Subject", ""))
        received = getattr(msg, "ReceivedTime", None)
        received_s = str(received) if received else ""
        sender = normalize(getattr(msg, "SenderEmailAddress", ""))
        return f"fallback:{sender}|{received_s}|{subj}"
    except Exception:
        return f"fallback:{id(msg)}"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default=os.path.join("references", "config.json"))
    ap.add_argument("--days", type=int, default=None)
    ap.add_argument("--max-items", type=int, default=None)
    ap.add_argument("--mode", choices=["report"], default="report")
    args = ap.parse_args()

    cfg = load_config(args.config)
    o = cfg.get("outlook", {})
    days = args.days if args.days is not None else int(o.get("days", 7))
    max_items = args.max_items if args.max_items is not None else int(o.get("maxItems", 200))

    state_path = cfg.get("state", {}).get("path", os.path.join("state", "state.json"))
    st = load_state(state_path)

    since = datetime.now() - timedelta(days=days)

    outlook = win32com.client.Dispatch("Outlook.Application")
    ns = outlook.GetNamespace("MAPI")

    mailbox = o.get("mailbox") or None
    if mailbox:
        root = ns.Folders.Item(mailbox)
    else:
        root = ns.GetDefaultFolder(6)  # olFolderInbox

    # If mailbox was provided, look for Inbox under it
    inbox = root
    try:
        if mailbox:
            inbox = root.Folders.Item("Inbox")
    except Exception:
        inbox = root

    items = inbox.Items
    items.Sort("[ReceivedTime]", True)

    action_keywords = [k.lower() for k in o.get("actionKeywords", [])]
    subject_bcast = [k.lower() for k in o.get("broadcastSubjectKeywords", [])]
    sender_bcast = [k.lower() for k in o.get("broadcastSenderDomains", [])]
    body_bcast = [k.lower() for k in o.get("broadcastBodyKeywords", [])]
    ignore_cc_only = bool(o.get("ignoreIfOnlyCc", True))

    flagged = []
    scanned = 0

    for msg in items:
        if scanned >= max_items:
            break
        scanned += 1

        try:
            received = msg.ReceivedTime
            # COM datetime -> python datetime
            received_dt = datetime.fromtimestamp(time.mktime(received.timetuple()))
        except Exception:
            continue

        if received_dt < since:
            break

        try:
            subject = normalize(msg.Subject)
            body = (msg.Body or "")
            sender = normalize(getattr(msg, "SenderEmailAddress", ""))
            to_line = normalize(getattr(msg, "To", ""))
            cc_line = normalize(getattr(msg, "CC", ""))
            unread = bool(getattr(msg, "UnRead", False))
        except Exception:
            continue

        key = message_key(msg)
        if key in st.dismissed:
            continue
        if is_snoozed(st, key):
            continue

        subj_l = subject.lower()
        sender_l = sender.lower()

        # Broadcast-ish filters
        if any(k in subj_l for k in subject_bcast):
            continue
        if any(k in sender_l for k in sender_bcast):
            continue
        body_lite = (body or "")[:4000].lower()
        if any(k in body_lite for k in body_bcast):
            continue

        # CC-only heuristic
        if ignore_cc_only and to_line.strip() == "" and cc_line.strip() != "":
            # Not perfect, but reduces noise
            continue

        # Action-needed heuristic
        text_l = (subject + "\n" + body[:2000]).lower()
        hits = [k for k in action_keywords if k in text_l]

        # If unread, we still flag even without keyword hits.
        if not unread and not hits:
            continue

        reason = []
        if unread:
            reason.append("unread")
        if hits:
            reason.append("keywords: " + ", ".join(sorted(set(hits))[:6]))

        flagged.append(
            {
                "key": key,
                "subject": subject,
                "sender": sender,
                "received": received_dt.isoformat(timespec="minutes"),
                "to": to_line,
                "cc": cc_line,
                "reason": "; ".join(reason),
            }
        )

    print(json.dumps({"since": since.isoformat(timespec="minutes"), "count": len(flagged), "items": flagged[:50]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
