"""Draft email replies for an Outlook Desktop message.

Requires: pywin32 (win32com)

This script can:
- Locate a recent message by subject keyword
- Print reply drafts (short + normal)
- Optionally create an Outlook Draft Reply (does NOT send)

NOTE: Actual text generation is done by the OpenClaw agent; this script is for
retrieval + creating the Outlook draft container.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timedelta

try:
    import win32com.client  # type: ignore
except Exception:
    print("Missing dependency: pywin32. Install with: pip install pywin32", file=sys.stderr)
    raise


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mailbox", default=None, help="Mailbox display name (optional)")
    ap.add_argument("--subject", required=True, help="Subject keyword to search")
    ap.add_argument("--days", type=int, default=7)
    ap.add_argument("--out", default="thread.json")
    ap.add_argument("--create-draft", action="store_true")
    args = ap.parse_args()

    outlook = win32com.client.Dispatch("Outlook.Application")
    ns = outlook.GetNamespace("MAPI")

    if args.mailbox:
        root = ns.Folders.Item(args.mailbox)
        try:
            inbox = root.Folders.Item("Inbox")
        except Exception:
            inbox = root
    else:
        inbox = ns.GetDefaultFolder(6)  # Inbox

    items = inbox.Items
    items.Sort("[ReceivedTime]", True)

    since = datetime.now() - timedelta(days=args.days)
    subj_kw = args.subject.lower()

    target = None
    for msg in items:
        try:
            received = msg.ReceivedTime
            received_dt = datetime.fromtimestamp(received.timestamp())
        except Exception:
            # Fallback if timestamp not available
            try:
                received_dt = datetime.fromtimestamp(received)
            except Exception:
                continue

        if received_dt < since:
            break

        try:
            subject = (msg.Subject or "")
        except Exception:
            continue

        if subj_kw in subject.lower():
            target = msg
            break

    if not target:
        print(f"No message found in last {args.days} days for subject containing: {args.subject}", file=sys.stderr)
        return 2

    # Extract minimal thread context
    data = {
        "subject": target.Subject,
        "sender": getattr(target, "SenderName", ""),
        "senderEmail": getattr(target, "SenderEmailAddress", ""),
        "received": str(getattr(target, "ReceivedTime", "")),
        "to": getattr(target, "To", ""),
        "cc": getattr(target, "CC", ""),
        "body": (target.Body or "")[:8000],
    }

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    if args.create_draft:
        reply = target.Reply()
        # Leave Body empty for the agent to fill, but keep the container open as Draft.
        reply.Save()
        print("Created Outlook draft reply.")

    print(f"Wrote thread context to: {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
